from typing import List, Any
from gru.agents.tools.core.embeddings.base import EmbeddingGenerator


class OpenAIEmbeddingGenerator(EmbeddingGenerator):
    MODELS = {
        "text-embedding-3-small": 1536,
        "text-embedding-3-large": 3072,
        "text-embedding-ada-002": 1536
    }

    def __init__(
            self,
            client: Any,
            model: str = "text-embedding-3-small",
            batch_size: int = 100
    ):
        self.client = client
        self.model = model or "text-embedding-3-small"
        if self.model not in self.MODELS:
            raise ValueError(f"Model {model} not supported. Choose from {list(self.MODELS.keys())}")
        self.batch_size = batch_size
        self._dimension = self.MODELS[self.model]

    @property
    def dimension(self) -> int:
        return self._dimension


    def generate(self, text: str) -> List[float]:
        response = self.client.embeddings.create(
            input=text,
            model=self.model
        )
        return response.data[0].embedding


    def generate_batch(self, texts: List[str]) -> List[List[float]]:
        all_embeddings = []
        for i in range(0, len(texts), self.batch_size):
            batch = texts[i:i + self.batch_size]
            response = self.client.embeddings.create(
                input=batch,
                model=self.model
            )
            embeddings = [data.embedding for data in response.data]
            all_embeddings.extend(embeddings)
        return all_embeddings
