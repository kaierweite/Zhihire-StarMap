"""KingbaseES 兼容性补丁。

KingbaseES 返回的版本字符串 `KingbaseES V009R001C010` 不符合 PostgreSQL 格式，
导致 SQLAlchemy 在 `_get_server_version_info` 中抛出 AssertionError。
此模块在引擎创建前修补 PostgreSQL dialect，对 KingbaseES 返回预设版本号。
"""
import re  # 正则提取版本数字


# KingbaseES 版本号到 PostgreSQL 虚拟版本的映射（major, minor, patch）
# V009R001C010 -> 版本号取 release 和 iteration 作为主次版本号
_KB_VERSION_MAP: dict[str, tuple[int, ...]] = {}


def _patch_pg_dialect() -> None:
    """修补 SQLAlchemy PostgreSQL dialect 的版本识别。

    在引擎首次连接时，若服务端版本字符串包含 "KingbaseES"，
    则返回预设版本号 (16, 0, 0) 而非抛出异常。
    """
    from sqlalchemy.dialects.postgresql.base import PGDialect  # PostgreSQL 方言基类

    # 保存原始方法引用
    orig_get_version = PGDialect._get_server_version_info

    def _patched_get_version(self, connection):
        """重写版本识别：对 KingbaseES 返回兼容版本号。"""
        # 先尝试原始的解析逻辑
        try:
            return orig_get_version(self, connection)
        except AssertionError:
            pass

        # 原始逻辑抛出 AssertionError 时，说明是 KingbaseES 等非标准版本
        # 直接从连接游标读取版本字符串
        cursor = connection.exec_driver_sql("SELECT version()")
        row = cursor.fetchone()
        if row and "KingbaseES" in str(row[0]):
            # KingbaseES V009R001C010 -> 映射为 PG 16 兼容版本
            return (16, 0, 0)
        # 其他无法识别的情况，仍抛原始异常
        raise

    # 替换为修补后的方法
    PGDialect._get_server_version_info = _patched_get_version


# 在模块加载时自动执行修补
_patch_pg_dialect()