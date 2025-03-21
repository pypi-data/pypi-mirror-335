from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

from gru.agents.clients.vector_db.models import CollectionModel


class VectorDBClient(ABC):
    
    @abstractmethod
    def create_collection(self, schema: CollectionModel):
        pass

    @abstractmethod
    def delete_collection(self, collection_name: str):
        pass

    @abstractmethod
    def list_collections(self) -> list[str]:
        pass

    @abstractmethod
    def get_collection_info(self, collection_name: str) -> CollectionModel:
        pass

    @abstractmethod
    def insert_documents(self, collection_name: str, documents: List[Dict[str, Any]]):
        pass

    @abstractmethod
    def update_document(self, collection_name: str, match_criteria: Dict[str, Any], document: Dict[str, Any]):
        pass

    @abstractmethod
    def delete_document(self, collection_name: str, match_criteria: Dict[str, Any]):
        pass

    @abstractmethod
    def similarity_search(
        self, 
        collection_name: str, 
        vector_field: str, 
        query_vector: list[float], 
        top_k: int, 
        search_params: Optional[Dict[str, Any]],
        output_fields: Optional[List[str]]
    ) -> list[Dict[str, Any]]:
        pass