import os
from typing import Optional, Type
from pydantic import BaseModel, Field
from langchain_core.runnables import RunnableConfig
from langchain_core.callbacks import CallbackManagerForToolRun
from langchain_core.tools import BaseTool

from gru.agents.checkpoint.task_results import TaskResultsRepository, TaskStatus


class PythonRunStatusToolInput(BaseModel):
    run_id: str = Field(description="run_id of the python code run")


class PythonRunStatusChecker(BaseTool):
    name: str = "get_python_run_status"
    description: str = "use this to get the status of a python code run"
    args_schema: Type[BaseModel] = PythonRunStatusToolInput
    return_direct: bool = True

    class Config:
        extra = "allow"

    def __init__(self):
        task_results_repo = TaskResultsRepository()
        super().__init__(task_results_repo=task_results_repo)
        self.task_results_repo = task_results_repo

    def _run(self, *args, **kwargs):
        return super()._run(*args, **kwargs)

    async def _arun(
        self,
        run_id: str,
        config: RunnableConfig,
        run_manager: Optional[CallbackManagerForToolRun] = None,
    ):
        agent_name = os.getenv("AGENT_NAME")
        result = await self.task_results_repo.get_result(
            agent_name, config["metadata"]["thread_id"], "run_python_code", run_id
        )

        if result:
            status, result_text = result
            if status == TaskStatus.PROCESSING.value:
                return status
            elif status == TaskStatus.COMPLETED.value:
                return result_text
        else:
            return "Python run task result not found"
