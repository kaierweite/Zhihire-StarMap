"""AI 驱动的职业规划分析器。

使用大模型分析用户简历与目标专业/岗位的差距，生成结构化学习路径思维导图。
"""
from __future__ import annotations

import json
import logging

logger = logging.getLogger(__name__)

_INPUT_LABELS = {
    "PROFESSION": "目标专业/方向",
    "JOB_DESCRIPTION": "目标岗位 JD（招聘要求）",
    "JOB_URL": "目标岗位招聘链接描述",
}


def build_prompt(
    target_text: str,
    input_type: str,
    user_skills: list[str],
    resume_summary: str | None = None,
) -> list[dict]:
    """构建 AI 分析提示词。

    Args:
        target_text: 用户输入的目标（专业名称 / JD 内容 / URL 描述）。
        input_type: 输入类型（PROFESSION / JOB_DESCRIPTION / JOB_URL）。
        user_skills: 用户已有的技能列表。
        resume_summary: 用户简历摘要（可选）。

    Returns:
        list[dict]: OpenAI 风格的消息列表。
    """
    system_prompt = """你是一位资深的职业规划师和技能图谱分析专家。
你需要基于用户已有的技能和简历信息，分析其与目标专业/岗位的差距，
并生成结构化的学习路径思维导图。

请严格按照以下格式输出纯 JSON（不要添加 markdown 代码块标记）：

{
  "target_role": "目标角色/专业名称",
  "analysis_summary": "一段分析总结，包括用户当前水平与目标的差距、建议方向等，不超过200字",
  "match_score": 匹配度分数(0-100之间的整数),
  "has_resume": true或false,
  "gap_skills": [
    {"skill_name": "技能名称", "requirement_level": "MUST", "description": "为什么需要这个技能"}
  ],
  "mind_map": {
    "name": "学习路径总览",
    "children": [
      {
        "name": "第一阶段名称",
        "children": [
          {"name": "具体技能/知识点"},
          {"name": "具体技能/知识点"}
        ]
      }
    ]
  }
}

要求：
1. mind_map 是一个树形结构，第一层子节点为学习阶段（3-5 个阶段），第二层为具体技能/知识点
2. gap_skills 按重要性排序，最多 10 项。MUST 为必备技能，NICE 为加分技能，BONUS 为锦上添花
3. match_score 基于用户已有技能与目标要求的重合度计算
4. analysis_summary 用中文，简洁专业
5. 如果用户没有简历信息 (has_resume=false)，请基于用户输入的技能进行分析
"""

    label = _INPUT_LABELS.get(input_type, "目标")
    user_skill_text = (
        "用户尚未录入技能信息"
        if not user_skills
        else f"用户已有技能：{', '.join(user_skills)}"
    )

    resume_text = ""
    if resume_summary:
        resume_text = f"\n用户简历摘要：{resume_summary[:500]}"

    user_prompt = f"## 用户信息\n{user_skill_text}{resume_text}\n\n## {label}\n{target_text}\n\n请全面分析用户与该目标的差距，生成详细的学习路径思维导图。"

    return [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt},
    ]


def _clean_json(text: str) -> str:
    """清理 LLM 返回文本，提取 JSON 部分。"""
    text = text.strip()
    if text.startswith("```json"):
        text = text[7:]
    elif text.startswith("```"):
        text = text[3:]
    if text.endswith("```"):
        text = text[:-3]
    return text.strip()


def _build_fallback(target_text: str) -> dict:
    """LLM 失败时返回降级数据。"""
    return {
        "target_role": target_text[:100],
        "analysis_summary": "AI 分析暂时不可用，请稍后重试",
        "match_score": 0,
        "has_resume": False,
        "gap_skills": [],
        "mind_map": {
            "name": "学习路径",
            "children": [
                {"name": "基础知识", "children": [{"name": "待补充"}]},
                {"name": "核心技能", "children": [{"name": "待补充"}]},
                {"name": "进阶提升", "children": [{"name": "待补充"}]},
            ],
        },
    }


async def analyze_and_plan(
    llm_chat_fn,
    target_text: str,
    input_type: str,
    user_skills: list[str],
    resume_summary: str | None = None,
) -> dict:
    """调用 LLM 分析差距并生成结构化规划数据。

    Args:
        llm_chat_fn: 异步 LLM 聊天函数，接受 messages 和 kwargs。
        target_text: 目标文本。
        input_type: 输入类型。
        user_skills: 用户技能列表。
        resume_summary: 简历摘要。

    Returns:
        dict: 结构化规划数据，包含 mind_map 和 gap_skills 等。
    """
    messages = build_prompt(target_text, input_type, user_skills, resume_summary)

    try:
        result = await llm_chat_fn(messages, temperature=0.3, max_tokens=4096)
        cleaned = _clean_json(result)
        data = json.loads(cleaned)

        # 保证必填字段
        data.setdefault("target_role", target_text[:100])
        data.setdefault("analysis_summary", "")
        data.setdefault("match_score", 0)
        data.setdefault("has_resume", resume_summary is not None)
        data.setdefault("gap_skills", [])
        data.setdefault("mind_map", {"name": "学习路径", "children": []})

        return data
    except json.JSONDecodeError:
        logger.error("LLM 返回非 JSON 格式: %s...", str(result)[:200])
        return _build_fallback(target_text)
    except Exception as e:
        logger.error("AI 规划生成失败: %s", e, exc_info=True)
        return _build_fallback(target_text)
