"""LLM 调用服务 —— 封装 DeepSeek-V4-Flash 的 OpenAI 兼容接口。

关键设计：
- 使用 OpenAI SDK，自动重试、流式等能力
- 全局复用一个 Client 实例（惰性初始化）
"""

from openai import OpenAI
from app.core.config import settings

_client: OpenAI | None = None


def get_client() -> OpenAI:
    global _client
    if _client is None:
        _client = OpenAI(
            api_key=settings.deepseek_api_key,
            base_url=settings.deepseek_base_url,
        )
    return _client


async def chat(
    messages: list[dict],
    model: str | None = None,
    temperature: float = 0.3,
    max_tokens: int = 2048,
) -> str:
    """通用对话接口：传入完整 messages 列表，返回模型回复文本"""
    client = get_client()
    response = client.chat.completions.create(
        model=model or settings.llm_model,
        messages=messages,
        temperature=temperature,
        max_tokens=max_tokens,
    )
    return response.choices[0].message.content or ""


async def chat_simple(prompt: str, system: str | None = None) -> str:
    """简化对话：只传用户 prompt + 可选 system prompt"""
    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})
    return await chat(messages)
