from typing import List, Dict, Any, Optional, Tuple
import numpy as np
from pathlib import Path
import chromadb
from chromadb.config import Settings

from utils.config import Config
from utils.logger import logger

class VectorStore:
    def __init__(self, collection_name: str = "default"):
        self.collection_name = collection_name
        self.chroma_client = None
        self.collection = None
        self._init_chroma()

    def _init_chroma(self):
        try:
            db_path = str(Config.CHROMA_DB_DIR / self.collection_name)
            Path(db_path).parent.mkdir(parents=True, exist_ok=True)

            self.chroma_client = chromadb.PersistentClient(
                path=db_path,
                settings=Settings(anonymized_telemetry=False)
            )
            logger.info(f"Chroma DB initialized at: {db_path}")
        except Exception as e:
            logger.error(f"Failed to initialize Chroma: {e}")
            raise

    def get_or_create_collection(self, metadata: Optional[Dict[str, Any]] = None):
        try:
            self.collection = self.chroma_client.get_or_create_collection(
                name=self.collection_name,
                metadata=metadata or {"description": f"Collection {self.collection_name}"}
            )
            logger.info(f"Collection '{self.collection_name}' ready")
        except Exception as e:
            logger.error(f"Failed to get/create collection: {e}")
            raise

    def add_vectors(self, ids: List[str], embeddings: List[np.ndarray],
                   documents: List[str], metadatas: List[Dict[str, Any]]):
        if self.collection is None:
            self.get_or_create_collection()

        try:
            self.collection.add(
                ids=ids,
                embeddings=embeddings.tolist() if isinstance(embeddings[0], np.ndarray) else embeddings,
                documents=documents,
                metadatas=metadatas
            )
            logger.info(f"Added {len(ids)} vectors to collection")
        except Exception as e:
            logger.error(f"Failed to add vectors: {e}")
            raise

    def search(self, query_embedding: np.ndarray, top_k: int = 5,
               filter_metadata: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        if self.collection is None:
            self.get_or_create_collection()

        try:
            results = self.collection.query(
                query_embeddings=query_embedding.tolist() if isinstance(query_embedding, np.ndarray) else query_embedding,
                n_results=top_k,
                where=filter_metadata
            )

            search_results = []
            if results and results['ids']:
                for i in range(len(results['ids'][0])):
                    search_results.append({
                        'id': results['ids'][0][i],
                        'distance': results['distances'][0][i],
                        'document': results['documents'][0][i],
                        'metadata': results['metadatas'][0][i] if results['metadatas'] else {}
                    })
            return search_results
        except Exception as e:
            logger.error(f"Search failed: {e}")
            return []

    def delete_by_ids(self, ids: List[str]):
        if self.collection is None:
            return
        try:
            self.collection.delete(ids=ids)
            logger.info(f"Deleted {len(ids)} vectors")
        except Exception as e:
            logger.error(f"Failed to delete vectors: {e}")

    def delete_by_filter(self, filter_metadata: Dict[str, Any]):
        if self.collection is None:
            return
        try:
            self.collection.delete(where=filter_metadata)
            logger.info(f"Deleted vectors matching filter: {filter_metadata}")
        except Exception as e:
            logger.error(f"Failed to delete by filter: {e}")

    def get_count(self) -> int:
        if self.collection is None:
            return 0
        return self.collection.count()
