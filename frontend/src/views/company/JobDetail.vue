<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { ArrowLeft, Edit, Clock, MapPin, Eye, X, Plus, Search, Send } from 'lucide-vue-next'
import { getJobDetail, listJobSkills, addJobSkill, removeJobSkill, updateJob, deleteJob, getJobApplications, type JobDetail, type JobApplicationItem, type JobSkillItem } from '@/api/job'
import { getCandidates, inviteCandidate, type CandidateRecommendation } from '@/api/match'
import { searchSkills, type SkillItem } from '@/api/skill'

const route = useRoute()
const router = useRouter()
const jobId = Number(route.params.id)

const detail = ref<JobDetail | null>(null)
const loading = ref(true)

// Skills
const skills = ref<JobSkillItem[]>([])
const addSkillKeyword = ref('')
const skillSearchResults = ref<SkillItem[]>([])
const showSkillSearch = ref(false)

// Applications
const applications = ref<JobApplicationItem[]>([])
const appLoading = ref(false)

// Candidates
const candidates = ref<CandidateRecommendation[]>([])
const candLoading = ref(false)
const invitedSet = ref<Set<number>>(new Set())

const statusLabels: Record<string, string> = { OPEN: '招聘中', CLOSED: '已关闭', DRAFT: '草稿' }
const statusType: Record<string, string> = { OPEN: 'success', CLOSED: 'info', DRAFT: 'warning' }
const jobTypeLabels: Record<string, string> = { FULL_TIME: '全职', PART_TIME: '兼职', INTERN: '实习' }
const appStatusLabels: Record<string, string> = { APPLIED: '已投递', REVIEWING: '筛选中', ACCEPTED: '已通过', REJECTED: '未通过' }
const appStatusType: Record<string, string> = { APPLIED: 'primary', REVIEWING: 'warning', ACCEPTED: 'success', REJECTED: 'danger' }

async function loadData() {
  loading.value = true
  try {
    const res = await getJobDetail(jobId)
    if (res.data.code === 200 && res.data.data) {
      detail.value = res.data.data
      skills.value = res.data.data.skills || []
    } else {
      ElMessage.error(res.data.message || '加载岗位详情失败')
    }
  } catch {
    ElMessage.error('网络异常')
  } finally {
    loading.value = false
  }
}

// Skills management
async function onAddSkill(skill: SkillItem) {
  if (skills.value.some(s => s.skill_id === skill.id)) {
    ElMessage.warning('该技能已存在')
    return
  }
  try {
    const res = await addJobSkill(jobId, { skill_id: skill.id, importance: 3, required_level: 'NICE' })
    if (res.data.code === 200) {
      skills.value.push({
        id: res.data.data.id,
        job_id: jobId,
        skill_id: skill.id,
        skill_name: skill.name,
        skill_category: skill.category,
        importance: 3,
        required_level: 'NICE',
      })
      addSkillKeyword.value = ''
      skillSearchResults.value = []
      ElMessage.success(`已添加技能「${skill.name}」`)
    }
  } catch {
    ElMessage.error('添加失败')
  }
}

async function onRemoveSkill(skill: JobSkillItem) {
  try {
    const res = await removeJobSkill(jobId, skill.skill_id)
    if (res.data.code === 200) {
      skills.value = skills.value.filter(s => s.id !== skill.id)
      ElMessage.success(`已移除「${skill.skill_name || '技能'}」`)
    }
  } catch {
    ElMessage.error('移除失败')
  }
}

async function onSearchSkill() {
  if (!addSkillKeyword.value.trim()) return
  try {
    const res = await searchSkills(addSkillKeyword.value, 20)
    if (res.data.code === 200) skillSearchResults.value = res.data.data || []
  } catch {
    skillSearchResults.value = []
  }
}

// Toggle status
async function toggleStatus() {
  if (!detail.value) return
  const newStatus = detail.value.status === 'OPEN' ? 'CLOSED' : 'OPEN'
  try {
    const res = await updateJob(jobId, { status: newStatus })
    if (res.data.code === 200) {
      detail.value.status = newStatus
      ElMessage.success(newStatus === 'OPEN' ? '岗位已开启' : '岗位已关闭')
    }
  } catch {
    ElMessage.error('操作失败')
  }
}

async function handleDelete() {
  try {
    await ElMessageBox.confirm('确定删除此岗位？删除后不可恢复。', '确认', { type: 'warning' })
    const res = await deleteJob(jobId)
    if (res.data.code === 200) {
      ElMessage.success('已删除')
      router.push('/company/jobs')
    }
  } catch { /* cancelled */ }
}

function formatSalary(min: number | null, max: number | null): string {
  if (min && max) return `${min}K-${max}K`
  if (min) return `${min}K起`
  if (max) return `至${max}K`
  return '面议'
}

function matchClass(s: number) { return s >= 80 ? 'high' : s >= 60 ? 'mid' : 'low' }
function scaleScore(value: number, max: number): number {
  return Math.min(Math.round((value / max) * 100), 100)
}

onMounted(loadData)
</script>

<template>
  <div class="page">
    <!-- Loading -->
    <div v-if="loading" class="loading-hint">加载中...</div>

    <template v-else-if="detail">
      <!-- Header -->
      <div class="header fade-up">
        <button class="back-btn" @click="router.push('/company/jobs')">
          <ArrowLeft :size="18" />
        </button>
        <div class="header-info">
          <div class="title-row">
            <h1>{{ detail.title }}</h1>
            <el-tag :type="statusType[detail.status] || 'info'" size="large">
              {{ statusLabels[detail.status] || detail.status }}
            </el-tag>
          </div>
          <div class="meta-row">
            <span v-if="detail.city"><MapPin :size="13" /> {{ detail.city }}</span>
            <span>{{ jobTypeLabels[detail.job_type] || detail.job_type }}</span>
            <span>{{ formatSalary(detail.salary_min, detail.salary_max) }}</span>
            <span v-if="detail.experience_min">{{ detail.experience_min }}年以上经验</span>
            <span v-if="detail.education_requirement">{{ detail.education_requirement }}</span>
            <span><Eye :size="13" /> {{ detail.views }} 次浏览</span>
            <span><Clock :size="13" /> {{ detail.created_at?.slice(0, 10) }}</span>
          </div>
        </div>
        <div class="header-actions">
          <el-button @click="router.push('/company/jobs/publish')"><Edit :size="14" /> 编辑</el-button>
          <el-button :type="detail.status === 'OPEN' ? 'warning' : 'success'" @click="toggleStatus">
            {{ detail.status === 'OPEN' ? '关闭岗位' : '开启岗位' }}
          </el-button>
          <el-button type="danger" plain @click="handleDelete">删除</el-button>
        </div>
      </div>

      <div class="grid-2col fade-up d1">
        <!-- Left: Job Info -->
        <div class="card">
          <h2 class="card-title">基本信息</h2>
          <el-descriptions :column="1" border size="small">
            <el-descriptions-item label="岗位名称">{{ detail.title }}</el-descriptions-item>
            <el-descriptions-item label="工作城市">{{ detail.city || '不限' }}</el-descriptions-item>
            <el-descriptions-item label="工作类型">{{ jobTypeLabels[detail.job_type] }}</el-descriptions-item>
            <el-descriptions-item label="薪资范围">{{ formatSalary(detail.salary_min, detail.salary_max) }}</el-descriptions-item>
            <el-descriptions-item label="经验要求">{{ detail.experience_min ? detail.experience_min + '年' : '不限' }}</el-descriptions-item>
            <el-descriptions-item label="学历要求">{{ detail.education_requirement || '不限' }}</el-descriptions-item>
            <el-descriptions-item label="浏览次数">{{ detail.views }}</el-descriptions-item>
            <el-descriptions-item label="创建时间">{{ detail.created_at?.slice(0, 16).replace('T', ' ') }}</el-descriptions-item>
            <el-descriptions-item label="更新时间">{{ detail.updated_at?.slice(0, 16).replace('T', ' ') }}</el-descriptions-item>
          </el-descriptions>

          <h2 class="card-title" style="margin-top:20px">职位描述</h2>
          <div class="desc-content">{{ detail.description || '暂无描述' }}</div>

          <h2 class="card-title" style="margin-top:20px" v-if="detail.benefits?.length">福利待遇</h2>
          <div class="benefits-list" v-if="detail.benefits?.length">
            <span v-for="b in detail.benefits" :key="b" class="benefit-tag">{{ b }}</span>
          </div>
        </div>

        <!-- Right: Skills + Applications + Candidates -->
        <div class="card">
          <!-- Skills -->
          <h2 class="card-title">技能要求</h2>
          <div class="skills-area">
            <div class="skills-list" v-if="skills.length">
              <div v-for="s in skills" :key="s.id" class="skill-item">
                <div class="skill-left">
                  <span class="skill-name">{{ s.skill_name || '#' + s.skill_id }}</span>
                  <span v-if="s.skill_category" class="skill-cat">{{ s.skill_category }}</span>
                  <el-tag size="small" :type="s.required_level === 'MUST' ? 'danger' : s.required_level === 'NICE' ? 'warning' : 'info'">
                    {{ s.required_level === 'MUST' ? '必备' : s.required_level === 'NICE' ? '加分' : 'Bonus' }}
                  </el-tag>
                  <span class="imp">重要度: {{ s.importance }}/5</span>
                </div>
                <el-button text type="danger" size="small" @click="onRemoveSkill(s)"><X :size="14" /></el-button>
              </div>
            </div>
            <el-empty v-else description="暂无技能要求" :image-size="50" />

            <!-- Add skill -->
            <div class="add-skill-row">
              <el-input v-model="addSkillKeyword" placeholder="搜索技能..." size="small" style="width:200px" @keyup.enter="onSearchSkill" />
              <el-button size="small" @click="onSearchSkill"><Search :size="14" /></el-button>
            </div>
            <div v-if="skillSearchResults.length" class="skill-results">
              <div v-for="s in skillSearchResults" :key="s.id" class="skill-option" @click="onAddSkill(s)">
                <span>{{ s.name }}</span>
                <span v-if="s.category" class="skill-cat">{{ s.category }}</span>
                <el-button text type="primary" size="small"><Plus :size="14" /></el-button>
              </div>
            </div>
          </div>

          <!-- Applications -->
          <h2 class="card-title" style="margin-top:20px">投递列表</h2>
          <div class="placeholder-note">
            投递列表需要后端增加 <code>GET /api/job/{id}/applications</code> 端点后方可显示。
            该功能已在前端 <code>job.ts</code> 中预定义，后端需要补充实现。
          </div>

          <!-- Candidates -->
          <h2 class="card-title" style="margin-top:20px">候选人推荐</h2>
          <div class="placeholder-note">
            候选人推荐使用 <code>GET /api/match/candidates/{job_id}</code>（已有），
            可在「候选人推荐」页面查看。
          </div>
        </div>
      </div>
    </template>

    <el-empty v-else description="岗位不存在" :image-size="80" />
  </div>
</template>

<style scoped lang="scss">
.page { max-width: 1000px; margin: 0 auto; }

@keyframes fadeUp { from { opacity: 0; transform: translateY(16px); } to { opacity: 1; transform: translateY(0); } }
.fade-up { opacity: 0; animation: fadeUp 0.4s cubic-bezier(0.22,1,0.36,1) forwards; }
.d1 { animation-delay: 0.08s; }

.loading-hint { text-align: center; padding: 60px; color: #909399; font-size: 14px; }

.header {
  display: flex; align-items: flex-start; gap: 16px; margin-bottom: 24px;
}
.back-btn {
  width: 38px; height: 38px; display: flex; align-items: center; justify-content: center;
  border-radius: 10px; border: 1px solid #e5e7eb; background: #fff; color: #606266;
  cursor: pointer; flex-shrink: 0; margin-top: 4px;
  &:hover { border-color: #1a3a5c; color: #1a3a5c; }
}
.header-info { flex: 1; }
.title-row { display: flex; align-items: center; gap: 12px; margin-bottom: 6px; }
.title-row h1 { font-size: 24px; font-weight: 700; color: #303133; margin: 0; }
.meta-row { display: flex; flex-wrap: wrap; gap: 12px; font-size: 13px; color: #909399; align-items: center; }
.header-actions { display: flex; gap: 8px; flex-shrink: 0; margin-top: 4px; }

.grid-2col { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; }
.card {
  background: #fff; border-radius: 12px; padding: 20px; border: 1px solid #e5e7eb;
}
.card-title { font-size: 16px; font-weight: 700; color: #303133; margin: 0 0 12px 0; }

.desc-content { font-size: 14px; color: #606266; line-height: 1.7; white-space: pre-wrap; }

.benefits-list { display: flex; flex-wrap: wrap; gap: 8px; }
.benefit-tag { font-size: 12px; padding: 4px 12px; border-radius: 999px; background: #dbeafe; color: #1e3a8a; }

.skills-area { margin-bottom: 8px; }
.skills-list { display: flex; flex-direction: column; gap: 6px; margin-bottom: 12px; }
.skill-item {
  display: flex; align-items: center; justify-content: space-between;
  padding: 8px 12px; border: 1px solid #e5e7eb; border-radius: 8px; background: #fafbfc;
}
.skill-left { display: flex; align-items: center; gap: 6px; flex-wrap: wrap; }
.skill-name { font-size: 13px; font-weight: 600; color: #303133; }
.skill-cat { font-size: 11px; color: #909399; padding: 1px 6px; background: #f3f4f5; border-radius: 4px; }
.imp { font-size: 11px; color: #909399; }

.add-skill-row { display: flex; gap: 6px; align-items: center; margin-top: 8px; }
.skill-results { border: 1px solid #e5e7eb; border-radius: 8px; max-height: 160px; overflow-y: auto; margin-top: 6px; }
.skill-option {
  display: flex; align-items: center; gap: 8px; padding: 8px 12px; cursor: pointer;
  border-bottom: 1px solid #f3f4f5; font-size: 13px;
  &:hover { background: #f8f9fa; }
  &:last-child { border-bottom: none; }
}

.placeholder-note {
  background: #fffbe6; border: 1px solid #ffe58f; border-radius: 8px; padding: 14px;
  font-size: 13px; color: #ad8b00; line-height: 1.6;
  code { background: #fff; padding: 1px 4px; border-radius: 3px; font-size: 12px; }
}

@media (max-width: 768px) { .grid-2col { grid-template-columns: 1fr; } }
</style>
