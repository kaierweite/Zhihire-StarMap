import asyncio, sys
sys.path.insert(0, r"C:\Users\Administrator\Desktop\Zhihire-StarMap\backend")
asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
from app.db import compat  # noqa
from app.db.session import async_engine
from sqlalchemy import text

async def main():
    async with async_engine.connect() as c:
        # 查 4 张子表是否存在
        tables = ["user_work_experience", "user_project_experience", "user_language", "user_certificate"]
        for t in tables:
            r = await c.execute(text("SELECT table_name FROM information_schema.tables WHERE table_name=:t"), {"t": t})
            exists = "EXISTS" if r.scalar() else "MISSING"
            print(f"{t}: {exists}")
        
        # 查 user_profile 的意向列
        r = await c.execute(text(
            "SELECT column_name FROM information_schema.columns "
            "WHERE table_name='user_profile' AND "
            "column_name IN ('expected_position','expected_worktype','expected_industry','work_experiences')"
        ))
        cols = [row[0] for row in r]
        print(f"\nuser_profile columns: {cols}")
        
        # 查 alembic_version 确认迁移已记录
        r = await c.execute(text("SELECT version_num FROM alembic_version"))
        print(f"\nalembic version: {r.scalar()}")

asyncio.run(main())
