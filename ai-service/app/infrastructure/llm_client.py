"""
LLM 客户端 — 统一封装 DeepSeek API 调用
"""

import httpx

from app.infrastructure.config_manager import settings
from app.exceptions import LLMCallError


class LLMClient:
    """DeepSeek 云端 LLM 客户端，单例使用"""

    def __init__(self):
        self._client: httpx.AsyncClient | None = None

    async def init(self) -> None:
        """初始化 HTTP 客户端"""
        self._client = httpx.AsyncClient(timeout=60.0)

    async def close(self) -> None:
        """关闭 HTTP 客户端"""
        if self._client:
            await self._client.aclose()
            self._client = None

    async def chat(self, prompt: str, temperature: float = 0.7) -> str:
        """
        调用 DeepSeek Chat API

        Args:
            prompt: 用户消息
            temperature: 温度参数

        Returns:
            LLM 返回的文本内容
        """
        if not self._client:
            raise LLMCallError("LLM 客户端未初始化")

        try:
            response = await self._client.post(
                f"{settings.deepseek_base_url}/chat/completions",
                headers={
                    "Authorization": f"Bearer {settings.deepseek_api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": settings.deepseek_model,
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": temperature,
                },
            )
            response.raise_for_status()
            return response.json()["choices"][0]["message"]["content"]
        except httpx.HTTPStatusError as e:
            raise LLMCallError(f"LLM HTTP 错误: {e.response.status_code}")
        except Exception as e:
            raise LLMCallError(f"LLM 调用异常: {str(e)}")


# 全局单例
llm_client = LLMClient()
