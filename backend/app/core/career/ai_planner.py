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
并生成结构化的学习路径思维导图和完整的职业规划报告。

请严格按照以下格式输出纯 JSON（不要添加 markdown 代码块标记）：

{
  "target_role": "目标角色/专业名称",
  "analysis_summary": "一段分析总结，包括用户当前水平与目标的差距、建议方向等，不超过200字",
  "match_score": 匹配度分数(0-100之间的整数),
  "has_resume": true或false,
  "ai_suggestions": [
    {"title": "建议内容1"},
    {"title": "建议内容2"},
    {"title": "建议内容3"},
    {"title": "建议内容4"},
    {"title": "建议内容5"}
  ],
  "strength_weakness": {
    "strengths": ["优势1", "优势2", "优势3", "优势4"],
    "weaknesses": ["不足1", "不足2", "不足3", "不足4"]
  },
  "career_stages": [
    {"stage": "初级阶段", "title": "初级职位名称"},
    {"stage": "中级阶段", "title": "中级职位名称"},
    {"stage": "高级阶段", "title": "高级职位名称"},
    {"stage": "管理阶段", "title": "管理职位名称"}
  ],
  "gap_skills": [
    {"skill_name": "技能名称", "requirement_level": "MUST", "current_level": 当前掌握程度(0-100), "target_level": 目标掌握程度(0-100), "description": "技能描述"}
  ],
  "growth_curve": [
    {"label": "现在", "value": 当前能力值},
    {"label": "3个月后", "value": 预计能力值},
    {"label": "6个月后", "value": 预计能力值},
    {"label": "12个月后", "value": 预计能力值}
  ],
  "learning_resources": [
    {"id": 1, "title": "资源名称", "rating": 评分(1-5), "type": "类型"},
    {"id": 2, "title": "资源名称", "rating": 评分(1-5), "type": "类型"},
    {"id": 3, "title": "资源名称", "rating": 评分(1-5), "type": "类型"}
  ],
  "employment_outlook": {
    "salary_range": "薪资范围",
    "demand_level": "需求等级",
    "growth_rate": "增长率"
  },
  "learning_stats": {
    "total_hours": 预计总学习时长(小时),
    "completed_courses": 已完成课程数,
    "planned_courses": 计划学习课程数,
    "certificates": 已获得证书数,
    "completion_rate": 当前完成率(0-100),
    "target_completion_rate": 目标完成率(0-100)
  },
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
6. ai_suggestions 提供 5 条具体的学习建议
7. strength_weakness 各列出 3-4 项优势和不足
8. career_stages 列出 3-5 个职业发展阶段
9. growth_curve 根据学习路径预测未来 1 年的能力增长曲线
10. learning_resources 推荐 3-5 个学习资源（书籍/课程/网站）
11. employment_outlook 分析目标职业的就业前景
12. learning_stats 估算学习数据（总学时、课程数等）
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
        "ai_suggestions": [
            {"title": "建议补充相关技能知识"},
            {"title": "建议多参加实践项目"},
            {"title": "建议学习行业前沿技术"},
            {"title": "建议完善个人简历"},
            {"title": "建议多进行模拟面试"},
        ],
        "strength_weakness": {
            "strengths": ["基础扎实", "学习能力强", "态度积极"],
            "weaknesses": ["经验不足", "技能有待提升", "需要更多实践"],
        },
        "career_stages": [
            {"stage": "入门", "title": "初级岗位"},
            {"stage": "成长", "title": "中级岗位"},
            {"stage": "成熟", "title": "高级岗位"},
            {"stage": "突破", "title": "专家/管理"},
        ],
        "gap_skills": [],
        "growth_curve": [
            {"label": "现在", "value": 0},
            {"label": "3个月后", "value": 30},
            {"label": "6个月后", "value": 60},
            {"label": "12个月后", "value": 85},
        ],
        "learning_resources": [
            {"id": 1, "title": "相关技能学习课程", "rating": 4.5, "type": "在线课程"},
            {"id": 2, "title": "行业经典书籍", "rating": 4.8, "type": "书籍"},
            {"id": 3, "title": "技术社区与博客", "rating": 4.3, "type": "网站"},
        ],
        "employment_outlook": {
            "salary_range": "待分析",
            "demand_level": "中等",
            "growth_rate": "稳定增长",
        },
        "learning_stats": {
            "total_hours": 0,
            "completed_courses": 0,
            "planned_courses": 0,
            "certificates": 0,
            "completion_rate": 0,
            "target_completion_rate": 100,
        },
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
        data.setdefault("ai_suggestions", [])
        data.setdefault("strength_weakness", {"strengths": [], "weaknesses": []})
        data.setdefault("career_stages", [])
        data.setdefault("gap_skills", [])
        data.setdefault("growth_curve", [])
        data.setdefault("learning_resources", [])
        data.setdefault("employment_outlook", {"salary_range": "", "demand_level": "", "growth_rate": ""})
        data.setdefault("learning_stats", {
            "total_hours": 0, "completed_courses": 0, "planned_courses": 0,
            "certificates": 0, "completion_rate": 0, "target_completion_rate": 0,
        })
        data.setdefault("mind_map", {"name": "学习路径", "children": []})

        return data
    except json.JSONDecodeError:
        logger.error("LLM 返回非 JSON 格式: %s...", str(result)[:200])
        return _build_fallback(target_text)
    except Exception as e:
        logger.error("AI 规划生成失败: %s", e, exc_info=True)
        return _build_fallback(target_text)
