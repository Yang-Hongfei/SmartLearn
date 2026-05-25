"""LLM Service — LangChain-based unified entry point.

Wraps ChatOpenAI with project-specific conveniences:
- chat(messages, **kwargs)        → raw string (backward-compatible with openai SDK signature)
- chat_simple(prompt, system=)    → string (one-shot user prompt)
- get_model()                     → ChatOpenAI instance for direct LCEL usage
- update_api_key(key)             → hot-swap default API key without restart
- set_request_key(key)            → per-request key via ContextVar (thread/async safe)
"""

from contextvars import ContextVar
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.messages import HumanMessage, SystemMessage, BaseMessage
from app.core.config import settings

# ---------------------------------------------------------------------------
# API key management — ContextVar for per-request isolation
# ---------------------------------------------------------------------------

# Per-request key set by middleware via X-Api-Key header.
# ContextVar is isolated per asyncio task — concurrent requests don't leak.
_request_key: ContextVar[str | None] = ContextVar("request_api_key", default=None)

# Default key from user settings (set via update_api_key / settings modal).
_default_api_key: str | None = None
_cleared: bool = False


def require_api_key() -> str:
    """Return the effective API key, or raise a clear error with guidance.

    Call this at the start of any LLM-dependent endpoint so the user gets
    immediate feedback instead of a cryptic 500 error.
    """
    key = get_effective_api_key()
    if not key:
        from fastapi import HTTPException
        raise HTTPException(
            status_code=400,
            detail="请先配置 DeepSeek API Key。点击右上角「设置」按钮，输入您的 DeepSeek API Key 即可使用 AI 功能。",
        )
    return key


def get_effective_api_key() -> str:
    """Return the currently active API key.

    Priority: per-request ContextVar > default (user-configured or .env).
    Returns "" if the user explicitly cleared their key.
    """
    req_key = _request_key.get()
    if req_key is not None:
        return req_key
    if _cleared:
        return ""
    return _default_api_key or settings.deepseek_api_key


def get_model() -> ChatOpenAI:
    """Return a ChatOpenAI instance with the current effective API key."""
    return _new_model(get_effective_api_key())


def _new_model(key: str) -> ChatOpenAI:
    return ChatOpenAI(
        model=settings.llm_model,
        api_key=key,
        base_url=settings.deepseek_base_url,
        temperature=0.3,
        max_tokens=2048,
    )


def update_api_key(key: str) -> bool:
    """Set the default API key (from user settings). Returns False if empty."""
    global _default_api_key, _cleared
    key = (key or "").strip()
    if not key:
        return False
    _default_api_key = key
    _cleared = False
    return True


def set_request_key(key: str):
    """Per-request API key from X-Api-Key header. Isolated via ContextVar.

    Does NOT touch the default key — each request sees only its own key.
    """
    _request_key.set(key.strip())


def clear_key():
    """Remove the default API key. AI calls will fail until a new key is set."""
    global _default_api_key, _cleared
    _default_api_key = None
    _cleared = True


def get_api_key_status() -> dict:
    """Return current API key status (masked)."""
    if _cleared:
        return {"configured": False, "source": "cleared", "masked": None}
    key = _default_api_key or settings.deepseek_api_key
    masked = key[:4] + "****" + key[-4:] if len(key) > 8 else "****"
    return {
        "configured": bool(key),
        "source": "custom" if _default_api_key else "env",
        "masked": masked,
    }


def _to_lc_messages(messages: list[dict]) -> list[BaseMessage]:
    """Convert openai-style dict messages to LangChain BaseMessage list."""
    lc = []
    for m in messages:
        role = m.get("role", "user")
        content = m.get("content", "")
        if role == "system":
            lc.append(SystemMessage(content=content))
        else:
            lc.append(HumanMessage(content=content))
    return lc


# ---------------------------------------------------------------------------
# Backward-compatible convenience helpers
# ---------------------------------------------------------------------------

async def chat(
    messages: list[dict],
    model: str | None = None,
    temperature: float = 0.3,
    max_tokens: int = 2048,
) -> str:
    """General chat — takes openai-style [{"role":"system","content":"..."}, ...].

    Uses LangChain ChatOpenAI under the hood. The model/temperature params
    create a temporary instance when overridden, otherwise reuse the singleton.
    """
    llm = get_model()
    if temperature != 0.3 or max_tokens != 2048:
        llm = ChatOpenAI(
            model=model or settings.llm_model,
            api_key=get_effective_api_key(),
            base_url=settings.deepseek_base_url,
            temperature=temperature,
            max_tokens=max_tokens,
        )

    lc_messages = _to_lc_messages(messages)
    response = await llm.ainvoke(lc_messages)
    return response.content or ""


async def chat_simple(prompt: str, system: str | None = None) -> str:
    """Simplified chat: user prompt + optional system prompt, returns string."""
    llm = get_model()
    if system:
        messages = [SystemMessage(content=system), HumanMessage(content=prompt)]
    else:
        messages = [HumanMessage(content=prompt)]
    response = await llm.ainvoke(messages)
    return response.content or ""


# ---------------------------------------------------------------------------
# LCEL building blocks — compose directly in callers
# ---------------------------------------------------------------------------

def make_chain(system_template: str, user_template: str = "{input}"):
    """Return a StrOutputParser chain from ChatPromptTemplate.

    Usage:
        chain = make_chain("You are a math tutor.", "Solve: {input}")
        result = await chain.ainvoke({"input": "2+2"})
    """
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_template),
        ("human", user_template),
    ])
    return prompt | get_model() | StrOutputParser()
