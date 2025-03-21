from pydantic import BaseModel
from typing import List, Optional

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

class SQLQueryResult(BaseModel):
    sql_query: str
    tables_used: Optional[List[str]] = None
    columns_used: Optional[List[str]] = None
    join_conditions: Optional[List[str]] = None