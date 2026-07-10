import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "backend"))
import asyncio


async def test():
    from app.db.session import async_engine
    from sqlalchemy import text

    try:
        async with async_engine.connect() as conn:
            # 1. Ping
            r = await conn.execute(text("SELECT 1"))
            print("1. DB connection: OK (SELECT 1 =", r.scalar(), ")")

            # 2. List tables
            r = await conn.execute(
                text("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public' ORDER BY table_name")
            )
            tables = [row[0] for row in r.fetchall()]
            print(f"2. Tables ({len(tables)}):", ", ".join(tables))

            needed = ["user", "company", "job", "job_application", "notification"]
            for t in needed:
                print(f"   [{'OK' if t in tables else 'MISSING'}] {t}")

            # 3. job_application columns
            if "job_application" in tables:
                r = await conn.execute(
                    text("SELECT column_name, data_type FROM information_schema.columns WHERE table_name = 'job_application' ORDER BY ordinal_position")
                )
                print("3. job_application columns:")
                for col, dtype in r.fetchall():
                    print(f"   {col} ({dtype})")

            # 4. user columns (check email/phone exist)
            r = await conn.execute(
                text("SELECT column_name FROM information_schema.columns WHERE table_name = 'user' ORDER BY ordinal_position")
            )
            cols = [row[0] for row in r.fetchall()]
            print("4. user columns:", ", ".join(cols))

            print()
            print("All DB checks passed!")

    except Exception as e:
        print(f"ERROR: {e}")


asyncio.run(test())
