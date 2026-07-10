import os, py_compile

# === 1. Job entity — add major and job_category ===
fp = r'C:\Users\Administrator\Desktop\Zhihire-StarMap\backend\app\models\entities\job.py'
with open(fp, 'r', encoding='utf-8') as f:
    c = f.read()
# Add fields after is_campus
old = '    is_campus: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)\n    benefits: Mapped[list | None]'
new = '    is_campus: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)\n    # 专业（用于按专业筛选）\n    major: Mapped[str | None] = mapped_column(String(200), nullable=True)\n    # 岗位分类（用于按职类筛选）\n    job_category: Mapped[str | None] = mapped_column(String(100), nullable=True)\n    benefits: Mapped[list | None]'
c = c.replace(old, new)
with open(fp, 'w', encoding='utf-8') as f:
    f.write(c)
print('1. Job entity: major, job_category added')

# === 2. Job schemas ===
fp = r'C:\Users\Administrator\Desktop\Zhihire-StarMap\backend\app\models\schemas\job.py'
with open(fp, 'r', encoding='utf-8') as f:
    c = f.read()

# JobSearchParams — add major and job_category
old = """class JobSearchParams(BaseModel):
    \"\"\"岗位搜索参数。\"\"\"
    keyword: str | None = Field(None, max_length=200)
    city: str | None = Field(None, max_length=100)
    education_requirement: str | None = Field(None, max_length=20)
    experience_min: int | None = Field(None, ge=0)
    salary_min: float | None = None
    salary_max: float | None = None
    job_type: str | None = Field(None, max_length=20)
    company_id: int | None = None
    status: str | None = Field(None, max_length=20)
    page: int = Field(default=1, ge=1)
    size: int = Field(default=20, ge=1, le=100)"""
new = """class JobSearchParams(BaseModel):
    \"\"\"岗位搜索参数。\"\"\"
    keyword: str | None = Field(None, max_length=200)
    city: str | None = Field(None, max_length=100)
    education_requirement: str | None = Field(None, max_length=20)
    experience_min: int | None = Field(None, ge=0)
    salary_min: float | None = None
    salary_max: float | None = None
    job_type: str | None = Field(None, max_length=20)
    major: str | None = Field(None, max_length=200)
    job_category: str | None = Field(None, max_length=100)
    company_id: int | None = None
    status: str | None = Field(None, max_length=20)
    page: int = Field(default=1, ge=1)
    size: int = Field(default=20, ge=1, le=100)"""
c = c.replace(old, new)

# JobItem — add major and job_category
old = '    is_campus: bool = False\n    benefits: list[str] | None = None\n    occupation_role_id: int | None = None\n    created_at: datetime\n    updated_at: datetime'
new = '    is_campus: bool = False\n    major: str | None = None\n    job_category: str | None = None\n    benefits: list[str] | None = None\n    occupation_role_id: int | None = None\n    created_at: datetime\n    updated_at: datetime'
c = c.replace(old, new)

# CreateJobRequest — add major and job_category
old = '    is_campus: bool = False\n    benefits: list[str] | None = None'
new = '    is_campus: bool = False\n    major: str | None = None\n    job_category: str | None = None\n    benefits: list[str] | None = None'
c = c.replace(old, new)

# UpdateJobRequest — add major and job_category
old = "    is_campus: bool | None = None\n    benefits: list[str] | None = None"
new = "    is_campus: bool | None = None\n    major: str | None = None\n    job_category: str | None = None\n    benefits: list[str] | None = None"
c = c.replace(old, new)

with open(fp, 'w', encoding='utf-8') as f:
    f.write(c)
print('2. Job schemas: major, job_category added to all models')

# === 3. API route — add query params for major and job_category ===
fp = r'C:\Users\Administrator\Desktop\Zhihire-StarMap\backend\app\api\v1\job.py'
with open(fp, 'r', encoding='utf-8') as f:
    c = f.read()
old = '    job_type: str | None = Query(None, max_length=20),\n    company_id: int | None = Query(None),'
new = '    job_type: str | None = Query(None, max_length=20),\n    major: str | None = Query(None, max_length=200),\n    job_category: str | None = Query(None, max_length=100),\n    company_id: int | None = Query(None),'
c = c.replace(old, new)
# Also add them to the service call
old = '            job_type=job_type,'
new = '            job_type=job_type,\n            major=major,\n            job_category=job_category,'
c = c.replace(old, new)
with open(fp, 'w', encoding='utf-8') as f:
    f.write(c)
print('3. API route: major, job_category query params added')

# === 4. Job service — add params ===
fp = r'C:\Users\Administrator\Desktop\Zhihire-StarMap\backend\app\services\job_service.py'
with open(fp, 'r', encoding='utf-8') as f:
    c = f.read()
# Update search_jobs signature
old = '    job_type: str | None = None,\n    company_id: int | None = None,'
new = '    job_type: str | None = None,\n    major: str | None = None,\n    job_category: str | None = None,\n    company_id: int | None = None,'
c = c.replace(old, new)
# Update the call to job_repository.search_jobs
old = '        job_type=job_type,\n        company_id=company_id,'
new = '        job_type=job_type,\n        major=major,\n        job_category=job_category,\n        company_id=company_id,'
c = c.replace(old, new)
# Update JobItem creation to include major and job_category
old = '    is_campus=r.is_campus,\n            benefits=r.benefits,'
new = '    is_campus=r.is_campus,\n            major=r.major,\n            job_category=r.job_category,\n            benefits=r.benefits,'
c = c.replace(old, new)
# Update create_job to pass major and job_category
old = '    is_campus=req.is_campus,\n        benefits=req.benefits,'
new = '    is_campus=req.is_campus,\n        major=req.major,\n        job_category=req.job_category,\n        benefits=req.benefits,'
c = c.replace(old, new)
with open(fp, 'w', encoding='utf-8') as f:
    f.write(c)
print('4. Job service: major, job_category added')

# === 5. Job repository — add filters ===
fp = r'C:\Users\Administrator\Desktop\Zhihire-StarMap\backend\app\repositories\job_repository.py'
with open(fp, 'r', encoding='utf-8') as f:
    c = f.read()
# Update search_jobs signature
old = '    job_type: str | None = None,\n    company_id: int | None = None,'
new = '    job_type: str | None = None,\n    major: str | None = None,\n    job_category: str | None = None,\n    company_id: int | None = None,'
c = c.replace(old, new)
# Add filters after job_type filter
old = "    if job_type:\n        base_cond.append(Job.job_type == job_type)\n    if company_id is not None:"
new = "    if job_type:\n        base_cond.append(Job.job_type == job_type)\n    if major:\n        base_cond.append(Job.major == major)\n    if job_category:\n        base_cond.append(Job.job_category == job_category)\n    if company_id is not None:"
c = c.replace(old, new)
with open(fp, 'w', encoding='utf-8') as f:
    f.write(c)
print('5. Job repository: major, job_category filters added')

# === 6. Frontend API types ===
fp = r'C:\Users\Administrator\Desktop\Zhihire-StarMap\frontend\src\api\job.ts'
with open(fp, 'r', encoding='utf-8') as f:
    c = f.read()
# Add major and job_category to JobSearchParams
old = '  job_type?: JobType\n  company_id?: number'
new = '  job_type?: JobType\n  major?: string\n  job_category?: string\n  company_id?: number'
c = c.replace(old, new)
# Add to JobItem
old = '  is_campus: boolean\n  benefits: string[] | null'
new = '  is_campus: boolean\n  major: string | null\n  job_category: string | null\n  benefits: string[] | null'
c = c.replace(old, new)
# Add to CreateJobForm
old = '  is_campus?: boolean\n  benefits?: string[] | null'
new = '  is_campus?: boolean\n  major?: string | null\n  job_category?: string | null\n  benefits?: string[] | null'
c = c.replace(old, new)
with open(fp, 'w', encoding='utf-8') as f:
    f.write(c)
print('6. Frontend API types updated')

# === 7. Migration file for the new columns ===
migration_content = '''"""day12: add major and job_category columns to job table.

Revision ID: c1d2e3f4a5b6
Revises: a0b1c2d3e4f5
Create Date: 2026-07-08 12:30:00.000000+08:00
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = 'c1d2e3f4a5b6'
down_revision: Union[str, None] = 'a0b1c2d3e4f5'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('job', sa.Column('major', sa.String(200), nullable=True))
    op.add_column('job', sa.Column('job_category', sa.String(100), nullable=True))


def downgrade() -> None:
    op.drop_column('job', 'job_category')
    op.drop_column('job', 'major')
'''
mig_fp = r'C:\Users\Administrator\Desktop\Zhihire-StarMap\backend\alembic\versions\2026_07_08_1230-c1d2e3f4a5b6_day12_add_major_and_job_category.py'
with open(mig_fp, 'w', encoding='utf-8') as f:
    f.write(migration_content)
print('7. Migration created: day12_add_major_and_job_category')

# === Verify all files ===
for p in [
    r'C:\Users\Administrator\Desktop\Zhihire-StarMap\backend\app\models\entities\job.py',
    r'C:\Users\Administrator\Desktop\Zhihire-StarMap\backend\app\models\schemas\job.py',
    r'C:\Users\Administrator\Desktop\Zhihire-StarMap\backend\app\api\v1\job.py',
    r'C:\Users\Administrator\Desktop\Zhihire-StarMap\backend\app\services\job_service.py',
    r'C:\Users\Administrator\Desktop\Zhihire-StarMap\backend\app\repositories\job_repository.py',
]:
    try:
        py_compile.compile(p, doraise=True)
        sz = os.path.getsize(p)
        print(f'  OK: {os.path.basename(p)} ({sz} bytes)')
    except py_compile.PyCompileError as e:
        print(f'  FAIL: {os.path.basename(p)}: {e}')
print('All done!')