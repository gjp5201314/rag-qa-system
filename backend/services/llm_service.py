import json
from typing import Dict, Any, Optional, List

from utils.config import Config
from utils.logger import logger

class LLMService:
    def __init__(self):
        self.provider = Config.LLM_PROVIDER
        self._init_provider()

    def _init_provider(self):
        if self.provider == "qwen":
            self._call_api = self._call_qwen
        elif self.provider == "doubao":
            self._call_api = self._call_doubao
        else:
            logger.warning(f"Unknown LLM provider: {self.provider}, using mock")
            self._call_api = self._mock_call

    def generate(self, prompt: str, context: str = "", **kwargs) -> str:
        try:
            return self._call_api(prompt, context, **kwargs)
        except Exception as e:
            logger.error(f"LLM generation failed: {e}")
            return f"抱歉，生成回答时出现错误: {str(e)}"

    def _call_qwen(self, prompt: str, context: str, **kwargs) -> str:
        try:
            import urllib.request
            import urllib.error

            api_key = Config.DASHSCOPE_API_KEY
            if not api_key:
                logger.warning("DASHSCOPE_API_KEY not set, using mock response")
                return self._mock_call(prompt, context)

            url = "https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation"
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }

            full_prompt = self._build_prompt(prompt, context)

            data = json.dumps({
                "model": Config.LLM_MODEL,
                "input": {"prompt": full_prompt},
                "parameters": {
                    "temperature": kwargs.get("temperature", Config.LLM_TEMPERATURE),
                    "max_tokens": kwargs.get("max_tokens", Config.LLM_MAX_TOKENS),
                    "top_p": 0.8
                }
            }).encode("utf-8")

            req = urllib.request.Request(url, data=data, headers=headers, method="POST")

            try:
                with urllib.request.urlopen(req, timeout=60) as response:
                    result = json.loads(response.read().decode("utf-8"))
                    if "output" in result and "text" in result["output"]:
                        return result["output"]["text"]
                    return str(result)
            except urllib.error.HTTPError as e:
                logger.error(f"Qwen API HTTP error: {e.code} - {e.read().decode()}")
                return self._mock_call(prompt, context)

        except Exception as e:
            logger.error(f"Qwen API call failed: {e}")
            return self._mock_call(prompt, context)

    def _call_doubao(self, prompt: str, context: str, **kwargs) -> str:
        try:
            import urllib.request
            import urllib.error

            api_key = Config.DOUBAO_API_KEY
            if not api_key:
                logger.warning("DOUBAO_API_KEY not set, using mock response")
                return self._mock_call(prompt, context)

            url = "https://ark.cn-beijing.volces.com/api/v3/chat/completions"
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }

            full_prompt = self._build_prompt(prompt, context)

            messages = [
                {"role": "system", "content": "你是一个专业的AI助手，基于给定上下文回答用户问题。"},
                {"role": "user", "content": f"上下文：\n{context}\n\n问题：{prompt}"}
            ]

            data = json.dumps({
                "model": Config.LLM_MODEL,
                "messages": messages,
                "temperature": kwargs.get("temperature", Config.LLM_TEMPERATURE),
                "max_tokens": kwargs.get("max_tokens", Config.LLM_MAX_TOKENS)
            }).encode("utf-8")

            req = urllib.request.Request(url, data=data, headers=headers, method="POST")

            try:
                with urllib.request.urlopen(req, timeout=60) as response:
                    result = json.loads(response.read().decode("utf-8"))
                    if "choices" in result and len(result["choices"]) > 0:
                        return result["choices"][0]["message"]["content"]
                    return str(result)
            except urllib.error.HTTPError as e:
                logger.error(f"Doubao API HTTP error: {e.code} - {e.read().decode()}")
                return self._mock_call(prompt, context)

        except Exception as e:
            logger.error(f"Doubao API call failed: {e}")
            return self._mock_call(prompt, context)

    def _mock_call(self, prompt: str, context: str) -> str:
        mock_response = f"【模拟回答】\n\n根据我检索到的资料，我来回答您的问题：\n\n**相关上下文：**\n{context[:500]}...\n\n**回答内容：**\n这是一个基于 RAG 检索增强生成技术的模拟回答。在实际部署时，请配置通义千问或豆包的 API Key 来获取真实的 AI 生成回答。\n\n**检索片段数：** {context.count('---') + 1} 段"

        logger.info("Using mock LLM response")
        return mock_response

    def _build_prompt(self, query: str, context: str) -> str:
        if not context:
            return f"请回答以下问题，如果上下文中没有相关信息，请说明：\n\n问题：{query}"

        return f"""基于以下上下文信息回答问题。如果上下文中没有相关信息，请明确说明。

---
上下文：
{context}
---

问题：{query}

回答："""

llm_service = LLMService()
