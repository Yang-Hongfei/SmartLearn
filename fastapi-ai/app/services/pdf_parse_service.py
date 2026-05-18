"""PDF 文本解析服务 —— 调用 Qwen-Max 从 PDF 原始文本中提取结构化 Q&A 对。"""

from app.services import llm_service
from app.core.utils import parse_llm_json

PDF_PARSE_SYSTEM_PROMPT = """你是一个专业的题目解析助手。你的任务是从教材/面试题 PDF 的原始文本中提取所有的问答对。

规则：
1. 忽略广告/推广内容（如"关注公众号"、"扫码领取"、"最近整理了"等），这些不是题目
2. 识别章节标题作为 topic（如"分布式理论"、"分布式锁"、"一、基础概念"等）
3. 每个编号的题目（如"1. xxx？"、"5.1 xxx？"）作为一个独立的问答对
4. 题目的答案可能是多段落文字，请将其合并为一个完整的 answer 字段
5. 如果题目包含 A/B/C/D 选项，type 设为 "single_choice"，options 提取为数组；否则 type 设为 "essay"
6. 根据内容复杂度估算 difficulty（1-5），一般面试题默认为 3
7. knowledge_point_ids 根据题目主题生成合理的 kp_xxx ID
8. 如果当前文本块在某个题目的答案中间被截断，该题目标记 truncated: true

返回严格的 JSON 格式：
{
  "questions": [
    {
      "topic": "章节标题",
      "question_number": "1",
      "content": "题目内容（不含编号）",
      "type": "single_choice 或 essay",
      "options": ["A. xxx", "B. xxx"] 或 null,
      "answer": "完整的答案内容",
      "difficulty": 3,
      "knowledge_point_ids": ["kp_xxx"],
      "truncated": false
    }
  ],
  "topics_found": ["章节1", "章节2"]
}
"""


async def parse_pdf_text(raw_text: str, filename: str = "", chunk_index: int = 0, total_chunks: int = 1) -> dict:
    """解析 PDF 原始文本，返回结构化的问答对列表。"""

    chunk_info = f"（第 {chunk_index + 1}/{total_chunks} 块）" if total_chunks > 1 else ""
    user_prompt = f"""请解析以下 PDF 文件的文本内容{chunk_info}，提取所有问答对。

文件名：{filename}

原始文本：
---
{raw_text}
---

请严格按照 JSON 格式返回结果。"""

    messages = [
        {"role": "system", "content": PDF_PARSE_SYSTEM_PROMPT},
        {"role": "user", "content": user_prompt}
    ]

    response = await llm_service.chat(messages, temperature=0.2, max_tokens=8192)
    result = parse_llm_json(response)

    questions = result.get("questions", [])
    topics_found = result.get("topics_found", [])

    # Filter out truncated questions (they'll appear in the next chunk)
    complete_questions = [q for q in questions if not q.get("truncated", False)]

    return {
        "questions": complete_questions,
        "total_extracted": len(complete_questions),
        "topics_found": topics_found,
    }
