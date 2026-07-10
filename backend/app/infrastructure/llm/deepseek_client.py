"""DeepSeek 云端大模型客户端。

封装对 DeepSeek API 的 HTTP 调用，提供 `chat()` 与 `vision()` 两个方法。
当配置中 `DEEPSEEK_API_KEY` 为空时，返回 mock 数据，便于无网络本地开发；
有 key 时通过 httpx 发送真实请求。所有大模型能力均走云端，不在本地加载模型。
"""
from typing import Any  # 任意类型

import httpx  # 异步 HTTP 客户端

from app.config.settings import settings  # 全局配置


class DeepSeekClient:
    """DeepSeek HTTP 客户端。

    兼具真实请求与无 key 时的 mock 兜底，使业务层无需感知网络可用性。

    Attributes:
        api_key: DeepSeek API Key，为空走 mock。
        base_url: 接口基础地址。
        chat_model: 对话模型名称。
        vision_model: 视觉模型名称。
        timeout: 请求超时时间（秒）。
    """

    def __init__(self) -> None:
        # 从配置读取 API Key，空字符串表示无 key
        self.api_key = settings.deepseek_api_key
        # 读取接口基础地址
        self.base_url = settings.deepseek_base_url
        # 对话模型名称
        self.chat_model = settings.deepseek_chat_model
        # 视觉模型名称
        self.vision_model = settings.deepseek_vision_model
        # 请求超时时间
        self.timeout = settings.deepseek_timeout

    @property
    def has_key(self) -> bool:
        """判断是否配置了真实 API Key。"""
        # 仅当 key 为非空字符串时才发真实请求
        return bool(self.api_key)

    def _mock_response(self, prompt: str, kind: str = "chat") -> str:
        """生成 mock 响应文本。

        Args:
            prompt: 用户输入提示词。
            kind: 调用类型 chat / vision。

        Returns:
            str: 便于本地调试的占位回复。
        """
        # 拼装 mock 回复，指明来源便于区分
        return f"[mock-{kind}] 当前未配置 DEEPSEEK_API_KEY，无法访问云端大模型。输入提示: {prompt[:50]}"

    async def chat(self, messages: list[dict[str, Any]], **kwargs: Any) -> str:
        """对话补全接口。

        Args:
            messages: OpenAI 风格的消息列表，如 [{"role":"user","content":"..."}]。
            **kwargs: 透传给接口的额外参数（如 temperature、max_tokens）。

        Returns:
            str: 模型回复的文本内容。
        """
        # 无 key 时直接返回 mock，避免发起会失败的网络请求
        if not self.has_key:
            # 取最后一条用户消息作为 mock 提示
            prompt = messages[-1].get("content", "") if messages else ""
            return self._mock_response(str(prompt), kind="chat")

        # 构造请求体，model 与 messages 为必填
        payload: dict[str, Any] = {
            "model": kwargs.pop("model", self.chat_model),  # 模型名称，默认配置值
            "messages": messages,  # 消息列表
            **kwargs,  # 透传额外参数
        }
        # 构造鉴权头
        headers = {
            "Authorization": f"Bearer {self.api_key}",  # Bearer 鉴权
            "Content-Type": "application/json",  # JSON 请求体
        }
        # 调用 /v1/chat/completions 端点
        return await self._post_chat(payload, headers)

    async def vision(self, messages: list[dict[str, Any]], **kwargs: Any) -> str:
        """视觉理解接口。

        Args:
            messages: 含图像内容（OpenAI vision 风格多模态消息）的消息列表。
            **kwargs: 透传给接口的额外参数。

        Returns:
            str: 模型回复的文本内容。
        """
        # 无 key 时返回 mock
        if not self.has_key:
            prompt = messages[-1].get("content", "") if messages else ""
            return self._mock_response(str(prompt), kind="vision")

        # 视觉端点复用 chat completions，仅模型名不同
        payload: dict[str, Any] = {
            "model": kwargs.pop("model", self.vision_model),  # 视觉模型名称
            "messages": messages,  # 多模态消息列表
            **kwargs,  # 透传额外参数
        }
        headers = {
            "Authorization": f"Bearer {self.api_key}",  # Bearer 鉴权
            "Content-Type": "application/json",  # JSON 请求体
        }
        return await self._post_chat(payload, headers)

    async def _post_chat(self, payload: dict[str, Any], headers: dict[str, str]) -> str:
        """发送 chat completions 请求并提取回复文本。

        Args:
            payload: 请求体。
            headers: 请求头。

        Returns:
            str: 模型回复的首条文本。

        Raises:
            RuntimeError: 请求失败或响应结构异常时抛出。
        """
        # 拼装完整端点地址
        url = f"{self.base_url}/v1/chat/completions"
        try:
            # 使用 httpx 异步发送，超时由配置控制
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(url, json=payload, headers=headers)
            # 非 2xx 直接抛错
            response.raise_for_status()
            # 解析 JSON 响应
            data = response.json()
            # 取首条回复内容
            return data["choices"][0]["message"]["content"]
        except Exception as exc:
            # 包装为运行时异常，避免业务层崩在 httpx 细节
            raise RuntimeError(f"DeepSeek 请求失败: {exc}") from exc


# 模块级单例，供业务层直接注入使用
deepseek_client = DeepSeekClient()