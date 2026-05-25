"""AI Guided Learning Mode - Plan-Execute-Reflection-RePlan loop.

All LLM calls use LangChain ChatPromptTemplate + ChatOpenAI chains.
"""

from fastapi import APIRouter, HTTPException
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from app.services import llm_service
from app.core.utils import parse_llm_json
from app.core.config import settings
import json

router = APIRouter(prefix="/api/learn", tags=["learning-agent"])


def _reraise_auth(e: Exception):
    """If the error is an authentication failure, surface it clearly to the frontend."""
    msg = str(e).lower()
    if "authentication" in msg or "governor" in msg or "unauthorized" in msg or "api key" in msg:
        raise HTTPException(status_code=500, detail=f"API Key 认证失败: {str(e)[:200]}")
    raise e


def _get(obj, *keys):
    for k in keys:
        if k in obj:
            return obj[k]
    return None


# -- helper: chunk long lists for LLM context --

def _chunk_questions(questions, max_per_chunk=30):
    """Split questions into chunks if there are too many for one LLM call."""
    for i in range(0, len(questions), max_per_chunk):
        yield questions[i:i + max_per_chunk]


# ---------------------------------------------------------------------------
# Prompt templates (module-level constants for testability)
# ---------------------------------------------------------------------------

PLAN_PROMPT = ChatPromptTemplate.from_messages([
    ("system", """你是一位资深的课程设计师和学科专家。你收到一份从 PDF 中提取的题库，
每道题包含 topic（主题）、content（题目内容摘要）、difficulty（难度 1-5）。

你的任务：
1. 通读所有题目，理解这个 PDF 涵盖的知识领域
2. 将题目按主题归类，提炼出 5-15 个核心知识点（按学习先后顺序排列）
3. 每个知识点写一段 150-300 字的教学讲解内容（包含核心概念、关键要点）
4. 为每个知识点指定匹配的题目 ID 列表

返回 JSON 格式：
{{"knowledgePoints": [
  {{
    "name": "知识点名称",
    "description": "一句话描述",
    "difficulty": 1-5,
    "order": 1,
    "explanation": "150-300字的教学讲解内容，要干货、清晰、有层次",
    "reason": "为什么应该学这个（与前置知识的关系）",
    "questionIds": [1, 5, 12]
  }},
  ...
]}}

规则：
- knowledgePoints 按 order 升序排列（从基础到进阶）
- 每个知识点至少匹配 1 道题，最多匹配 20 道题
- 每道题只能归属一个知识点
- explanation 必须基于题库内容的实际主题来写，不要编造无关内容
- 名称和描述用中文
只返回 JSON，不要加任何解释。"""),
    ("human", "PDF 名称：{pdf_name}\n\n题库内容（共 {question_count} 题）：\n{questions_json}"),
])

JUDGE_PROMPT = ChatPromptTemplate.from_messages([
    ("human", """你是一位阅卷老师。请按以下步骤评判学生答案：

第一步：仔细读题。题目问的是什么？需要学生回答哪些核心要点？题目没问的内容不算核心要点。
第二步：读标准答案。标准答案可能包含超出题目要求的补充知识，但评判时以题目问了什么为准，不以标准答案有多少为准。
第三步：对比学生答案。学生答到了题目的核心要点吗？有没有明显错误？

关键原则：
- 如果学生答全了题目问的核心要点，即使标准答案里有更多内容，也该给高分
- 标准答案中的默认值、占用大小、历史背景等如题目没问，遗漏不扣分
- 只有题目明确问了但学生没答、或答错了，才扣分

题目：{q_text}
标准答案（供参考，可能包含超出题目要求的补充内容）：{correct_answer}
学生答案：{user_answer}

返回 JSON：
{{"score": 0.0-1.0, "level": "完全正确|基本答对|部分正确|答错", "reason": "一句话说明（需指出学生答到了什么、遗漏了题目要求的什么）"}}

评分标准：
1.0 完全正确 — 题目问的核心要点全部命中，无明显错误
0.7-0.9 基本答对 — 核心要点命中，但题目要求的部分细节遗漏
0.4-0.6 部分正确 — 命中一半左右或存在部分理解偏差
0.0-0.3 答错 — 核心概念错误或完全偏离题目
只返回 JSON。"""),
])

TEST_GEN_PROMPT = ChatPromptTemplate.from_messages([
    ("human", """你是一位考官。学生刚学完以下 {kp_count} 个知识点，需要出 {test_size} 道综合测试题。

知识点及其题目 ID 列表：{kp_summary}

请从每个知识点的题目 ID 中挑选 1-3 道最有代表性的题目，确保测试覆盖所有知识点。
返回 JSON：{{"selectedIds": [1, 5, 12, ...]}}（仅 ID 列表，共 {test_size} 个）
只返回 JSON。"""),
])

EVAL_PROMPT = ChatPromptTemplate.from_messages([
    ("human", """你是一位考官。学生完成了一次综合测试，共 {answer_count} 道题。

测试答题记录：{answers_json}

请评估：
1. 整体掌握度（0.0-1.0）
2. 哪些知识点薄弱（列出名称）
3. 如果掌握度低于 {threshold}，为薄弱知识点规划一个新的学习路径（3-5个节点）

返回 JSON：
{{
  "mastery": 0.0-1.0,
  "weakPointNames": ["知识点名", ...],
  "newLearningPath": [
    {{
      "name": "知识点名",
      "description": "一句话描述",
      "difficulty": 1-5,
      "explanation": "100-200字教学讲解",
      "reason": "为什么需要重新学这个"
    }},
    ...
  ] or null
}}
只返回 JSON。"""),
])


# ---------------------------------------------------------------------------
# generate-plan  —  the heart of AI-guided learning
# ---------------------------------------------------------------------------

@router.post("/generate-plan")
async def generate_plan(req: dict):
    """LLM reads every question from the PDF, distills them into knowledge points,
    orders basic→advanced, writes teaching outlines, and matches which questions
    belong to each knowledge point.

    Request: {
        "pdf_import_id": 1,
        "pdf_name": "concurrency.pdf",
        "questions": [
            {"id": 1, "topic": "Thread", "type": "single_choice",
             "content": "Which method starts a thread?", "difficulty": 2,
             "correctAnswer": "start()"},
            ...
        ]
    }

    Response: {
        "learningPath": [
            {
                "knowledgePoint": {"id":"kp_0","name":"...","description":"...","difficulty":1},
                "reason": "why learn this",
                "explanation": "detailed teaching content",
                "questionIds": [1, 5, 12]
            },
            ...
        ]
    }
    """
    questions = _get(req, "questions")
    pdf_name = _get(req, "pdf_name", "pdfName") or "Unknown PDF"

    if not questions or not isinstance(questions, list) or len(questions) == 0:
        raise HTTPException(status_code=400, detail="No questions provided from this PDF.")

    llm_service.require_api_key()

    # Build a compact representation: topic + content summary
    compact = []
    for q in questions:
        content = (_get(q, "content") or "")[:120]
        topic = _get(q, "topic") or ""
        qtype = _get(q, "type") or "single_choice"
        diff = _get(q, "difficulty") or 1
        qid = _get(q, "id")
        compact.append({
            "id": qid,
            "topic": topic,
            "type": qtype,
            "difficulty": diff,
            "content": content,
        })

    questions_json = json.dumps(compact, ensure_ascii=False)

    try:
        llm = ChatOpenAI(
            model=settings.llm_model,
            api_key=llm_service.get_effective_api_key(),
            base_url=settings.deepseek_base_url,
            temperature=0.3,
            max_tokens=4096,
        )
        chain = PLAN_PROMPT | llm
        response = await chain.ainvoke({"pdf_name": pdf_name, "question_count": len(compact), "questions_json": questions_json})
        plan_data = parse_llm_json(response.content or "")
    except HTTPException:
        raise
    except Exception as e:
        _reraise_auth(e)
        raise HTTPException(status_code=500, detail=f"LLM学习计划生成失败: {str(e)[:300]}")

    kps = plan_data.get("knowledgePoints", [])
    if not kps:
        raise HTTPException(status_code=500, detail="LLM returned no knowledge points")

    # Sort by order
    kps.sort(key=lambda k: k.get("order", 99))

    learning_path = []
    for i, kp in enumerate(kps):
        node = {
            "knowledgePoint": {
                "id": f"kp_{i}",
                "name": kp.get("name", f"Topic {i+1}"),
                "description": kp.get("description", ""),
                "difficulty": kp.get("difficulty", 1),
                "category": kp.get("name", ""),
            },
            "reason": kp.get("reason", ""),
            "explanation": kp.get("explanation", ""),
            "questionIds": kp.get("questionIds", []),
        }
        learning_path.append(node)

    return {"learningPath": learning_path}


# ---------------------------------------------------------------------------
# submit-answer  —  AI semantic judging
# ---------------------------------------------------------------------------

@router.post("/submit-answer")
async def submit_answer(req: dict):
    """AI semantic judging for all question types.

    - Choice/true_false: exact match (instant)
    - Essay/fill_blank: LLM compares semantics, returns 0.0-1.0 score
    """
    user_answer = (_get(req, "userAnswer", "user_answer") or "").strip()
    correct_answer = (_get(req, "correctAnswer", "correct_answer") or "").strip()

    llm_service.require_api_key()

    question_data = _get(req, "questionJson", "question_json", "question")
    q_type = ""
    q_text = ""
    if isinstance(question_data, dict):
        q_type = (question_data.get("type") or "").lower()
        q_text = question_data.get("content", "")
    elif isinstance(question_data, str):
        q_text = question_data

    is_choice = q_type in ("single_choice", "true_false")
    need_ai = True  # default: use AI judge

    if is_choice:
        is_correct = user_answer.lower() == correct_answer.lower()
        if is_correct:
            return {
                "isCorrect": True, "score": 1.0, "level": "完全正确",
                "reflectionSummary": "回答正确。",
                "conclusion": "forward",
            }
        # Wrong choice: use AI for reflection analysis
        score = 0.0
        level = "答错"
        judge_reason = ""

    if need_ai:
        try:
            chain = JUDGE_PROMPT | llm_service.get_model()
            response = await chain.ainvoke({
                "q_text": q_text,
                "correct_answer": correct_answer,
                "user_answer": user_answer,
            })
            judge_data = parse_llm_json(response.content or "")
        except Exception as e:
            _reraise_auth(e)
            judge_data = {}

        score = float(judge_data.get("score", 0.0))
        level = judge_data.get("level", "答错")
        judge_reason = judge_data.get("reason", "")
    else:
        # Choice question, wrong answer
        score = 0.0
        level = "答错"
        judge_reason = f"正确答案是 {correct_answer}"

    if score >= 0.85:
        conclusion = "forward"
        reflection = level
    elif score >= 0.5:
        conclusion = "reinforce"
        reflection = f"{level}。" + (judge_reason if judge_reason else "需要巩固。")
    else:
        conclusion = "reinforce"
        reflection = f"{level}。" + (judge_reason if judge_reason else "基础薄弱。")

    return {
        "isCorrect": score >= 0.85,
        "score": score,
        "level": level,
        "reflectionSummary": reflection,
        "conclusion": conclusion,
    }


# ---------------------------------------------------------------------------
# generate-test  —  comprehensive final exam
# ---------------------------------------------------------------------------

@router.post("/generate-test")
async def generate_test(req: dict):
    """AI selects N questions covering all learned knowledge points.

    Request: {"knowledgePoints": [{"name":"...","questionIds":[1,2,3]}, ...], "totalQuestions": 115}
    Response: {"testQuestions": [{id, type, content, options, ...}]}
    """
    kps = _get(req, "knowledgePoints") or []
    total = _get(req, "totalQuestions") or 10

    llm_service.require_api_key()

    if not kps:
        raise HTTPException(status_code=400, detail="No knowledge points provided")

    # Build a summary of all KP names
    kp_names = [kp.get("name", "") for kp in kps]
    all_qids = []
    for kp in kps:
        qids = kp.get("questionIds", [])
        all_qids.extend(qids)

    # Determine test size: 2-3 questions per KP, capped at total
    n_per_kp = min(3, max(1, len(all_qids) // max(len(kps), 1)))
    test_size = min(len(kps) * n_per_kp, len(all_qids), 20)

    # LLM selects which question IDs to use for the test
    kp_summary = json.dumps([
        {"name": kp.get("name"), "questionIds": kp.get("questionIds", [])}
        for kp in kps
    ], ensure_ascii=False)

    try:
        chain = TEST_GEN_PROMPT | llm_service.get_model()
        response = await chain.ainvoke({
            "kp_count": len(kps), "test_size": test_size, "kp_summary": kp_summary,
        })
        data = parse_llm_json(response.content or "")
    except Exception as e:
        _reraise_auth(e)
        # Fallback: pick evenly from each KP
        selected = []
        for kp in kps:
            qids = kp.get("questionIds", [])
            if qids:
                selected.append(qids[0])
        data = {"selectedIds": selected}

    return {"selectedIds": data.get("selectedIds", [])}


# ---------------------------------------------------------------------------
# evaluate-test  —  score the test and decide pass / re-plan
# ---------------------------------------------------------------------------

@router.post("/evaluate-test")
async def evaluate_test(req: dict):
    """Evaluate test results. If mastery < threshold, generate a new learning plan.

    Request: {
        "answers": [{"questionId":1, "question":"...", "userAnswer":"...", "correctAnswer":"..."}, ...],
        "knowledgePoints": [{"name":"...", "questionIds":[...]}, ...],
        "threshold": 0.7
    }
    Response: {
        "mastery": 0.65,
        "passed": false,
        "weakPoints": ["Thread Safety", "CAS"],
        "newLearningPath": [...] or null
    }
    """
    answers = _get(req, "answers") or []
    kps = _get(req, "knowledgePoints") or []
    threshold = _get(req, "threshold") or 0.7

    llm_service.require_api_key()

    if not answers:
        raise HTTPException(status_code=400, detail="No answers provided")

    # Build test summary for LLM
    compact = []
    for a in answers:
        compact.append({
            "qid": a.get("questionId"),
            "content": (a.get("question") or a.get("content") or "")[:100],
            "user": a.get("userAnswer", ""),
            "correct": a.get("correctAnswer", ""),
        })

    try:
        chain = EVAL_PROMPT | llm_service.get_model()
        response = await chain.ainvoke({
            "answer_count": len(answers),
            "answers_json": json.dumps(compact, ensure_ascii=False),
            "threshold": threshold,
        })
        data = parse_llm_json(response.content or "")
    except Exception as e:
        _reraise_auth(e)
        data = {}

    mastery = float(data.get("mastery", 0.5))
    weak_names = data.get("weakPointNames", [])
    new_path = data.get("newLearningPath")

    # If passed, no new path needed
    if mastery >= threshold:
        return {
            "mastery": mastery,
            "passed": True,
            "weakPoints": weak_names,
            "newLearningPath": None,
        }

    # Build learning path nodes from weak points
    learning_path = []
    if new_path and isinstance(new_path, list):
        for i, node in enumerate(new_path):
            learning_path.append({
                "knowledgePoint": {
                    "id": f"retest_{i}",
                    "name": node.get("name", f"Weak point {i+1}"),
                    "description": node.get("description", ""),
                    "difficulty": node.get("difficulty", 3),
                    "category": "补强",
                },
                "reason": node.get("reason", ""),
                "explanation": node.get("explanation", ""),
                "questionIds": [],
            })

    return {
        "mastery": mastery,
        "passed": False,
        "weakPoints": weak_names,
        "newLearningPath": learning_path,
    }
