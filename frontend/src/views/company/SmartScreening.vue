<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Search, MapPin, Send, X } from 'lucide-vue-next'
import { getCandidates, inviteCandidate } from '@/api/match'
import { listJobs } from '@/api/job'
import type { JobItem } from '@/api/job'
import type { CandidateRecommendation } from '@/api/match'
import { getCompanyProfile } from '@/api/company'

const loading = ref(false)
const jobsLoading = ref(true)
const candidates = ref<CandidateRecommendation[]>([])
const companyJobs = ref<JobItem[]>([])
const selectedJobId = ref<number | null>(null)

const keyword = ref('')
const filterCity = ref('')
const filterEdu = ref('')

const filtered = computed(() => {
  let list = candidates.value
  if (keyword.value) {
    const kw = keyword.value.toLowerCase()
    list = list.filter(c => c.name.toLowerCase().includes(kw))
  }
  if (filterCity.value) {
    list = list.filter(c => c.match_detail.breakdown.city.detail.includes(filterCity.value))
  }
  return list.sort((a, b) => b.score - a.score)
})

const hasFilters = computed(() => keyword.value || filterCity.value || filterEdu.value)

function clearAll() {
  keyword.value = ''
  filterCity.value = ''
  filterEdu.value = ''
}

async function loadCompanyJobs() {
  jobsLoading.value = true
  try {
    const profileRes = await getCompanyProfile()
    const companyId = profileRes.data.data.id
    const jobsRes = await listJobs({ company_id: companyId, status: 'ALL', size: 100 })
    companyJobs.value = jobsRes.data.data.records || []
  } catch {
    companyJobs.value = []
  } finally {
    jobsLoading.value = false
  }
}

async function fetchCandidates() {
  if (!selectedJobId.value) {
    candidates.value = []
    return
  }
  loading.value = true
  try {
    const res = await getCandidates(selectedJobId.value)
    candidates.value = res.data.data.candidates || []
  } catch {
    candidates.value = []
    ElMessage.error('加载候选人失败')
  } finally {
    loading.value = false
  }
}

async function handleInvite(c: CandidateRecommendation) {
  if (!selectedJobId.value) return
  try {
    await inviteCandidate({ resume_id: c.resume_id, job_id: selectedJobId.value })
    ElMessage.success('已向 ' + c.name + ' 发送面试邀请')
  } catch {
    // handled by interceptor
  }
}

function matchClass(s: number) {
  return s >= 80 ? 'high' : s >= 60 ? 'mid' : 'low'
}

onMounted(loadCompanyJobs)
</script>

<template>
  <div class="page">
    <h1 class="page-title fade-up">智能筛选</h1>
    <p class="page-desc fade-up d1">开放式人才搜索，按技能、城市、学历多维度筛选候选人</p>

    <div class="filter-card fade-up d2">
      <div class="filter-row">
        <div class="job-selector">
          <label>选择岗位：</label>
          <select v-model="selectedJobId" class="job-sel" @change="fetchCandidates">
            <option value="" disabled>请选择岗位</option>
            <option v-for="j in companyJobs" :key="j.id" :value="j.id">{{ j.title }}</option>
          </select>
          <span v-if="!companyJobs.length && !jobsLoading" class="hint">暂无岗位，请先发布</span>
        </div>
        <div class="search-box"><Search :size="16" /><input v-model="keyword" placeholder="搜索候选人姓名..." /></div>
        <input v-model="filterCity" class="sel" placeholder="城市筛选" />
        <button v-if="hasFilters" class="clear-btn" @click="clearAll"><X :size="14" /> 清除</button>
      </div>
      <div class="filter-count">共 <strong>{{ filtered.length }}</strong> 位候选人</div>
    </div>

    <div v-if="loading" class="loading-hint">加载中...</div>
    <div v-else-if="!selectedJobId" class="empty-hint">请先选择一个岗位查看候选人</div>
    <div v-else class="talent-grid">
      <div v-for="c in filtered" :key="c.resume_id" class="talent-card fade-up">
        <div class="talent-header">
          <div class="talent-avatar">{{ c.name.charAt(0) }}</div>
          <div class="talent-info">
            <h3>{{ c.name }}</h3>
            <p>{{ c.match_detail.breakdown?.edu?.detail || '' }}</p>
          </div>
          <div class="match-badge" :class="matchClass(c.score)">{{ c.score }}%</div>
        </div>
        <div class="talent-meta">
          <span><MapPin :size="12" /> {{ c.match_detail.breakdown?.city?.detail || '' }}</span>
        </div>
        <div class="talent-skills">
          <span v-for="s in (c.match_detail.breakdown?.skill?.hit || [])" :key="s" class="skill-tag hit">{{ s }}</span>
          <span v-for="s in (c.match_detail.breakdown?.skill?.miss || [])" :key="s" class="skill-tag miss">{{ s }}</span>
        </div>
        <p class="rationale">{{ c.match_detail.rationale }}</p>
        <button class="invite-btn" @click="handleInvite(c)">
          <Send :size="13" /> 面试邀请
        </button>
      </div>
      <el-empty v-if="!filtered.length && !loading" description="暂无匹配候选人" :image-size="80" />
    </div>
  </div>
</template>

<style scoped lang="scss">
.page { max-width: 1000px; margin: 0 auto; }
@keyframes fadeUp { from { opacity: 0; transform: translateY(20px); } to { opacity: 1; transform: translateY(0); } }
.fade-up { opacity: 0; animation: fadeUp 0.5s cubic-bezier(0.22,1,0.36,1) forwards; }
.d1 { animation-delay: 0.08s; } .d2 { animation-delay: 0.15s; }
.page-title { font-size: 28px; font-weight: 700; color: #303133; margin-bottom: 6px; }
.page-desc { font-size: 14px; color: #909399; margin-bottom: 20px; }

.filter-card { background: #fff; border-radius: 12px; padding: 16px 20px; border: 1px solid #e5e7eb; margin-bottom: 20px; }
.filter-row { display: flex; gap: 8px; align-items: center; flex-wrap: wrap; }
.job-selector { display: flex; align-items: center; gap: 8px; margin-right: 8px; label { font-size: 13px; font-weight: 600; color: #303133; white-space: nowrap; } }
.job-sel { padding: 8px 10px; border: 1px solid #dcdfe6; border-radius: 8px; font-size: 13px; background: #fff; outline: none; min-width: 160px; &:focus { border-color: #1a3a5c; } }
.hint { font-size: 12px; color: #909399; }
.search-box { flex: 1; min-width: 180px; display: flex; align-items: center; gap: 8px; padding: 8px 12px; border: 1px solid #dcdfe6; border-radius: 8px; background: #fff; input { flex: 1; border: none; outline: none; font-size: 13px; } svg { color: #909399; } &:focus-within { border-color: #1a3a5c; } }
.sel { padding: 8px 10px; border: 1px solid #dcdfe6; border-radius: 8px; font-size: 12px; background: #fff; outline: none; &:focus { border-color: #1a3a5c; } }
.clear-btn { display: flex; align-items: center; gap: 4px; padding: 6px 12px; border-radius: 6px; border: 1px solid #f56c6c; background: none; color: #f56c6c; font-size: 12px; cursor: pointer; &:hover { background: #f56c6c; color: #fff; } }
.filter-count { font-size: 13px; color: #909399; margin-top: 10px; }

.loading-hint, .empty-hint { text-align: center; padding: 60px; color: #909399; font-size: 14px; }

.talent-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 14px; }
.talent-card { background: #fff; border-radius: 12px; padding: 18px; border: 1px solid #e5e7eb; transition: all 0.3s; &:hover { box-shadow: 0 8px 24px rgba(0,0,0,0.06); transform: translateY(-2px); } }
.talent-header { display: flex; align-items: center; gap: 10px; margin-bottom: 8px; }
.talent-avatar { width: 40px; height: 40px; border-radius: 50%; background: #dbeafe; color: #1a3a5c; display: flex; align-items: center; justify-content: center; font-size: 16px; font-weight: 700; flex-shrink: 0; }
.talent-info { flex: 1; h3 { font-size: 15px; font-weight: 600; color: #303133; } p { font-size: 12px; color: #909399; } }
.match-badge { font-size: 14px; font-weight: 700; padding: 4px 10px; border-radius: 999px; &.high { background: rgba(25,135,84,0.12); color: #198754; } &.mid { background: rgba(184,134,11,0.12); color: #b8860b; } &.low { background: rgba(220,53,69,0.12); color: #dc3545; } }
.talent-meta { font-size: 12px; color: #909399; margin-bottom: 8px; span { display: flex; align-items: center; gap: 3px; } }
.talent-skills { display: flex; flex-wrap: wrap; gap: 6px; margin-bottom: 8px; }
.skill-tag { font-size: 11px; padding: 2px 10px; border-radius: 4px; &.hit { background: #d4edda; color: #155724; } &.miss { background: #f8d7da; color: #721c24; } }
.rationale { font-size: 12px; color: #606266; line-height: 1.6; margin: 0 0 12px 0; }
.invite-btn { width: 100%; display: flex; align-items: center; justify-content: center; gap: 4px; padding: 8px; border-radius: 999px; background: #1a3a5c; color: #fff; font-size: 13px; font-weight: 600; border: none; cursor: pointer; &:hover { background: #24507a; } }

@media (max-width: 900px) { .talent-grid { grid-template-columns: repeat(2, 1fr); } }
@media (max-width: 600px) { .talent-grid { grid-template-columns: 1fr; } }
</style>
