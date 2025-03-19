from pydantic import BaseModel
from typing import List


class QueryIntent(BaseModel):
    entities: List[str]
    domains: List[str]


class RetrievalResult(BaseModel):
    tables: List[str]
    schemas: List[str]
    documentation: List[str]
    examples: List[str]
    low_cardinality_values: List[str] = []
    domain_knowledge: List[str] = []
    opt_rules: List[str] = []
