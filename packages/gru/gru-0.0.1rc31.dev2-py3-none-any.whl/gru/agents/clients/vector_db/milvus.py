import os
from typing import Any, Dict, List, Optional
from pymilvus import (
    Collection,
    CollectionSchema,
    DataType,
    FieldSchema,
    connections,
    utility
)
from gru.agents.clients.vector_db.base import VectorDBClient
from gru.agents.clients.vector_db.models import CollectionField, CollectionIndex, CollectionModel, FieldDataType

CANSO_TO_MILVUS_TYPES: dict[FieldDataType, DataType] = {
        FieldDataType.INT64: DataType.INT64,
        FieldDataType.VARCHAR : DataType.VARCHAR,
        FieldDataType.FLOAT_VECTOR: DataType.FLOAT_VECTOR,
        FieldDataType.FLOAT: DataType.FLOAT,
        FieldDataType.BOOL: DataType.BOOL
    }

MILVUS_TO_CANSO_TYPES: dict[DataType, FieldDataType] = {
    DataType.INT64: FieldDataType.INT64,
    DataType.VARCHAR : FieldDataType.VARCHAR,
    DataType.FLOAT_VECTOR: FieldDataType.FLOAT_VECTOR,
    DataType.FLOAT: FieldDataType.FLOAT,
    DataType.BOOL: FieldDataType.BOOL
}


class MilvusClient(VectorDBClient):

    def __init__(self):
        try:
            connections.connect(
                alias="default",
                host=os.getenv("VECTOR_DB_HOST"),
                port=int(os.getenv("VECTOR_DB_PORT", "19530")),
                user=os.getenv("VECTOR_DB_USER", "root"),
                password=os.getenv("VECTOR_DB_PASSWORD"),
                timeout=int(os.getenv("VECTOR_DB_CONNECTION_TIMEOUT", "30"))
            )
        except Exception as e:
            raise ConnectionError(f"Failed to connect to Milvus: {str(e)}")

    def _create_field_schema(self, field: CollectionField) -> FieldSchema:
        match field.data_type:
            case FieldDataType.FLOAT_VECTOR:
                if field.dimension is None:
                    raise Exception(f"Dimension is required for FLOAT_VECTOR field {field.name}")
                return FieldSchema(
                    name = field.name,
                    dtype = CANSO_TO_MILVUS_TYPES[field.data_type],
                    dim = field.dimension,
                    is_primary = field.is_primary,
                    auto_id = field.auto_id
                )
            case _:
                return FieldSchema(
                    name=field.name,
                    dtype=CANSO_TO_MILVUS_TYPES[field.data_type],
                    is_primary=field.is_primary,
                    auto_id=field.auto_id,
                    max_length=field.max_length
                )
            
    def _create_search_expression(self, match_criteria: Dict[str, Any]):
        field_criterias = []
        for key, value in match_criteria.items():
            if isinstance(value, str):
                field_criterias.append(f'{key} == "{value}"')
            else:
                 field_criterias.append(f'{key} == {value}')
        search_expression = " and ".join(field_criterias)
        return search_expression

    def create_collection(self, schema: CollectionModel):
        if utility.has_collection(schema.name):
            print(f"collection {schema.name} already exists. Skipping creation.")
            return
        
        field_schemas = [
            self._create_field_schema(field) 
            for field in schema.fields
        ]

        collection_schema = CollectionSchema(fields=field_schemas, description=schema.description)
        collection = Collection(name=schema.name, schema=collection_schema)

        for index in schema.indexes:
            collection.create_index(field_name = index.field_name, index_params=index.params)

        collection.load()
    

    def delete_collection(self, collection_name: str):
        utility.drop_collection(collection_name)

    
    def list_collections(self) -> list[str]:
        return utility.list_collections()
    
    def get_collection_info(self, collection_name) -> CollectionModel:
        if not utility.has_collection(collection_name):
            raise Exception(f"collection {collection_name} does not exist")
        
        collection = Collection(collection_name)

        fields: list[CollectionField] = []
        for field in collection.schema.fields:
            collection_field = CollectionField(
                name=field.name,
                data_type=MILVUS_TO_CANSO_TYPES[field.dtype],
                is_primary=field.is_primary
            )

            if hasattr(field, "dim") and field.dim is not None:
                collection_field.dimension = field.dim
            if hasattr(field, "max_length") and field.max_length is not None:
                collection_field.max_length = field.max_length

            fields.append(collection_field)
        
        indexes: list[CollectionIndex] = []
        for index in collection.indexes:
            indexes.append(CollectionIndex(
                field_name = index.field_name,
                params= index.params.get("params", {})
            ))
        
        return CollectionModel(
            name=collection_name,
            description=collection.schema.description,
            fields=fields,
            indexes=indexes,
        )


    def insert_documents(self, collection_name: str, documents: List[Dict[str, Any]]):
        collection = Collection(collection_name)
        collection.insert(documents)
    

    def update_document(self, collection_name: str, match_criteria: Dict[str, Any], document: Dict[str, Any]):
        collection = Collection(collection_name)

        search_expression = self._create_search_expression(match_criteria)

        result = collection.query(expr = search_expression, output_fields=list(match_criteria.keys()))
        if not result:
            raise Exception(f"Document with match criteria {match_criteria} not found")
        
        collection.delete(search_expression)

        collection.insert([document])
    

    def delete_document(self, collection_name: str, match_criteria: Dict[str, Any]):
        collection = Collection(collection_name)
        search_expression = self._create_search_expression(match_criteria)
        collection.delete(search_expression)


    def similarity_search(
        self, 
        collection_name: str, 
        vector_field: str, 
        query_vector: list[float], 
        top_k: int = 5, 
        search_params: Dict[str, Any] = {"metric_type":  "L2", "params": {"nprobe": 10}},
        output_fields: Optional[List[str]] = None
    ) -> list[Dict[str, Any]]:

        collection = Collection(collection_name)
        if output_fields is None:
            schema = collection.schema
            output_fields = [field.name for field in schema.fields 
                            if field.name != vector_field]
            
        results = collection.search(
            data=[query_vector], 
            anns_field=vector_field,
            param=search_params,
            limit=top_k,
            output_fields=output_fields,
        )

        search_results = []
        for hits in results:
            for hit in hits:
                result = {"score": hit.score}
                for field in output_fields:
                    result[field] = hit.entity.get(field)
                search_results.append(result)
        
        return search_results
    

        




        
