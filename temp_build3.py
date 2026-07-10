import os
import py_compile as pc

# === 1. Update api/job.ts — add new fields to JobItem and JobDetail ===
fp = r'C:\Users\Administrator\Desktop\Zhihire-StarMap\frontend\src\api\job.ts'
with open(fp, 'r', encoding='utf-8') as f:
    c = f.read()

# Add fields to JobItem
c = c.replace('export interface JobItem {\n  id: number\n  company_id: number\n  company_name: string | null',
              'export interface JobItem {\n  id: number\n  company_id: number\n  company_name: string | null\n  industry: string | null\n  scale: string | null\n  company_type: string | null')
c = c.replace('  salary_min: number | null\n  salary_max: number | null\n  job_type: JobType\n  status: JobStatus\n  views: number\n  benefits: string[] | null\n  occupation_role_id: number | null\n  created_at: string\n  updated_at: string',
              '  salary_min: number | null\n  salary_max: number | null\n  job_type: JobType\n  status: JobStatus\n  views: number\n  is_campus: boolean\n  benefits: string[] | null\n  occupation_role_id: number | null\n  created_at: string\n  updated_at: string')

# Add is_campus to JobDetail
c = c.replace('  salary_min: number | null\n  salary_max: number | null\n  job_type: JobType\n  description: string | null',
              '  salary_min: number | null\n  salary_max: number | null\n  job_type: JobType\n  description: string | null\n  is_campus: boolean')

# Add is_campus to CreateJobForm
c = c.replace('export interface CreateJobForm {\n  title: string\n  city?: string | null\n  education_requirement?: string | null\n  experience_min?: number | null\n  salary_min?: number | null\n  salary_max?: number | null\n  job_type: JobType\n  description?: string | null\n  occupation_role_id?: number | null\n  benefits?: string[] | null',
              'export interface CreateJobForm {\n  title: string\n  city?: string | null\n  education_requirement?: string | null\n  experience_min?: number | null\n  salary_min?: number | null\n  salary_max?: number | null\n  job_type: JobType\n  description?: string | null\n  occupation_role_id?: number | null\n  is_campus?: boolean\n  benefits?: string[] | null')

with open(fp, 'w', encoding='utf-8') as f:
    f.write(c)
print('1. api/job.ts updated')

# === 2. Update JobPublish.vue — add is_campus, salary unit to yuan ===
fp = r'C:\Users\Administrator\Desktop\Zhihire-StarMap\frontend\src\views\company\JobPublish.vue'
with open(fp, 'r', encoding='utf-8') as f:
    c = f.read()

# Add is_campus to reactive form
c = c.replace("  job_type: 'FULL_TIME',", "  job_type: 'FULL_TIME',\n  is_campus: false,")

# Add is_campus field after job_type select (in the form template)
old = '''          <el-form-item label="薪资范围（K/月）">'''
new = '''          <el-form-item label="校招岗位">
            <el-switch v-model="form.is_campus" active-text="是" inactive-text="否" />
          </el-form-item>

          <el-form-item label="薪资范围（元/月）">'''
c = c.replace(old, new)

# Change salary input max from 200 to 200000
c = c.replace(':min="0" :max="200"', ':min="0" :max="200000"')

# Add is_campus to the submit data
c = c.replace('''      title: form.title.trim(),
      city: form.city,
      education_requirement: form.education_requirement,
      experience_min: form.experience_min,
      salary_min: form.salary_min,
      salary_max: form.salary_max,
      job_type: form.job_type,
      description: form.description,
      benefits: form.benefits,''', '''      title: form.title.trim(),
      city: form.city,
      education_requirement: form.education_requirement,
      experience_min: form.experience_min,
      salary_min: form.salary_min,
      salary_max: form.salary_max,
      job_type: form.job_type,
      description: form.description,
      is_campus: form.is_campus,
      benefits: form.benefits,''')

with open(fp, 'w', encoding='utf-8') as f:
    f.write(c)
print('2. JobPublish.vue updated')

# === 3. Delete/archive old cache files ===
cache = r'C:\Users\Administrator\Desktop\Zhihire-StarMap\frontend\src\views\user\JobRecommend_script.vue'
if os.path.exists(cache):
    os.remove(cache)
print('3. Cleaned up temp files')

# Verification
for p in [
    r'C:\Users\Administrator\Desktop\Zhihire-StarMap\frontend\src\api\job.ts',
    r'C:\Users\Administrator\Desktop\Zhihire-StarMap\frontend\src\views\company\JobPublish.vue',
]:
    sz = os.path.getsize(p)
    print(f'  OK: {os.path.basename(p)} ({sz} bytes)')