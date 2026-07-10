import os, py_compile
filepath = r'C:\Users\Administrator\Desktop\Zhihire-StarMap\backend\app\services\job_service.py'
with open(filepath, 'r', encoding='utf-8') as f:
    partial = f.read()
partial = partial.replace('\ufeff', '')
content = partial.strip()

# Append search_jobs function (ASCII only)
content += '\n\nasync def search_jobs(db, keyword=None, city=None, education_requirement=None, experience_min=None, salary_min=None, salary_max=None, job_type=None, company_id=None, status=None, page=1, size=20):\n'
content += '    from app.repositories import job_repository, company_repository\n'
content += '    from app.models.schemas.job import JobItem\n'
content += '    records, total = await job_repository.search_jobs(db, keyword=keyword, city=city, education_requirement=education_requirement, experience_min=experience_min, salary_min=salary_min, salary_max=salary_max, job_type=job_type, company_id=company_id, status=status, page=page, size=size)\n'
content += '    company_ids = list({r.company_id for r in records})\n'
content += '    companies = {}\n'
content += '    for cid in company_ids:\n'
content += '        c = await company_repository.get_by_company_id(db, cid)\n'
content += '        if c: companies[cid] = c\n'
content += '    items = []\n'
content += '    for r in records:\n'
content += '        comp = companies.get(r.company_id)\n'
content += '        items.append(JobItem(id=r.id, company_id=r.company_id, company_name=comp.company_name if comp else None, title=r.title, city=r.city, education_requirement=r.education_requirement, experience_min=r.experience_min, salary_min=float(r.salary_min) if r.salary_min is not None else None, salary_max=float(r.salary_max) if r.salary_max is not None else None, job_type=r.job_type, status=r.status, views=r.views, benefits=r.benefits, occupation_role_id=r.occupation_role_id, created_at=r.created_at, updated_at=r.updated_at))\n'
content += '    return items, total\n'

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(content)
try:
    py_compile.compile(filepath, doraise=True)
    size = os.path.getsize(filepath)
    lines = content.count('\n')
    print(f"OK: {size} bytes, {lines+1} lines")
except py_compile.PyCompileError as e:
    print(f"FAIL: {e}")