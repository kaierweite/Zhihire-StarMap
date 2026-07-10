<script setup lang="ts">
import { ref, onMounted } from "vue"
import { ElMessage } from "element-plus"
import { Send } from "lucide-vue-next"
import { getCandidates, inviteCandidate } from "@/api/match"
import { listJobs } from "@/api/job"
import type { JobItem } from "@/api/job"
import { getCompanyProfile } from "@/api/company"


// ====== 岗位选择 ======
const companyJobs = ref<JobItem[]>([])
const selectedJobId = ref<number | null>(null)
const jobsLoading = ref(true)

// ====== 候选人数据 ======
interface Candidate {
  resume_id: number
  user_id: number
  name: string
  score: number
  skillScore: number
  eduScore: number
  expScore: number
  cityScore: number
  rationale: string
  invited: boolean
}

const candidates = ref<Candidate[]>([])
const loading = ref(false)
const error = ref("")

function scaleScore(value: number, max: number): number {
  return Math.min(Math.round((value / max) * 100), 100)
}

// ====== 加载企业岗位 ======
async function loadCompanyJobs() {
  jobsLoading.value = true
  try {
    const profileRes = await getCompanyProfile()
    const companyId = profileRes.data.data.id
    const jobsRes = await listJobs({ company_id: companyId, status: "ALL", size: 100 })
    companyJobs.value = jobsRes.data.data.records || []
    if (companyJobs.value.length > 0) {
      selectedJobId.value = companyJobs.value[0].id
      await fetchCandidates()
    }
  } catch {
    companyJobs.value = []
  } finally {
    jobsLoading.value = false
  }
}

// ====== 获取候选人推荐 ======
async function fetchCandidates() {
  if (!selectedJobId.value) return
  loading.value = true
  error.value = ""
  try {
    const res = await getCandidates(selectedJobId.value)
    const items = res.data.data.candidates
    candidates.value = items.map((c) => {
      const md = c.match_detail
      return {
        resume_id: c.resume_id,
        user_id: c.user_id,
        name: c.name,
        score: Math.round(c.score),
        skillScore: scaleScore(md.breakdown.skill.score, 10),
        eduScore: scaleScore(md.breakdown.edu.score, 12),
        expScore: scaleScore(md.breakdown.exp.score, 10),
        cityScore: scaleScore(md.breakdown.city.score, 10),
        rationale: md.rationale,
        invited: false,
      }
    })
  } catch (e: any) {
    error.value = e?.message || "加载候选人失败"
    candidates.value = []
  } finally {
    loading.value = false
  }
}

onMounted(loadCompanyJobs)

async function handleInvite(c: Candidate) {
  if (!selectedJobId.value) return
  try {
    await inviteCandidate({ resume_id: c.resume_id, job_id: selectedJobId.value })
    c.invited = true
    ElMessage.success("已向 " + c.name + " 发送面试邀请")
  } catch {
    /* error handled by interceptor */
  }
}

function matchClass(s: number) {
  return s >= 80 ? "high" : s >= 60 ? "mid" : "low"
}

function selectedJobTitle(): string {
  const job = companyJobs.value.find((j) => j.id === selectedJobId.value)
  return job?.title || "未选择"
}
</script>

<template>
  <div class="page">
    <h1 class="page-title fade-up">候选人推荐</h1>
    <p class="page-desc fade-up d1">AI 基于岗位需求与候选人技能图谱的智能匹配推荐</p>

    <!-- 岗位选择器 -->
    <div class="job-selector fade-up d2">
      <label class="selector-label">选择岗位</label>
      <div class="selector-row">
        <select v-model="selectedJobId" class="job-select" @change="fetchCandidates">
          <option v-for="job in companyJobs" :key="job.id" :value="job.id">
            {{ job.title }}
          </option>
        </select>
        <span class="hint" v-if="companyJobs.length === 0 && !jobsLoading">暂无岗位，请先发布岗位</span>
      </div>
    </div>

    <!-- 加载态 -->
    <div v-if="loading" class="loading-state">
      <div v-for="i in 3" :key="i" class="skeleton-card">
        <div class="skeleton-row skeleton-title" />
        <div class="skeleton-row skeleton-meta" />
        <div class="skeleton-row skeleton-bars">
          <div v-for="j in 4" :key="j" class="skeleton-bar" />
        </div>
      </div>
    </div>

    <!-- 错误态 -->
    <div v-else-if="error" class="empty-state">
      <p>加载失败</p>
      <span>{{ error }}</span>
      <button class="retry-btn" @click="fetchCandidates">重新加载</button>
    </div>

    <!-- 候选人列表 -->
    <template v-else>
      <div class="summary-bar" v-if="selectedJobId">
        当前岗位：<strong>{{ selectedJobTitle() }}</strong> &nbsp;|&nbsp; 共 <strong>{{ candidates.length }}</strong> 位候选人
      </div>

      <div class="card-list">
        <div v-for="c in candidates" :key="c.resume_id" class="card fade-up">
          <div class="card-main">
            <div class="card-left">
              <div class="card-title-row">
                <h3>{{ c.name }}</h3>
              </div>
              <!-- 四维子分 -->
              <div class="sub-scores">
                <div class="ss">
                  <span>技能</span>
                  <div class="ss-bar"><div class="ss-fill" :style="{ width: c.skillScore + '%' }" /></div>
                  <span class="ss-val">{{ c.skillScore }}</span>
                </div>
                <div class="ss">
                  <span>学历</span>
                  <div class="ss-bar"><div class="ss-fill edu" :style="{ width: c.eduScore + '%' }" /></div>
                  <span class="ss-val">{{ c.eduScore }}</span>
                </div>
                <div class="ss">
                  <span>经验</span>
                  <div class="ss-bar"><div class="ss-fill exp" :style="{ width: c.expScore + '%' }" /></div>
                  <span class="ss-val">{{ c.expScore }}</span>
                </div>
                <div class="ss">
                  <span>城市</span>
                  <div class="ss-bar"><div class="ss-fill city" :style="{ width: c.cityScore + '%' }" /></div>
                  <span class="ss-val">{{ c.cityScore }}</span>
                </div>
              </div>
              <p class="rationale"><strong>匹配依据：</strong>{{ c.rationale }}</p>
            </div>
            <div class="card-right">
              <div class="match-circle" :class="matchClass(c.score)">
                <span class="match-num">{{ c.score }}</span>
                <span class="match-lbl">匹配</span>
              </div>
              <button
                class="invite-btn"
                :class="{ invited: c.invited }"
                :disabled="c.invited"
                @click="handleInvite(c)"
              >
                <Send :size="14" /> {{ c.invited ? "已邀请" : "面试邀请" }}
              </button>
            </div>
          </div>
        </div>

        <!-- 空态 -->
        <div v-if="candidates.length === 0 && !loading" class="empty-state">
          <p>暂无候选人匹配</p>
          <span>该岗位尚未匹配到合适的候选人</span>
        </div>
      </div>
    </template>
  </div>
</template>

<style scoped lang="scss">
.page { max-width: 900px; margin: 0 auto; padding: 24px 16px; }

@keyframes fadeUp { from { opacity: 0; transform: translateY(20px); } to { opacity: 1; transform: translateY(0); } }
.fade-up { opacity: 0; animation: fadeUp 0.5s cubic-bezier(0.22,1,0.36,1) forwards; }
.d1 { animation-delay: 0.08s; } .d2 { animation-delay: 0.15s; }

.page-title { font-size: 28px; font-weight: 700; color: #303133; margin-bottom: 6px; }
.page-desc { font-size: 14px; color: #909399; margin-bottom: 20px; }

/* 岗位选择器 */
.job-selector {
  background: #fff; border-radius: 12px; padding: 16px 20px;
  border: 1px solid #e5e7eb; margin-bottom: 20px;
}
.selector-label { font-size: 13px; font-weight: 600; color: #303133; margin-bottom: 8px; display: block; }
.selector-row { display: flex; align-items: center; gap: 12px; }
.job-select {
  flex: 1; max-width: 360px; appearance: none; padding: 8px 32px 8px 12px;
  border: 1px solid #dcdfe6; border-radius: 8px; font-size: 14px; color: #303133;
  background: #fff; cursor: pointer; outline: none;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='16' height='16' viewBox='0 0 24 24' fill='none' stroke='%23909399' stroke-width='2'%3E%3Cpolyline points='6 9 12 15 18 9'/%3E%3C/svg%3E");
  background-repeat: no-repeat; background-position: right 8px center;
  &:focus { border-color: #1a3a5c; }
}
.hint { font-size: 13px; color: #909399; }

.summary-bar {
  font-size: 13px; color: #606266; margin-bottom: 14px;
  strong { color: #303133; }
}

/* 加载骨架 */
.loading-state { display: flex; flex-direction: column; gap: 14px; }
.skeleton-card {
  background: #fff; border-radius: 12px; padding: 20px; border: 1px solid #e5e7eb;
  display: flex; flex-direction: column; gap: 12px;
}
.skeleton-row { border-radius: 4px; background: linear-gradient(90deg, #eee 25%, #f5f5f5 50%, #eee 75%); background-size: 200% 100%; animation: shimmer 1.5s infinite; }
.skeleton-title { height: 18px; width: 40%; }
.skeleton-meta { height: 14px; width: 30%; }
.skeleton-bars { display: grid; grid-template-columns: repeat(4, 1fr); gap: 8px; }
.skeleton-bar { height: 4px; border-radius: 2px; }
@keyframes shimmer { 0% { background-position: 200% 0; } 100% { background-position: -200% 0; } }

.retry-btn { margin-top: 12px; padding: 8px 20px; border-radius: 8px; background: #1a3a5c; color: #fff; border: none; cursor: pointer; font-size: 14px; &:hover { background: #24507a; } }

.card-list { display: flex; flex-direction: column; gap: 14px; }
.card { background: #fff; border-radius: 12px; padding: 20px; border: 1px solid #e5e7eb; transition: all 0.3s; &:hover { box-shadow: 0 6px 20px rgba(0,0,0,0.05); } }
.card-main { display: flex; gap: 20px; }
.card-left { flex: 1; }
.card-right { display: flex; flex-direction: column; align-items: center; gap: 10px; flex-shrink: 0; width: 100px; }
.card-title-row { display: flex; align-items: center; gap: 10px; margin-bottom: 12px; h3 { font-size: 16px; font-weight: 700; color: #303133; } }

.sub-scores { display: grid; grid-template-columns: repeat(4, 1fr); gap: 8px; margin-bottom: 10px; }
.ss { display: flex; align-items: center; gap: 4px; font-size: 11px; color: #909399; span:first-child { width: 24px; } }
.ss-bar { flex: 1; height: 4px; border-radius: 2px; background: #e9ecef; overflow: hidden; }
.ss-fill { height: 100%; border-radius: 2px; background: #1a3a5c; transition: width 0.6s; &.edu { background: #0ea5e9; } &.exp { background: #8b5cf6; } &.city { background: #f59e0b; } }
.ss-val { width: 22px; text-align: right; font-weight: 600; color: #303133; }
.rationale { font-size: 12px; color: #606266; line-height: 1.6; strong { color: #303133; } }

.match-circle { width: 56px; height: 56px; border-radius: 50%; display: flex; flex-direction: column; align-items: center; justify-content: center; font-weight: 700; &.high { background: rgba(25,135,84,0.12); color: #198754; } &.mid { background: rgba(184,134,11,0.12); color: #b8860b; } &.low { background: rgba(220,53,69,0.12); color: #dc3545; } }
.match-num { font-size: 18px; line-height: 1; }
.match-lbl { font-size: 9px; opacity: 0.8; }

.invite-btn { display: flex; align-items: center; gap: 4px; padding: 6px 14px; border-radius: 999px; background: #1a3a5c; color: #fff; font-size: 12px; font-weight: 600; border: none; cursor: pointer; &:hover:not(.invited) { background: #24507a; } &.invited { background: #d4edda; color: #155724; cursor: default; } }

.empty-state { text-align: center; padding: 60px 20px; color: #909399; p { font-size: 16px; font-weight: 600; margin-bottom: 4px; } span { font-size: 13px; } }

@media (max-width: 768px) {
  .card-main { flex-direction: column; }
  .card-right { flex-direction: row; width: 100%; justify-content: flex-end; }
  .sub-scores { grid-template-columns: repeat(2, 1fr); }
}
</style>
