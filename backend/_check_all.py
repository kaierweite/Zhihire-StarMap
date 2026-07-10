import asyncio, sys
sys.path.insert(0, r"C:\Users\Administrator\Desktop\Zhihire-StarMap\backend")
asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

from app.db import compat  # noqa
from app.db.session import async_engine
from sqlalchemy import text

async def main():
    async with async_engine.connect() as c:
        # 1. 连接测试
        r = await c.execute(text("SELECT version()"))
        print("DB connected:", r.scalar()[:60])
        
        # 2. 检查所有关键表
        tables = [
            "user", "user_profile", "user_skill", "skill", "skill_synonym",
            "upload_file", "resume", "parse_task", "resume_optimization",
            "user_work_experience", "user_project_experience", "user_language", "user_certificate",
            "company", "notification", "occupation_role", "job", "job_skill",
            "skill_relation", "occupation_role_skill", "match_result", "recommend_record",
            "career_plan", "ability_graph", "ai_chat_history",
            "login_log", "operation_log",
            "interview_session", "interview_question", "interview_answer", "interview_report",
            "alembic_version"
        ]
        for tbl in tables:
            r = await c.execute(text(
                "SELECT table_name FROM information_schema.tables WHERE table_name=:t"
            ), {"t": tbl})
            exists = "✓" if r.scalar() else "✗"
            if exists == "✓":
                # 检查行数
                try:
                    rc = await c.execute(text(f"SELECT count(*) FROM \"{tbl}\" WHERE deleted_at='0' OR deleted_at IS NULL"))
                    cnt = rc.scalar()
                    print(f"  {exists} {tbl:35s} {cnt:>6} rows")
                except:
                    rc = await c.execute(text(f"SELECT count(*) FROM \"{tbl}\""))
                    cnt = rc.scalar()
                    print(f"  {exists} {tbl:35s} {cnt:>6} rows")
            else:
                print(f"  {exists} {tbl}")
        
        # 3. 检查 user_profile 关键字段
        print("\n--- user_profile key columns ---")
        r = await c.execute(text(
            "SELECT column_name, data_type FROM information_schema.columns "
            "WHERE table_name='user_profile' ORDER BY ordinal_position"
        ))
        for row in r:
            print(f"  {row[0]:25s} {row[1]}")
        
        # 4. 检查 4 张子表字段
        for tbl in ["user_work_experience", "user_project_experience", "user_language", "user_certificate"]:
            print(f"\n--- {tbl} ---")
            r = await c.execute(text(
                "SELECT column_name, data_type, is_nullable FROM information_schema.columns "
                "WHERE table_name=:t ORDER BY ordinal_position"
            ), {"t": tbl})
            for row in r:
                print(f"  {row[0]:20s} {row[1]:10s} nullable={row[2]}")

asyncio.run(main())
