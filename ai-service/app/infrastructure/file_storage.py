"""
文件读取工具 — 读取本地文件内容（简历/JD）
"""

from pathlib import Path

from app.exceptions import FileReadError


class FileStorage:
    """本地文件读取，支持 pdf / docx / txt"""

    @staticmethod
    def read_text(file_path: str) -> str:
        """
        读取纯文本文件

        Args:
            file_path: 文件绝对路径

        Returns:
            文件文本内容
        """
        path = Path(file_path)
        if not path.exists():
            raise FileReadError(f"文件不存在: {file_path}")
        if not path.is_file():
            raise FileReadError(f"路径不是文件: {file_path}")
        try:
            return path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            return path.read_text(encoding="gbk")

    @staticmethod
    def get_file_type(file_path: str) -> str:
        """根据扩展名返回文件类型"""
        suffix = Path(file_path).suffix.lower()
        type_map = {
            ".pdf": "pdf",
            ".docx": "docx",
            ".doc": "docx",
            ".txt": "txt",
        }
        return type_map.get(suffix, "unknown")


# 全局单例
file_storage = FileStorage()
