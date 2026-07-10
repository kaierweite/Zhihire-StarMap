"""文件本地存储防腐层。

负责上传文件的落地、读取与访问 URL 生成，
将文件系统细节隔离在 infrastructure 层内，业务层只拿到抽象路径。
"""
import os  # 路径拼接与目录创建
import shutil  # 高阶文件操作（如保存到目标路径）
import uuid  # 生成唯一文件名，避免冲突
from pathlib import Path  # 面向对象的路径操作

from fastapi import UploadFile  # FastAPI 上传文件类型

from app.config.settings import settings  # 全局配置（存储目录与 URL 前缀）


class FileStore:
    """本地文件存储。

    Attributes:
        storage_dir: 文件落地物理目录。
        base_url: 文件对外访问的 URL 前缀。
    """

    def __init__(self) -> None:
        # 取配置中的存储目录并转为绝对路径，便于稳定定位
        self.storage_dir = Path(settings.file_storage_dir).resolve()
        # 取配置中的 URL 前缀
        self.base_url = settings.file_base_url
        # 启动时确保目录存在，缺失则递归创建
        self.storage_dir.mkdir(parents=True, exist_ok=True)

    def _build_filename(self, original: str) -> str:
        """基于原始文件名生成唯一存储文件名。

        Args:
            original: 原始文件名，用于提取扩展名。

        Returns:
            str: 带扩展名的唯一文件名。
        """
        # 生成全局唯一标识
        unique = uuid.uuid4().hex
        # 取扩展名，缺失则为空
        _, ext = os.path.splitext(original)
        # 组合唯一文件名，保留原有扩展名
        return f"{unique}{ext}"

    async def save(self, file: UploadFile, subdir: str = "") -> str:
        """保存上传文件并返回相对访问路径。

        Args:
            file: FastAPI 上传文件对象。
            subdir: 可选子目录，用于按业务分类存储。

        Returns:
            str: 形如 `/files/abc123.pdf` 的访问路径。
        """
        # 确定目标目录：根存储目录 + 可选子目录
        target_dir = self.storage_dir / subdir if subdir else self.storage_dir
        # 确保子目录存在
        target_dir.mkdir(parents=True, exist_ok=True)
        # 生成唯一文件名
        filename = self._build_filename(file.filename or "upload")
        # 目标完整物理路径
        dest = target_dir / filename

        # 异步读取流并写到磁盘：以管理维护上下文拿到 file-like 对象
        with dest.open("wb") as buffer:
            # file.file 是 SpooledTemporaryFile，直接复制以节省内存
            shutil.copyfileobj(file.file, buffer)

        # 拼装相对访问路径，业务层存库使用返回值
        relative = filename if not subdir else f"{subdir}/{filename}"
        return f"{self.base_url}/{relative}"

    def resolve_path(self, access_path: str) -> Path:
        """将访问路径还原为磁盘物理路径。

        Args:
            access_path: save 返回的访问路径。

        Returns:
            Path: 对应的物理文件路径。
        """
        # 去掉 URL 前缀，得到相对子路径
        relative = access_path.removeprefix(self.base_url).lstrip("/")
        # 拼接到存储目录
        return self.storage_dir / relative


# 模块级单例
file_store = FileStore()