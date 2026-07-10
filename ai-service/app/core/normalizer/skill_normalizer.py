"""
技能归一化器 — 调用 LLM 对原始技能文本进行归一化
"""

from app.infrastructure.llm_client import llm_client


async def normalize_skills(raw_text: str) -> list[str]:
    """
    从原始文本中提取并归一化技能列表

    Args:
        raw_text: 简历或 JD 的原始文本

    Returns:
        归一化后的技能名称列表
    """
    prompt = (
        "请从以下文本中提取所有技能名称，归一化为标准名称，"
        "以 JSON 数组格式返回，不要包含其他内容。\n\n"
        f"文本:\n{raw_text}"
    )
    result = await llm_client.chat(prompt, temperature=0.3)
    # 尝试解析 JSON 数组
    try:
        import json
        skills = json.loads(result)
        if isinstance(skills, list):
            return [str(s) for s in skills]
    except Exception:
        pass
    # 降级：按逗号分割
    return [s.strip() for s in result.split(",") if s.strip()]
