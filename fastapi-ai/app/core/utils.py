"""共享工具函数 —— 多个 service 和 api 模块共用的纯函数。

这些函数不依赖任何外部服务，无副作用，可安全地在任何地方调用。
"""

import re
import json
from datetime import datetime


def now_iso() -> str:
    """返回当前时间的 ISO 格式字符串，用于 API 响应的 generated_at 字段"""
    return datetime.now().isoformat()


def parse_llm_json(text: str) -> dict:
    """从 LLM 回复中提取 JSON 对象。

    LLM 经常在 JSON 外面包裹 ```json ... ``` 或 ``` ... ```，
    这个函数会逐层尝试剥离这些包裹，尽量拿到纯净的 JSON。

    即使彻底解析失败，也返回空 dict 而不是抛异常，
    保证分析流程不会因 LLM 输出格式不稳定而中断。
    """
    # 尝试 1：直接解析（LLM 返回纯净 JSON）
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    # 尝试 2：提取 ```json ... ``` 代码块
    if "```json" in text:
        start = text.index("```json") + 7
        end = text.find("```", start)
        if end != -1:
            text = text[start:end]
    elif "```" in text:
        # 尝试 3：提取 ``` ... ``` 代码块
        start = text.index("```") + 3
        end = text.find("```", start)
        if end != -1:
            text = text[start:end]

    # 尝试 4：剥离包裹后再解析
    try:
        return json.loads(text.strip())
    except json.JSONDecodeError:
        return {}


def extract_keywords(text: str, min_len: int = 2, max_count: int = 10) -> list[str]:
    """从用户问题中提取关键词，用于混合检索中的关键词召回支路。

    去标点 → 按空格分词 → 过滤短词 → 截取前 N 个。
    """
    # 中英文标点的并集
    cleaned = re.sub(r"[，。！？、；：""''【】《》（）\s,.!?;:\"'()\[\]]+", " ", text)
    words = [w for w in cleaned.split() if len(w) >= min_len]
    return words[:max_count]


def meta(doc: dict, key: str, default=None):
    """安全获取文档的 metadata 子字段。

    等价于 doc["metadata"][key]，但当 metadata 为 None 或 key 不存在时
    返回 default 而不是抛 KeyError / TypeError。
    """
    return (doc.get("metadata") or {}).get(key, default)


def merge_dedup(*lists: list[dict], key: str = "id") -> list[dict]:
    """合并多个结果列表，按 key 字段去重。

    先到先得（前面的列表优先级更高），用于合并向量检索和关键词检索结果。
    """
    seen: set[str] = set()
    merged: list[dict] = []
    for lst in lists:
        for item in lst:
            k = item.get(key, "")
            if k not in seen:
                seen.add(k)
                merged.append(item)
    return merged
