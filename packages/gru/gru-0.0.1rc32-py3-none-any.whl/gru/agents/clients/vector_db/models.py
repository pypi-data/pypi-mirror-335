from enum import StrEnum
from typing import Any, Dict, List
from pydantic import BaseModel

class FieldDataType(StrEnum):
    INT64 = "INT64"
    VARCHAR = "VARCHAR"
    FLOAT_VECTOR = "FLOAT_VECTOR"
    FLOAT = "FLOAT"
    BOOL = "BOOL"

class CollectionField(BaseModel):
    name: str
    is_primary: bool = False
    data_type: FieldDataType
    dimension: int | None = None
    max_length: int | None = None
    auto_id: bool = False

class CollectionIndex(BaseModel):
    field_name: str
    params: Dict[str, Any]

class CollectionModel(BaseModel):
    name: str
    description: str
    fields: List[CollectionField]
    indexes: List[CollectionIndex]

