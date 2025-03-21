from gru.agents.tools.core.code_generator.sql import SQLCodeGenerator
from gru.agents.tools.core.context_retriever.sql import SQLContextRetriever
from gru.agents.tools.core.embeddings.base import EmbeddingGenerator
from gru.agents.tools.core.code_generator.models import QueryIntent, RetrievalResult, SQLQueryResult
from gru.agents.tools.core.llm_client.base import LLMClient
from gru.agents.prompts.text_to_sql import (
    QUERY_ANALYZER_USER_PROMPT_TEMPLATE,
    QUERY_ANALYZER_SYSTEM_PROMPT,
)

from gru.agents.clients.vector_db.base import VectorDBClient


class TextToSQLService:
    def __init__(
        self,
        llm_client: LLMClient,
        embedding_generator: EmbeddingGenerator,
        vector_db_client: VectorDBClient
    ):
        self.llm_client = llm_client
        self.context_retriever = SQLContextRetriever(embedding_generator, vector_db_client)
        self.code_generator = SQLCodeGenerator(llm_client)

    async def convert_to_sql(self, query: str) -> str:
        try:
            intent = await self._analyze_query(query)
            context = await self.context_retriever.retrieve_context(query, top_k=5)
            sql_query_result = await self._generate_sql(query, intent, context)

            # await self.context_retriever.store_conversation(query, sql)

            return sql_query_result.sql_query
        except Exception as e:
            return f"Error while generating SQL query: {str(e)}"
            

    async def _analyze_query(self, query: str) -> QueryIntent:
        user_prompt = QUERY_ANALYZER_USER_PROMPT_TEMPLATE.format(query=query)
        response = await self.llm_client.generate(
            QUERY_ANALYZER_SYSTEM_PROMPT, user_prompt
        )

        # TODO - Response parsing logic is a placeholder - will define proper response models later.

        lines = response.split("\n")
        entities = lines[0].replace("Entities:", "").strip().strip("[]").split(",")
        domains = lines[1].replace("Domains:", "").strip().strip("[]").split(",")

        return QueryIntent(
            entities=[e.strip() for e in entities if e.strip()],
            domains=[d.strip() for d in domains if d.strip()],
        )

    async def _generate_sql(
        self, query: str, intent: QueryIntent, context: RetrievalResult
    ) -> SQLQueryResult:
        return await self.code_generator.generate_code(query, intent, context)
