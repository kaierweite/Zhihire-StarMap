import asyncio, sys
sys.path.insert(0, r"C:\Users\Administrator\Desktop\Zhihire-StarMap\backend")
asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
from app.db import compat  # noqa
from app.db.session import async_engine
from sqlalchemy import text

async def main():
    async with async_engine.connect() as c:
        checks = {
            "user_profile intention cols": (
                "SELECT column_name, data_type FROM information_schema.columns "
                "WHERE table_name='user_profile' AND column_name IN "
                "('expected_position','expected_worktype','expected_industry')"
            ),
            "user_work_experience": (
                "SELECT column_name, data_type FROM information_schema.columns "
                "WHERE table_name='user_work_experience' ORDER BY ordinal_position"
            ),
            "user_project_experience": (
                "SELECT column_name, data_type FROM information_schema.columns "
                "WHERE table_name='user_project_experience' ORDER BY ordinal_position"
            ),
            "user_language": (
                "SELECT column_name, data_type FROM information_schema.columns "
                "WHERE table_name='user_language' ORDER BY ordinal_position"
            ),
            "user_certificate": (
                "SELECT column_name, data_type FROM information_schema.columns "
                "WHERE table_name='user_certificate' ORDER BY ordinal_position"
            ),
            "upload_file (day03)": (
                "SELECT column_name, data_type FROM information_schema.columns "
                "WHERE table_name='upload_file' ORDER BY ordinal_position"
            ),
            "resume (day03)": (
                "SELECT column_name, data_type FROM information_schema.columns "
                "WHERE table_name='resume' ORDER BY ordinal_position"
            ),
            "parse_task (day03)": (
                "SELECT column_name, data_type FROM information_schema.columns "
                "WHERE table_name='parse_task' ORDER BY ordinal_position"
            ),
            "resume_optimization (day03)": (
                "SELECT column_name, data_type FROM information_schema.columns "
                "WHERE table_name='resume_optimization' ORDER BY ordinal_position"
            ),
        }
        for label, sql in checks.items():
            print(f"\n--- {label} ---")
            r = await c.execute(text(sql))
            for row in r:
                print(f"  {row[0]:25s} {row[1]}")

asyncio.run(main())
