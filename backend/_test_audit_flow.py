import asyncio
import sys
if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

from app.db.session import async_session_factory
from app.models.entities.user import User
from app.models.entities.company import Company
from passlib.context import CryptContext
from sqlalchemy import select
from datetime import datetime

pwd = CryptContext(schemes=["bcrypt"])

async def test():
    async with async_session_factory() as db:
        # Find the test company
        all_companies = await db.execute(select(Company).where(Company.deleted_at == "0"))
        for c in all_companies.scalars().all():
            print(f"Company id={c.id}: {c.company_name}")
            print(f"  audit_status={c.audit_status}")
        
        # Find or create the admin user
        admin_user = None
        admin_result = await db.execute(select(User).where(User.username == "testadmin"))
        admin_user = admin_result.scalar_one_or_none()
        
        if admin_user:
            print(f"\nAdmin user: {admin_user.username}, current role: {admin_user.role}")
            if admin_user.role != "ADMIN":
                admin_user.role = "ADMIN"
                admin_user.updated_at = datetime.now()
                await db.flush()
                print("  -> Updated to ADMIN role")
        else:
            print("Creating new admin user...")
            hashed = pwd.hash("Admin123456")
            admin_user = User(
                username="testadmin",
                email="admin@test.com",
                password_hash=hashed,
                role="ADMIN",
                status="NORMAL",
                created_at=datetime.now(),
                updated_at=datetime.now(),
            )
            db.add(admin_user)
            await db.flush()
            print(f"  Created with id={admin_user.id}")
        
        await db.commit()

asyncio.run(test())
print("\nDone")
