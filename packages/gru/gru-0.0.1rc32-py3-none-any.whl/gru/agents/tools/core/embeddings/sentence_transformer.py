# from typing import List, Any
# from sentence_transformers import SentenceTransformer
# from gru.agents.tools.core.embeddings.base import EmbeddingGenerator
#
#
# class SentenceTransformerEmbeddingGenerator(EmbeddingGenerator):
#     MODELS = {
#         "all-MiniLM-L6-v2": 384,
#         "all-mpnet-base-v2": 768,
#         "paraphrase-multilingual-MiniLM-L12-v2": 384
#     }
#
#     def __init__(
#             self,
#             client: Any,
#             model: str = "all-MiniLM-L6-v2",
#             batch_size: int = 32
#     ):
#         self.client = client
#         if model not in self.MODELS:
#             raise ValueError(f"Model {model} not supported. Choose from {list(self.MODELS.keys())}")
#
#         self.model_name = model
#         self.model = SentenceTransformer(model)
#         self.batch_size = batch_size
#         self._dimension = self.MODELS[model]
#
#     @property
#     def dimension(self) -> int:
#         return self._dimension
#
#     async def generate(self, text: str) -> List[float]:
#         """Generate embeddings for a single text string"""
#         embedding = self.model.encode(text)
#         return embedding.tolist()
#
#     async def generate_batch(self, texts: List[str]) -> List[List[float]]:
#         """Generate embeddings for a batch of text strings"""
#         all_embeddings = []
#         for i in range(0, len(texts), self.batch_size):
#             batch = texts[i:i + self.batch_size]
#             embeddings = self.model.encode(batch)
#             # Convert numpy arrays to lists for serialization
#             embeddings_list = [emb.tolist() for emb in embeddings]
#             all_embeddings.extend(embeddings_list)
#         return all_embeddings