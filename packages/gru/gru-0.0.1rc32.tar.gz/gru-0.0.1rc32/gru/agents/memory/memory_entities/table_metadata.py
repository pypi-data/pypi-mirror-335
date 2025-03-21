from typing import Any, Dict, List
from gru.agents.tools.core.embeddings.base import EmbeddingGenerator
from gru.agents.memory.memory_entities.base import MemoryEntityRepository
from gru.agents.clients.vector_db.base import VectorDBClient
from gru.agents.clients.vector_db.models import CollectionField, CollectionIndex, CollectionModel, FieldDataType

class TableMetadataRepository(MemoryEntityRepository):

    COLLECTION_NAME = "canso_table_metadata"
    VECTOR_FIELD_NAME = "schema_embeddings"

    def __init__(self, vector_db_client: VectorDBClient, embedding_generator: EmbeddingGenerator):
        self.vector_db_client = vector_db_client
        self.embedding_generator = embedding_generator

    def setup(self):
        fields = [
            CollectionField(name="table_name", is_primary=True, data_type=FieldDataType.VARCHAR, max_length=200),
            # CollectionField(name="table_description", data_type=FieldDataType.VARCHAR, max_length=2000),
            CollectionField(name="schema", data_type=FieldDataType.VARCHAR, max_length=65535),
            # CollectionField(name="table_embeddings", data_type=FieldDataType.FLOAT_VECTOR, dimension=self.embedding_generator.dimension),
            CollectionField(name="schema_embeddings", data_type=FieldDataType.FLOAT_VECTOR, dimension=self.embedding_generator.dimension)
        ]

        indexes = [
            # CollectionIndex(field_name="table_embeddings", params={"index_type": "IVF_FLAT", "metric_type": "L2"}),
            CollectionIndex(field_name="schema_embeddings", params={"index_type": "IVF_FLAT", "metric_type": "L2", "params": { "nlist": 1024 }}),
        ]

        collection = CollectionModel(
            name=self.COLLECTION_NAME,
            description="Table metadata collection",
            fields=fields,
            indexes=indexes
        )

        self.vector_db_client.create_collection(collection)
    
    
    def search_tables_and_schemas(self, query: str, top_k: int = 5) -> tuple[list[str], list[str]]:
        output_fields = ["table_name", "schema"]
        query_vector = self.embedding_generator.generate(query)
        results = self.vector_db_client.similarity_search(
            collection_name=self.COLLECTION_NAME,
            query_vector=query_vector,
            vector_field=self.VECTOR_FIELD_NAME,
            top_k=top_k,
            output_fields=output_fields
        )

        tables = [result.get("table_name", "") for result in results]
        schemas = [result.get("schema", "") for result in results]

        return tables, schemas
    
    def store(self, data: Dict[str, Any]):
        self._validate_fields(data)

        # data["table_embeddings"] = self.embedding_generator.generate(data["table_description"])
        data["schema_embeddings"] = self.embedding_generator.generate(data["schema"])

        self.vector_db_client.insert_documents(self.COLLECTION_NAME, [data])

    def update(self, data: Dict[str, Any]):
        self._validate_fields(data)
        # data["table_embeddings"] = self.embedding_generator.generate(data["table_description"])
        data["schema_embeddings"] = self.embedding_generator.generate(data["schema"])

        match_criteria = {"table_name": data["table_name"]}

        self.vector_db_client.update_document(self.COLLECTION_NAME, match_criteria, data)

    def delete(self, match_criteria: dict[str, Any]):
        self.vector_db_client.delete_document(self.COLLECTION_NAME, match_criteria)

    def search(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        query_vector = self.embedding_generator.generate(query)
        output_fields = ["table_name", "schema"]
        
        results = self.vector_db_client.similarity_search(
            collection_name=self.COLLECTION_NAME,
            vector_field=self.VECTOR_FIELD_NAME,
            query_vector=query_vector,
            top_k=top_k,
            output_fields=output_fields
        )

        return results

    def _validate_fields(self, data: Dict[str, Any]):
        required_fields = ["table_name", "schema"]
        for field in required_fields:
            if field not in data:
                raise Exception(f"Missing field {field} in data")
    
        
    
    