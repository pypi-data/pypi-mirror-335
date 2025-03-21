from abc import ABC, abstractmethod
from typing import Optional


class LLMClient(ABC):
    @abstractmethod
    async def generate(self, system_prompt: str, user_prompt: str) -> Optional[str]:
        pass
