"""答案分析服务 —— SmartLearn 的核心诊断引擎。

这是 SpringBoot 对接的核心服务，实现"分析-诊断-处方"闭环：
  收到题目 + 用户答案
    │
    ① 基础判题（规则匹配，毫秒级）
    │
    ② LLM 深度分析（Qwen-Max 同时做 3 件事）：
    │   - 错题解析（错误类型、错误原因、正确解题思路）
    │   - 薄弱点诊断（每个关联知识点的掌握度评估 + 判断依据）
    │   - 以上全部以 JSON 格式返回，方便程序解析
    │
    ③ Neo4j 补全（用图数据库补全知识点名称，保证返回结构一致）
    │
    ④ 学习路径生成（从薄弱点出发，Neo4j 图遍历 + LLM 学习建议）

为什么判题不交给 LLM：
- 选择题/判断题的判题是确定性的，规则匹配比 LLM 更快更可靠
- LLM 专注于分析"为什么错"，而不是判断"对还是错"
"""

from app.core.utils import parse_llm_json
from app.services import llm_service, path_service, kg_service

# 告诉 LLM 返回什么格式，以及各字段的含义
ERROR_ANALYSIS_PROMPT = """你是一个算法教学助手。分析学生的答题结果，给出诊断报告。

输出 JSON 格式：
{
  "is_correct": true/false,
  "error_analysis": {
    "explanation": "本题的详细解析，解释正确答案为什么对",
    "error_type": "概念混淆/知识漏洞/粗心错误/完全不会/方法错误",
    "error_detail": "针对学生错误答案的具体分析，指出哪里理解错了"
  },
  "weak_point_analysis": [
    {
      "knowledge_point_id": "对应知识点ID",
      "knowledge_point_name": "知识点名称",
      "current_mastery": 0.0-1.0,
      "reason": "为什么判断学生这个知识点薄弱"
    }
  ]
}

要求：
- explanation 要包含核心概念解释和解题思路
- 答对时 error_analysis 可简短，weak_point_analysis 给出巩固建议
- 答错时 error_analysis 要深入分析错误原因
- current_mastery: 0.0完全不会 0.3似懂非懂 0.6基本掌握 1.0完全掌握
- 只输出 JSON，不要其他内容"""


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
    """分析一次答题，返回诊断结果。

    返回 dict 结构参见 schemas.py 中的 AnswerAnalysisResponse。
    """
    # ① 规则判题（确定性，不需要 LLM）
    is_correct = _judge(question_type, user_answer, correct_answer)

    # ② 构造详细 prompt 让 LLM 深度分析
    options_text = "\n".join(options) if options else "无"
    kp_text = ", ".join(knowledge_point_ids) if knowledge_point_ids else "未知"

    prompt = (
        f"题目信息：\n"
        f"- 题目ID：{question_id}\n- 类型：{question_type}\n- 难度：{'⭐' * difficulty}\n"
        f"- 涉及知识点ID：{kp_text}\n- 题目内容：{question_content}\n"
        f"- 选项：{options_text}\n- 正确答案：{correct_answer}\n"
        f"- 学生答案：{user_answer}\n- 判题结果：{'正确' if is_correct else '错误'}\n"
    )

    response = await llm_service.chat([
        {"role": "system", "content": ERROR_ANALYSIS_PROMPT},
        {"role": "user", "content": prompt},
    ])
    analysis = parse_llm_json(response)

    # ③ 用 Neo4j 补全：确保知识点名称来自知识图谱，而非依赖 LLM 的猜测
    weak_points_raw = analysis.get("weak_point_analysis", [])
    rich_weak_points = await _enrich_weak_points(
        knowledge_point_ids or [], weak_points_raw, is_correct,
    )

    # ④ 从薄弱点出发规划学习路径
    weak_tuples = [(wp["knowledge_point_id"], wp["current_mastery"]) for wp in rich_weak_points]
    learning_path = await path_service.generate_learning_path(
        user_id=user_id, weak_points=weak_tuples, target_ids=None, max_nodes=5,
    )

    # 组装返回
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
        } if not is_correct else None),  # 答对不需要错题解析
        "weak_point_analysis": rich_weak_points,
        "learning_path": learning_path if not is_correct else [],  # 答对不需要学习路径
    }


async def _enrich_weak_points(
    kp_ids: list[str], llm_analysis: list[dict], is_correct: bool,
) -> list[dict]:
    """用 Neo4j 补全薄弱点的名称和掌握度信息。

    策略：如果 LLM 已经分析了某个知识点，用 LLM 的判断；
    否则用默认值（答对 → 0.7，答错 → 0.3）。
    """
    result = []
    for kp_id in kp_ids:
        kp = await kg_service.get_knowledge_point(kp_id)
        # 查找 LLM 是否分析过这个知识点
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
    """基础判题：规则匹配，不依赖 LLM。

    支持三种题型：
    - 单选/判断：精确匹配（忽略大小写和首尾空格）
    - 填空：精确匹配 或 包含匹配（容忍格式差异）
    """
    ua = user_answer.strip().upper()
    ca = correct_answer.strip().upper()
    if question_type in ("single_choice", "true_false"):
        return ua == ca
    return ua == ca or ca in ua or ua in ca
