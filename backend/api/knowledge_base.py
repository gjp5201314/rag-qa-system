from flask import Blueprint, request, jsonify

from models.database import db
from services.document_service import doc_service
from utils.logger import logger

kb_bp = Blueprint('knowledge_base', __name__)

@kb_bp.route('/knowledge-bases', methods=['POST'])
def create_knowledge_base():
    try:
        data = request.get_json()
        if not data or not data.get('name'):
            return jsonify({"error": "Name is required"}), 400

        name = data['name'].strip()
        description = data.get('description', '')

        try:
            kb_id = db.create_knowledge_base(name, description)
            logger.info(f"Knowledge base created: {kb_id}")
            return jsonify({
                "id": kb_id,
                "name": name,
                "description": description,
                "message": "Knowledge base created successfully"
            }), 201
        except Exception as e:
            if "UNIQUE constraint" in str(e):
                return jsonify({"error": "Knowledge base name already exists"}), 400
            raise

    except Exception as e:
        logger.error(f"Create knowledge base error: {e}")
        return jsonify({"error": str(e)}), 500

@kb_bp.route('/knowledge-bases', methods=['GET'])
def get_knowledge_bases():
    try:
        knowledge_bases = db.get_knowledge_bases()

        for kb in knowledge_bases:
            docs = db.get_documents(kb['id'])
            kb['document_count'] = len(docs)
            kb['completed_count'] = len([d for d in docs if d['status'] == 'completed'])

        return jsonify({"knowledge_bases": knowledge_bases})
    except Exception as e:
        logger.error(f"Get knowledge bases error: {e}")
        return jsonify({"error": str(e)}), 500

@kb_bp.route('/knowledge-bases/<int:kb_id>', methods=['GET'])
def get_knowledge_base(kb_id):
    try:
        knowledge_base = db.get_knowledge_base(kb_id)
        if not knowledge_base:
            return jsonify({"error": "Knowledge base not found"}), 404

        docs = db.get_documents(kb_id)
        knowledge_base['document_count'] = len(docs)
        knowledge_base['completed_count'] = len([d for d in docs if d['status'] == 'completed'])

        return jsonify({"knowledge_base": knowledge_base})
    except Exception as e:
        logger.error(f"Get knowledge base error: {e}")
        return jsonify({"error": str(e)}), 500

@kb_bp.route('/knowledge-bases/<int:kb_id>', methods=['PUT'])
def update_knowledge_base(kb_id):
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "Invalid request"}), 400

        knowledge_base = db.get_knowledge_base(kb_id)
        if not knowledge_base:
            return jsonify({"error": "Knowledge base not found"}), 404

        return jsonify({"message": "Update not implemented, use create/delete"})
    except Exception as e:
        logger.error(f"Update knowledge base error: {e}")
        return jsonify({"error": str(e)}), 500

@kb_bp.route('/knowledge-bases/<int:kb_id>', methods=['DELETE'])
def delete_knowledge_base(kb_id):
    try:
        kb = db.get_knowledge_base(kb_id)
        if not kb:
            return jsonify({"error": "Knowledge base not found"}), 404

        rag_engine = doc_service.get_rag_engine(kb_id)
        rag_engine.delete_knowledge_base_vectors(kb_id)

        docs = db.get_documents(kb_id)
        for doc in docs:
            doc_service.delete_document(doc['id'])

        db.delete_knowledge_base(kb_id)

        logger.info(f"Knowledge base deleted: {kb_id}")
        return jsonify({"message": "Knowledge base deleted successfully"})

    except Exception as e:
        logger.error(f"Delete knowledge base error: {e}")
        return jsonify({"error": str(e)}), 500
