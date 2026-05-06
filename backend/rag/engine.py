from typing import List, Dict, Any, Optional, Tuple
import uuid
from pathlib import Path
import json

from utils.config import Config
from utils.logger import logger
from rag.document_processor import DocumentProcessor
from rag.embedder import Embedder
from rag.vector_store import VectorStore
from rag.bm25 import HybridSearch
from rag.reranker import Reranker

class RAGEngine:
    def __init__(self, collection_name: str = "default"):
        self.collection_name = collection_name
        self.doc_processor = DocumentProcessor()
        self.embedder = Embedder()
        self.vector_store = VectorStore(collection_name)
        self.hybrid_search = HybridSearch(alpha=Config.HYBRID_ALPHA)
        self.reranker = Reranker()

    def load_document(self, file_path: str, kb_id: int, doc_id: int) -> bool:
        try:
            file_path_obj = Path(file_path)
            file_type = file_path_obj.suffix.lstrip('.').lower()

            logger.info(f"Loading document: {file_path}, type: {file_type}")

            chunks = self.doc_processor.process_file(file_path, file_type)

            if not chunks:
                logger.warning(f"No chunks extracted from {file_path}")
                return False

            self._index_chunks(chunks, kb_id, doc_id)

            logger.info(f"Document loaded successfully: {doc_id}, chunks: {len(chunks)}")
            return True

        except Exception as e:
            logger.error(f"Failed to load document: {e}")
            return False

    def _index_chunks(self, chunks: List[Dict[str, Any]], kb_id: int, doc_id: int):
        if not chunks:
            return

        batch_size = 50
        total_batches = (len(chunks) + batch_size - 1) // batch_size

        for batch_idx in range(total_batches):
            start_idx = batch_idx * batch_size
            end_idx = min(start_idx + batch_size, len(chunks))
            batch_chunks = chunks[start_idx:end_idx]

            texts = [chunk['content'] for chunk in batch_chunks]
            embeddings = self.embedder.embed_documents(texts)

            ids = [f"kb{kb_id}_doc{doc_id}_chunk{start_idx + i}" for i in range(len(batch_chunks))]
            documents = texts
            metadatas = [
                {
                    "kb_id": kb_id,
                    "doc_id": doc_id,
                    "chunk_id": batch_chunks[i]['chunk_id'],
                    "source_file": batch_chunks[i]['source_file'],
                    "char_count": batch_chunks[i]['char_count']
                }
                for i in range(len(batch_chunks))
            ]

            self.vector_store.add_vectors(ids, embeddings, documents, metadatas)
            logger.info(f"Indexed batch {batch_idx + 1}/{total_batches} ({len(batch_chunks)} chunks)")

        self._incremental_bm25_index(texts, ids)

    def _sync_bm25_index(self):
        self.vector_store.get_or_create_collection()
        all_docs = self.vector_store.collection.get(include=["documents", "metadatas"])
        if all_docs and all_docs['documents']:
            vector_ids = all_docs.get('ids', [])
            self.hybrid_search.index_documents(all_docs['documents'], vector_ids)

    def _incremental_bm25_index(self, texts: List[str], ids: List[str]):
        if texts and ids:
            self.hybrid_search.index_documents(texts, ids)
            logger.info(f"Indexed {len(texts)} documents to BM25")

    def search(self, query: str, kb_id: Optional[int] = None,
               top_k: int = None, rerank: bool = True) -> List[Dict[str, Any]]:
        if top_k is None:
            top_k = Config.TOP_K

        try:
            self.vector_store.get_or_create_collection()
            if self.vector_store.get_count() == 0:
                logger.info("Knowledge base is empty, skipping search")
                return []

            query_embedding = self.embedder.embed_query(query)

            filter_metadata = {"kb_id": kb_id} if kb_id else None

            vector_results = self.vector_store.search(
                query_embedding,
                top_k=top_k * 2,
                filter_metadata=filter_metadata
            )

            if not vector_results:
                logger.info("No vector search results")
                return []

            hybrid_results = self.hybrid_search.search(
                query,
                vector_results,
                top_k=top_k * 2
            )

            if rerank:
                reranked_results = self.reranker.rerank(
                    query,
                    hybrid_results,
                    top_k=Config.RERANK_TOP_K
                )
                return reranked_results

            return hybrid_results[:top_k]

        except Exception as e:
            logger.error(f"Search failed: {e}")
            return []

    def delete_document_vectors(self, doc_id: int):
        try:
            filter_metadata = {"doc_id": doc_id}
            self.vector_store.delete_by_filter(filter_metadata)
            self._sync_bm25_index()
            logger.info(f"Deleted vectors for document: {doc_id}")
        except Exception as e:
            logger.error(f"Failed to delete document vectors: {e}")

    def delete_knowledge_base_vectors(self, kb_id: int):
        try:
            filter_metadata = {"kb_id": kb_id}
            self.vector_store.delete_by_filter(filter_metadata)
            self._sync_bm25_index()
            logger.info(f"Deleted vectors for knowledge base: {kb_id}")
        except Exception as e:
            logger.error(f"Failed to delete KB vectors: {e}")
