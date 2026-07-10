"""
PDF 文档解析器 — 使用 pdfplumber 提取文本
"""

from app.exceptions import DocumentParseError


def parse_pdf(file_path: str) -> str:
    """
    解析 PDF 文件，提取全部文本

    Args:
        file_path: PDF 文件路径

    Returns:
        提取的文本内容
    """
    try:
        import pdfplumber

        texts = []
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                text = page.extract_text()
                if text:
                    texts.append(text)
        return "\n".join(texts)
    except Exception as e:
        raise DocumentParseError(f"PDF 解析失败: {str(e)}")
