import asyncio
import sys

sys.path.insert(0, r"C:\Users\Administrator\Desktop\Zhihire-StarMap\backend")

from sqlalchemy import delete, select, text

from app.db import compat  # noqa: F401
from app.db.session import async_engine


async def main():
    async with async_engine.begin() as conn:
        # 找到测试用户
        result = await conn.execute(
            text("SELECT id FROM \"user\" WHERE username LIKE 'test_d2%' OR username LIKE 'test_ht%'")
        )
        user_ids = [r[0] for r in result.all()]
        if user_ids:
            ids_csv = ",".join(str(i) for i in user_ids)
            # 清理关联数据（按外键依赖顺序）
            await conn.execute(text(f"DELETE FROM user_skill WHERE user_id IN ({ids_csv})"))
            await conn.execute(text(f"DELETE FROM user_profile WHERE user_id IN ({ids_csv})"))
            await conn.execute(text(f"DELETE FROM \"user\" WHERE id IN ({ids_csv})"))
            print(f"deleted {len(user_ids)} test users and related data")
        else:
            print("no test users found")

        # 删除测试创建的候选技能
        result = await conn.execute(
            text("SELECT id, name FROM skill WHERE name IN ('不存在的新技能XYZ','新候选技能ABC')")
        )
        cand = result.all()
        if cand:
            for c in cand:
                await conn.execute(text(f"DELETE FROM skill_synonym WHERE skill_id = {c[0]}"))
            await conn.execute(
                text("DELETE FROM skill WHERE name IN ('不存在的新技能XYZ','新候选技能ABC')")
            )
            print(f"deleted candidate skills: {[c[1] for c in cand]}")
        else:
            print("no candidate test skills")


asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
asyncio.run(main())
