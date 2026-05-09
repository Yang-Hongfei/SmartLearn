"""LLM 调用服务 —— 封装 Qwen-Max（阿里云百炼）的 OpenAI 兼容接口。

关键设计：
- 使用 OpenAI SDK 而非手动 HTTP 请求，获得自动重试、流式等能力
- 全局复用一个 Client 实例（惰性初始化），避免每次请求都重建连接
- base_url 指向 DashScope 兼容端点，可换成任何 OpenAI 兼容服务
"""

from openai import OpenAI
from app.core.config import settings

# 模块级单例：整个 FastAPI 进程共享一个 HTTPS 连接池
_client: OpenAI | None = None


def get_client() -> OpenAI:
    """获取 OpenAI 客户端（惰性初始化，仅首次调用时创建连接）"""
    global _client
    if _client is None:
        _client = OpenAI(
            api_key=settings.dashscope_api_key,
            base_url=settings.dashscope_base_url,
        )
    return _client


async def chat(
    messages: list[dict],
    model: str | None = None,
    temperature: float = 0.3,    # 低温度 → 输出更稳定，适合教学场景
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
