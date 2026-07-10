import asyncio, sys
sys.path.insert(0, r"C:\Users\Administrator\Desktop\Zhihire-StarMap\backend")
asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
from app.db import compat  # noqa
from app.db.session import async_engine
from sqlalchemy import text

async def main():
    async with async_engine.connect() as c:
        tables = [
            "user", "user_profile", "user_skill", "skill", "skill_synonym",
            "upload_file", "resume", "parse_task", "resume_optimization",
            "user_work_experience", "user_project_experience", "user_language", "user_certificate",
            "company", "notification", "occupation_role", "job", "job_skill",
            "skill_relation", "occupation_role_skill", "match_result", "recommend_record",
            "career_plan", "ability_graph", "ai_chat_history",
            "login_log", "operation_log",
            "interview_session", "interview_question", "interview_answer", "interview_report",
        ]
        for tbl in tables:
            r = await c.execute(text("SELECT table_name FROM information_schema.tables WHERE table_name=:t"), {"t": tbl})
            if r.scalar():
                try:
                    rc = await c.execute(text(f"SELECT count(*) FROM \"{tbl}\""))
                    cnt = rc.scalar()
                    print(f"  [OK] {tbl:35s} {cnt:>6} rows")
                except Exception as e:
                    print(f"  [OK] {tbl:35s} count_error: {str(e)[:50]}")
            else:
                print(f"  [--] {tbl}")

asyncio.run(main())
