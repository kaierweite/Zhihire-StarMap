"""
解析服务 — 编排文档解析 + LLM 结构化提取 + 技能归一化
"""

import logging

from app.core.parser.pdf_parser import parse_pdf
from app.core.parser.docx_parser import parse_docx
from app.core.normalizer.skill_normalizer import normalize_skills
from app.infrastructure.llm_client import llm_client
from app.infrastructure.file_storage import file_storage

logger = logging.getLogger("zhihire.ai.parse")

# 简历解析 prompt
RESUME_PROMPT = (
    "请从以下简历文本中提取结构化信息，严格以 JSON 格式输出：\n"
    "{\n"
    '  "skills": ["技能1", "技能2"],\n'
    '  "experience": [{"company": "公司名", "role": "职位", "years": 2}],\n'
    '  "education": {"degree": "本科", "school": "学校名", "major": "专业"},\n'
    '  "summary": "一句话总结"\n'
    "}\n\n"
    "简历文本：\n{text}"
)

# JD 解析 prompt
JOB_PROMPT = (
    "请从以下岗位描述中提取结构化信息，严格以 JSON 格式输出：\n"
    "{\n"
    '  "skills": ["必会技能1", "必会技能2"],\n'
    '  "occupation_role_name": "岗位名称",\n'
    '  "requirements": {"degree": "学历要求", "experience_years": 3, "city": "城市"}\n'
    "}\n\n"
    "岗位描述：\n{text}"
)


def _extract_text(file_path: str) -> str:
    """根据文件类型提取文本"""
    file_type = file_storage.get_file_type(file_path)
    if file_type == "pdf":
        return parse_pdf(file_path)
    elif file_type == "docx":
        return parse_docx(file_path)
    else:
        return file_storage.read_text(file_path)


async def parse_resume(file_path: str) -> dict:
    """
    简历解析：提取文本 → LLM 结构化 → 技能归一化

    Returns:
        {"raw_text": "...", "skills": ["归一化技能"], "parsed_data": {...}}
    """
    raw_text = _extract_text(file_path)
    prompt = RESUME_PROMPT.replace("{text}", raw_text[:4000])
    parsed = await llm_client.chat_json(prompt, temperature=0.3)

    raw_skills = parsed.get("skills", [])
    normalized = await normalize_skills(raw_skills)
    canonical_skills = [item.get("canonical_name", item.get("raw", "")) for item in normalized]

    return {
        "raw_text": raw_text[:2000],
        "skills": canonical_skills,
        "parsed_data": {
            "experience": parsed.get("experience", []),
            "education": parsed.get("education", {}),
            "summary": parsed.get("summary", ""),
        },
    }


async def parse_job(file_path: str) -> dict:
    """
    岗位 JD 解析：提取文本 → LLM 结构化 → 技能归一化

    Returns:
        {"raw_text": "...", "skills": ["归一化技能"], "parsed_data": {...}}
    """
    raw_text = _extract_text(file_path)
    prompt = JOB_PROMPT.replace("{text}", raw_text[:4000])
    parsed = await llm_client.chat_json(prompt, temperature=0.3)

    raw_skills = parsed.get("skills", [])
    normalized = await normalize_skills(raw_skills)
    canonical_skills = [item.get("canonical_name", item.get("raw", "")) for item in normalized]

    return {
        "raw_text": raw_text[:2000],
        "skills": canonical_skills,
        "parsed_data": {
            "occupation_role_name": parsed.get("occupation_role_name", ""),
            "requirements": parsed.get("requirements", {}),
        },
    }
