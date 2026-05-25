"""LLM Service — LangChain-based unified entry point.

Wraps ChatOpenAI with project-specific conveniences:
- chat(messages, **kwargs)        → raw string (backward-compatible with openai SDK signature)
- chat_simple(prompt, system=)    → string (one-shot user prompt)
- get_model()                     → ChatOpenAI instance for direct LCEL usage
- update_api_key(key)             → hot-swap API key without restart
"""

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.messages import HumanMessage, SystemMessage, BaseMessage
from app.core.config import settings

# ---------------------------------------------------------------------------
# Singleton model —  lazily created, hot-swappable
# ---------------------------------------------------------------------------

_model: ChatOpenAI | None = None
_custom_api_key: str | None = None


def get_model() -> ChatOpenAI:
    """Return the shared ChatOpenAI instance."""
    global _model
    key = _custom_api_key or settings.deepseek_api_key
    if _model is None:
        _model = _new_model(key)
    return _model


def _new_model(key: str) -> ChatOpenAI:
    return ChatOpenAI(
        model=settings.llm_model,
        api_key=key,
        base_url=settings.deepseek_base_url,
        temperature=0.3,
        max_tokens=2048,
    )


def update_api_key(key: str) -> bool:
    """Hot-swap the API key (used by settings endpoint)."""
    global _model, _custom_api_key
    key = (key or "").strip()
    if not key:
        return False
    _custom_api_key = key
    _model = _new_model(key)
    return True


def set_request_key(key: str | None):
    """Per-request key from X-Api-Key header. None = use .env default."""
    global _model, _custom_api_key
    if key:
        _custom_api_key = key
        _model = _new_model(key)
    else:
        _custom_api_key = None
        _model = _new_model(settings.deepseek_api_key)


def get_api_key_status() -> dict:
    """Return current API key status (masked)."""
    key = _custom_api_key or settings.deepseek_api_key
    masked = key[:4] + "****" + key[-4:] if len(key) > 8 else "****"
    return {
        "configured": bool(key),
        "source": "custom" if _custom_api_key else "env",
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
            api_key=settings.deepseek_api_key,
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
