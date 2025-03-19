from typing import List, Optional
from github import Github, Auth
from gru.agents.tools.core.code_loader.base import CodeLoader
import os

class GitHubLoader(CodeLoader):
    """Implementation of CodeLoader for GitHub repositories."""
    
    def __init__(self, token: Optional[str] = None):
        """
        Initialize with GitHub token.
        
        Args:
            token: GitHub authentication token. If None, will attempt to use GITHUB_TOKEN environment variable.
        """
        
        self.token = token or os.environ.get("GITHUB_TOKEN")
        
        if self.token is None:
            raise ValueError("GitHub token not provided and GITHUB_TOKEN environment variable not set")

    def _get_repo(self, identifier: str):
        """
        Get a GitHub repository object.
        
        Args:
            identifier: Repository name in format "owner/repo"
            
        Returns:
            A GitHub repository object
        """
        auth = Auth.Token(self.token)
        g = Github(auth=auth)
        return g.get_repo(identifier)
    
        
    def retrieve_code(self, identifier: str, path: Optional[str] = None) -> str:
        """
        Retrieve code from a GitHub repository.
        
        Args:
            identifier: Repository name in format "owner/repo"
            path: File path within the repository
            
        Returns:
            The source code as a string
        """
        
        repo = self._get_repo(identifier)
        
        contents = repo.get_contents(path)
        return contents.decoded_content.decode()
    
    def list_contents(self, identifier: str, path: Optional[str] = "") -> List[str]:
        """
        List all file paths in a GitHub repository.
        
        Args:
            identifier: Repository name in format "owner/repo"
            path: Optional directory path within the repository to start listing from
            
        Returns:
            List of file paths in the repository
        """
        
        repo = self._get_repo(identifier)
        contents = repo.get_contents(path or "")
        
        result = []
        while contents:
            file_content = contents.pop(0)
            if file_content.type == "dir":
                contents.extend(repo.get_contents(file_content.path))
            else:
                result.append(file_content.path)
                
        return result
