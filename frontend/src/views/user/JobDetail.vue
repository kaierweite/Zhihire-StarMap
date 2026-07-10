<script setup lang="ts">
import { ref, onMounted } from "vue"
import { useRoute } from "vue-router"
import { ElMessage } from "element-plus"
import {
  ChevronRight, Send, MapPin, Lightbulb, Briefcase, Building2,
  Heart, GraduationCap, Clock, Wifi,
} from "lucide-vue-next"
import type { JobDetail, JobSkillItem } from "@/api/job"
import { getJobDetail, applyJob } from "@/api/job"
import type { GapSkill } from "@/types/graph"
import { getUserGraph } from "@/api/graph"

const route = useRoute()
const jobId = Number(route.params.id) || 1
const jobDetail = ref<JobDetail | null>(null)
const loading = ref(true)
const errorMessage = ref('')
const gapSkills = ref<GapSkill[]>([])
const graphLoaded = ref(false)
const applied = ref(false)

const typeDisplay: Record<string, string> = {
  FULL_TIME: "全职",
  PART_TIME: "兼职",
  INTERN: "实习",
}

const logoColors = [
  "#dbeafe", "#d4edda", "#e8d5f5", "#fff3cd", "#f8d7da",
]

function logoInfo(name: string | null) {
  const first = (name || "?").charAt(0)
  const idx = (name || "").length % logoColors.length
  return { char: first, color: logoColors[idx] }
}

function salaryDisplay(min: number | null, max: number | null): string {
  const minK = min && min > 0 ? Math.round(min / 1000) : null
  const maxK = max && max > 0 ? Math.round(max / 1000) : null
  
  if (minK != null && maxK != null) {
    if (minK === maxK) return `${minK}K`
    return `${minK}-${maxK}K`
  }
  if (minK != null) return `${minK}K起`
  if (maxK != null) return `最高${maxK}K`
  return "面议"
}

function expDisplay(min: number | null): string {
  if (min == null) return "经验不限"
  if (min === 0) return "在校/应届"
  return `${min}年以上`
}

function skillCategories(skills: JobSkillItem[]): string {
  const cats = new Set(skills.map((s) => s.skill_category).filter(Boolean))
  return cats.size ? [...cats].join(" / ") : "-"
}

const benefitIcons = [Heart, Clock, Wifi, GraduationCap, Briefcase, Building2]

async function handleApply() {
  if (applied.value || !jobDetail.value) return
  try {
    const res = await applyJob(jobDetail.value.id)
    applied.value = true
    ElMessage.success("投递成功")
  } catch (err: any) {
    if (err?.response?.data?.code === 409) {
      applied.value = true
      ElMessage.info("已投递过该岗位")
    }
  }
}

onMounted(async () => {
  loading.value = true
  try {
    const res = await getJobDetail(jobId)
    jobDetail.value = res.data.data

    const roleId = res.data.data.occupation_role_id
    if (roleId != null) {
      try {
        const graphRes = await getUserGraph(roleId)
        gapSkills.value = (graphRes.data.data as any).gap_skills || []
      } catch (err: any) {
        // graph may not be ready
      }
    }
  } catch (err: any) {
    errorMessage.value = err?.response?.data?.message || '岗位加载失败，请稍后重试'
  } finally {
    loading.value = false
    graphLoaded.value = true
  }
})
</script>

<template>
  <div class="detail-page">
    <div class="detail-container">
      <div class="breadcrumb animate-up">
        <router-link to="/user/jobs/search">职位搜索</router-link>
        <ChevronRight :size="14" />
        <span>{{ jobDetail?.title || "加载中..." }}</span>
      </div>

      <div v-if="loading" class="loading-state">加载中...</div>
      <template v-else-if="jobDetail">
        <div class="detail-layout">
          <div class="detail-main">
            <section class="card animate-up">
              <div class="job-header">
                <div class="job-logo" :style="{ background: logoInfo(jobDetail.company_name).color }">
                  {{ logoInfo(jobDetail.company_name).char }}
                </div>
                <div>
                  <h1 class="job-name">{{ jobDetail.title }}</h1>
                  <p class="job-company-name">{{ jobDetail.company_name }}</p>
                  <p class="job-location"><MapPin :size="14" /> {{ jobDetail.city || "-" }}</p>
                </div>
              </div>
              <div class="job-tags">
                <span class="tag-primary">{{ typeDisplay[jobDetail.job_type] || jobDetail.job_type }}</span>
                <span class="tag-neutral">{{ expDisplay(jobDetail.experience_min) }}</span>
                <span class="tag-neutral">{{ jobDetail.education_requirement || "学历不限" }}</span>
              </div>
            </section>

            <section class="card animate-up d1">
              <h2 class="section-heading"><Briefcase :size="20" /> 岗位描述</h2>
              <div class="job-desc"><p>{{ jobDetail.description || "暂无岗位描述" }}</p></div>
            </section>

            <section v-if="jobDetail.skills && jobDetail.skills.length" class="card animate-up d2">
              <h2 class="section-heading">
                <GraduationCap :size="20" /> 技能要求
                <small style="font-weight:400;color:#909399;font-size:13px">（{{ skillCategories(jobDetail.skills) }}）</small>
              </h2>
              <div class="skills-grid">
                <span v-for="s in jobDetail.skills" :key="s.skill_id" class="skill-badge">
                  {{ s.skill_name }}
                  <span class="skill-level">{{ s.required_level }}</span>
                </span>
              </div>
            </section>

            <section v-if="jobDetail.benefits && jobDetail.benefits.length" class="card animate-up d3">
              <h2 class="section-heading"><Heart :size="20" /> 福利待遇</h2>
              <div class="benefits-grid">
                <div v-for="(b, i) in jobDetail.benefits" :key="b" class="benefit-item">
                  <component :is="benefitIcons[i % benefitIcons.length]" :size="20" />
                  <span>{{ b }}</span>
                </div>
              </div>
            </section>
          </div>

          <div class="detail-sidebar">
            <div class="sticky-area">
              <section class="card animate-up d1">
                <h2 class="section-heading">能力差距分析</h2>
                <div v-if="gapSkills.length" class="gap-list">
                  <div v-for="g in gapSkills" :key="g.skill_name" class="gap-item">
                    <span class="gap-name">{{ g.skill_name }}</span>
                    <span class="gap-level" :class="g.requirement_level.toLowerCase()">{{ g.requirement_level }}</span>
                  </div>
                </div>
                <div v-else class="gap-empty">
                  <Lightbulb :size="20" />
                  <p v-if="graphLoaded">尚无差距分析数据，请先完善能力图谱</p>
                  <p v-else>加载中...</p>
                </div>
              </section>

              <div class="action-row">
                <button
                  class="apply-btn"
                  :class="{ applied }"
                  :disabled="applied"
                  @click="handleApply"
                >
                  <Send :size="16" /> {{ applied ? "已投递" : "立即投递" }}
                </button>
              </div>

              <section class="card">
                <h2 class="section-heading"><Building2 :size="20" /> 企业信息</h2>
                <div class="company-info-grid">
                  <div class="company-row"><span>企业名称</span><span class="company-val">{{ jobDetail.company_name || "-" }}</span></div>
                  <div v-if="jobDetail.occupation_role_name" class="company-row"><span>岗位方向</span><span class="company-val">{{ jobDetail.occupation_role_name }}</span></div>
                  <div class="company-row"><span>浏览量</span><span class="company-val">{{ jobDetail.views }}</span></div>
                  <div class="company-row"><span>发布时间</span><span class="company-val">{{ jobDetail.created_at?.slice(0, 10) || "-" }}</span></div>
                </div>
              </section>
            </div>
          </div>
        </div>
      </template>
      <div v-else class="loading-state">{{ errorMessage || "岗位加载失败" }}</div>
    </div>
  </div>
</template>

<style scoped lang="scss">
.detail-page { padding: 24px 16px; }
.detail-container { max-width: 1100px; margin: 0 auto; }
@keyframes fadeUp { from { opacity: 0; transform: translateY(20px); } to { opacity: 1; transform: translateY(0); } }
.animate-up { opacity: 0; animation: fadeUp 0.5s cubic-bezier(0.22,1,0.36,1) forwards; }
.d1 { animation-delay: 0.08s; } .d2 { animation-delay: 0.15s; } .d3 { animation-delay: 0.22s; }
.loading-state { text-align: center; padding: 60px; color: #909399; font-size: 15px; }
.breadcrumb { display: flex; align-items: center; gap: 6px; margin-bottom: 20px; font-size: 13px; color: #909399; a { color: #909399; text-decoration: none; &:hover { color: #1a3a5c; } } span:last-child { color: #303133; font-weight: 500; } }
.detail-layout { display: grid; grid-template-columns: 1fr 380px; gap: 24px; }
.card { background: #fff; border-radius: 12px; padding: 24px; border: 1px solid #e5e7eb; margin-bottom: 16px; }
.section-heading { display: flex; align-items: center; gap: 8px; font-size: 18px; font-weight: 600; color: #303133; margin-bottom: 16px; svg { color: #1a3a5c; } }
.job-header { display: flex; align-items: center; gap: 16px; margin-bottom: 16px; }
.job-logo { width: 56px; height: 56px; border-radius: 14px; display: flex; align-items: center; justify-content: center; font-size: 24px; font-weight: 700; flex-shrink: 0; }
.job-name { font-size: 28px; font-weight: 700; color: #303133; letter-spacing: -0.5px; margin-bottom: 4px; }
.job-company-name { font-size: 16px; color: #606266; margin-bottom: 4px; }
.job-location { display: flex; align-items: center; gap: 4px; font-size: 13px; color: #909399; }
.job-tags { display: flex; gap: 8px; flex-wrap: wrap; }
.tag-primary { font-size: 12px; padding: 4px 14px; border-radius: 4px; background: #dbeafe; color: #1e3a8a; font-weight: 600; }
.tag-neutral { font-size: 12px; padding: 4px 14px; border-radius: 4px; background: #f3f4f5; color: #606266; }
.job-desc { p { font-size: 14px; color: #606266; line-height: 1.8; } }
.skills-grid { display: flex; flex-wrap: wrap; gap: 10px; }
.skill-badge { font-size: 14px; padding: 6px 18px; border-radius: 6px; background: #dbeafe; color: #1e3a8a; font-weight: 600; display: inline-flex; align-items: center; gap: 6px; }
.skill-level { font-size: 10px; padding: 1px 6px; border-radius: 3px; background: rgba(30,58,138,0.12); font-weight: 700; }
.benefits-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 10px; }
.benefit-item { display: flex; align-items: center; gap: 10px; padding: 10px 14px; border-radius: 8px; background: #f8f9fa; font-size: 13px; font-weight: 500; color: #303133; svg { color: #1a3a5c; } }
.detail-sidebar .sticky-area { position: sticky; top: 80px; }
.gap-list { display: flex; flex-direction: column; gap: 10px; }
.gap-item { display: flex; align-items: center; justify-content: space-between; padding: 8px 12px; border-radius: 6px; background: #f8f9fa; font-size: 13px; }
.gap-name { font-weight: 600; color: #303133; }
.gap-level { font-size: 11px; padding: 2px 8px; border-radius: 999px; font-weight: 600; &.must { background: #f8d7da; color: #721c24; } &.nice { background: #fff3cd; color: #856404; } &.bonus { background: #d4edda; color: #155724; } }
.gap-empty { display: flex; flex-direction: column; align-items: center; gap: 10px; padding: 20px 0; color: #c0c4cc; svg { color: #c0c4cc; } p { font-size: 13px; text-align: center; line-height: 1.5; } }
.action-row { display: flex; gap: 12px; margin-bottom: 16px; }
.apply-btn { flex: 1; display: flex; align-items: center; justify-content: center; gap: 8px; padding: 12px 0; border-radius: 999px; background: #1a3a5c; color: #fff; font-size: 15px; font-weight: 600; border: none; cursor: pointer; transition: all 0.3s; &:hover:not(:disabled) { background: #24507a; transform: translateY(-1px); } &.applied, &:disabled { background: #d4edda; color: #155724; cursor: default; } }
.company-info-grid { display: flex; flex-direction: column; gap: 12px; }
.company-row { display: flex; justify-content: space-between; font-size: 14px; color: #909399; }
.company-val { color: #303133; font-weight: 500; }
@media (max-width: 900px) { .detail-layout { grid-template-columns: 1fr; } .detail-sidebar { order: -1; } .benefits-grid { grid-template-columns: repeat(2, 1fr); } }
</style>