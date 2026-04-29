import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).parent.parent.parent

env_path = BASE_DIR / ".env"
if env_path.exists():
    load_dotenv(env_path)

class Config:
    FLASK_APP = os.getenv("FLASK_APP", "app.py")
    FLASK_ENV = os.getenv("FLASK_ENV", "development")
    DEBUG = os.getenv("DEBUG", "True").lower() == "true"

    HOST = os.getenv("HOST", "0.0.0.0")
    PORT = int(os.getenv("PORT", 5000))

    DATA_DIR = BASE_DIR / "data"
    KNOWLEDGE_BASES_DIR = DATA_DIR / "knowledge_bases"
    CHROMA_DB_DIR = DATA_DIR / "chroma_db"
    LOG_DIR = BASE_DIR / "logs"
    DATABASE_PATH = DATA_DIR / "rag_system.db"

    os.makedirs(KNOWLEDGE_BASES_DIR, exist_ok=True)
    os.makedirs(CHROMA_DB_DIR, exist_ok=True)
    os.makedirs(LOG_DIR, exist_ok=True)

    CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", 500))
    CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", 50))
    TOP_K = int(os.getenv("TOP_K", 5))
    RERANK_TOP_K = int(os.getenv("RERANK_TOP_K", 3))
    HYBRID_ALPHA = float(os.getenv("HYBRID_ALPHA", 0.7))

    BGE_MODEL = os.getenv("BGE_MODEL", "BAAI/bge-large-zh-v1.5")
    RERANKER_MODEL = os.getenv("RERANKER_MODEL", "BAAI/bge-reranker-large")

    LLM_PROVIDER = os.getenv("LLM_PROVIDER", "qwen")
    DASHSCOPE_API_KEY = os.getenv("DASHSCOPE_API_KEY", "")
    DOUBAO_API_KEY = os.getenv("DOUBAO_API_KEY", "")
    LLM_MODEL = os.getenv("LLM_MODEL", "qwen-plus")
    LLM_TEMPERATURE = float(os.getenv("LLM_TEMPERATURE", 0.7))
    LLM_MAX_TOKENS = int(os.getenv("LLM_MAX_TOKENS", 2000))

    MAX_UPLOAD_SIZE = int(os.getenv("MAX_UPLOAD_SIZE", 50 * 1024 * 1024))
    ALLOWED_EXTENSIONS = {"pdf", "txt", "md", "doc", "docx"}

    CORS_ORIGINS = os.getenv("CORS_ORIGINS", "*").split(",")

if Config.DASHSCOPE_API_KEY:
    print(f"[CONFIG] DASHSCOPE_API_KEY loaded: {Config.DASHSCOPE_API_KEY[:10]}...")
