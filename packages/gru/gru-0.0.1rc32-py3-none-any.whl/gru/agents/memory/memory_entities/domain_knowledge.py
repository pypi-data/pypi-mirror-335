from typing import Any, Dict, List
from gru.agents.tools.core.embeddings.base import EmbeddingGenerator
from gru.agents.memory.memory_entities.base import MemoryEntityRepository
from gru.agents.clients.vector_db.base import VectorDBClient
from gru.agents.clients.vector_db.models import CollectionField, CollectionIndex, CollectionModel, FieldDataType


class DomainKnowledgeRepository(MemoryEntityRepository):

    COLLECTION_NAME = "canso_domain_knowledge"
    VECTOR_FIELD_NAME = "embeddings"

    def __init__(self, vector_db_client: VectorDBClient, embedding_generator: EmbeddingGenerator):
        self.vector_db_client = vector_db_client
        self.embedding_generator = embedding_generator

    def setup(self):
        fields = [
            CollectionField(name="fact", is_primary=True, data_type=FieldDataType.VARCHAR, max_length=200),
            CollectionField(name="explanation", data_type=FieldDataType.VARCHAR, max_length=65535),
            CollectionField(name="logic", data_type=FieldDataType.VARCHAR, max_length=65535),
            CollectionField(name="embeddings", data_type=FieldDataType.FLOAT_VECTOR, dimension=self.embedding_generator.dimension)
        ]

        indexes = [
            CollectionIndex(field_name="embeddings", params={"index_type": "IVF_FLAT", "metric_type": "L2", "params": { "nlist": 1024 }})
        ]

        collection = CollectionModel(
            name=self.COLLECTION_NAME,
            description="Table documentation collection",
            fields=fields,
            indexes=indexes
        )

        self.vector_db_client.create_collection(collection)

    def get_documentations(self, query: str, top_k: int = 5):
        query_vector = self.embedding_generator.generate(query)
        output_fields = ["explanation"]
        
        results = self.vector_db_client.similarity_search(
            collection_name=self.COLLECTION_NAME,
            vector_field=self.VECTOR_FIELD_NAME,
            query_vector=query_vector,
            top_k=top_k,
            output_fields=output_fields
        )
        return [result.get("explanation", "") for result in results]
    
    def store(self, data: Dict[str, Any]):
        self._validate_fields(data)

        data["embeddings"] = self.embedding_generator.generate(data["explanation"])
        self.vector_db_client.insert_documents(self.COLLECTION_NAME, [data])

    def update(self, data: Dict[str, Any]):
        self._validate_fields(data)
        data["embeddings"] = self.embedding_generator.generate(data["embeddings"])

        match_criteria = {"fact": data["fact"]}

        self.vector_db_client.update_document(self.COLLECTION_NAME, match_criteria, data)

    def delete(self, match_criteria: dict[str, Any]):
        self.vector_db_client.delete_document(self.COLLECTION_NAME, match_criteria)

    def search(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        query_vector = self.embedding_generator.generate(query)
        output_fields = ["fact", "explanation", "logic"]
        
        results = self.vector_db_client.similarity_search(
            collection_name=self.COLLECTION_NAME,
            vector_field=self.VECTOR_FIELD_NAME,
            query_vector=query_vector,
            top_k=top_k,
            output_fields=output_fields
        )

        return results

    def _validate_fields(self, data: Dict[str, Any]):
        required_fields = ["fact", "explanation", "logic"]
        for field in required_fields:
            if field not in data:
                raise Exception(f"Missing field {field} in data")