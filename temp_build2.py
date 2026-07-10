import os, py_compile

# 1. Update job service — add company fields to search_jobs results
fp = r'C:\Users\Administrator\Desktop\Zhihire-StarMap\backend\app\services\job_service.py'
with open(fp, 'r', encoding='utf-8') as f:
    c = f.read()

# In search_jobs, the JobItem creation needs company_type/industry/scale
old = "        items.append(JobItem(\n            id=r.id, company_id=r.company_id,\n            company_name=comp.company_name if comp else None,\n            title=r.title, city=r.city,\n            education_requirement=r.education_requirement,\n            experience_min=r.experience_min,\n            salary_min=float(r.salary_min) if r.salary_min is not None else None,\n            salary_max=float(r.salary_max) if r.salary_max is not None else None,\n            job_type=r.job_type, status=r.status, views=r.views,\n            benefits=r.benefits, occupation_role_id=r.occupation_role_id,\n            created_at=r.created_at, updated_at=r.updated_at,\n        ))"
new = "        items.append(JobItem(\n            id=r.id, company_id=r.company_id,\n            company_name=comp.company_name if comp else None,\n            industry=comp.industry if comp else None,\n            scale=comp.scale if comp else None,\n            company_type=comp.company_type if comp else None,\n            title=r.title, city=r.city,\n            education_requirement=r.education_requirement,\n            experience_min=r.experience_min,\n            salary_min=float(r.salary_min) if r.salary_min is not None else None,\n            salary_max=float(r.salary_max) if r.salary_max is not None else None,\n            job_type=r.job_type, status=r.status, views=r.views,\n            is_campus=r.is_campus,\n            benefits=r.benefits, occupation_role_id=r.occupation_role_id,\n            created_at=r.created_at, updated_at=r.updated_at,\n        ))"
c = c.replace(old, new)

# Also update get_job_detail to include is_campus and company fields in JobDetail
old = "    return JobDetail(\n        id=job.id, company_id=job.company_id,\n        company_name=company.company_name,\n        occupation_role_id=job.occupation_role_id,\n        occupation_role_name=role_name,\n        title=job.title, city=job.city,\n        education_requirement=job.education_requirement,\n        experience_min=job.experience_min,\n        salary_min=float(job.salary_min) if job.salary_min is not None else None,\n        salary_max=float(job.salary_max) if job.salary_max is not None else None,\n        job_type=job.job_type, description=job.description,\n        requirements=job.requirements, source=job.source,\n        status=job.status, views=job.views + 1 if increment_view else job.views,\n        benefits=job.benefits, skills=skills,\n        created_at=job.created_at, updated_at=job.updated_at,\n    )"
new = "    return JobDetail(\n        id=job.id, company_id=job.company_id,\n        company_name=company.company_name,\n        occupation_role_id=job.occupation_role_id,\n        occupation_role_name=role_name,\n        title=job.title, city=job.city,\n        education_requirement=job.education_requirement,\n        experience_min=job.experience_min,\n        salary_min=float(job.salary_min) if job.salary_min is not None else None,\n        salary_max=float(job.salary_max) if job.salary_max is not None else None,\n        job_type=job.job_type, description=job.description,\n        requirements=job.requirements, source=job.source,\n        status=job.status, views=job.views + 1 if increment_view else job.views,\n        is_campus=job.is_campus,\n        benefits=job.benefits, skills=skills,\n        created_at=job.created_at, updated_at=job.updated_at,\n    )"
c = c.replace(old, new)

# Also update create_job to pass is_campus
old = "    job = Job(\n        company_id=company.id,\n        occupation_role_id=req.occupation_role_id,\n        title=req.title,\n        city=req.city,\n        education_requirement=req.education_requirement,\n        experience_min=req.experience_min,\n        salary_min=req.salary_min,\n        salary_max=req.salary_max,\n        job_type=req.job_type,\n        description=req.description,\n        benefits=req.benefits,\n    )"
new = "    job = Job(\n        company_id=company.id,\n        occupation_role_id=req.occupation_role_id,\n        title=req.title,\n        city=req.city,\n        education_requirement=req.education_requirement,\n        experience_min=req.experience_min,\n        salary_min=req.salary_min,\n        salary_max=req.salary_max,\n        job_type=req.job_type,\n        description=req.description,\n        is_campus=req.is_campus,\n        benefits=req.benefits,\n    )"
c = c.replace(old, new)

with open(fp, 'w', encoding='utf-8') as f:
    f.write(c)

# Verify
import py_compile
try:
    py_compile.compile(fp, doraise=True)
    sz = os.path.getsize(fp)
    print(f'OK: job_service.py ({sz} bytes)')
except py_compile.PyCompileError as e:
    print(f'FAIL: {e}')