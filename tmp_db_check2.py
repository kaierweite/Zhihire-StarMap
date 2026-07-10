import sys, os, asyncio, selectors
if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
sys.path.insert(0, r"C:\Users\Administrator\Desktop\Zhihire-StarMap\backend")

async def test():
    from sqlalchemy import text
    from app.db.session import async_engine
    async with async_engine.connect() as conn:
        r = await conn.execute(text("SELECT 1"))
        print("1. DB ping:", r.scalar())

        r = await conn.execute(
            text("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public' ORDER BY table_name")
        )
        tables = [row[0] for row in r.fetchall()]
        needed = ["user", "company", "job", "job_application"]
        for t in needed:
            status = "OK" if t in tables else "MISSING"
            print(f"   [{status}] {t}")

        if "job_application" in tables:
            r = await conn.execute(
                text("SELECT column_name, data_type FROM information_schema.columns WHERE table_name = 'job_application' ORDER BY ordinal_position")
            )
            print("job_application columns:")
            for col, dtype in r.fetchall():
                print(f"   {col} ({dtype})")

    print()
    print("All DB checks passed!")

asyncio.run(test())
