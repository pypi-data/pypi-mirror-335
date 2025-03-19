import os
from typing import Optional, Type
from langchain_core.tools import BaseTool
from pydantic import BaseModel, Field
from langchain_core.runnables import RunnableConfig
from langchain_core.callbacks import CallbackManagerForToolRun

from gru.agents.checkpoint.task_results import TaskResultsRepository, TaskStatus
from gru.agents.task_server.celery import TaskMetadata, submit_task


class PythonCodeRunnerInput(BaseModel):
    repository: str = Field(description="code repository which has the code to execute")
    file_path_to_execute: str = Field(
        description="path of the python file in the repository"
    )
    arguments: list[str] = Field(
        description="arguments required to execute the python file"
    )
    run_id: str = Field(description="random unique id to identify each run")


class PythonCodeRunner(BaseTool):
    name: str = "run_python_code"
    description: str = (
        "use this tool to submit a python file present in a repository for execution."
    )
    args_schema: Type[BaseModel] = PythonCodeRunnerInput
    return_direct: bool = True

    class Config:
        extra = "allow"

    def __init__(self, token: str):
        task_results_repo = TaskResultsRepository()
        super().__init__(token=token, task_results_repo=task_results_repo)
        self.token = token
        self.task_results_repo = task_results_repo

    def _run(self, *args, **kwargs):
        return super()._run(*args, **kwargs)

    async def _arun(
        self,
        repository: str,
        file_path_to_execute: str,
        arguments: list[str],
        run_id: str,
        config: RunnableConfig,
        run_manager: Optional[CallbackManagerForToolRun] = None,
    ):
        agent_url = os.getenv("AGENT_URL")
        agent_name = os.getenv("AGENT_NAME")

        metadata = TaskMetadata(
            prompt_id=config["metadata"]["thread_id"],
            tool_call_id=run_id,
            agent_name=agent_name,
            agent_callback_url=f"http://{agent_url}/save-task-result",
        )

        task_attributes = {
            "repository": repository,
            "token": self.token,
            "file_path_to_execute": file_path_to_execute,
            "arguments": arguments,
        }

        submit_task(self.name, metadata, task_attributes)
        await self.task_results_repo.update(
            agent_name,
            config["metadata"]["thread_id"],
            self.name,
            run_id,
            TaskStatus.PROCESSING,
        )

        return "The python file has been submitted for execution with run_id {run_id}. Ask the user to check the status later."
