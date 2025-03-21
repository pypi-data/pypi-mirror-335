from typing import Any, Dict, List
from gru.agents.tools.core.embeddings.base import EmbeddingGenerator
from gru.agents.memory.memory_entities.base import MemoryEntityRepository
from gru.agents.clients.vector_db.base import VectorDBClient
from gru.agents.clients.vector_db.models import CollectionField, CollectionIndex, CollectionModel, FieldDataType


class ExamplesRepository(MemoryEntityRepository):

    COLLECTION_NAME = "canso_examples"
    VECTOR_FIELD_NAME = "embeddings"

    def __init__(self, vector_db_client: VectorDBClient, embedding_generator: EmbeddingGenerator):
        self.vector_db_client = vector_db_client
        self.embedding_generator = embedding_generator

    def setup(self):
        fields = [
            CollectionField(name="name", is_primary=True, data_type=FieldDataType.VARCHAR, max_length=200),
            CollectionField(name="description", data_type=FieldDataType.VARCHAR, max_length=65535),
            CollectionField(name="content", data_type=FieldDataType.VARCHAR, max_length=65535),
            CollectionField(name="embeddings", data_type=FieldDataType.FLOAT_VECTOR, dimension=self.embedding_generator.dimension)
        ]

        indexes = [
            CollectionIndex(field_name="embeddings", params={"index_type": "IVF_FLAT", "metric_type": "L2", "params": { "nlist": 1024 }})
        ]

        collection = CollectionModel(
            name=self.COLLECTION_NAME,
            description="Example queries collection",
            fields=fields,
            indexes=indexes
        )

        self.vector_db_client.create_collection(collection)

    def get_examples(self, query: str, top_k: int = 5):
        query_vector = self.embedding_generator.generate(query)
        output_fields = ["content"]
        
        results = self.vector_db_client.similarity_search(
            collection_name=self.COLLECTION_NAME,
            vector_field=self.VECTOR_FIELD_NAME,
            query_vector=query_vector,
            top_k=top_k,
            output_fields=output_fields
        )
        return [result.get("content", "") for result in results]
    
    def store(self, data: Dict[str, Any]):
        self._validate_fields(data)

        data["embeddings"] = self.embedding_generator.generate(data["content"])
        self.vector_db_client.insert_documents(self.COLLECTION_NAME, [data])

    def update(self, data: Dict[str, Any]):
        self._validate_fields(data)
        data["embeddings"] = self.embedding_generator.generate(data["content"])

        match_criteria = {"name": data["name"]}

        self.vector_db_client.update_document(self.COLLECTION_NAME, match_criteria, data)

    def delete(self, match_criteria: dict[str, Any]):
        self.vector_db_client.delete_document(self.COLLECTION_NAME, match_criteria)

    def search(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        query_vector = self.embedding_generator.generate(query)
        output_fields = ["name", "description", "content"]
        
        results = self.vector_db_client.similarity_search(
            collection_name=self.COLLECTION_NAME,
            vector_field=self.VECTOR_FIELD_NAME,
            query_vector=query_vector,
            top_k=top_k,
            output_fields=output_fields
        )

        return results

    def _validate_fields(self, data: Dict[str, Any]):
        required_fields = ["name", "description", "content"]
        for field in required_fields:
            if field not in data:
                raise Exception(f"Missing field {field} in data")