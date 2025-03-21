from abc import ABC, abstractmethod
from typing import Any, Dict, List

class MemoryEntityRepository(ABC):
    
    @abstractmethod
    def store(self, data: Dict[str, Any]):
        pass

    @abstractmethod
    def update(self, data: Dict[str, Any]):
        pass

    @abstractmethod
    def delete(self, match_criteria: Dict[str, Any]):
        pass

    @abstractmethod
    def search(self, query: str, top_k:int) -> List[Dict[str, Any]]:
        pass