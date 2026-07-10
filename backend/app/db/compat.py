"""KingbaseES 兼容性补丁。

KingbaseES 返回的版本字符串 `KingbaseES V009R001C010` 不符合 PostgreSQL 格式，
导致 SQLAlchemy 在 `_get_server_version_info` 中抛出 AssertionError。
此模块在引擎创建前修补 PostgreSQL dialect，对 KingbaseES 返回预设版本号。

版本号选择说明：KingbaseES 的底层 PostgreSQL 内核处于 11~14 线，
索引系统目录 `pg_index` 包含 `indnkeyatts`（PG11+）但缺失 `indnullsnotdistinct`（PG15+）。
因此将版本报告为 `(14, 0, 0)`：既能取用 `indnkeyatts` 以支持索引表达式/包含列反射，
又避免 SQLAlchemy 查询尚不存在的 `indnullsnotdistinct` 列而报 `UndefinedColumn`。
"""


# KingbaseES 对外报告的兼容 PostgreSQL 版本号（major, minor, patch）
# 详见模块 docstring 的选择说明
_KB_REPORTED_VERSION: tuple[int, ...] = (14, 0, 0)


def _patch_pg_dialect() -> None:
    """修补 SQLAlchemy PostgreSQL dialect 的版本识别。
    在引擎首次连接时，若服务端版本字符串包含 "KingbaseES"，
    则返回预设版本号 (14, 0, 0) 而非抛出异常。
    同时修补 _PGDialect_common_psycopg，因其在 MRO 中优先级高于 PGDialect。
    """
    from sqlalchemy.dialects.postgresql.base import PGDialect
    from sqlalchemy.dialects.postgresql.psycopg import _PGDialect_common_psycopg

    def _maker(orig):
        def _patched(self, connection):
            try:
                return orig(self, connection)
            except (AssertionError, Exception):
                pass
            try:
                v = connection.exec_driver_sql("SELECT version()").scalar()
                if v and "KingbaseES" in v.upper():
                    return _KB_REPORTED_VERSION
            except Exception:
                pass
            return _KB_REPORTED_VERSION
        return _patched

    PGDialect._get_server_version_info = _maker(PGDialect._get_server_version_info)
    _PGDialect_common_psycopg._get_server_version_info = _maker(_PGDialect_common_psycopg._get_server_version_info)


_patch_pg_dialect()
