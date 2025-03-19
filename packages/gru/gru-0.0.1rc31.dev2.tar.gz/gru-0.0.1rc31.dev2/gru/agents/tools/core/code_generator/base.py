from abc import ABC, abstractmethod
from gru.agents.tools.core.code_generator.models import QueryIntent, RetrievalResult


class CodeGenerator(ABC):
    def __init__(self, llm_client):
        self.llm_client = llm_client

    @abstractmethod
    async def generate_code(
        self, query: str, intent: QueryIntent, context: RetrievalResult
    ) -> str:
        pass
