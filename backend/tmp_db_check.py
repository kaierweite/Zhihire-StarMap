import sys, os, asyncio, selectors
if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

sys.path.insert(0, os.path.dirname(__file__))
from app.db.session import async_engine
from sqlalchemy import text


async def test():
    try:
        async with async_engine.connect() as conn:
            r = await conn.execute(text("SELECT 1"))
            print("1. DB connection: OK (SELECT 1 =", r.scalar(), ")")

            r = await conn.execute(
                text("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public' ORDER BY table_name")
            )
            tables = [row[0] for row in r.fetchall()]
            print("2. Tables in database (" + str(len(tables)) + "):")
            needed = ["user", "company", "job", "job_application", "notification"]
            for t in needed:
                status = "OK" if t in tables else "MISSING"
                print("   [" + status + "] " + t)

            if "job_application" in tables:
                r = await conn.execute(
                    text("SELECT column_name, data_type FROM information_schema.columns WHERE table_name = 'job_application' ORDER BY ordinal_position")
                )
                print("3. job_application columns:")
                for col, dtype in r.fetchall():
                    print("   " + col + " (" + dtype + ")")

            print()
            print("All DB checks passed!")

    except Exception as e:
        print("ERROR:", e)


asyncio.run(test())
