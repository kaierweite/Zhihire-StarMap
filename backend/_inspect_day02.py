import asyncio
import sys

async def main():
    sys.path.insert(0, r"C:\Users\Administrator\Desktop\Zhihire-StarMap\backend")
    from app.db import compat  # noqa: F401
    from app.db.session import async_engine
    from sqlalchemy import text
    async with async_engine.connect() as conn:
        for tbl in ["user_profile", "user_skill", "skill"]:
            r = await conn.execute(text(
                "SELECT column_name, data_type, is_nullable, column_default "
                "FROM information_schema.columns WHERE table_name=:t ORDER BY ordinal_position"
            ), {"t": tbl})
            print(f"=== {tbl} ===")
            for row in r:
                print(row)
        c = await conn.execute(text("SELECT count(*) FROM skill WHERE deleted_at='0'"))
        print("skill count:", c.scalar())

asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
asyncio.run(main())
