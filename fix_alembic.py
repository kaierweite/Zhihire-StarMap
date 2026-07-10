import sys, asyncio
sys.path.insert(0, "backend")
from app.db import compat  # noqa: F401
if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

from app.db.session import async_engine
from sqlalchemy import text

async def fix():
    async with async_engine.connect() as conn:
        result = await conn.execute(text("SELECT * FROM alembic_version"))
        print(f"Current: {result.scalar_one_or_none()}")
        
        await conn.execute(text("DELETE FROM alembic_version"))
        await conn.execute(text("INSERT INTO alembic_version (version_num) VALUES ('b0c1d2e3f4a5')"))
        await conn.commit()
        
        result = await conn.execute(text("SELECT * FROM alembic_version"))
        print(f"Updated to: {result.scalar_one_or_none()}")

asyncio.run(fix())
