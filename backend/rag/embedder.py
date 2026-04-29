from typing import List, Dict, Any, Optional
import numpy as np

from utils.config import Config
from utils.logger import logger

class Embedder:
    def __init__(self, model_name: Optional[str] = None):
        self.model_name = model_name or Config.BGE_MODEL
        self._model = None
        self._tokenizer = None

    def _load_model(self):
        if self._model is None:
            try:
                from transformers import AutoModel, AutoTokenizer
                logger.info(f"Loading BGE model: {self.model_name}")
                self._tokenizer = AutoTokenizer.from_pretrained(self.model_name)
                self._model = AutoModel.from_pretrained(self.model_name)
                self._model.eval()
                logger.info("BGE model loaded successfully")
            except Exception as e:
                logger.error(f"Failed to load BGE model: {e}")
                raise

    def embed_query(self, query: str) -> np.ndarray:
        self._load_model()
        return self._embed_single(query)

    def embed_documents(self, texts: List[str]) -> List[np.ndarray]:
        self._load_model()
        return self._embed_batch(texts)

    def _embed_single(self, text: str) -> np.ndarray:
        import torch
        with torch.no_grad():
            inputs = self._tokenizer(text, return_tensors="pt", padding=True,
                                     truncation=True, max_length=512)
            outputs = self._model(**inputs)
            embedding = outputs.last_hidden_state[:, 0, :].numpy()
        return self._normalize(embedding[0])

    def _embed_batch(self, texts: List[str]) -> List[np.ndarray]:
        import torch
        with torch.no_grad():
            inputs = self._tokenizer(texts, return_tensors="pt", padding=True,
                                     truncation=True, max_length=512)
            outputs = self._model(**inputs)
            embeddings = outputs.last_hidden_state[:, 0, :].numpy()
        return [self._normalize(emb) for emb in embeddings]

    def _normalize(self, vector: np.ndarray) -> np.ndarray:
        norm = np.linalg.norm(vector)
        if norm == 0:
            return vector
        return vector / norm

    def get_dimension(self) -> int:
        self._load_model()
        import torch
        dummy_input = self._tokenizer("test", return_tensors="pt")
        with torch.no_grad():
            output = self._model(**dummy_input)
        return output.last_hidden_state.shape[-1]
