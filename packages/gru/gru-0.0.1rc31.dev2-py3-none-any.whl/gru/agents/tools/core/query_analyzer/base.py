from abc import ABC, abstractmethod
from gru.agents.tools.core.code_generator.models import QueryIntent


class QueryAnalyzer(ABC):
    def __init__(self, llm_client):
        self.llm_client = llm_client

    @abstractmethod
    def analyze_query(self, query: str) -> QueryIntent:
        pass
