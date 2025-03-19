from typing import Optional, Type
from langchain_core.tools import BaseTool
from pydantic import BaseModel, Field
from langchain_core.callbacks import CallbackManagerForToolRun
from gru.agents.tools.core.code_loader.github import GitHubLoader
from gru.agents.tools.core.code_analyzer.argument import ArgumentAnalyzer


class PythonArgumentsToolInput(BaseModel):
    repository: str = Field(description="repository containing the python file")
    file_path: str = Field(description="path of the python file in the repository")


class PythonArgumentsTool(BaseTool):
    name: str = "get_python_file_arguments"
    description: str = (
        "Use this to determine the command line arguments that are required to execute a python file present in a repository"
    )
    args_schema: Type[BaseModel] = PythonArgumentsToolInput
    return_direct: bool = True

    class Config:
        extra = "allow"

    def __init__(self, token: str):
        super().__init__(token=token)
        self.token = token
        self.code_loader = GitHubLoader(token)
        self.analyzer = ArgumentAnalyzer()

    def _run(self, *args, **kwargs):
        return super()._run(*args, **kwargs)
    
    async def _arun(
        self,
        repository: str,
        file_path: str,
        run_manager: Optional[CallbackManagerForToolRun] = None,
    ):
        
        source = self.code_loader.retrieve_code(repository, file_path)
        
        
        arg_details = self.analyzer.analyze(source)

        return arg_details
