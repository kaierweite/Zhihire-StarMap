"""
面试评答器 — 对照 expected_points 逐条评分
"""

from app.infrastructure.llm_client import llm_client


async def evaluate_answer(
    question_content: str,
    expected_points: list[str],
    user_answer: str,
) -> dict:
    """
    评分面试回答

    Returns:
        {"score": 0-100, "feedback": "...", "matched_points": [...], "missed_points": [...]}
    """
    prompt = (
        "你是一位专业面试评分官。请根据以下信息对候选人的回答进行评分。\n\n"
        f"题目：{question_content}\n"
        f"参考要点：{', '.join(expected_points)}\n"
        f"候选人回答：{user_answer}\n\n"
        "请严格以 JSON 格式输出：\n"
        '{"score": 85, "feedback": "评语", "matched_points": ["命中要点1"], "missed_points": ["遗漏要点1"]}'
    )
    try:
        result = await llm_client.chat_json(prompt, temperature=0.3)
        if isinstance(result, dict) and "score" in result:
            return result
    except Exception:
        pass
    # 降级：简单关键词匹配
    answer_lower = user_answer.lower()
    matched = [p for p in expected_points if p.lower() in answer_lower]
    missed = [p for p in expected_points if p.lower() not in answer_lower]
    score = round(len(matched) / max(len(expected_points), 1) * 100, 2)
    return {
        "score": score,
        "feedback": f"命中 {len(matched)}/{len(expected_points)} 个要点",
        "matched_points": matched,
        "missed_points": missed,
    }
