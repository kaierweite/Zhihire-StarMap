import sys, asyncio
sys.path.insert(0, '.')
from app.db import compat  # noqa: F401
if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
from app.db.session import async_engine
from sqlalchemy import text

async def verify():
    async with async_engine.connect() as conn:
        for tname in ('match_result', 'recommend_record'):
            result = await conn.execute(text(
                "SELECT column_name, data_type FROM information_schema.columns "
                "WHERE table_name = :t AND table_schema = current_schema() "
                "ORDER BY ordinal_position"
            ), {"t": tname})
            print(f'=== {tname} ===')
            for c in result.all():
                print(f'  {c[0]:20s} {c[1]:15s}')
        vr = await conn.execute(text('SELECT version_num FROM alembic_version'))
        print(f'Alembic: {vr.scalar_one()}')

asyncio.run(verify())
