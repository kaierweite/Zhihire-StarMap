import os

p = r"C:\Users\Administrator\Desktop\Zhihire-StarMap\backend\app\db\compat.py"

with open(p, "r", encoding="utf-8") as f:
    c = f.read()

new_func = '''def _patch_pg_dialect() -> None:
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
    _PGDialect_common_psycopg._get_server_version_info = _maker(_PGDialect_common_psycopg._get_server_version_info)'''


start = c.find("def _patch_pg_dialect() -> None:")
end = c.find("\n_patch_pg_dialect()")
if start == -1 or end == -1:
    print("ERROR: could not find markers")
else:
    c = c[:start] + new_func + "\n\n" + c[end:]
    with open(p, "w", encoding="utf-8") as f:
        f.write(c)
    print("OK: compat.py updated")
