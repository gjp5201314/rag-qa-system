from flask import Blueprint, request, jsonify
from werkzeug.utils import secure_filename
import os

from services.document_service import doc_service
from utils.logger import logger

document_bp = Blueprint('document', __name__)

ALLOWED_EXTENSIONS = {'pdf', 'txt', 'md', 'doc', 'docx'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@document_bp.route('/documents/upload', methods=['POST'])
def upload_document():
    try:
        if 'file' not in request.files:
            return jsonify({"error": "No file provided"}), 400

        file = request.files['file']
        kb_id = request.form.get('knowledge_base_id', type=int)

        if not kb_id:
            return jsonify({"error": "knowledge_base_id is required"}), 400

        if file.filename == '':
            return jsonify({"error": "No file selected"}), 400

        if not allowed_file(file.filename):
            return jsonify({"error": "File type not allowed"}), 400

        result = doc_service.upload_document(file, kb_id)

        if result.get('success'):
            return jsonify({
                "id": result['doc_id'],
                "filename": result['filename'],
                "file_size": result['file_size'],
                "status": "uploaded",
                "message": "Document uploaded successfully"
            })
        else:
            return jsonify({"error": result.get('error', "Upload failed")}), 400

    except Exception as e:
        logger.error(f"Upload document error: {e}")
        return jsonify({"error": str(e)}), 500

@document_bp.route('/documents/<int:doc_id>/process', methods=['POST'])
def process_document(doc_id):
    try:
        doc = doc_service.get_document(doc_id)
        if not doc:
            return jsonify({"error": "Document not found"}), 404

        success = doc_service.process_document(doc_id, doc['knowledge_base_id'])

        if success:
            return jsonify({
                "id": doc_id,
                "status": "completed",
                "message": "Document processed successfully"
            })
        else:
            return jsonify({
                "id": doc_id,
                "status": "failed",
                "message": "Document processing failed"
            })

    except Exception as e:
        logger.error(f"Process document error: {e}")
        return jsonify({"error": str(e)}), 500

@document_bp.route('/documents', methods=['GET'])
def get_documents():
    try:
        kb_id = request.args.get('knowledge_base_id', type=int)
        documents = doc_service.get_documents(kb_id)
        return jsonify({"documents": documents})
    except Exception as e:
        logger.error(f"Get documents error: {e}")
        return jsonify({"error": str(e)}), 500

@document_bp.route('/documents/<int:doc_id>', methods=['GET'])
def get_document(doc_id):
    try:
        document = doc_service.get_document(doc_id)
        if not document:
            return jsonify({"error": "Document not found"}), 404
        return jsonify({"document": document})
    except Exception as e:
        logger.error(f"Get document error: {e}")
        return jsonify({"error": str(e)}), 500

@document_bp.route('/documents/<int:doc_id>', methods=['DELETE'])
def delete_document(doc_id):
    try:
        success = doc_service.delete_document(doc_id)
        if success:
            return jsonify({"message": "Document deleted successfully"})
        return jsonify({"error": "Document not found"}), 404
    except Exception as e:
        logger.error(f"Delete document error: {e}")
        return jsonify({"error": str(e)}), 500
