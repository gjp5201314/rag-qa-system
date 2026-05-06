import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from waitress import serve
from app import app
from utils.logger import logger
from utils.config import Config

def main():
    logger.info("=" * 50)
    logger.info("RAG 智能问答系统启动中...")
    logger.info(f"Host: {Config.HOST}")
    logger.info(f"Port: {Config.PORT}")
    logger.info(f"Debug: {Config.DEBUG}")
    logger.info("=" * 50)

    if Config.DEBUG:
        app.run(
            host=Config.HOST,
            port=Config.PORT,
            debug=Config.DEBUG,
            use_reloader=False
        )
    else:
        logger.info("Starting with Waitress production server...")
        serve(
            app,
            host=Config.HOST,
            port=Config.PORT,
            threads=4
        )

if __name__ == '__main__':
    main()
