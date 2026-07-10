import re, os

BASE = r"C:\Users\Administrator\Desktop\Zhihire-StarMap\backend"

# === 1. Add schema models to job.py ===
sp = os.path.join(BASE, r"app\models\schemas\job.py")
with open(sp, encoding="utf-8") as f:
    content = f.read()

marker = "class ApplyJobResult"
if "class UpdateApplicationStatusRequest" not in content:
    idx = content.index(marker)
    end = content.find("\nclass ", idx + 1)
    insert_pos = end if end > 0 else len(content)

    new_code = (
        '\n'
        '\n'
        'class UpdateApplicationStatusRequest(BaseModel):\n'
        '    """更新投递状态请求。"""\n'
        '    status: str = Field(..., description="ACCEPTED / REJECTED")\n'
        '\n'
        '\n'
        'class UpdateApplicationStatusResult(BaseModel):\n'
        '    """更新投递状态结果。"""\n'
        '    id: int\n'
        '    status: str\n'
    )
    content = content[:insert_pos] + new_code + content[insert_pos:]
    with open(sp, "w", encoding="utf-8") as f:
        f.write(content)
    print("Added schema models")

# === 2. Add update_application_status to job_service.py ===
jp = os.path.join(BASE, r"app\services\job_service.py")
with open(jp, encoding="utf-8") as f:
    content = f.read()

if "async def update_application_status" not in content:
    new_func = (
        '\n'
        '\n'
        'async def update_application_status(\n'
        '    db: AsyncSession, company_id: int, application_id: int, status: str,\n'
        ') -> dict:\n'
        '    """企业更新投递状态（ACCEPTED/REJECTED），并发送通知给求职者。"""\n'
        '    from app.repositories import job_application_repository\n'
        '    from app.repositories import company_repository\n'
        '\n'
        '    app = await job_application_repository.get_by_id(db, application_id)\n'
        '    if app is None:\n'
        '        raise BusinessError(404, "投递记录不存在")\n'
        '\n'
        '    job = await job_repository.get_by_id(db, app.job_id)\n'
        '    if job is None or job.company_id != company_id:\n'
        '        raise BusinessError(404, "岗位不存在")\n'
        '\n'
        '    app.status = status\n'
        '    await db.flush()\n'
        '\n'
        '    # Send APPLICATION notification to the candidate\n'
        '    try:\n'
        '        company = await company_repository.get_by_company_id(db, company_id)\n'
        '        company_name = company.company_name if company else ""\n'
        '        await send_notification(\n'
        '            db,\n'
        '            user_id=app.user_id,\n'
        '            title="投递状态更新",\n'
        '            type_="APPLICATION",\n'
        '            content=f"{company_name}已处理您的「{job.title}」投递，状态为：{status}。",\n'
        '        )\n'
        '    except Exception:\n'
        '        pass\n'
        '\n'
        '    await db.commit()\n'
        '    return {"id": app.id, "status": app.status}\n'
    )
    content += new_func
    with open(jp, "w", encoding="utf-8") as f:
        f.write(content)
    print("Added service function")

# === 3. Add router endpoint ===
rp = os.path.join(BASE, r"app\api\v1\job.py")
with open(rp, encoding="utf-8") as f:
    content = f.read()

if "update_application_status" not in content:
    # Update imports
    old_block = (
        'from app.models.schemas.job import (\n'
        '    ApplyJobRequest,\n'
        '    AddJobSkillRequest,\n'
        '    CreateJobRequest,\n'
        '    JobApplicationItem,\n'
        '    JobDetail,\n'
        '    JobItem,\n'
        '    JobSkillItem,\n'
        '    UpdateJobRequest,\n'
        ')\n'
    )
    new_block = (
        'from app.models.schemas.job import (\n'
        '    ApplyJobRequest,\n'
        '    AddJobSkillRequest,\n'
        '    CreateJobRequest,\n'
        '    JobApplicationItem,\n'
        '    JobDetail,\n'
        '    JobItem,\n'
        '    JobSkillItem,\n'
        '    UpdateApplicationStatusRequest,\n'
        '    UpdateJobRequest,\n'
        ')\n'
    )
    if old_block in content:
        content = content.replace(old_block, new_block)

    # Add new endpoint
    new_endpoint = (
        '\n'
        '\n'
        '@router.put("/{job_id}/applications/{application_id}/status", summary="更新投递状态")\n'
        'async def update_application_status(\n'
        '    job_id: int,\n'
        '    application_id: int,\n'
        '    req: UpdateApplicationStatusRequest,\n'
        '    current_user: User = Depends(require_role(RoleEnum.COMPANY)),\n'
        '    db: AsyncSession = Depends(get_db),\n'
        ') -> Result:\n'
        '    """企业处理投递：通过/淘汰。"""\n'
        '    try:\n'
        '        company = await company_repository.get_by_user_id(db, current_user.id)\n'
        '        if company is None:\n'
        '            return Result.error(403, "企业不存在")\n'
        '        result = await job_service.update_application_status(\n'
        '            db, company.id, application_id, req.status,\n'
        '        )\n'
        '    except BusinessError as exc:\n'
        '        return Result.error(code=exc.code, message=exc.message, data=exc.data)\n'
        '    return Result.success(data=result, message="投递状态已更新")\n'
    )
    content += new_endpoint
    with open(rp, "w", encoding="utf-8") as f:
        f.write(content)
    print("Added router endpoint")

print("All patches applied!")
