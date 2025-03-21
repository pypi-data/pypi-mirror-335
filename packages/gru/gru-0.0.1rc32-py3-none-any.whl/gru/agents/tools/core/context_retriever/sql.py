from gru.agents.tools.core.code_generator.models import RetrievalResult
from gru.agents.tools.core.context_retriever.base import ContextRetriever
from gru.agents.tools.core.embeddings.base import EmbeddingGenerator
from gru.agents.memory.memory_entities.examples import ExamplesRepository
from gru.agents.memory.memory_entities.domain_knowledge import DomainKnowledgeRepository
from gru.agents.memory.memory_entities.table_metadata import TableMetadataRepository
from gru.agents.clients.vector_db.base import VectorDBClient

# TODO - Support retrieval of low cardinality values
class SQLContextRetriever(ContextRetriever):
    def __init__(
        self,
        embedding_generator: EmbeddingGenerator,
        vector_db_client: VectorDBClient
    ):
        self.table_metadata_repo = TableMetadataRepository(vector_db_client, embedding_generator)
        self.table_metadata_repo.setup()

        self.table_documentation_repo = DomainKnowledgeRepository(vector_db_client, embedding_generator)
        self.table_documentation_repo.setup()

        self.example_queries_repo = ExamplesRepository(vector_db_client, embedding_generator)
        self.example_queries_repo.setup()

    async def retrieve_context(self, query: str, top_k: int = 5) -> RetrievalResult:

        tables, schemas = self.table_metadata_repo.search_tables_and_schemas(query, top_k)
        examples = self.example_queries_repo.get_examples(query, top_k)
        documentation = self.table_documentation_repo.get_documentations(query, top_k)

        return RetrievalResult(
            tables=tables,
            schemas=schemas,
            documentation=documentation,
            examples=examples
        )
