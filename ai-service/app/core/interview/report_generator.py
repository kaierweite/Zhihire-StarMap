"""
面试报告生成器 — 汇总评分 + 五维雷达图
"""

from app.infrastructure.llm_client import llm_client

# 五维雷达图维度（与 match_detail breakdown 对齐）
RADAR_DIMENSIONS = ["专业知识", "逻辑思维", "沟通表达", "岗位匹配", "发展潜力"]


async def generate_report(
    session_id: str,
    questions: list[dict],
    evaluations: list[dict],
) -> dict:
    """
    生成面试报告

    Returns:
        {"overall_score": 0-100, "radar": {"维度": 分数}, "feedback": [...]}
    """
    if not evaluations:
        return {
            "overall_score": 0,
            "radar": {d: 0 for d in RADAR_DIMENSIONS},
            "feedback": ["暂无面试数据"],
        }

    # 计算综合分
    scores = [e.get("score", 0) for e in evaluations]
    overall = round(sum(scores) / len(scores), 2)

    # 用 LLM 生成五维评分和评语
    eval_summary = "\n".join(
        f"题目{i+1}: {q.get('content', '')[:50]}... 得分: {e.get('score', 0)} 评语: {e.get('feedback', '')}"
        for i, (q, e) in enumerate(zip(questions, evaluations))
    )
    prompt = (
        "你是面试报告生成专家。根据以下面试评分数据，生成五维雷达图评分和综合评语。\n\n"
        f"面试评分摘要：\n{eval_summary}\n\n"
        f"五维维度：{', '.join(RADAR_DIMENSIONS)}\n\n"
        "请严格以 JSON 格式输出：\n"
        '{"radar": {"专业知识": 85, "逻辑思维": 78, ...}, "feedback": ["评语1", "评语2"]}'
    )
    try:
        result = await llm_client.chat_json(prompt, temperature=0.3)
        if isinstance(result, dict):
            return {
                "overall_score": overall,
                "radar": result.get("radar", {d: overall for d in RADAR_DIMENSIONS}),
                "feedback": result.get("feedback", [f"综合得分: {overall}"]),
            }
    except Exception:
        pass

    # 降级：用综合分填充所有维度
    return {
        "overall_score": overall,
        "radar": {d: overall for d in RADAR_DIMENSIONS},
        "feedback": [f"综合得分: {overall}", f"共回答 {len(evaluations)} 道题"],
    }
