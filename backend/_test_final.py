import asyncio, sys
if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
from app.db import compat  # noqa: F401

async def test():
    from app.db.session import AsyncSessionLocal
    from app.services.career_service import generate_plan
    
    async with AsyncSessionLocal() as db:
        try:
            result = await generate_plan(db, user_id=54, target_role_id=1)
            print('SUCCESS')
            d = result.model_dump()
            print('target_role:', d['target_role'])
            print('gap_skills:', len(d['gap_skills']))
            print('score:', d['score'])
        except Exception as e:
            import traceback
            traceback.print_exc()

asyncio.run(test())
