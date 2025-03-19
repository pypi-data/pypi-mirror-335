from typing import Any, Dict, List
from gru.agents.dependencies.clients import get_vector_db_client
from gru.agents.schemas.memory import MemoryDeleteRequest, MemoryRetrieveParams, MemoryStoreRequest, MemoryUpdateRequest
from gru.agents.tools.core.embeddings.base import EmbeddingGenerator
from gru.agents.memory.memory_entities.base import MemoryEntityRepository
from gru.agents.memory.memory_entities.domain_knowledge import DomainKnowledgeRepository
from gru.agents.memory.memory_entities.examples import ExamplesRepository
from gru.agents.memory.memory_entities.table_metadata import TableMetadataRepository

class CansoMemory:

    def __init__(self, embedding_generator: EmbeddingGenerator):
        self.embedding_generator = embedding_generator
        self.vector_db_client = get_vector_db_client()

    def get_repository(self, collection_name: str) -> MemoryEntityRepository:
        match collection_name:
            case "canso_table_metadata":
                return TableMetadataRepository(self.vector_db_client, self.embedding_generator)
            case "canso_examples":
                return ExamplesRepository(self.vector_db_client, self.embedding_generator)
            case "canso_domain_knowledge":
                return DomainKnowledgeRepository(self.vector_db_client, self.embedding_generator)
            case _:
                raise Exception(f"Invalid collection name {collection_name}")
            
    def store(self, request: MemoryStoreRequest):
        repo = self.get_repository(request.collection_name)
        repo.store(request.data)

    def update(self, request: MemoryUpdateRequest):
        repo = self.get_repository(request.collection_name)
        repo.update(request.data)

    def delete(self, request: MemoryDeleteRequest):
        repo = self.get_repository(request.collection_name)
        repo.delete(request.match_criteria)

    def search(self, request: MemoryRetrieveParams) -> List[Dict[str, Any]]:
        repo = self.get_repository(request.collection_name)
        return repo.search(request.query, request.top_k)
        
            