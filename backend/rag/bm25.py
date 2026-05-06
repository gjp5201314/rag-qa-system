import math
from typing import List, Dict, Any, Tuple
from collections import Counter
import re

class BM25:
    def __init__(self, k1: float = 1.5, b: float = 0.75):
        self.k1 = k1
        self.b = b
        self.avg_doc_length = 0
        self.doc_lengths = []
        self.doc_freqs = {}
        self.idf = {}
        self.num_docs = 0
        self.corpus = []

    def index(self, documents: List[str]):
        self.corpus = documents
        self.num_docs = len(documents)
        self.doc_lengths = []
        self.doc_freqs = {}

        for doc in documents:
            doc = doc.lower()
            terms = self._tokenize(doc)
            self.doc_lengths.append(len(terms))
            self.avg_doc_length = sum(self.doc_lengths) / self.num_docs if self.num_docs > 0 else 0

            unique_terms = set(terms)
            for term in unique_terms:
                self.doc_freqs[term] = self.doc_freqs.get(term, 0) + 1

        for term, df in self.doc_freqs.items():
            self.idf[term] = math.log((self.num_docs - df + 0.5) / (df + 0.5) + 1)

    def add_documents(self, documents: List[str]):
        if not documents:
            return
            
        for doc in documents:
            self.corpus.append(doc)
            self.num_docs += 1
            
            doc = doc.lower()
            terms = self._tokenize(doc)
            self.doc_lengths.append(len(terms))
            
            unique_terms = set(terms)
            for term in unique_terms:
                self.doc_freqs[term] = self.doc_freqs.get(term, 0) + 1

        total_length = sum(self.doc_lengths)
        self.avg_doc_length = total_length / self.num_docs if self.num_docs > 0 else 0

        for term, df in self.doc_freqs.items():
            self.idf[term] = math.log((self.num_docs - df + 0.5) / (df + 0.5) + 1)

    def _tokenize(self, text: str) -> List[str]:
        text = text.lower()
        tokens = re.findall(r'\w+', text)
        return [t for t in tokens if len(t) > 1]

    def get_scores(self, query: str) -> List[float]:
        query_terms = self._tokenize(query.lower())
        scores = []

        for i, doc in enumerate(self.corpus):
            doc_terms = self._tokenize(doc.lower())
            doc_term_freqs = Counter(doc_terms)
            score = 0.0
            doc_length = self.doc_lengths[i]

            for term in query_terms:
                if term not in self.idf:
                    continue

                tf = doc_term_freqs.get(term, 0)
                idf = self.idf[term]

                numerator = tf * (self.k1 + 1)
                denominator = tf + self.k1 * (1 - self.b + self.b * doc_length / self.avg_doc_length)

                score += idf * (numerator / denominator) if denominator > 0 else 0

            scores.append(score)

        return scores

    def search(self, query: str, top_k: int = 5) -> List[Tuple[int, float]]:
        scores = self.get_scores(query)
        indexed_scores = list(enumerate(scores))
        sorted_scores = sorted(indexed_scores, key=lambda x: x[1], reverse=True)
        return sorted_scores[:top_k]

class HybridSearch:
    def __init__(self, alpha: float = 0.7):
        self.alpha = alpha
        self.bm25 = BM25()
        self.vector_results_cache = {}
        self.doc_id_to_index = {}
        self.initialized = False

    def index_documents(self, documents: List[str], doc_ids: List[str] = None):
        if not self.initialized:
            self.bm25.index(documents)
            self.initialized = True
            if doc_ids:
                self.doc_id_to_index = {doc_id: idx for idx, doc_id in enumerate(doc_ids)}
        else:
            base_idx = len(self.bm25.corpus)
            self.bm25.add_documents(documents)
            if doc_ids:
                for i, doc_id in enumerate(doc_ids):
                    self.doc_id_to_index[doc_id] = base_idx + i
            
        self.vector_results_cache = {}

    def search(self, query: str, vector_results: List[Dict[str, Any]],
               top_k: int = 5) -> List[Dict[str, Any]]:
        bm25_scores = self.bm25.get_scores(query)

        max_bm25 = max(bm25_scores) if bm25_scores and max(bm25_scores) > 0 else 1
        bm25_normalized = [s / max_bm25 for s in bm25_scores]

        for i, result in enumerate(vector_results):
            result_id = result.get('id', '')
            vector_score = 1 - result.get('distance', 1.0)
            vector_score = max(0, min(1, vector_score))

            if result_id in self.doc_id_to_index:
                idx = self.doc_id_to_index[result_id]
                if idx < len(bm25_normalized):
                    bm25_norm = bm25_normalized[idx]
                    combined_score = self.alpha * vector_score + (1 - self.alpha) * bm25_norm
                else:
                    combined_score = vector_score
            else:
                idx_score = i / max(len(vector_results), 1)
                bm25_norm = bm25_normalized[i] if i < len(bm25_normalized) else idx_score
                combined_score = self.alpha * vector_score + (1 - self.alpha) * bm25_norm

            result['combined_score'] = combined_score
            result['vector_score'] = vector_score
            result['bm25_score'] = bm25_norm

        vector_results.sort(key=lambda x: x.get('combined_score', 0), reverse=True)
        return vector_results[:top_k]
