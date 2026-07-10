"""
面试出题器 — 根据 JD + 用户技能生成面试题
"""

import json
import uuid

from app.infrastructure.llm_client import llm_client

QUESTION_TYPES = ["TECHNICAL", "BEHAVIORAL", "SITUATIONAL", "RESUME_BASED"]


async def generate_questions(
    job_skills: list[str],
    user_skills: list[str],
    count: int = 5,
) -> list[dict]:
    """
    生成面试题

    Returns:
        [{"question_id": "...", "type": "...", "content": "...", "expected_points": [...]}]
    """
    prompt = (
        f"你是一位专业面试官。请根据以下信息生成 {count} 道面试题。\n\n"
        f"岗位技能要求：{', '.join(job_skills)}\n"
        f"候选人技能：{', '.join(user_skills)}\n\n"
        "题型分布：TECHNICAL（技术题）、BEHAVIORAL（行为题）、SITUATIONAL（情景题）、RESUME_BASED（简历追问）\n"
        "每道题输出 JSON 格式：\n"
        '{"type": "TECHNICAL", "content": "题目内容", "expected_points": ["要点1", "要点2"]}\n\n'
        "请以 JSON 数组格式输出所有题目，不要包含其他文字。"
    )
    try:
        result = await llm_client.chat_json(prompt, temperature=0.5)
        if isinstance(result, list):
            for q in result:
                q["question_id"] = str(uuid.uuid4())[:8]
            return result
        if isinstance(result, dict) and "questions" in result:
            for q in result["questions"]:
                q["question_id"] = str(uuid.uuid4())[:8]
            return result["questions"]
    except Exception:
        pass
    # 降级：返回默认题
    return [
        {
            "question_id": str(uuid.uuid4())[:8],
            "type": "TECHNICAL",
            "content": f"请介绍一下你对 {job_skills[0] if job_skills else '相关技术'} 的理解。",
            "expected_points": ["基本概念", "实际应用"],
        }
    ]
