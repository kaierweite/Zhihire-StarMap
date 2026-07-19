<script setup lang="ts">
import { ref, reactive, computed } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { ArrowLeft, Send, Upload, Search, Briefcase, Loader2 } from 'lucide-vue-next'
import {
  createJob, uploadJd, getJdParseResult, batchAddJobSkills,
  type CreateJobForm, type JdParseResult, type BatchAddJobSkillRequest,
} from '@/api/job'
import { searchSkills, type SkillItem } from '@/api/skill'

const router = useRouter()
const loading = ref(false)

const form = reactive<CreateJobForm>({
  title: '',
  city: '',
  education_requirement: '',
  experience_min: null,
  salary_min: null,
  salary_max: null,
  job_type: 'FULL_TIME',
  is_campus: false,
  major: '',
  job_category: '',
  description: '',
  benefits: [],
})

// JD upload
const jdUploading = ref(false)
const parseResult = ref<JdParseResult | null>(null)
const showJdResult = ref(false)

// Skill management
interface JobSkillForm {
  skill_id: number
  name: string
  category: string | null
  required_level: string
  importance: number
}
const jobSkills = ref<JobSkillForm[]>([])
const skillSearchKeyword = ref('')
const skillSearchResults = ref<SkillItem[]>([])
const skillSearching = ref(false)
const showSkillSearch = ref(false)

const eduOptions = ['不限', '高中', '大专', '本科', '硕士', '博士']

const jobCategories = [
  { value: 'TECH', label: '技术/研发' },
  { value: 'PRODUCT', label: '产品/运营' },
  { value: 'MARKET', label: '市场/销售' },
  { value: 'DESIGN', label: '设计/创意' },
  { value: 'ADMIN', label: '行政/人事' },
  { value: 'FINANCE', label: '财务/法务' },
  { value: 'MANUFACTURE', label: '生产/制造' },
  { value: 'EDUCATION', label: '教育/培训' },
  { value: 'MEDICAL', label: '医疗/健康' },
  { value: 'OTHER', label: '其他' },
]

const majorGroups = [
  { category: '工学', majors: ['计算机科学与技术', '软件工程', '电子信息工程', '通信工程', '自动化', '机械工程', '土木工程', '材料科学与工程', '电气工程', '建筑学', '环境工程', '生物工程', '化学工程与工艺', '交通运输'] },
  { category: '理学', majors: ['数学与应用数学', '信息与计算科学', '物理学', '化学', '生物科学', '统计学', '地理科学', '应用物理学'] },
  { category: '管理学', majors: ['工商管理', '市场营销', '会计学', '财务管理', '人力资源管理', '信息管理与信息系统', '电子商务', '物流管理'] },
  { category: '经济学', majors: ['经济学', '金融学', '国际经济与贸易', '财政学', '保险学', '金融工程', '投资学'] },
  { category: '文学', majors: ['汉语言文学', '英语', '日语', '新闻学', '广告学', '传播学', '翻译'] },
  { category: '法学', majors: ['法学', '知识产权', '社会工作'] },
  { category: '医学', majors: ['临床医学', '护理学', '药学', '中医学', '口腔医学', '医学影像技术', '预防医学'] },
  { category: '艺术学', majors: ['视觉传达设计', '环境设计', '产品设计', '动画', '数字媒体艺术', '音乐表演'] },
  { category: '教育学', majors: ['教育学', '学前教育', '小学教育', '体育教育', '教育技术学'] },
  { category: '其他', majors: ['不限专业'] },
]

const majorOptions = computed(() => {
  const options: { label: string; group: string }[] = []
  for (const group of majorGroups) {
    for (const major of group.majors) {
      options.push({ label: major, group: group.category })
    }
  }
  return options
})

const benefitsOptions = ['五险一金', '年终奖', '带薪年假', '餐补', '双休', '弹性工作', '定期体检', '员工旅游', '节日福利', '股票期权']

function goBack() {
  router.push('/company/jobs')
}

// JD Upload
function handleFileChange(uploadFile: any) {
  if (uploadFile && uploadFile.raw) {
    handleJdUpload(uploadFile.raw)
  }
}
 async function handleJdUpload(file: File) {
   jdUploading.value = true
   try {
     const res = await uploadJd(file)
     if (res.data.code === 200 && res.data.data) {
       const taskId = res.data.data.task_id
       const interval = setInterval(async () => {
         try {
           const resultRes = await getJdParseResult(taskId)
           if (resultRes.data.code === 200 && resultRes.data.data) {
             const data = resultRes.data.data
             if (data.status === 'SUCCESS') {
               clearInterval(interval)
               applyJdResult(data)
             } else if (data.status === 'FAILED') {
               clearInterval(interval)
               ElMessage.error('JD 解析失败，请手动填写')
             }
           }
         } catch {
           clearInterval(interval)
         }
       }, 2000)
     } else {
       ElMessage.error(res.data.message || '上传失败')
     }
   } catch (e: any) {
     ElMessage.error(e?.response?.data?.message || e.message || '网络异常')
   } finally {
     jdUploading.value = false
   }
 }

function applyJdResult(data: JdParseResult) {
  if (data.title) form.title = data.title
  if (data.city) form.city = data.city
  if (data.education_requirement) form.education_requirement = data.education_requirement
  if (data.experience_min != null) form.experience_min = data.experience_min
  if (data.salary_min != null) form.salary_min = data.salary_min
  if (data.salary_max != null) form.salary_max = data.salary_max
  if (data.job_type) form.job_type = data.job_type as 'FULL_TIME' | 'PART_TIME' | 'INTERN'
  if (data.description) form.description = data.description
  if (data.benefits) form.benefits = data.benefits

  if (data.skills && data.skills.length > 0) {
    for (const s of data.skills) {
      if (!jobSkills.value.some(js => js.skill_id === s.skill_id)) {
        jobSkills.value.push({
          skill_id: s.skill_id,
          name: s.name,
          category: s.category || null,
          required_level: 'MUST',
          importance: 3,
        })
      }
    }
  }

  parseResult.value = data
  showJdResult.value = true
  ElMessage.success('JD 解析完成，已自动填充岗位信息')
}

// Skill search
async function handleSkillSearch() {
  if (!skillSearchKeyword.value.trim()) return
  skillSearching.value = true
  try {
    const res = await searchSkills(skillSearchKeyword.value.trim())
    if (res.data.code === 200) {
      skillSearchResults.value = res.data.data || []
    }
  } catch {
    skillSearchResults.value = []
  } finally {
    skillSearching.value = false
  }
}

function addSkill(skill: SkillItem) {
  if (jobSkills.value.some(js => js.skill_id === skill.id)) {
    ElMessage.warning('该技能已添加')
    return
  }
  jobSkills.value.push({
    skill_id: skill.id,
    name: skill.name,
    category: skill.category,
    required_level: 'NICE',
    importance: 3,
  })
  skillSearchKeyword.value = ''
  skillSearchResults.value = []
}

function removeSkill(index: number) {
  jobSkills.value.splice(index, 1)
}

function handleLevelChange(index: number, level: string) {
  jobSkills.value[index].required_level = level
}

function handleImportanceChange(index: number, importance: number) {
  jobSkills.value[index].importance = importance
}

// Submit
async function handleSubmit() {
  if (!form.title.trim()) {
    ElMessage.warning('请输入岗位名称')
    return
  }
  if (!form.city?.trim()) form.city = null
  if (!form.education_requirement?.trim()) form.education_requirement = null
  if (!form.description?.trim()) form.description = null
  if (form.benefits && form.benefits.length === 0) form.benefits = null

  loading.value = true
  try {
    const res = await createJob({
      ...form,
      title: form.title.trim(),
    })
    if (res.data.code === 200 && res.data.data) {
      const jobId = res.data.data.id
      if (jobSkills.value.length > 0) {
        const skillRequests: BatchAddJobSkillRequest[] = jobSkills.value.map(s => ({
          skill_id: s.skill_id,
          importance: s.importance,
          required_level: s.required_level,
        }))
        await batchAddJobSkills(jobId, skillRequests)
      }
      ElMessage.success(`岗位「${form.title}」发布成功`)
      router.push('/company/jobs')
    } else {
      ElMessage.error(res.data.message || '发布失败')
    }
  } catch {
    ElMessage.error('网络异常，请稍后重试')
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="page">
    <div class="page-header fade-up">
      <button class="back-btn" @click="goBack"><ArrowLeft :size="18" /></button>
      <div class="header-text">
        <h1>发布岗位</h1>
        <span class="subtitle">填写岗位信息，发布招聘需求</span>
      </div>
    </div>

    <!-- JD Upload Card -->
    <div class="jd-upload-card fade-up d1">
      <div class="jd-upload-header">
        <Upload :size="20" />
        <span>上传职位描述（JD）文件</span>
        <span class="jd-hint">支持 PDF / Word 格式，系统自动提取岗位信息与技能要求</span>
      </div>
      <div class="jd-upload-area">
        <el-upload
          :show-file-list="false"
          :auto-upload="false"
          :on-change="handleFileChange"
          accept=".pdf,.doc,.docx"
        >
          <el-button type="primary" :loading="jdUploading" :disabled="jdUploading">
            <Upload :size="16" style="margin-right:4px" />
            {{ jdUploading ? '解析中...' : '上传 JD 文件' }}
          </el-button>
        </el-upload>
      </div>
      <div v-if="showJdResult && parseResult" class="jd-result">
        <div class="jd-result-header">
          <Briefcase :size="16" />
          <span>已解析：{{ parseResult.title || '未识别' }}</span>
        </div>
        <div v-if="parseResult.skills && parseResult.skills.length > 0" class="jd-skills">
          <span class="jd-skills-label">识别到 {{ parseResult.skills.length }} 项技能：</span>
          <div class="skill-tags">
            <span v-for="s in parseResult.skills" :key="s.skill_id" class="skill-tag">{{ s.name }}</span>
          </div>
        </div>
        <div v-else class="no-skills"><span>未提取到技能</span></div>
      </div>
    </div>

    <!-- Form Card -->
    <div class="form-card fade-up d1">
      <el-form :model="form" label-width="120px" size="large">
        <el-form-item label="岗位名称" required>
          <el-input v-model="form.title" placeholder="例如：高级前端工程师" maxlength="100" show-word-limit />
        </el-form-item>

        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="工作城市">
              <el-input v-model="form.city" placeholder="例如：北京、上海" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="学历要求">
              <el-select v-model="form.education_requirement" placeholder="不限" clearable style="width:100%">
                <el-option v-for="e in eduOptions" :key="e" :label="e" :value="e" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="经验要求（年）">
              <el-input-number v-model="form.experience_min" :min="0" :max="20" style="width:100%" placeholder="最低年限" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="工作类型">
              <el-select v-model="form.job_type" style="width:100%">
                <el-option label="全职" value="FULL_TIME" />
                <el-option label="兼职" value="PART_TIME" />
                <el-option label="实习" value="INTERN" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>

        <el-form-item label="薪资范围（元/月）">
          <el-row :gutter="20">
            <el-col :span="12">
              <el-input-number v-model="form.salary_min" :min="0" :max="200000" style="width:100%" placeholder="最低薪资" />
            </el-col>
            <el-col :span="12">
              <el-input-number v-model="form.salary_max" :min="0" :max="200000" style="width:100%" placeholder="最高薪资" />
            </el-col>
          </el-row>
        </el-form-item>

        <el-form-item label="校招岗位">
          <el-switch v-model="form.is_campus" active-text="是校招岗位" inactive-text="社会招聘" />
        </el-form-item>

        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="岗位分类">
              <el-select v-model="form.job_category" placeholder="选择岗位分类" clearable filterable style="width:100%">
                <el-option v-for="c in jobCategories" :key="c.value" :label="c.label" :value="c.value" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="需求专业">
              <el-select v-model="form.major" placeholder="选择或搜索专业" clearable filterable style="width:100%">
                <el-option v-for="m in majorOptions" :key="m.label" :label="m.label" :value="m.label" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>

        <el-form-item label="职位描述">
          <el-input v-model="form.description" type="textarea" :rows="6" placeholder="请描述岗位职责、任职要求、团队介绍等..." maxlength="5000" show-word-limit />
        </el-form-item>

        <el-form-item label="福利标签">
          <el-select v-model="form.benefits" multiple filterable allow-create default-first-option placeholder="输入福利后回车添加" style="width:100%">
            <el-option v-for="b in benefitsOptions" :key="b" :label="b" :value="b" />
          </el-select>
          <div class="form-hint">可从下拉选择常见福利，或输入自定义福利后回车</div>
        </el-form-item>

        <!-- Skill Requirements -->
        <el-form-item label="技能要求">
          <div class="skill-section">
            <div class="skill-search-bar">
              <el-input v-model="skillSearchKeyword" placeholder="搜索技能名称" style="width:300px" @keyup.enter="handleSkillSearch">
                <template #prefix><Search :size="16" /></template>
              </el-input>
              <el-button type="primary" @click="handleSkillSearch" :loading="skillSearching">搜索</el-button>
            </div>

            <div v-if="skillSearchResults.length > 0" class="skill-search-results">
              <div v-for="skill in skillSearchResults" :key="skill.id" class="search-result-item">
                <div class="skill-info">
                  <span class="skill-name">{{ skill.name }}</span>
                  <span v-if="skill.category" class="skill-category">{{ skill.category }}</span>
                </div>
                <el-button size="small" type="primary" plain @click="addSkill(skill)">添加</el-button>
              </div>
            </div>

            <div v-if="skillSearchKeyword && !skillSearching && skillSearchResults.length === 0" class="no-results">
              <span>未找到匹配的技能，请尝试其他关键词</span>
            </div>

            <div v-if="jobSkills.length > 0" class="skills-list">
              <div v-for="(skill, index) in jobSkills" :key="skill.skill_id" class="skill-item">
                <div class="skill-info">
                  <span class="skill-name-tag">{{ skill.name }}</span>
                  <span v-if="skill.category" class="skill-category-tag">{{ skill.category }}</span>
                </div>
                <div class="skill-controls">
                  <el-select :value="skill.required_level" size="small" style="width:110px" @change="(v: string) => handleLevelChange(index, v)">
                    <el-option label="MUST" value="MUST" />
                    <el-option label="NICE" value="NICE" />
                    <el-option label="BONUS" value="BONUS" />
                  </el-select>
                  <el-input-number :value="skill.importance" :min="1" :max="5" size="small" style="width:100px" @change="(v: number) => handleImportanceChange(index, v)" />
                  <el-button size="small" type="danger" plain @click="removeSkill(index)">移除</el-button>
                </div>
              </div>
            </div>

            <div v-else class="no-skills-hint">
              <span>暂无技能要求，搜索并添加技能</span>
            </div>
          </div>
        </el-form-item>

        <el-form-item>
          <div class="form-actions">
            <el-button size="large" @click="goBack">取消</el-button>
            <el-button type="primary" size="large" :loading="loading" @click="handleSubmit">
              <Send :size="16" style="margin-right:4px" />
              {{ loading ? '发布中...' : '发布岗位' }}
            </el-button>
          </div>
        </el-form-item>
      </el-form>
    </div>

    <!-- Tips Card -->
    <div class="tips-card fade-up d2">
      <h3>发布提示</h3>
      <ul>
        <li>岗位名称建议包含职位类型，如"高级前端工程师"</li>
        <li>详细的职位描述能吸引更合适的候选人</li>
        <li>薪资范围请填写月薪，单位为元</li>
        <li>发布后可在岗位管理中编辑或添加技能要求</li>
        <li>企业信息需审核通过后岗位才会对外展示</li>
      </ul>
    </div>
  </div>
</template>

<style scoped lang="scss">
.page { padding: 24px 16px; max-width: 960px; margin: 0 auto; }

@keyframes fadeUp { from { opacity: 0; transform: translateY(20px); } to { opacity: 1; transform: translateY(0); } }
.fade-up { opacity: 0; animation: fadeUp 0.5s cubic-bezier(0.22,1,0.36,1) forwards; }
.d1 { animation-delay: 0.08s; } .d2 { animation-delay: 0.15s; }

.page-header {
  display: flex; align-items: center; gap: 14px; margin-bottom: 24px;
  .back-btn {
    width: 38px; height: 38px; display: flex; align-items: center; justify-content: center;
    border-radius: 10px; border: 1px solid #bfc9c3; background: #fff; color: #404944; cursor: pointer;
    transition: all 0.2s;
    &:hover { border-color: #003527; color: #003527; }
  }
  .header-text {
    h1 { font-size: 28px; font-weight: 700; color: #121c28; margin: 0 0 2px 0; }
    .subtitle { font-size: 14px; color: #404944; }
  }
}

.jd-upload-card {
  background: #fff; border-radius: 12px; padding: 20px; border: 1px solid #bfc9c3; margin-bottom: 20px;
  .jd-upload-header { display: flex; align-items: center; gap: 8px; margin-bottom: 16px; font-size: 15px; font-weight: 600; color: #121c28; svg { color: #003527; } }
  .jd-hint { font-size: 12px; font-weight: 400; color: #404944; }
  .jd-upload-area { margin-bottom: 12px; }
  .jd-result {
    padding: 12px; border-radius: 8px; background: #f0f9ff; border: 1px solid #bae6fd;
    .jd-result-header { display: flex; align-items: center; gap: 6px; font-size: 14px; font-weight: 600; color: #1e3a8a; margin-bottom: 8px; }
    .jd-skills { margin-top: 8px; }
    .jd-skills-label { font-size: 13px; color: #404944; display: block; margin-bottom: 6px; }
    .no-skills { font-size: 13px; color: #404944; margin-top: 4px; }
  }
}

.form-card {
  background: #fff; border-radius: 12px; padding: 28px 32px; border: 1px solid #bfc9c3; margin-bottom: 20px;
}

.form-hint { font-size: 12px; color: #404944; margin-top: 4px; }

.skill-section {
  width: 100%;
  .skill-search-bar { display: flex; gap: 8px; margin-bottom: 12px; }
  .skill-search-results {
    border: 1px solid #bfc9c3; border-radius: 8px; padding: 8px; margin-bottom: 12px; max-height: 200px; overflow-y: auto;
    .search-result-item { display: flex; align-items: center; justify-content: space-between; padding: 8px 12px; border-radius: 6px; transition: background 0.15s; &:hover { background: #f8f9ff; } }
    .skill-info { display: flex; align-items: center; gap: 8px; }
    .skill-name { font-size: 14px; font-weight: 500; color: #121c28; }
    .skill-category { font-size: 11px; color: #404944; background: #f3f4f5; padding: 1px 6px; border-radius: 3px; }
  }
  .no-results { padding: 12px 0; color: #404944; font-size: 13px; margin-bottom: 8px; }
  .skills-list { display: flex; flex-direction: column; gap: 8px; margin-top: 8px; }
  .skill-item {
    display: flex; align-items: center; justify-content: space-between; gap: 12px;
    padding: 10px 14px; border-radius: 8px; background: #f9fafb; border: 1px solid #eef0f2;
    .skill-info { display: flex; align-items: center; gap: 8px; }
    .skill-name-tag { font-size: 14px; font-weight: 600; color: #121c28; }
    .skill-category-tag { font-size: 11px; color: #404944; background: #eef0f2; padding: 1px 6px; border-radius: 3px; }
    .skill-controls { display: flex; align-items: center; gap: 8px; }
  }
  .no-skills-hint { font-size: 13px; color: #bfc9c3; }
}

.form-actions { display: flex; gap: 12px; justify-content: center; padding-top: 8px; }

.tips-card {
  background: #fff; border-radius: 12px; padding: 20px 24px; border: 1px solid #bfc9c3;
  h3 { font-size: 16px; font-weight: 600; color: #121c28; margin: 0 0 12px 0; }
  ul { margin: 0; padding: 0; list-style: none; }
  li {
    position: relative; padding-left: 16px; font-size: 13px; color: #404944; line-height: 1.8;
    &::before { content: ''; position: absolute; left: 0; top: 10px; width: 6px; height: 6px; border-radius: 50%; background: #003527; }
  }
}

@media (max-width: 768px) {
  .form-card { padding: 20px 16px; }
  .el-row .el-col { width: 100% !important; }
}
</style>
