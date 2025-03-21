from typing import Optional
from langchain_core.tools import BaseTool
from pydantic import BaseModel, Field
from langchain_core.callbacks import CallbackManagerForToolRun
from gru.agents.framework_wrappers.memory import CansoMemory


class MemoryQueryInput(BaseModel):
    """Input for memory query operations."""
    collection_name: str = Field(
        description="Name of the memory collection to search within"
    )
    query: str = Field(
        description="Natural language query to find relevant information in memory"
    )
    top_k: int = Field(
        default=5, 
        description="Number of most relevant results to return"
    )


class MemoryRetrievalTool(BaseTool):
    """Tool for retrieving information from CansoMemory."""
    
    name: str = "query_memory"
    description: str = "Use this tool to retrieve information from memory based on natural language queries"
    args_schema: type[BaseModel] = MemoryQueryInput
    return_direct: bool = False
    memory: CansoMemory = Field(description="CansoMemory instance to use for retrieval")

    
    def __init__(self, memory: CansoMemory):
        super().__init__(memory=memory)
        self.memory = memory
    
    def _run(self, *args, **kwargs):
        raise NotImplementedError("This tool only supports async")
    
    async def _arun(
        self,
        collection_name: str,
        query: str,
        top_k: int = 5,
        run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> str:
        try:
            results = await self.memory.retrieve(
                query=query,
                collection_name=collection_name,
                top_k=top_k
            )
            
            if not results:
                return "No relevant information found in memory."
            
            # Format the results into a readable response
            response = f"Found {len(results)} relevant memories:\n\n"
            
            for i, result in enumerate(results, 1):
                score = result.get("score", 0.0)
                text = result.get("text", "")
                
                # Format any metadata worth displaying
                metadata_str = ""
                if metadata := result.get("metadata"):
                    if isinstance(metadata, dict):
                        important_meta = {k: v for k, v in metadata.items() 
                                          if k not in ["embedding", "created_at"]}
                        if important_meta:
                            metadata_str = "\nMetadata: " + ", ".join(f"{k}: {v}" 
                                          for k, v in important_meta.items())
                
                response += f"{i}. [Relevance: {score:.2f}] {text}{metadata_str}\n\n"
            
            return response
            
        except Exception as e:
            return f"Error retrieving from memory: {str(e)}"
