import os

p = r"C:\Users\Administrator\Desktop\Zhihire-StarMap\backend\app\api\v1\job.py"
with open(p, "r", encoding="utf-8") as f:
    c = f.read()

# 1. Update docstring
c = c.replace("8 个端点", "9 个端点")
c = c.replace(
    "- DELETE /api/job/{job_id}/skills/{skill_id} - 移除技能要求（企业）",
    "- DELETE /api/job/{job_id}/skills/{skill_id} - 移除技能要求（企业）\n- GET /api/job/{job_id}/applications - 投递列表（企业）",
)

# 2. Add import
old_import = "    AddJobSkillRequest,\n    CreateJobRequest,"
new_import = "    AddJobSkillRequest,\n    CreateJobRequest,\n    JobApplicationItem,"
c = c.replace(old_import, new_import)

# 3. Add the route before the apply route
old_route = '@router.post("/{job_id}/apply", summary="投递简历")'
new_route_block = '''@router.get("/{job_id}/applications", summary="投递列表（企业）")
async def list_job_applications(
    job_id: int,
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    current_user: User = Depends(require_role(RoleEnum.COMPANY)),
    db: AsyncSession = Depends(get_db),
) -> Result:
    try:
        company = await company_repository.get_by_user_id(db, current_user.id)
        if company is None:
            return Result.error(403, "企业不存在")
        items, total = await job_service.list_job_applications(
            db, company.id, job_id, page=page, size=size,
        )
    except BusinessError as exc:
        return Result.error(code=exc.code, message=exc.message, data=exc.data)
    return Result.success(
        data=PageResult(
            records=[i.model_dump() for i in items],
            total=total,
            page=page,
            size=size,
        ),
    )


''' + old_route

c = c.replace(old_route, new_route_block)

with open(p, "w", encoding="utf-8") as f:
    f.write(c)

print("Done: route added")
