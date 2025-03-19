import json
import os
from typing import Any, List

import psycopg
from psycopg_pool import AsyncConnectionPool
from gru.agents.checkpoint.postgres import PostgresAsyncConnectionPool
from gru.agents.framework_wrappers import AgentWorkflow
from langgraph.graph import StateGraph

from gru.agents.schemas import AgentInvokeRequest
from langchain_core.runnables import RunnableConfig
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver

from gru.agents.schemas.schemas import (
    AgentConversationRequest,
    AgentConversationResponse,
    TaskCompleteRequest,
)
from langchain_core.messages import ToolMessage


class LanggraphWorkflow(AgentWorkflow):

    def __init__(
        self, stateGraph: StateGraph, interrupt_before: List[str] | None = None
    ) -> None:
        super().__init__()
        self.state_graph = stateGraph
        self.interrupt_before = interrupt_before

    async def setup(self):
        checkpoint_db_type = os.getenv("CHECKPOINT_DB_TYPE", "postgres")
        if checkpoint_db_type == "postgres":
            pool = PostgresAsyncConnectionPool().get()
            checkpointer = await self._setup_postgres_checkpointer(pool)
            if self.interrupt_before is not None:
                self.compiled_graph = self.state_graph.compile(
                    checkpointer=checkpointer, interrupt_before=self.interrupt_before
                )
            else:
                self.compiled_graph = self.state_graph.compile(
                    checkpointer=checkpointer
                )

    async def _setup_postgres_checkpointer(self, pool: AsyncConnectionPool):
        checkpointer = AsyncPostgresSaver(pool)
        async with pool.connection() as conn:
            async with conn.cursor() as cur:
                try:
                    await cur.execute(
                        """
                        SELECT EXISTS (
                            SELECT FROM information_schema.tables 
                            WHERE  table_schema = 'public'
                            AND    table_name   = 'checkpoints'
                        );
                    """
                    )
                    table_exists = (await cur.fetchone())[0]

                    if not table_exists:
                        print("Checkpoints table does not exist. Running setup...")
                        await checkpointer.setup()
                    else:
                        print("Checkpoints table already exists. Skipping setup.")
                except psycopg.Error as e:
                    print(f"Error checking for checkpoints table: {e}")
                    raise e
        return checkpointer

    async def invoke(self, request: AgentInvokeRequest) -> dict[str, Any]:
        config = RunnableConfig(
            configurable={"thread_id": request.prompt_id},
        )
        return await self.compiled_graph.ainvoke(
            input=request.prompt_body, config=config
        )

    async def resume(self, request: TaskCompleteRequest) -> dict[str, Any]:
        config = RunnableConfig(
            configurable={"thread_id": request.prompt_id},
        )
        state = await self.compiled_graph.aget_state(config=config)

        ## todo : Support for Custom state?
        await self.compiled_graph.aupdate_state(
            config=config,
            values={
                "messages": [
                    ToolMessage(
                        content=json.dumps(request.result),
                        name=request.task_type,
                        tool_call_id=request.tool_call_id,
                    )
                ]
            },
            as_node=state.next[0],
        )

        result = await self.compiled_graph.ainvoke(input=None, config=config)
        return result

    async def converse(
        self, request: AgentConversationRequest
    ) -> AgentConversationResponse:
        config = RunnableConfig(configurable={"thread_id": request.conversation_id})
        user_message = request.message
        messages = await self._get_invocation_message_based_on_state(
            config, user_message
        )

        await self.compiled_graph.ainvoke(messages, config=config)
        agent_message = await self._get_agent_message_based_on_state(config)

        return AgentConversationResponse(message=agent_message)

    async def _get_invocation_message_based_on_state(self, config, user_message):
        snapshot = await self.compiled_graph.aget_state(config)
        pending_tool_calls = self._get_pending_tool_calls(snapshot)
        if pending_tool_calls and len(pending_tool_calls) > 0:
            # Scenario 1: when graph was interrupted to get toolcall confirmation from user.
            if user_message.strip() == "y" or user_message.strip() == "Y":
                # Scenario 1.1: when user confirms the tool call. The graph continues with tool call execution.
                messages = None
            else:
                # Scenario 1.2: when user denies tool call with some input. Tool response is fabricated as below.
                messages = {
                    "messages": [
                        ToolMessage(
                            tool_call_id=pending_tool_calls[0]["id"],
                            content=f"Tool call denied by user. Reasoning: '{user_message}'. Continue assisting, accounting for the user's input.",
                        )
                    ]
                }
        else:
            # Scenario 2: Normal user message
            messages = {"messages": ("user", user_message)}
        return messages

    async def _get_agent_message_based_on_state(self, config):
        snapshot = await self.compiled_graph.aget_state(config)
        pending_tool_calls = self._get_pending_tool_calls(snapshot)
        if pending_tool_calls and len(pending_tool_calls) > 0:
            # Scenario 1: When graph is interrupted to get tool call confirmation from user
            result = self._prepare_tool_call_confirmation_message(pending_tool_calls)
        else:
            # Scenario 2: Normal Agent Message
            result = snapshot.values["messages"][-1].content
        return result

    def _prepare_tool_call_confirmation_message(self, pending_tool_calls):
        result = f"I'll be calling the tool {pending_tool_calls[0]['name']} with following arguments:\n"
        args = pending_tool_calls[0]["args"]
        for arg in args:
            result = result + f"{arg}: {args[arg]}\n"
        result = (
            result
            + "Do you approve of this action? Type 'y' to continue; otherwise, explain your requested changed."
        )
        return result

    def _get_pending_tool_calls(self, snapshot):
        return snapshot.values["messages"][-1].tool_calls if snapshot.next else None
