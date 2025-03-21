from typing import Optional, Type
from langchain_core.tools import BaseTool
from pydantic import BaseModel, Field
from langchain_core.callbacks import CallbackManagerForToolRun
from gru.agents.tools.core.code_loader.github import GitHubLoader


class GitRepoContentToolInput(BaseModel):
    repository: str = Field(
        description="repository of which the contents are to be retrieved"
    )


class GitRepoContentRetriever(BaseTool):
    name: str = "get_git_repo_contents"
    description: str = (
        "Use this to get file paths of all the files in a github repository"
    )
    args_schema: Type[BaseModel] = GitRepoContentToolInput
    return_direct: bool = True

    class Config:
        extra = "allow"

    def __init__(self, token: str):
        super().__init__(token=token)
        self.token = token
        self.code_loader = GitHubLoader(token)

    def _run(self, *args, **kwargs):
        return super()._run(*args, **kwargs)

    async def _arun(
        self,
        repository: str,
        run_manager: Optional[CallbackManagerForToolRun] = None,
    ):
    
        result = self.code_loader.list_contents(repository)
        return result
