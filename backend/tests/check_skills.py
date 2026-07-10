"""Check user_skill records for zm_test2 user."""
import asyncio, sys, json
sys.path.insert(0, "backend")
if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
from app.db import compat
import app.db.session
from sqlalchemy import text

async def main():
    async with app.db.session.async_engine.connect() as conn:
        # Find zm_test2 user
        r = await conn.execute(text("SELECT id, username FROM public.user WHERE username = 'zm_test2'"))
        row = r.first()
        if not row:
            print("User zm_test2 NOT FOUND")
            return
        uid = row[0]
        print(f"User id={uid}: {row[1]}")

        # Check user_skill
        r = await conn.execute(text("SELECT COUNT(*) FROM user_skill WHERE user_id = :uid AND deleted_at = '0'"), {"uid": uid})
        count = r.scalar()
        print(f"user_skill count: {count}")

        # Check latest parse_task
        r = await conn.execute(text("SELECT id, status, file_id FROM parse_task WHERE user_id = :uid ORDER BY id DESC LIMIT 3"), {"uid": uid})
        for task in r:
            print(f"  task id={task[0]} status={task[1]} file_id={task[2]}")

asyncio.run(main())
