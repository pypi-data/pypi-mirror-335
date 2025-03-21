from enum import Enum
from typing import Optional
from gru.agents.tools.core.embeddings.openai import OpenAIEmbeddingGenerator
# from gru.agents.tools.core.embeddings.sentence_transformer import SentenceTransformerEmbeddingGenerator
from gru.agents.tools.core.embeddings.base import EmbeddingGenerator

class EmbeddingType(Enum):
    """Enum for supported embedding types"""
    OPENAI = "openai"
    # SENTENCE_TRANSFORMER = "sentence_transformer"

class EmbeddingFactory:
    """Factory class for creating embedding generators"""
    @staticmethod
    def get_embedding_generator(
        embedding_type: EmbeddingType,
        client = None,
        model: Optional[str] = None,
        batch_size: Optional[int] = None
        ) -> EmbeddingGenerator:
        """Get an embedding generator based on the type"""
        if embedding_type == EmbeddingType.OPENAI:
            return OpenAIEmbeddingGenerator(client=client, model=model, batch_size=batch_size)
        # elif embedding_type == EmbeddingType.SENTENCE_TRANSFORMER:
        #     if model is None:
        #         model = "all-MiniLM-L6-v2"
        #     if batch_size is None:
        #         batch_size = 32
        #     return SentenceTransformerEmbeddingGenerator(client=client, model=model, batch_size=batch_size)
        else:
            raise ValueError(f"Unsupported embedding type: {embedding_type}")