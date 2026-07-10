p = r"C:\Users\Administrator\Desktop\Zhihire-StarMap\backend\app\repositories\job_application_repository.py"
with open(p, encoding="utf-8") as f:
    content = f.read()

new_func = """
async def get_by_id(db: AsyncSession, application_id: int) -> JobApplication | None:
    \"\"\"按 ID 查询投递记录。\"\"\"
    stmt = select(JobApplication).where(
        JobApplication.id == application_id,
        JobApplication.deleted_at == "0",
    )
    result = await db.execute(stmt)
    return result.scalar_one_or_none()
"""

if "async def get_by_id" not in content:
    marker = "async def list_by_job("
    idx = content.index(marker)
    end = content.find("\nasync def ", idx + 1)
    if end < 0:
        end = len(content)
    content = content[:end] + new_func + content[end:]
    with open(p, "w", encoding="utf-8") as f:
        f.write(content)
    print("Added get_by_id to job_application_repository")
else:
    print("get_by_id already exists")
