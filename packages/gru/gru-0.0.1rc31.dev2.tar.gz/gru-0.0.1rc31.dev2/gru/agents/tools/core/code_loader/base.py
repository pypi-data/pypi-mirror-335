from abc import ABC, abstractmethod
from typing import List, Optional


class CodeLoader(ABC):
    """Abstract base class for code loading from different sources."""
    
    @abstractmethod
    def retrieve_code(self, identifier: str, path: Optional[str] = None) -> str:
        """
        Retrieve code from a source.
        
        Args:
            identifier: Source identifier (e.g. repository name)
            path: Optional path within the source
            
        Returns:
            The source code as a string
        """
        pass
    
    @abstractmethod
    def list_contents(self, identifier: str, path: Optional[str] = None) -> List[str]:
        """
        List all file paths in a source.
        
        Args:
            identifier: Source identifier (e.g. repository name)
            path: Optional path within the source to start listing from
            
        Returns:
            List of file paths
        """
        pass
