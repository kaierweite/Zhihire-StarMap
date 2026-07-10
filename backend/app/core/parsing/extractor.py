"""?????????

?? pdfplumber (PDF) ? python-docx (DOCX) ????????
???????????/?????
"""
from pathlib import Path


def extract_text(file_path: str | Path) -> str:
    """??????????????

    Args:
        file_path: ???????

    Returns:
        str: ?????????

    Raises:
        ValueError: ???????
        FileNotFoundError: ??????
    """
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"?????: {file_path}")

    suffix = path.suffix.lower()
    if suffix == ".pdf":
        return _extract_pdf(path)
    elif suffix in (".doc", ".docx"):
        return _extract_docx(path)
    else:
        raise ValueError(f"??????: {suffix}")


def _extract_pdf(path: Path) -> str:
    """?? pdfplumber ?? PDF ???

    Args:
        path: PDF ?????

    Returns:
        str: ???????
    """
    import pdfplumber
    pages_text: list[str] = []
    with pdfplumber.open(str(path)) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if text:
                pages_text.append(text.strip())
    return "\n\n".join(pages_text)


def _extract_docx(path: Path) -> str:
    """?? python-docx ?? DOCX ???

    Args:
        path: DOCX ?????

    Returns:
        str: ???????
    """
    from docx import Document
    doc = Document(str(path))
    paragraphs: list[str] = []
    for p in doc.paragraphs:
        if p.text.strip():
            paragraphs.append(p.text.strip())
    return "\n\n".join(paragraphs)


def extract_images_as_base64(file_path: str | Path) -> list[str]:
    """??????????? base64??? vision ????

    ????? PDF??? pdfplumber ??????
    DOCX ???????

    Args:
        file_path: ???????

    Returns:
        list[str]: base64 ????????? data:image/png;base64, ????
    """
    path = Path(file_path)
    if not path.exists():
        return []

    suffix = path.suffix.lower()
    if suffix == ".pdf":
        return _extract_pdf_images(path)
    return []


def _extract_pdf_images(path: Path) -> list[str]:
    """? PDF ????? PNG ?? base64?

    Args:
        path: PDF ?????

    Returns:
        list[str]: base64 ????????
    """
    images: list[str] = []
    try:
        import pdfplumber
        with pdfplumber.open(str(path)) as pdf:
            for page in pdf.pages:
                img = page.to_image(resolution=150)
                from io import BytesIO
                import base64
                buf = BytesIO()
                img.save(buf, format="PNG")
                b64 = base64.b64encode(buf.getvalue()).decode("utf-8")
                images.append(f"data:image/png;base64,{b64}")
    except Exception:
        pass
    return images
