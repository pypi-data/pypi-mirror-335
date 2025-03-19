from typing import Optional, Type
from pydantic import BaseModel, Field
from langchain_core.tools import BaseTool
from langchain_core.callbacks import CallbackManagerForToolRun
from gru.agents.dependencies.clients import get_vector_db_client
from gru.agents.tools.core.embeddings.base import EmbeddingGenerator
from gru.agents.tools.core.llm_client.base import LLMClient
from gru.agents.tools.core.services.text_to_sql import TextToSQLService

class SQLQueryGeneratorInput(BaseModel):
    query: str = Field(description="Natural language input for generating SQL query")

class SQLQueryGeneratorTool(BaseTool):
    name: str = "sql_query_generator"
    description: str = "Use this tool to generate sql queries."
    args_schema: Type[BaseModel] = SQLQueryGeneratorInput
    return_direct: bool = True

    class Config:
        extra = "allow"

    def __init__(self, llm_client:LLMClient, embedding_generator: EmbeddingGenerator):
        vector_db_client = get_vector_db_client()
        if vector_db_client is None:
            raise Exception("Vector DB is mandatory for SQLQueryGeneratorTool")
        service = TextToSQLService(llm_client, embedding_generator, vector_db_client)
        super().__init__(service=service)
        self.service = service

    def _run(self, *args, **kwargs):
        return super()._run(*args, **kwargs)

    async def _arun(
        self,
        query: str,
        run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> str:
        return await self.service.convert_to_sql(query)
