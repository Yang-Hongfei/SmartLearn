"""PDF text parsing — LangChain ChatPromptTemplate + ChatOpenAI pipeline."""

from langchain_core.prompts import ChatPromptTemplate
from app.services import llm_service
from app.core.utils import parse_llm_json

PDF_PARSE_PROMPT = ChatPromptTemplate.from_messages([
    ("system", """你是一个专业的题目解析助手。你的任务是从教材/面试题 PDF 的原始文本中提取所有的问答对。

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
{{
  "questions": [
    {{
      "topic": "章节标题",
      "question_number": "1",
      "content": "题目内容（不含编号）",
      "type": "single_choice 或 essay",
      "options": ["A. xxx", "B. xxx"] 或 null,
      "answer": "完整的答案内容",
      "difficulty": 3,
      "knowledge_point_ids": ["kp_xxx"],
      "truncated": false
    }}
  ],
  "topics_found": ["章节1", "章节2"]
}}"""),
    ("human", """请解析以下 PDF 文件的文本内容{chunk_info}，提取所有问答对。

文件名：{filename}

原始文本：
---
{raw_text}
---

请严格按照 JSON 格式返回结果。"""),
])


async def parse_pdf_text(raw_text: str, filename: str = "", chunk_index: int = 0, total_chunks: int = 1) -> dict:
    """Parse PDF raw text into structured Q&A pairs using LangChain prompt template."""

    chunk_info = f"（第 {chunk_index + 1}/{total_chunks} 块）" if total_chunks > 1 else ""

    llm = llm_service.get_model()
    # Temporary instance for lower temp + higher max_tokens on PDF parsing
    from langchain_openai import ChatOpenAI
    from app.core.config import settings
    llm = ChatOpenAI(
        model=settings.llm_model,
        api_key=settings.deepseek_api_key,
        base_url=settings.deepseek_base_url,
        temperature=0.2,
        max_tokens=8192,
    )

    chain = PDF_PARSE_PROMPT | llm
    response = await chain.ainvoke({
        "chunk_info": chunk_info,
        "filename": filename,
        "raw_text": raw_text,
    })
    result = parse_llm_json(response.content or "")

    questions = result.get("questions", [])
    topics_found = result.get("topics_found", [])

    complete_questions = [q for q in questions if not q.get("truncated", False)]

    return {
        "questions": complete_questions,
        "total_extracted": len(complete_questions),
        "topics_found": topics_found,
        "truncated_count": len(questions) - len(complete_questions),
    }
