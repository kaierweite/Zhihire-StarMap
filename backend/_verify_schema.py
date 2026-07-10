"""数据库连接与表格结构验证脚本。"""
import asyncio
import sys

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

from app.db import compat  # noqa: F401
from sqlalchemy import text
from sqlalchemy.ext.asyncio import async_engine_from_config
from app.config.settings import settings


async def main():
    eng = async_engine_from_config(
        {"sqlalchemy.url": settings.database_url}, prefix="sqlalchemy."
    )
    async with eng.connect() as c:
        r = await c.execute(text("SELECT 1"))
        print(f"[OK] DB connected, SELECT 1 = {r.scalar()}")

        r = await c.execute(
            text(
                "SELECT column_name, data_type, is_nullable, column_default "
                "FROM information_schema.columns "
                "WHERE table_schema='public' AND table_name='user' "
                "ORDER BY ordinal_position"
            )
        )
        cols = r.fetchall()
        print(f"\n=== user table ({len(cols)} columns) ===")
        expect_user = {
            "id", "username", "password", "email", "phone",
            "role", "status", "avatar_url",
            "created_at", "updated_at", "deleted_at",
        }
        actual = {row[0] for row in cols}
        missing = expect_user - actual
        extra = actual - expect_user
        if missing:
            print(f"  MISSING: {missing}")
        if extra:
            print(f"  EXTRA: {extra}")
        if not missing and not extra:
            print("  All expected columns present")
        for row in cols:
            print(f"  {row[0]:15s} {row[1]:25s} nullable={row[2]}")

        r = await c.execute(
            text(
                "SELECT column_name, data_type, is_nullable, column_default "
                "FROM information_schema.columns "
                "WHERE table_schema='public' AND table_name='company' "
                "ORDER BY ordinal_position"
            )
        )
        cols = r.fetchall()
        print(f"\n=== company table ({len(cols)} columns) ===")
        expect_comp = {
            "id", "user_id", "company_name", "industry", "scale",
            "website", "logo_url", "description", "address",
            "contact_name", "contact_phone", "contact_email",
            "audit_status", "audit_reason",
            "created_at", "updated_at", "deleted_at",
        }
        actual = {row[0] for row in cols}
        missing = expect_comp - actual
        extra = actual - expect_comp
        if missing:
            print(f"  MISSING: {missing}")
        if extra:
            print(f"  EXTRA: {extra}")
        if not missing and not extra:
            print("  All expected columns present")
        for row in cols:
            print(f"  {row[0]:20s} {row[1]:25s} nullable={row[2]}")

        r = await c.execute(
            text("SELECT count(*) FROM \"user\" WHERE deleted_at = '0'")
        )
        print(f"\n[OK] user.active rows = {r.scalar()}")
        r = await c.execute(
            text("SELECT count(*) FROM company WHERE deleted_at = '0'")
        )
        print(f"[OK] company.active rows = {r.scalar()}")

    await eng.dispose()
    print("\nAll checks passed")


asyncio.run(main())
