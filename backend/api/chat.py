from flask import Blueprint, request, jsonify
from services.chat_service import chat_service
from models.database import db
from utils.logger import logger

chat_bp = Blueprint('chat', __name__)

@chat_bp.route('/chat', methods=['POST'])
def chat():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "Invalid request data"}), 400

        message = data.get('message', '').strip()
        session_id = data.get('session_id')
        kb_id = data.get('knowledge_base_id')

        if not message:
            return jsonify({"error": "Message cannot be empty"}), 400

        answer, sources, new_session_id = chat_service.chat(
            message=message,
            session_id=session_id,
            kb_id=kb_id
        )

        return jsonify({
            "answer": answer,
            "sources": sources,
            "session_id": new_session_id
        })

    except Exception as e:
        logger.error(f"Chat API error: {e}")
        return jsonify({"error": str(e)}), 500

@chat_bp.route('/chat/sessions', methods=['GET'])
def get_sessions():
    try:
        kb_id = request.args.get('knowledge_base_id', type=int)
        sessions = chat_service.get_sessions(kb_id)
        return jsonify({"sessions": sessions})
    except Exception as e:
        logger.error(f"Get sessions error: {e}")
        return jsonify({"error": str(e)}), 500

@chat_bp.route('/chat/sessions/<int:session_id>', methods=['GET'])
def get_session(session_id):
    try:
        session = chat_service.get_session(session_id)
        if not session:
            return jsonify({"error": "Session not found"}), 404
        return jsonify({"session": session})
    except Exception as e:
        logger.error(f"Get session error: {e}")
        return jsonify({"error": str(e)}), 500

@chat_bp.route('/chat/sessions', methods=['POST'])
def create_session():
    try:
        data = request.get_json() or {}
        title = data.get('title', '')
        kb_id = data.get('knowledge_base_id')
        session_id = chat_service.create_session(title, kb_id)
        return jsonify({"session_id": session_id, "message": "Session created"})
    except Exception as e:
        logger.error(f"Create session error: {e}")
        return jsonify({"error": str(e)}), 500

@chat_bp.route('/chat/sessions/<int:session_id>', methods=['DELETE'])
def delete_session(session_id):
    try:
        success = chat_service.delete_session(session_id)
        if success:
            return jsonify({"message": "Session deleted"})
        return jsonify({"error": "Session not found"}), 404
    except Exception as e:
        logger.error(f"Delete session error: {e}")
        return jsonify({"error": str(e)}), 500

@chat_bp.route('/chat/history/<int:session_id>', methods=['GET'])
def get_chat_history(session_id):
    try:
        messages = chat_service.get_messages(session_id)
        for msg in messages:
            if msg.get('sources'):
                try:
                    msg['sources'] = eval(msg['sources'])
                except:
                    pass
        return jsonify({"messages": messages})
    except Exception as e:
        logger.error(f"Get chat history error: {e}")
        return jsonify({"error": str(e)}), 500
