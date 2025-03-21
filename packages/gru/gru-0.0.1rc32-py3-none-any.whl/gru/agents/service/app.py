from contextlib import asynccontextmanager
import json
import os
from typing import Annotated, Optional
from fastapi import BackgroundTasks, Depends, FastAPI, Header, Response
import uvicorn
from gru.agents.checkpoint.task_results import TaskResultsRepository, TaskStatus
from gru.agents.framework_wrappers import AgentWorkflow
from gru.agents.memory.canso_memory import CansoMemory
from gru.agents.schemas import AgentInvokeRequest, AgentInvokeResponse
from gru.agents.schemas.schemas import AgentConversationRequest, TaskCompleteRequest
import logging
from gru.agents.utils.logging import get_log_fields

from gru.agents.schemas.memory import (
    MemoryRetrieveResponse,
    MemoryStoreRequest,
    MemoryRetrieveParams,
    MemoryUpdateRequest,
    MemoryDeleteRequest,
    MemoryResponse
)

agent_name = os.getenv("AGENT_NAME")

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

@asynccontextmanager
async def lifespan(app: FastAPI):

    workflow: AgentWorkflow = app.state.workflow
    await workflow.setup()
    app.state.task_results_repo = TaskResultsRepository()
    await app.state.task_results_repo.setup()
    yield


api = FastAPI(lifespan=lifespan)

def get_memory() -> CansoMemory:
    return api.state.memory

async def invoke_workflow(request: AgentInvokeRequest):
    try:
        workflow: AgentWorkflow = api.state.workflow
        output = await workflow.invoke(request)
        # Todo: Save output to DB table
        print(output)
    except Exception as e:
        logger.error(
            f"AI agent: invoke api failed - {e}",
            extra=get_log_fields(correlation_id=request.prompt_id),
        )


async def resume_workflow(request: TaskCompleteRequest):
    try:
        workflow: AgentWorkflow = api.state.workflow
        output = await workflow.resume(request)
        # Todo: Save output to DB table
        print(output)
    except Exception as e:
        logger.error(
            f"AI agent: resume workflow failed: {e}",
            extra=get_log_fields(correlation_id=request.prompt_id),
        )


async def update_task_result(request: TaskCompleteRequest):
    try:
        task_results_repo: TaskResultsRepository = api.state.task_results_repo
        await task_results_repo.update(
            agent_name,
            request.prompt_id,
            request.task_type,
            request.tool_call_id,
            TaskStatus.COMPLETED,
            json.dumps(request.result),
        )
    except Exception as e:
        logger.error(
            f"AI agent: Error while upddating task result - {e}",
            extra=get_log_fields(correlation_id=request.prompt_id),
        )


@api.post("/invoke")
async def invoke(
    request: AgentInvokeRequest, background_tasks: BackgroundTasks
) -> AgentInvokeResponse:
    background_tasks.add_task(invoke_workflow, request)
    return AgentInvokeResponse(prompt_id=request.prompt_id)


@api.post("/converse")
async def converse(request: AgentConversationRequest):
    try:
        workflow: AgentWorkflow = api.state.workflow
        return await workflow.converse(request)
    except Exception as e:
        logger.error(
            f"AI agent converse api failed: {e}",
            extra=get_log_fields(correlation_id=request.conversation_id),
        )
        raise e


@api.post("/task-complete")
async def task_complete(
    request: TaskCompleteRequest, background_tasks: BackgroundTasks
):
    background_tasks.add_task(resume_workflow, request)
    return Response(status_code=200)


@api.post("/save-task-result")
async def save_task_result(
    request: TaskCompleteRequest, background_tasks: BackgroundTasks
):
    background_tasks.add_task(update_task_result, request)
    return Response(status_code=200)


@api.post("/memory", response_model=MemoryResponse)
async def store_memory(
    correlation_id: Annotated[str, Header()],
    request: MemoryStoreRequest, 
    memory: CansoMemory = Depends(get_memory)
):
    try:
        memory.store(request)
        return MemoryResponse(message="Document stored successfully")
    except Exception as e:
        logger.error(
            f"Failed to store memory: {e}",
            extra=get_log_fields(correlation_id=correlation_id),
        )
        raise e

@api.get("/memory", response_model=MemoryRetrieveResponse)
async def retrieve_memory(
    correlation_id: Annotated[str, Header()],
    params: MemoryRetrieveParams = Depends(), 
    memory: CansoMemory = Depends(get_memory)
):
    try:
        results = memory.search(params)
        return MemoryRetrieveResponse(results=results)
    except Exception as e:
        logger.error(
            f"Failed to retrieve memory: {e}",
            extra=get_log_fields(correlation_id=correlation_id),
        )
        raise e

@api.patch("/memory", response_model=MemoryResponse)
async def update_memory(
    correlation_id: Annotated[str, Header()],
    request: MemoryUpdateRequest, 
    memory: CansoMemory = Depends(get_memory)
):
    try:
        memory.update(request)
        return MemoryResponse(message="Document updated successfully")
    except Exception as e:
        logger.error(
            f"Failed to update memory: {e}",
            extra=get_log_fields(correlation_id=correlation_id),
        )
        raise e

@api.delete("/memory", response_model=MemoryResponse)
async def delete_memory(
    correlation_id: Annotated[str, Header()],
    request: MemoryDeleteRequest, 
    memory: CansoMemory = Depends(get_memory)
):

    try:
        memory.delete(request)
        return MemoryResponse(message="Document deleted successfully")
    except Exception as e:
        logger.error(
            f"Failed to delete memory: {e}",
            extra=get_log_fields(correlation_id=correlation_id),
        )
        raise e


class App:


    def __init__(self, workflow: AgentWorkflow, memory: Optional[CansoMemory] = None):

        api.state.workflow = workflow
        if memory is not None:
            api.state.memory = memory

    def run(self):
        uvicorn.run(api, host="0.0.0.0", port=8080)
