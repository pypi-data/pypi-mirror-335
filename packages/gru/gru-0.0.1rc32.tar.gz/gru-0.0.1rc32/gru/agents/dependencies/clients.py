from functools import lru_cache
import os

from gru.agents.clients.vector_db.base import VectorDBClient
from gru.agents.clients.vector_db.milvus import MilvusClient


vector_db_client = None
if os.getenv("VECTOR_DB_HOST") is not None:
    vector_db_type = os.getenv("VECTOR_DB_TYPE", "milvus")
    if vector_db_type == "milvus":
        vector_db_client = MilvusClient()

@lru_cache
def get_vector_db_client() -> VectorDBClient | None:
    return vector_db_client