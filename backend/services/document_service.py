import os
import uuid
from pathlib import Path
from typing import Optional, List, Dict, Any

from models.database import db
from rag.engine import RAGEngine
from utils.config import Config
from utils.logger import logger

class DocumentService:
    def __init__(self):
        self.rag_engines: Dict[int, RAGEngine] = {}

    def get_rag_engine(self, kb_id: int) -> RAGEngine:
        if kb_id not in self.rag_engines:
            self.rag_engines[kb_id] = RAGEngine(collection_name=f"kb_{kb_id}")
        return self.rag_engines[kb_id]

    def upload_document(self, file, kb_id: int) -> Dict[str, Any]:
        try:
            if not file:
                return {"success": False, "error": "No file provided"}

            filename = file.filename
            ext = Path(filename).suffix.lstrip('.').lower()

            if ext not in Config.ALLOWED_EXTENSIONS:
                return {"success": False, "error": f"File type not allowed: {ext}"}

            kb = db.get_knowledge_base(kb_id)
            if not kb:
                return {"success": False, "error": "Knowledge base not found"}

            unique_filename = f"{uuid.uuid4().hex}_{filename}"
            file_path = Config.KNOWLEDGE_BASES_DIR / str(kb_id) / unique_filename
            file_path.parent.mkdir(parents=True, exist_ok=True)

            file.save(str(file_path))
            file_size = os.path.getsize(str(file_path))

            doc_id = db.create_document(
                kb_id=kb_id,
                filename=filename,
                file_path=str(file_path),
                file_size=file_size,
                file_type=ext
            )

            logger.info(f"Document uploaded: {filename}, doc_id: {doc_id}")

            return {
                "success": True,
                "doc_id": doc_id,
                "filename": filename,
                "file_size": file_size
            }

        except Exception as e:
            logger.error(f"Document upload failed: {e}")
            return {"success": False, "error": str(e)}

    def process_document(self, doc_id: int, kb_id: int) -> bool:
        try:
            doc = db.get_document(doc_id)
            if not doc:
                logger.error(f"Document not found: {doc_id}")
                return False

            db.update_document_status(doc_id, "processing")

            rag_engine = self.get_rag_engine(kb_id)
            success = rag_engine.load_document(doc['file_path'], kb_id, doc_id)

            if success:
                chunks_count = rag_engine.vector_store.get_count()
                db.update_document_status(doc_id, "completed", chunks_count)
                logger.info(f"Document processed successfully: {doc_id}")
            else:
                db.update_document_status(doc_id, "failed")
                logger.error(f"Document processing failed: {doc_id}")

            return success

        except Exception as e:
            logger.error(f"Document processing error: {e}")
            db.update_document_status(doc_id, "failed")
            return False

    def get_documents(self, kb_id: Optional[int] = None) -> List[Dict[str, Any]]:
        return db.get_documents(kb_id)

    def get_document(self, doc_id: int) -> Optional[Dict[str, Any]]:
        return db.get_document(doc_id)

    def delete_document(self, doc_id: int) -> bool:
        try:
            doc = db.get_document(doc_id)
            if not doc:
                return False

            kb_id = doc['knowledge_base_id']
            rag_engine = self.get_rag_engine(kb_id)
            rag_engine.delete_document_vectors(doc_id)

            if os.path.exists(doc['file_path']):
                os.remove(doc['file_path'])

            db.delete_document(doc_id)

            logger.info(f"Document deleted: {doc_id}")
            return True

        except Exception as e:
            logger.error(f"Document deletion failed: {e}")
            return False

doc_service = DocumentService()
