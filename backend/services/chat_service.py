import json
from typing import Dict, Any, Optional, List, Tuple

from models.database import db
from services.document_service import doc_service
from services.llm_service import llm_service
from utils.logger import logger

class ChatService:
    def __init__(self):
        pass

    def create_session(self, title: str = "", kb_id: Optional[int] = None) -> int:
        return db.create_chat_session(title, kb_id)

    def get_sessions(self, kb_id: Optional[int] = None) -> List[Dict[str, Any]]:
        return db.get_chat_sessions(kb_id)

    def get_session(self, session_id: int) -> Optional[Dict[str, Any]]:
        return db.get_chat_session(session_id)

    def delete_session(self, session_id: int) -> bool:
        return db.delete_chat_session(session_id)

    def get_messages(self, session_id: int) -> List[Dict[str, Any]]:
        return db.get_chat_messages(session_id)

    def chat(self, message: str, session_id: Optional[int] = None,
             kb_id: Optional[int] = None) -> Tuple[str, List[Dict[str, Any]], int]:
        try:
            if not message or not message.strip():
                return "消息不能为空", [], session_id or 0

            if session_id:
                session = db.get_chat_session(session_id)
                if session:
                    kb_id = kb_id or session.get('knowledge_base_id')
                db.create_chat_message(session_id, "user", message)
            else:
                session_id = db.create_chat_session(kb_id=kb_id)
                db.create_chat_message(session_id, "user", message)

            if kb_id is None:
                answer = self._chat_without_kb(message)
                sources = []
            else:
                answer, sources = self._chat_with_rag(message, kb_id)

            sources_json = json.dumps(sources, ensure_ascii=False)
            msg_id = db.create_chat_message(session_id, "assistant", answer, sources_json)

            logger.info(f"Chat response generated for session {session_id}")

            return answer, sources, session_id

        except Exception as e:
            logger.error(f"Chat error: {e}")
            return f"抱歉，出现错误: {str(e)}", [], session_id or 0

    def _chat_without_kb(self, message: str) -> str:
        return """您好！我是 RAG 智能问答助手。

目前还没有上传任何文档到知识库，无法为您提供基于文档的检索增强回答。

请先在「知识库管理」页面上传文档（PDF、TXT 或 Markdown 格式），然后我就能根据文档内容回答您的问题。

您也可以：
- 创建一个新的知识库
- 上传文档并自动处理
- 开始新的对话"""

    def _chat_with_rag(self, message: str, kb_id: int) -> Tuple[str, List[Dict[str, Any]]]:
        try:
            rag_engine = doc_service.get_rag_engine(kb_id)

            search_results = rag_engine.search(message, kb_id=kb_id)

            if not search_results:
                return """我在当前知识库中没有找到与您问题相关的内容。

可能的原因：
1. 知识库中尚未上传文档
2. 上传的文档尚未处理完成
3. 您的问题与文档内容不相关

建议您：
- 检查知识库是否有已处理的文档
- 尝试换一种方式描述您的问题
- 上传更多相关文档""", []

            context = self._build_context(search_results)

            context_summary = f"根据搜索到的 {len(search_results)} 个相关片段：\n\n"
            for i, result in enumerate(search_results[:3], 1):
                source = result.get('metadata', {}).get('source_file', '未知')
                snippet = result['document'][:200]
                context_summary += f"【片段 {i}】(来源: {source})\n{snippet}...\n\n"

            answer = llm_service.generate(message, context)

            sources = [
                {
                    "content": result['document'][:300],
                    "source": result.get('metadata', {}).get('source_file', '未知'),
                    "score": round(result.get('rerank_score', result.get('combined_score', 0)), 4)
                }
                for result in search_results
            ]

            return answer, sources

        except Exception as e:
            logger.error(f"RAG chat error: {e}")
            return f"检索或生成回答时出错: {str(e)}", []

    def _build_context(self, search_results: List[Dict[str, Any]]) -> str:
        context_parts = []
        for i, result in enumerate(search_results, 1):
            context_parts.append(f"【文档片段 {i}】\n{result['document']}")
        return "\n\n".join(context_parts)

chat_service = ChatService()
