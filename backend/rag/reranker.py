from typing import List, Dict, Any, Optional
import os
import numpy as np

from utils.config import Config
from utils.logger import logger

os.environ['HF_ENDPOINT'] = 'https://hf-mirror.com'

class Reranker:
    def __init__(self, model_name: Optional[str] = None):
        self.model_name = model_name or Config.RERANKER_MODEL
        self._model = None
        self._tokenizer = None

    def _load_model(self):
        if self._model is None:
            try:
                from sentence_transformers import CrossEncoder
                logger.info(f"Loading Reranker model: {self.model_name}")
                self._model = CrossEncoder(self.model_name, max_length=512)
                logger.info("Reranker model loaded successfully")
            except Exception as e:
                logger.warning(f"Failed to load reranker model: {e}, using fallback scoring")
                self._model = None

    def rerank(self, query: str, candidates: List[Dict[str, Any]],
               top_k: int = 3) -> List[Dict[str, Any]]:
        if not candidates:
            return []

        if self._model is None:
            self._load_model()

        if self._model is not None:
            try:
                return self._rerank_with_model(query, candidates, top_k)
            except Exception as e:
                logger.error(f"Rerank failed: {e}")

        return self._rerank_fallback(query, candidates, top_k)

    def _rerank_with_model(self, query: str, candidates: List[Dict[str, Any]],
                          top_k: int) -> List[Dict[str, Any]]:
        pairs = [[query, cand['document']] for cand in candidates]
        scores = self._model.predict(pairs)

        for i, cand in enumerate(candidates):
            cand['rerank_score'] = float(scores[i])
            cand['original_score'] = cand.get('combined_score', cand.get('distance', 0))
            cand['distance'] = 1 - float(scores[i])

        candidates.sort(key=lambda x: x.get('rerank_score', 0), reverse=True)
        return candidates[:top_k]

    def _rerank_fallback(self, query: str, candidates: List[Dict[str, Any]],
                        top_k: int) -> List[Dict[str, Any]]:
        query_terms = set(query.lower().split())
        for cand in candidates:
            doc_terms = set(cand['document'].lower().split())
            overlap = len(query_terms & doc_terms)
            rerank_score = overlap / max(len(query_terms), 1)
            cand['rerank_score'] = rerank_score

        candidates.sort(key=lambda x: x.get('rerank_score', 0), reverse=True)
        return candidates[:top_k]
