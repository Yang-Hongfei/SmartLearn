"""Answer analysis service — SmartLearn core diagnostic engine, now LangChain-native.

Flow:
  1. Rule-based judge (milliseconds, no LLM)
  2. LLM deep analysis via ChatPromptTemplate chain
  3. Neo4j enrichment (official knowledge point names)
  4. Learning path generation (graph traversal + LLM suggestions)
"""

from langchain_core.prompts import ChatPromptTemplate
from app.core.utils import parse_llm_json
from app.services import llm_service, path_service, kg_service

ERROR_ANALYSIS_PROMPT = ChatPromptTemplate.from_messages([
    ("system", """你是一个算法教学助手。分析学生的答题结果，给出诊断报告。

输出 JSON 格式：
{{
  "is_correct": true/false,
  "error_analysis": {{
    "explanation": "本题的详细解析，解释正确答案为什么对",
    "error_type": "概念混淆/知识漏洞/粗心错误/完全不会/方法错误",
    "error_detail": "针对学生错误答案的具体分析，指出哪里理解错了"
  }},
  "weak_point_analysis": [
    {{
      "knowledge_point_id": "对应知识点ID",
      "knowledge_point_name": "知识点名称",
      "current_mastery": 0.0-1.0,
      "reason": "为什么判断学生这个知识点薄弱"
    }}
  ]
}}

评判原则（非常重要）：
- 先理解题目问了什么，题目没问的内容不算核心要点
- 标准答案可能包含超出题目要求的补充知识（如默认值、占用大小），这些不是扣分依据
- 学生只要答全了题目问的核心要点就该给高分，遗漏题目未要求的补充内容不扣分
- 只有题目明确问了但学生没答、或答错了，才在 error_analysis 中指出

要求：
- explanation 要包含核心概念解释和解题思路
- 答对时 error_analysis 可简短，weak_point_analysis 给出巩固建议
- 答错时 error_analysis 要深入分析错误原因
- current_mastery: 0.0完全不会 0.3似懂非懂 0.6基本掌握 1.0完全掌握
- 只输出 JSON，不要其他内容"""),
    ("human", """题目信息：
- 题目ID：{question_id}
- 类型：{question_type}
- 难度：{difficulty_stars}
- 涉及知识点ID：{kp_text}
- 题目内容：{question_content}
- 选项：{options_text}
- 正确答案：{correct_answer}
- 学生答案：{user_answer}
- 判题结果：{judge_result}"""),
])


async def analyze_answer(
    user_id: str,
    question_id: str,
    question_content: str,
    question_type: str,
    correct_answer: str,
    user_answer: str,
    options: list[str] | None = None,
    knowledge_point_ids: list[str] | None = None,
    difficulty: int = 1,
) -> dict:
    """Analyze one answer submission. Returns enriched diagnosis dict."""

    # 0. Guard: API key must be configured
    llm_service.require_api_key()

    # 1. Rule-based judge
    is_correct = _judge(question_type, user_answer, correct_answer)

    # 2. LangChain LLM chain for deep analysis
    options_text = "\n".join(options) if options else "无"
    kp_text = ", ".join(knowledge_point_ids) if knowledge_point_ids else "未知"

    chain = ERROR_ANALYSIS_PROMPT | llm_service.get_model()
    response = await chain.ainvoke({
        "question_id": question_id,
        "question_type": question_type,
        "difficulty_stars": "⭐" * difficulty,
        "kp_text": kp_text,
        "question_content": question_content,
        "options_text": options_text,
        "correct_answer": correct_answer,
        "user_answer": user_answer,
        "judge_result": "正确" if is_correct else "错误",
    })
    analysis = parse_llm_json(response.content or "")

    # 3. Neo4j enrichment
    weak_points_raw = analysis.get("weak_point_analysis", [])
    rich_weak_points = await _enrich_weak_points(
        knowledge_point_ids or [], weak_points_raw, is_correct,
    )

    # 4. Learning path
    weak_tuples = [(wp["knowledge_point_id"], wp["current_mastery"]) for wp in rich_weak_points]
    learning_path = await path_service.generate_learning_path(
        user_id=user_id, weak_points=weak_tuples, target_ids=None, max_nodes=5,
    )

    # Assemble response
    error_analysis = analysis.get("error_analysis", {})
    return {
        "user_id": user_id,
        "question_id": question_id,
        "is_correct": is_correct,
        "error_analysis": ({
            "user_answer": user_answer,
            "correct_answer": correct_answer,
            "explanation": error_analysis.get("explanation", ""),
            "error_type": error_analysis.get("error_type", ""),
            "error_detail": error_analysis.get("error_detail", ""),
        } if not is_correct else None),
        "weak_point_analysis": rich_weak_points,
        "learning_path": learning_path if not is_correct else [],
    }


async def _enrich_weak_points(
    kp_ids: list[str], llm_analysis: list[dict], is_correct: bool,
) -> list[dict]:
    """Merge LLM mastery scores with Neo4j official knowledge point names."""
    result = []
    for kp_id in kp_ids:
        kp = await kg_service.get_knowledge_point(kp_id)
        existing = next(
            (w for w in llm_analysis if w.get("knowledge_point_id") == kp_id), None
        )
        result.append({
            "knowledge_point_id": kp_id,
            "knowledge_point_name": kp["name"] if kp else kp_id,
            "current_mastery": (
                existing.get("current_mastery", 0.5) if existing
                else (0.7 if is_correct else 0.3)
            ),
            "reason": (
                existing.get("reason", "") if existing
                else ("已掌握该知识点" if is_correct else "需要复习该知识点")
            ),
        })
    return result


def _judge(question_type: str, user_answer: str, correct_answer: str) -> bool:
    """Deterministic answer comparison — no LLM needed for choice/true-false."""
    ua = user_answer.strip().upper()
    ca = correct_answer.strip().upper()
    if question_type in ("single_choice", "true_false"):
        return ua == ca
    # For fill_blank / essay: exact match first, then contains with length guard
    # to avoid trivial substring matches (e.g. "A" matching "Java")
    if ua == ca:
        return True
    shorter = ua if len(ua) < len(ca) else ca
    longer = ca if len(ua) < len(ca) else ua
    if len(shorter) >= 2 and shorter in longer:
        return True
    return False
