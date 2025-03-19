from abc import ABC, abstractmethod
from typing import List

class EmbeddingGenerator(ABC):

    @property
    @abstractmethod
    def dimension(self) -> int:
        pass

    @abstractmethod
    def generate(self, text: str) -> List[float]:
        pass

    @abstractmethod
    def generate_batch(self, texts: List[str]) -> List[List[float]]:
        pass