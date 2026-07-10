"""
面试服务 — 编排出题 / 评答 / 报告
"""

import logging

from app.core.interview.question_generator import generate_questions
from app.core.interview.evaluator import evaluate_answer
from app.core.interview.report_generator import generate_report

logger = logging.getLogger("zhihire.ai.interview")

# 内存缓存：session_id -> {questions, evaluations}
_sessions: dict[str, dict] = {}


async def get_questions(job_skills: list[str], user_skills: list[str], count: int = 5) -> list[dict]:
    """生成面试题"""
    return await generate_questions(job_skills, user_skills, count)


async def submit_answer(session_id: str, question_id: str, question_content: str, expected_points: list[str], answer: str) -> dict:
    """提交答案并评分"""
    result = await evaluate_answer(question_content, expected_points, answer)
    # 缓存到会话
    if session_id not in _sessions:
        _sessions[session_id] = {"questions": [], "evaluations": []}
    _sessions[session_id]["evaluations"].append(result)
    return result


async def get_report(session_id: str) -> dict:
    """获取面试报告"""
    session = _sessions.get(session_id, {"questions": [], "evaluations": []})
    return await generate_report(session_id, session["questions"], session["evaluations"])
