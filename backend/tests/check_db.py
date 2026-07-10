"""Check database connection and table structures."""
import asyncio, sys
sys.path.insert(0, "backend")
if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

from app.db import compat  # apply KingbaseES patch before engine creation
import app.db.session

from sqlalchemy import text

async def main():
    # 1. Connection
    try:
        async with app.db.session.async_engine.connect() as conn:
            r = await conn.execute(text("SELECT 1"))
            print(f"DB Connection: OK ({r.scalar()})")
    except Exception as e:
        print(f"DB Connection: FAIL - {e}")
        return

    # 2. List all tables
    async with app.db.session.async_engine.connect() as conn:
        rows = await conn.execute(text("""
            SELECT table_name, column_name, data_type
            FROM information_schema.columns
            WHERE table_schema = 'public'
            ORDER BY table_name, ordinal_position
        """))
        tables = {}
        for r in rows:
            tn = r[0]
            if tn not in tables:
                tables[tn] = []
            tables[tn].append(r[1] + " (" + r[2] + ")")

        print(f"\nTotal tables: {len(tables)}")

        # Required tables check
        required = [
            # Day00-02
            "user", "user_profile", "company",
            "skill", "skill_synonym",
            "user_skill", "user_work_experience", "user_project_experience",
            "user_language", "user_certificate",
            # Day03
            "upload_file", "resume", "parse_task", "resume_optimization",
            # Day04
            "skill_relation", "role", "role_skill", "ability_graph",
        ]

        for t in required:
            status = "[OK]" if t in tables else "[MISS]"
            print(f"  {status} {t}")

        # Day04 detail
        print("\n=== Day04 tables detail ===")
        for t in ["skill_relation", "role", "role_skill", "ability_graph", "skill"]:
            if t in tables:
                print(f"\n  {t}:")
                for c in tables[t]:
                    print(f"    {c}")
            else:
                print(f"\n  {t}: NOT FOUND")

        # Gap analysis
        needed = ["skill_relation", "role", "role_skill", "ability_graph"]
        print("\n\n=== Day04 Gap ===")
        for t in needed:
            if t in tables:
                print(f"  [EXISTS] {t}")
            else:
                print(f"  [CREATE] {t}")

asyncio.run(main())
