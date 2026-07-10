"""Day02 冒烟测试：注册 -> 登录 -> GET profile -> PUT profile -> GET profile。
不依赖 HTTP 客户端，直接调用 service 层验证业务逻辑。
"""
import asyncio
import sys

sys.path.insert(0, r"C:\Users\Administrator\Desktop\Zhihire-StarMap\backend")

from app.db import compat  # noqa: F401
from app.db.session import AsyncSessionLocal
from app.models.entities.user import User
from app.models.schemas.auth import RegisterForm
from app.models.schemas.user import UserProfileUpdateForm
from app.services import auth_service, user_service


async def main():
    import time
    suffix = f"d2{int(time.time())}"
    username = f"test_{suffix}"
    form = RegisterForm(
        username=username,
        password="pass123456",
        role="USER",
        email=f"{username}@ex.com",
        phone="13800000000",
    )

    async with AsyncSessionLocal() as db:
        await auth_service.register(db, form)
        user = await __import__("app.repositories.user_repository", fromlist=["get_by_username"]).get_by_username(db, username)
        print("registered:", user.id, user.username)

        # GET profile (auto-create empty profile)
        dto = await user_service.get_profile(db, user)
        print("GET profile1 completeness:", dto.profile_completeness, "skills:", len(dto.skills))

        # PUT profile - update basic info + education + skills (mix exact, synonym, new candidate)
        upd = UserProfileUpdateForm(
            real_name="张三",
            gender="MALE",
            education="本科",
            school="电子科技大学",
            major="计算机科学与技术",
            current_city="成都",
            expected_city="成都",
            expected_salary_min=15000,
            expected_salary_max=25000,
            bio="热爱前端，熟悉 Vue 3 与 TypeScript。",
            skills=["Vue.js", "TypeScript", "不存在的新技能XYZ", "spring boot", "React"],
        )
        dto2 = await user_service.update_profile(db, user, upd)
        print("PUT profile2 completeness:", dto2.profile_completeness)
        print("  real_name:", dto2.real_name, "school:", dto2.school)
        print("  skills:", [(s.name, s.category) for s in dto2.skills])

        # GET profile again to confirm persistence
        dto3 = await user_service.get_profile(db, user)
        print("GET profile3 completeness:", dto3.profile_completeness, "skills:", len(dto3.skills))
        skill_names = sorted(s.name for s in dto3.skills)
        print("  skill_names persisted:", skill_names)

        # Verify candidate skill created
        from sqlalchemy import select
        from app.models.entities.skill import Skill
        r = await db.execute(select(Skill).where(Skill.name == "不存在的新技能XYZ"))
        cand = r.scalar_one_or_none()
        print("  candidate skill status:", cand.status if cand else "MISSING")

        # PUT with empty skills -> should soft-delete all user_skill
        upd_empty = UserProfileUpdateForm(skills=[])
        dto4 = await user_service.update_profile(db, user, upd_empty)
        print("PUT empty skills -> skills count:", len(dto4.skills))

        # salary sanity check
        from app.services.errors import BusinessError
        bad = UserProfileUpdateForm(expected_salary_min=30000, expected_salary_max=20000)
        try:
            await user_service.update_profile(db, user, bad)
            print("  ERROR: salary check failed")
        except BusinessError as e:
            print("  salary check ok:", e.code, e.message)


asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
asyncio.run(main())
