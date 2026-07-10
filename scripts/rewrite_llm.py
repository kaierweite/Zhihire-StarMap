"""Rewrite llm_client.py with multi-provider runtime config support."""

import textwrap, os

path = os.path.join(os.path.dirname(__file__), '..', 'ai-service', 'app', 'infrastructure', 'llm_client.py')

content = textwrap.dedent('''\
    """
    LLM 客户端 — 统一封装多提供商 Chat API 调用
    支持 chat / chat_json，内含重试和超时；支持运行时配置热加载
    """

    import json
    import logging

    import httpx

    from app.infrastructure.config_manager import settings
    from app.exceptions import LLMCallError

    logger = logging.getLogger("zhihire.ai.llm")

    MAX_RETRIES = 2
    TIMEOUT_SECONDS = 30.0


    class LLMProvider:
        """单个 LLM 提供商运行时配置"""

        __slots__ = ("id", "name", "base_url", "api_key", "default_model",
                     "temperature", "max_tokens", "enabled")

        def __init__(self, *, id: str, name: str, base_url: str, api_key: str,
                     default_model: str, temperature: float = 0.7,
                     max_tokens: int = 4096, enabled: bool = True):
            self.id = id
            self.name = name
            self.base_url = base_url
            self.api_key = api_key
            self.default_model = default_model
            self.temperature = temperature
            self.max_tokens = max_tokens
            self.enabled = enabled

        def to_headers(self) -> dict:
            return {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            }

        def chat_url(self) -> str:
            return f"{self.base_url.rstrip('/')}/chat/completions"


    class LLMClient:
        """多提供商 LLM 客户端，运行时可切换"""

        def __init__(self):
            self._client: httpx.AsyncClient | None = None
            self._providers: dict[str, LLMProvider] = {}
            self._active_id: str = "deepseek"

        # ── 生命周期 ──────────────────────────────────────────────
        async def init(self) -> None:
            self._client = httpx.AsyncClient(timeout=TIMEOUT_SECONDS)
            # 启动时从 settings 加载默认提供商
            self._providers["deepseek"] = LLMProvider(
                id="deepseek",
                name="DeepSeek",
                base_url=settings.deepseek_base_url,
                api_key=settings.deepseek_api_key,
                default_model=settings.deepseek_model,
            )
            logger.info("LLM 客户端已初始化 (默认: deepseek)")

        async def close(self) -> None:
            if self._client:
                await self._client.aclose()
                self._client = None

        # ── 运行时配置 ────────────────────────────────────────────
        def update_provider(self, provider: LLMProvider) -> None:
            """运行时更新/新增提供商配置"""
            self._providers[provider.id] = provider
            logger.info(f"提供商配置已更新: {provider.id}")

        def remove_provider(self, provider_id: str) -> None:
            self._providers.pop(provider_id, None)

        def set_active(self, provider_id: str) -> None:
            if provider_id not in self._providers:
                raise ValueError(f"提供商不存在: {provider_id}")
            self._active_id = provider_id
            logger.info(f"活跃提供商切换为: {provider_id}")

        def get_active(self) -> LLMProvider:
            p = self._providers.get(self._active_id)
            if not p:
                raise LLMCallError(f"活跃提供商未配置: {self._active_id}")
            return p

        def get_all_providers(self) -> list[LLMProvider]:
            return list(self._providers.values())

        # ── Chat 接口 ─────────────────────────────────────────────
        async def chat(
            self,
            prompt: str,
            system_prompt: str | None = None,
            temperature: float | None = None,
            provider_id: str | None = None,
        ) -> str:
            """
            调用 Chat API，返回纯文本

            Args:
                prompt: 用户消息
                system_prompt: 系统提示（可选）
                temperature: 温度参数（None 用提供商默认）
                provider_id: 指定提供商（None 用活跃提供商）
            """
            provider = self._resolve_provider(provider_id)
            temp = temperature if temperature is not None else provider.temperature
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})
            return await self._call_api(provider, messages, temp)

        async def chat_json(
            self,
            prompt: str,
            system_prompt: str | None = None,
            temperature: float = 0.3,
            provider_id: str | None = None,
        ) -> dict:
            """
            调用 Chat API，强制 JSON 输出

            Args:
                prompt: 用户消息
                system_prompt: 系统提示（可选）
                temperature: 温度参数（JSON 模式建议低温）
                provider_id: 指定提供商

            Returns:
                解析后的 JSON 字典
            """
            provider = self._resolve_provider(provider_id)
            json_instruction = (
                "请严格以 JSON 格式输出，不要包含 markdown 代码块标记或额外文字。"
            )
            full_prompt = f"{json_instruction}\\n\\n{prompt}"
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": full_prompt})

            raw = await self._call_api(provider, messages, temperature)
            text = raw.strip()
            if text.startswith("```"):
                lines = text.split("\\n")
                text = "\\n".join(lines[1:-1]) if len(lines) > 2 else text
            try:
                return json.loads(text)
            except json.JSONDecodeError as e:
                logger.warning(f"JSON 解析失败，返回原始文本: {e}")
                return {"raw_text": text, "parse_error": True}

        # ── 内部实现 ──────────────────────────────────────────────
        def _resolve_provider(self, provider_id: str | None) -> LLMProvider:
            pid = provider_id or self._active_id
            p = self._providers.get(pid)
            if not p:
                raise LLMCallError(f"提供商未配置: {pid}")
            if not p.enabled:
                raise LLMCallError(f"提供商已禁用: {pid}")
            return p

        async def _call_api(
            self, provider: LLMProvider, messages: list[dict], temperature: float
        ) -> str:
            """底层 API 调用，含重试机制"""
            if not self._client:
                raise LLMCallError("LLM 客户端未初始化")

            last_error = None
            for attempt in range(MAX_RETRIES + 1):
                try:
                    response = await self._client.post(
                        provider.chat_url(),
                        headers=provider.to_headers(),
                        json={
                            "model": provider.default_model,
                            "messages": messages,
                            "temperature": temperature,
                            "max_tokens": provider.max_tokens,
                        },
                    )
                    response.raise_for_status()
                    return response.json()["choices"][0]["message"]["content"]
                except httpx.HTTPStatusError as e:
                    last_error = f"HTTP {e.response.status_code}"
                    logger.warning(
                        f"[{provider.id}] LLM 调用失败 (尝试 {attempt + 1}): {last_error}"
                    )
                except httpx.TimeoutException:
                    last_error = "请求超时"
                    logger.warning(f"[{provider.id}] LLM 调用超时 (尝试 {attempt + 1})")
                except Exception as e:
                    last_error = str(e)
                    logger.warning(
                        f"[{provider.id}] LLM 调用异常 (尝试 {attempt + 1}): {last_error}"
                    )

            raise LLMCallError(
                f"[{provider.id}] LLM 调用失败（重试 {MAX_RETRIES} 次后）: {last_error}"
            )

    # 全局单例
    llm_client = LLMClient()
''')

with open(path, 'w', encoding='utf-8') as f:
    f.write(content)

print(f"Done. New file size: {len(content)} bytes")
