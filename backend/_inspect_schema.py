import asyncio
import sys

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

from app.db import compat  # noqa: F401
from sqlalchemy import text
from sqlalchemy.ext.asyncio import async_engine_from_config
from app.config import settings


async def main():
    eng = async_engine_from_config(
        {"sqlalchemy.url": settings.database_url}, prefix="sqlalchemy."
    )
    async with eng.connect() as c:
        r = await c.execute(
            text(
                "SELECT table_name FROM information_schema.tables "
                "WHERE table_schema='public' ORDER BY table_name"
            )
        )
        print("TABLES:", [x[0] for x in r.fetchall()])
        for t in ["user", "company"]:
            r = await c.execute(
                text(
                    f"SELECT column_name,data_type,is_nullable,column_default "
                    f"FROM information_schema.columns WHERE table_schema='public' "
                    f"AND table_name='{t}' ORDER BY ordinal_position"
                )
            )
            print("==", t, "==")
            for row in r.fetchall():
                print("  ", row)
    await eng.dispose()


asyncio.run(main())
