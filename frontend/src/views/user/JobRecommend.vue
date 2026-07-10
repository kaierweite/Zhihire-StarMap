<script setup lang="ts">
import { ref, computed, onMounted } from "vue"
import { ElMessage, ElMessageBox } from "element-plus"
import {
  MapPin, GraduationCap, Briefcase, Building2, Send, Brain, FileText,
  ChevronDown, X, SlidersHorizontal, ArrowUpDown,
} from "lucide-vue-next"
import { getRecommendedJobs, applyMatchJob } from "@/api/match"
import { getJobDetail } from "@/api/job"
import type { JobDetail as JobDetailType } from "@/api/job"

const filterCity = ref("")
const filterEdu = ref("")
const filterType = ref("")
const filterCompanyType = ref("")
const filterSalary = ref("")
const sortBy = ref<"match" | "salary">("match")
const currentPage = ref(1)
const pageSize = 5
const loading = ref(true)
const error = ref("")

const jobTypeMap: Record<string, string> = {
  FULL_TIME: "全职", PART_TIME: "兼职", INTERN: "实习",
}

interface Job {
  id: number; resume_id: number; title: string; company: string
  logo: string; logoColor: string; city: string; exp: string; edu: string
  salary: string; salaryNum: number; type: string
  companyType: string; industry: string; companySize: string
  score: number; tags: string[]; tagTypes: string[]
  skillScore: number; eduScore: number; expScore: number; cityScore: number
  rationale: string; graphHints: string[]; applied: boolean
}

function scaleScore(value: number, max: number): number {
  return Math.min(Math.round((value / max) * 100), 100)
}

const allJobs = ref<Job[]>([])

async function fetchRecommendations() {
  loading.value = true
  error.value = ""
  try {
    const res = await getRecommendedJobs()
    const jobs = res.data.data.jobs
    const details = await Promise.all(
      jobs.map((job) =>
        getJobDetail(job.job_id).then((r) => r.data.data).catch((): null => null),
      ),
    )
    allJobs.value = jobs.map((job, idx) => {
      const detail: JobDetailType | null = details[idx]
      const md = job.match_detail
      return {
        id: job.job_id, resume_id: job.resume_id,
        title: job.title, company: job.company_name,
        score: Math.round(job.score),
        skillScore: scaleScore(md.breakdown.skill.score, 10),
        eduScore: scaleScore(md.breakdown.edu.score, 12),
        expScore: scaleScore(md.breakdown.exp.score, 10),
        cityScore: scaleScore(md.breakdown.city.score, 10),
        rationale: md.rationale, graphHints: md.graph_hints,
        city: detail?.city || "",
        exp: detail?.experience_min ? detail.experience_min + "年" : "",
        edu: detail?.education_requirement || "",
        type: detail?.job_type ? (jobTypeMap[detail.job_type] || detail.job_type) : "",
        salary: detail?.salary_min != null && detail.salary_min > 0 ? Math.round(detail.salary_min / 1000) + "-" + (detail.salary_max && detail.salary_max > 0 ? Math.round(detail.salary_max / 1000) : "?") + "K" : "",
        salaryNum: detail?.salary_min ?? 0,
        companyType: "", industry: "", companySize: "",
        tags: ["AI推荐"], tagTypes: ["ai"],
        logo: job.company_name.charAt(0), logoColor: "#dbeafe",
        applied: false,
      }
    })
  } catch (e: any) {
    error.value = e?.message || "加载推荐失败"
    allJobs.value = []
  } finally {
    loading.value = false
  }
}

onMounted(fetchRecommendations)

const filteredJobs = computed(() => {
  let result = allJobs.value.filter((j) => {
    if (filterCity.value && j.city !== filterCity.value) return false
    if (filterEdu.value && j.edu !== filterEdu.value) return false
    if (filterType.value && j.type !== filterType.value) return false
    if (filterCompanyType.value && j.companyType !== filterCompanyType.value) return false
    if (filterSalary.value) {
      const parts = filterSalary.value.split("-")
      const min = Number(parts[0]) || 0; const max = Number(parts[1]) || 999
      if (j.salaryNum < min || j.salaryNum > max) return false
    }
    return true
  })
  result.sort((a, b) => sortBy.value === "match" ? b.score - a.score : b.salaryNum - a.salaryNum)
  return result
})

const pagedJobs = computed(() => {
  const start = (currentPage.value - 1) * pageSize
  return filteredJobs.value.slice(start, start + pageSize)
})

const totalPages = computed(() => Math.ceil(filteredJobs.value.length / pageSize))

function clearFilters() {
  filterCity.value = ""; filterEdu.value = ""; filterType.value = ""
  filterCompanyType.value = ""; filterSalary.value = ""; currentPage.value = 1
}

function matchClass(score: number) {
  if (score >= 80) return "match-high"
  if (score >= 60) return "match-mid"
  return "match-low"
}

async function handleApply(job: Job) {
  try {
    await ElMessageBox.confirm(
      "确认投递" + job.title + " · " + job.company,
      "投递确认",
      { confirmButtonText: "确认投递", cancelButtonText: "取消", type: "info" },
    )
    await applyMatchJob({ job_id: job.id, resume_id: job.resume_id })
    job.applied = true
    ElMessage.success("已投递" + job.title + "，企业端已收到你的简历")
  } catch { /* cancelled */ }
}
</script>

<template>
  <div class="recommend-page">
    <div class="recommend-container">
      <h1 class="page-title fade-up">智能岗位推荐</h1>
      <p class="page-desc fade-up d1">基于 AI 语义匹配的精准推荐，四维评分一目了然</p>

      <div v-if="loading" class="loading-state">
        <div v-for="i in 3" :key="i" class="skeleton-card">
          <div class="skeleton-row skeleton-title" />
          <div class="skeleton-row skeleton-meta" />
          <div class="skeleton-row skeleton-bars">
            <div v-for="j in 4" :key="j" class="skeleton-bar" />
          </div>
        </div>
      </div>

      <div v-else-if="error" class="empty-state">
        <p>加载失败</p>
        <span>{{ error }}</span>
        <button class="retry-btn" @click="fetchRecommendations">重新加载</button>
      </div>

      <template v-else>
        <div class="filter-bar fade-up d2">
          <div class="filter-row">
            <select v-model="filterCity" class="filter-select">
              <option value="">工作城市</option>
              <option>北京</option><option>上海</option><option>杭州</option>
              <option>深圳</option><option>成都</option><option>武汉</option>
            </select>
            <select v-model="filterEdu" class="filter-select">
              <option value="">学历</option>
              <option>大专</option><option>本科</option><option>硕士</option><option>博士</option>
            </select>
            <select v-model="filterType" class="filter-select">
              <option value="">工作性质</option>
              <option>全职</option><option>实习</option><option>兼职</option>
            </select>
            <select v-model="filterCompanyType" class="filter-select">
              <option value="">公司性质</option>
              <option>互联网大厂</option><option>国企央企</option><option>创业公司</option><option>上市公司</option>
            </select>
            <select v-model="filterSalary" class="filter-select">
              <option value="">薪资</option>
              <option value="8-15">8K-15K</option><option value="15-25">15K-25K</option>
              <option value="25-40">25K-40K</option><option value="40-999">40K以上</option>
            </select>
            <select v-model="sortBy" class="filter-select sort-select">
              <option value="match">按匹配度</option>
              <option value="salary">按薪资</option>
            </select>
            <button v-if="filterCity || filterEdu || filterType || filterCompanyType || filterSalary" class="clear-btn" @click="clearFilters">
              <X :size="14" /> 清除
            </button>
          </div>
          <div class="filter-count">
            共 <strong>{{ filteredJobs.length }}</strong> 个匹配职位
          </div>
        </div>

        <div class="job-list">
          <div v-for="job in pagedJobs" :key="job.id" class="job-card fade-up">
            <div class="job-card-inner">
              <div class="job-left">
                <div class="job-header">
                  <h3 class="job-title">
                    {{ job.title }}
                    <span v-for="(tag, idx) in job.tags" :key="tag" class="job-tag" :class="job.tagTypes[idx]">{{ tag }}</span>
                  </h3>
                </div>
                <div class="job-meta-row">
                  <span class="job-meta">{{ job.exp || "经验不限" }}</span>
                  <span class="job-meta-dot">·</span>
                  <span class="job-meta">{{ job.edu || "学历不限" }}</span>
                  <span class="job-meta-dot">·</span>
                  <span class="job-meta">{{ job.type || "全职" }}</span>
                  <span class="job-meta-dot">·</span>
                  <span class="job-meta">{{ job.city || "不限" }}</span>
                </div>
                <div class="company-row">
                  <div class="company-logo" :style="{ background: job.logoColor }">{{ job.logo }}</div>
                  <span class="company-name">{{ job.company }}</span>
                </div>
              </div>

              <div class="job-center">
                <div class="match-dashboard">
                  <div class="circle-scores">
                    <div class="circle-score-item">
                      <svg class="score-circle" viewBox="0 0 52 52">
                        <circle cx="26" cy="26" r="22" class="circle-bg" />
                        <circle cx="26" cy="26" r="22" class="circle-fill skill" :style="{ strokeDasharray: job.skillScore * 1.38 + ' 138' }" transform="rotate(-90, 26, 26)" />
                        <text x="26" y="28" text-anchor="middle" class="circle-text">{{ job.skillScore }}%</text>
                      </svg>
                      <span class="circle-label">技能</span>
                    </div>
                    <div class="circle-score-item">
                      <svg class="score-circle" viewBox="0 0 52 52">
                        <circle cx="26" cy="26" r="22" class="circle-bg" />
                        <circle cx="26" cy="26" r="22" class="circle-fill exp" :style="{ strokeDasharray: job.expScore * 1.38 + ' 138' }" transform="rotate(-90, 26, 26)" />
                        <text x="26" y="28" text-anchor="middle" class="circle-text">{{ job.expScore }}%</text>
                      </svg>
                      <span class="circle-label">经验</span>
                    </div>
                    <div class="circle-score-item">
                      <svg class="score-circle" viewBox="0 0 52 52">
                        <circle cx="26" cy="26" r="22" class="circle-bg" />
                        <circle cx="26" cy="26" r="22" class="circle-fill city" :style="{ strokeDasharray: job.cityScore * 1.38 + ' 138' }" transform="rotate(-90, 26, 26)" />
                        <text x="26" y="28" text-anchor="middle" class="circle-text">{{ job.cityScore }}%</text>
                      </svg>
                      <span class="circle-label">位置</span>
                    </div>
                    <div class="circle-score-item">
                      <svg class="score-circle" viewBox="0 0 52 52">
                        <circle cx="26" cy="26" r="22" class="circle-bg" />
                        <circle cx="26" cy="26" r="22" class="circle-fill edu" :style="{ strokeDasharray: job.eduScore * 1.38 + ' 138' }" transform="rotate(-90, 26, 26)" />
                        <text x="26" y="28" text-anchor="middle" class="circle-text">{{ job.eduScore }}%</text>
                      </svg>
                      <span class="circle-label">文化</span>
                    </div>
                    <div class="circle-score-item main-score">
                      <svg class="score-circle" viewBox="0 0 52 52">
                        <circle cx="26" cy="26" r="22" class="circle-bg" />
                        <circle cx="26" cy="26" r="22" class="circle-fill main" :class="matchClass(job.score)" :style="{ strokeDasharray: job.score * 1.38 + ' 138' }" transform="rotate(-90, 26, 26)" />
                        <text x="26" y="28" text-anchor="middle" class="circle-text">{{ job.score }}%</text>
                      </svg>
                      <span class="circle-label">总体匹配</span>
                    </div>
                  </div>
                </div>
              </div>

              <div class="job-right">
                <span v-if="job.salary" class="job-salary">{{ job.salary }}</span>
                <div class="job-actions">
                  <button
                    class="action-btn apply"
                    :class="{ applied: job.applied }"
                    :disabled="job.applied"
                    @click="handleApply(job)"
                  >
                    <Send :size="14" /> {{ job.applied ? "已投递" : "投递简历" }}
                  </button>
                  <button class="action-btn interview" title="模拟面试"><Brain :size="14" /> AI模拟面试</button>
                  <router-link :to="`/user/jobs/${job.id}`" class="action-btn detail"><FileText :size="14" /> 查看详情</router-link>
                </div>
              </div>
            </div>
          </div>

          <div v-if="pagedJobs.length === 0" class="empty-state">
            <p>暂无匹配职位</p>
            <span>试试调整筛选条件</span>
          </div>
        </div>

        <div v-if="totalPages > 1" class="pagination">
          <button class="page-btn" :disabled="currentPage <= 1" @click="currentPage--">&lt;</button>
          <button v-for="p in totalPages" :key="p" class="page-btn" :class="{ active: p === currentPage }" @click="currentPage = p">{{ p }}</button>
          <button class="page-btn" :disabled="currentPage >= totalPages" @click="currentPage++">&gt;</button>
        </div>
      </template>
    </div>
  </div>
</template>

<style scoped lang="scss">
.recommend-page { padding: 24px 16px; }
.recommend-container { max-width: 1280px; margin: 0 auto; }

@keyframes fadeUp { from { opacity: 0; transform: translateY(20px); } to { opacity: 1; transform: translateY(0); } }
.fade-up { opacity: 0; animation: fadeUp 0.5s cubic-bezier(0.22,1,0.36,1) forwards; }
.d1 { animation-delay: 0.08s; } .d2 { animation-delay: 0.15s; }

.page-title { font-size: 36px; font-weight: 700; color: #303133; letter-spacing: -1px; margin-bottom: 6px; }
.page-desc { font-size: 16px; color: #909399; margin-bottom: 24px; }

.loading-state { display: flex; flex-direction: column; gap: 12px; }
.skeleton-card { background: #fff; border-radius: 12px; padding: 20px; border: 1px solid #e5e7eb; display: flex; flex-direction: column; gap: 12px; }
.skeleton-row { border-radius: 4px; background: linear-gradient(90deg, #eee 25%, #f5f5f5 50%, #eee 75%); background-size: 200% 100%; animation: shimmer 1.5s infinite; }
.skeleton-title { height: 20px; width: 60%; }
.skeleton-meta { height: 14px; width: 40%; }
.skeleton-bars { display: grid; grid-template-columns: repeat(4, 1fr); gap: 10px; }
.skeleton-bar { height: 4px; border-radius: 2px; }
@keyframes shimmer { 0% { background-position: 200% 0; } 100% { background-position: -200% 0; } }

.retry-btn { margin-top: 12px; padding: 8px 20px; border-radius: 8px; background: #003527; color: #fff; border: none; cursor: pointer; font-size: 14px; &:hover { background: #064e3b; } }

.filter-bar { background: #fff; border-radius: 12px; padding: 16px 20px; border: 1px solid #e5e7eb; margin-bottom: 20px; }
.filter-row { display: flex; align-items: center; gap: 8px; flex-wrap: wrap; }
.filter-select { appearance: none; padding: 6px 28px 6px 10px; border: 1px solid #dcdfe6; border-radius: 8px; font-size: 12px; color: #606266; background: #fff; cursor: pointer; outline: none; background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='14' height='14' viewBox='0 0 24 24' fill='none' stroke='%23909399' stroke-width='2'%3E%3Cpolyline points='6 9 12 15 18 9'/%3E%3C/svg%3E"); background-repeat: no-repeat; background-position: right 6px center; transition: border-color 0.2s; &:focus { border-color: #003527; } }
.sort-select { font-weight: 600; }
.clear-btn { display: inline-flex; align-items: center; gap: 4px; padding: 6px 12px; border-radius: 6px; border: 1px solid #f56c6c; background: none; color: #f56c6c; font-size: 12px; cursor: pointer; transition: all 0.2s; &:hover { background: #f56c6c; color: #fff; } }
.filter-count { font-size: 13px; color: #909399; margin-top: 10px; }

.job-list { display: flex; flex-direction: column; gap: 20px; }
.job-card { background: #fff; border-radius: 16px; border: 1px solid #e5e7eb; padding: 20px; transition: all 0.3s; &:hover { box-shadow: 0 8px 28px rgba(0,0,0,0.08); } }
.job-card-inner { display: flex; gap: 24px; align-items: stretch; }
.job-left { flex: 1; min-width: 0; display: flex; flex-direction: column; }
.job-header { display: flex; align-items: center; margin-bottom: 8px; }
.job-title { font-size: 16px; font-weight: 700; color: #003527; display: flex; align-items: center; gap: 8px; flex-wrap: wrap; }
.job-tag { font-size: 11px; font-weight: 600; padding: 2px 8px; border-radius: 999px; &.ai { background: rgba(14,165,233,0.1); color: #0ea5e9; } &.hot { background: rgba(239,68,68,0.1); color: #ef4444; } &.new { background: rgba(16,185,129,0.1); color: #10b981; } &.urgent { background: rgba(245,158,11,0.1); color: #f59e0b; } }
.job-meta-row { display: flex; align-items: center; gap: 4px; margin-bottom: 10px; flex-wrap: wrap; }
.job-meta { font-size: 12px; color: #606266; }
.job-meta-dot { color: #dcdfe6; margin: 0 4px; }
.company-row { display: flex; align-items: center; gap: 8px; font-size: 13px; color: #606266; }
.company-logo { width: 24px; height: 24px; border-radius: 6px; display: flex; align-items: center; justify-content: center; font-size: 11px; font-weight: 700; flex-shrink: 0; }
.company-name { font-weight: 500; color: #303133; }

.job-center { flex: 1.2; min-width: 0; display: flex; flex-direction: column; }
.match-dashboard { background: #ffffff; border-radius: 12px; padding: 14px; flex: 1; display: flex; flex-direction: column; }
.circle-scores { display: grid; grid-template-columns: repeat(5, 1fr); gap: 8px; flex: 1; }
.circle-score-item { display: flex; flex-direction: column; align-items: center; gap: 4px; }
.score-circle { width: 52px; height: 52px; }
.circle-bg { fill: none; stroke: #e5e7eb; stroke-width: 4; }
.circle-fill { fill: none; stroke-width: 4; stroke-linecap: round; transition: stroke-dasharray 0.6s ease; &.skill { stroke: #1a3a5c; } &.exp { stroke: #0ea5e9; } &.city { stroke: #f59e0b; } &.edu { stroke: #8b5cf6; } &.main.match-high { stroke: #198754; } &.main.match-mid { stroke: #b8860b; } &.main.match-low { stroke: #dc3545; } }
.circle-text { font-size: 10px; font-weight: 700; fill: #303133; }
.circle-text-num { font-size: 12px; font-weight: 700; fill: #303133; }
.circle-text-label { font-size: 7px; font-weight: 600; fill: #909399; }
.circle-label { font-size: 10px; color: #909399; }

.job-right { display: flex; flex-direction: column; align-items: flex-end; gap: 10px; flex-shrink: 0; width: 130px; }
.job-salary { font-size: 18px; font-weight: 700; color: #003527; white-space: nowrap; }

.job-actions { display: flex; flex-direction: column; gap: 6px; width: 100%; }
.action-btn { display: flex; align-items: center; justify-content: center; gap: 4px; padding: 6px 10px; border-radius: 6px; font-size: 11px; font-weight: 600; cursor: pointer; transition: all 0.2s; text-decoration: none; border: none; white-space: nowrap; }
.action-btn.apply { background: rgba(255,255,255,0.9); color: #003527; border: 1px solid #003527; &:hover:not(.applied) { background: #003527; color: #fff; border-color: #003527; } &.applied { background: #d4edda; color: #155724; cursor: default; border-color: transparent; } }
.action-btn.interview { background: rgba(14,165,233,0.08); color: #0ea5e9; border: 1px solid rgba(14,165,233,0.2); &:hover { background: rgba(14,165,233,0.15); } }
.action-btn.detail { background: #fff; color: #606266; border: 1px solid #dcdfe6; &:hover { border-color: #003527; color: #003527; } }

.empty-state { text-align: center; padding: 60px 20px; color: #909399; p { font-size: 16px; font-weight: 600; margin-bottom: 4px; } span { font-size: 13px; } }

.pagination { display: flex; justify-content: center; gap: 6px; margin-top: 28px; }
.page-btn { min-width: 36px; height: 36px; border-radius: 8px; border: 1px solid #dcdfe6; background: #fff; color: #606266; font-size: 13px; font-weight: 500; cursor: pointer; transition: all 0.2s; &:hover:not(:disabled) { border-color: #003527; color: #003527; } &.active { background: #003527; color: #fff; border-color: #003527; } &:disabled { opacity: 0.4; cursor: default; } }

@media (max-width: 900px) {
  .job-card-inner { flex-direction: column; }
  .job-center { margin-top: 16px; }
  .job-right { width: 100%; flex-direction: row; align-items: center; justify-content: space-between; }
  .job-actions { flex-direction: row; width: auto; }
  .circle-scores { grid-template-columns: repeat(2, 1fr); }
}
@media (max-width: 768px) {
  .page-title { font-size: 28px; }
}
</style>