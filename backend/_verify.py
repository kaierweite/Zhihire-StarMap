import asyncio, sys
sys.path.insert(0, r"C:\Users\Administrator\Desktop\Zhihire-StarMap\backend")
asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
from app.db import compat  # noqa
from app.db.session import async_engine
from sqlalchemy import text

async def main():
    async with async_engine.connect() as c:
        for tbl in ["user_work_experience","user_project_experience","user_language","user_certificate"]:
            r = await c.execute(text("SELECT column_name, data_type FROM information_schema.columns WHERE table_name=:t ORDER BY ordinal_position"), {"t": tbl})
            print(f"{tbl}: {[row[0] for row in r]}")
        r = await c.execute(text("SELECT column_name FROM information_schema.columns WHERE table_name='user_profile' AND column_name IN ('expected_position','expected_worktype','expected_industry')"))
        print("new cols:", [row[0] for row in r])
        r = await c.execute(text("SELECT column_name FROM information_schema.columns WHERE table_name='user_profile' AND column_name IN ('work_experiences','project_experiences','languages','certificates')"))
        print("jsonb still:", [row[0] for row in r])
asyncio.run(main())
