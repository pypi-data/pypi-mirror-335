from abc import ABC, abstractmethod
from typing import Any

class CodeAnalyzer(ABC):
    """Abstract base class for code analysis."""
    
    @abstractmethod
    def analyze(self, source_code: str) -> Any:
        """
        Analyze the provided source code.
        
        Args:
            source_code: Source code as a string
            
        Returns:
            Analysis results, type depends on the specific analyzer
        """
        pass
