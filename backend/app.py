import os
import sys
from pathlib import Path
from dotenv import load_dotenv

sys.path.insert(0, str(Path(__file__).parent))

env_path = Path(__file__).parent / '.env'
if env_path.exists():
    load_dotenv(env_path)
    print(f"Loaded environment from {env_path}")

from flask import Flask, jsonify
from flask_cors import CORS

from api import chat_bp, document_bp, kb_bp
from utils.config import Config
from utils.logger import logger

def create_app():
    app = Flask(__name__)
    app.config['MAX_CONTENT_LENGTH'] = Config.MAX_UPLOAD_SIZE
    app.config['UPLOAD_FOLDER'] = str(Config.KNOWLEDGE_BASES_DIR)

    CORS(app, resources={
        r"/api/*": {
            "origins": Config.CORS_ORIGINS,
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization"]
        }
    })

    app.register_blueprint(chat_bp, url_prefix='/api')
    app.register_blueprint(document_bp, url_prefix='/api')
    app.register_blueprint(kb_bp, url_prefix='/api')

    @app.route('/')
    def index():
        return jsonify({
            "name": "RAG 智能问答系统",
            "version": "1.0.0",
            "status": "running",
            "endpoints": {
                "chat": "/api/chat",
                "documents": "/api/documents",
                "knowledge_bases": "/api/knowledge-bases",
                "health": "/api/health"
            }
        })

    @app.route('/api/health')
    def health():
        return jsonify({
            "status": "healthy",
            "database": str(Config.DATABASE_PATH),
            "chroma_db": str(Config.CHROMA_DB_DIR)
        })

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({"error": "Endpoint not found"}), 404

    @app.errorhandler(500)
    def internal_error(error):
        logger.error(f"Internal server error: {error}")
        return jsonify({"error": "Internal server error"}), 500

    @app.errorhandler(413)
    def file_too_large(error):
        return jsonify({"error": "File too large. Maximum size is 50MB"}), 413

    logger.info("Flask application created successfully")
    return app

app = create_app()

if __name__ == '__main__':
    logger.info("Starting RAG System API Server...")
    app.run(
        host=Config.HOST,
        port=Config.PORT,
        debug=Config.DEBUG
    )
