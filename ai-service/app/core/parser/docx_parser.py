"""
DOCX 文档解析器 — 使用 python-docx 提取文本
"""

from app.exceptions import DocumentParseError


def parse_docx(file_path: str) -> str:
    """
    解析 DOCX 文件，提取全部文本

    Args:
        file_path: DOCX 文件路径

    Returns:
        提取的文本内容
    """
    try:
        from docx import Document

        doc = Document(file_path)
        paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
        return "\n".join(paragraphs)
    except Exception as e:
        raise DocumentParseError(f"DOCX 解析失败: {str(e)}")
