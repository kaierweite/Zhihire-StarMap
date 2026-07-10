"""Check database connection and table structures."""
import asyncio, sys, json
sys.path.insert(0, "backend")
if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
from sqlalchemy import text

async def main():
    from app.db.session import async_engine
    # 1. Connection
    try:
        async with async_engine.connect() as conn:
            r = await conn.execute(text("SELECT 1"))
            print(f"DB Connection: OK ({r.scalar()})")
    except Exception as e:
        print(f"DB Connection: FAIL - {e}")
        return

    # 2. List all tables + columns
    async with async_engine.connect() as conn:
        rows = await conn.execute(text("""
            SELECT table_name, column_name, data_type, character_maximum_length, is_nullable
            FROM information_schema.columns
            WHERE table_schema = 'public'
            ORDER BY table_name, ordinal_position
        """))
        tables = {}
        for r in rows:
            tn = r[0]
            if tn not in tables:
                tables[tn] = []
            tables[tn].append({
                "col": r[1], "type": r[2],
                "len": r[3], "null": r[4]
            })

        required = [
            "user", "user_profile", "company",
            "skill", "skill_synonym", "skill_relation",
            "role", "role_skill",
            "user_skill", "user_work_experience", "user_project_experience",
            "user_language", "user_certificate",
            "upload_file", "resume", "parse_task", "resume_optimization",
            "ability_graph"
        ]

        print(f"\nAll tables ({len(tables)}):")
        for tname in required:
            if tname in tables:
                cols = [c['col'] for c in tables[tname]]
                print(f"  [OK] {tname}: {', '.join(cols[:6])}...")
            else:
                print(f"  [MISS] {tname} -- NOT FOUND")

        # Print full structure for Day04-relevant tables
        print("\nDetailed: skill_relation / role / role_skill / ability_graph")
        for tname in ["skill_relation", "role", "role_skill", "ability_graph", "skill"]:
            if tname in tables:
                for c in tables[tname]:
                    print(f"  {tname}.{c['col']} ({c['type']})")
            else:
                print(f"  {tname}: TABLE NOT FOUND")

asyncio.run(main())
