from typing import Any, Dict, List, Optional
from pydantic import BaseModel

class MemoryStoreRequest(BaseModel):
    collection_name: str
    data: Dict[str, Any]

class MemoryRetrieveParams(BaseModel):
    collection_name: str
    query: str
    top_k: Optional[int] = 5

class MemoryRetrieveResponse(BaseModel):
    results: List[Dict[str, Any]]

class MemoryUpdateRequest(BaseModel):
    collection_name: str
    data: Dict[str, Any]

class MemoryDeleteRequest(BaseModel):
    collection_name: str
    match_criteria: Dict[str, Any]

class MemoryResponse(BaseModel):
    message: str