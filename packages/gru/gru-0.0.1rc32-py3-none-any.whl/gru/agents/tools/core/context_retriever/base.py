from abc import ABC, abstractmethod
from gru.agents.tools.core.code_generator.models import RetrievalResult


class ContextRetriever(ABC):

    @abstractmethod
    async def retrieve_context(self, query: str, top_k: int) -> RetrievalResult:
        """Retrieves all relevant context for the query"""
        pass
