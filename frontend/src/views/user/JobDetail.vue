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
import { getUserGraph, getJobGraph } from "@/api/graph"
import AbilityGapChart from "@/components/match/AbilityGapChart.vue"

const route = useRoute()
const jobId = Number(route.params.id) || 1
const jobDetail = ref<JobDetail | null>(null)
const loading = ref(true)
const errorMessage = ref('')
const gapSkills = ref<GapSkill[]>([])
const graphLoaded = ref(false)
const applied = ref(false)
const showGapChart = ref(false)

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
              
              <div class="company-info-bar">
                <div class="company-info-item"><Building2 :size="14" /> {{ jobDetail.company_name }}</div>
                <div class="company-info-item"><Eye :size="14" /> {{ jobDetail.views }} 浏览</div>
                <div class="company-info-item"><Calendar :size="14" /> {{ jobDetail.created_at?.slice(0, 10) || "-" }}</div>
              </div>
            </section>

            <section class="card animate-up d1">
              <h2 class="section-heading"><Briefcase :size="20" /> 岗位描述</h2>
              <div class="job-desc"><p>{{ jobDetail.description || "暂无岗位描述" }}</p></div>
              
              <div class="gap-analysis">
                <h3 class="gap-heading">能力差距分析</h3>
                <div v-if="gapSkills.length" class="gap-list">
                  <div v-for="g in gapSkills" :key="g.skill_name" class="gap-item">
                    <span class="gap-name">{{ g.skill_name }}</span>
                    <span class="gap-level" :class="g.requirement_level.toLowerCase()">{{ g.requirement_level }}</span>
                  </div>
                </div>
                <div v-else class="gap-empty">
                  <Lightbulb :size="16" />
                  <p v-if="graphLoaded">尚无差距分析数据，请先完善能力图谱</p>
                  <p v-else>加载中...</p>
                </div>
                
                <div class="gap-chart-wrapper">
                  <AbilityGapChart :visible="graphLoaded" :job-id="jobId" />
                </div>
              </div>
            </section>

            <section v-if="jobDetail.skills && jobDetail.skills.length" class="card animate-up d2">
              <h2 class="section-heading">
                <GraduationCap :size="20" /> 技能要求
                <small style="font-weight:400;color:#404944;font-size:13px">（{{ skillCategories(jobDetail.skills) }}）</small>
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
        </div>

        <div class="fixed-footer">
          <button
            class="apply-btn"
            :class="{ applied }"
            :disabled="applied"
            @click="handleApply"
          >
            <Send :size="16" /> {{ applied ? "已投递" : "立即投递" }}
          </button>
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
.loading-state { text-align: center; padding: 60px; color: #404944; font-size: 15px; }
.breadcrumb { display: flex; align-items: center; gap: 6px; margin-bottom: 20px; font-size: 13px; color: #404944; a { color: #404944; text-decoration: none; &:hover { color: #003527; } } span:last-child { color: #121c28; font-weight: 500; } }
.detail-layout { display: flex; justify-content: center; }
.detail-main { width: 100%; max-width: 800px; }
.card { background: #fff; border-radius: 12px; padding: 24px; border: 1px solid #bfc9c3; margin-bottom: 16px; }
.section-heading { display: flex; align-items: center; gap: 8px; font-size: 18px; font-weight: 600; color: #121c28; margin-bottom: 16px; svg { color: #003527; } }
.job-header { display: flex; align-items: center; gap: 16px; margin-bottom: 16px; }
.job-logo { width: 56px; height: 56px; border-radius: 14px; display: flex; align-items: center; justify-content: center; font-size: 24px; font-weight: 700; flex-shrink: 0; }
.job-name { font-size: 28px; font-weight: 700; color: #121c28; letter-spacing: -0.5px; margin-bottom: 4px; }
.job-company-name { font-size: 16px; color: #404944; margin-bottom: 4px; }
.job-location { display: flex; align-items: center; gap: 4px; font-size: 13px; color: #404944; }
.job-tags { display: flex; gap: 8px; flex-wrap: wrap; margin-bottom: 16px; }
.tag-primary { font-size: 12px; padding: 4px 14px; border-radius: 4px; background: #003527; color: #fff; font-weight: 600; }
.tag-neutral { font-size: 12px; padding: 4px 14px; border-radius: 4px; background: #f3f4f5; color: #404944; }
.company-info-bar { display: flex; gap: 20px; padding-top: 16px; border-top: 1px solid #e8e8e8; }
.company-info-item { display: flex; align-items: center; gap: 6px; font-size: 13px; color: #404944; svg { color: #003527; } }
.job-desc { p { font-size: 14px; color: #404944; line-height: 1.8; } }
.gap-analysis { margin-top: 20px; padding-top: 20px; border-top: 1px solid #e8e8e8; }
.gap-heading { font-size: 15px; font-weight: 600; color: #121c28; display: flex; align-items: center; gap: 8px; margin-bottom: 12px; }
.gap-analysis .gap-list { display: flex; flex-wrap: wrap; gap: 8px; }
.gap-analysis .gap-item { display: inline-flex; align-items: center; gap: 6px; padding: 6px 12px; border-radius: 6px; background: #f8f9fa; font-size: 13px; }
.gap-analysis .gap-name { font-weight: 600; color: #121c28; }
.gap-analysis .gap-level { font-size: 10px; padding: 1px 6px; border-radius: 999px; font-weight: 600; &.must { background: #f8d7da; color: #721c24; } &.nice { background: #fff3cd; color: #856404; } &.bonus { background: #d4edda; color: #155724; } }
.gap-analysis .gap-empty { display: flex; align-items: center; gap: 8px; padding: 12px 0; color: #bfc9c3; svg { color: #bfc9c3; } p { font-size: 13px; margin: 0; } }
.gap-chart-wrapper { margin-top: 16px; }
.skills-grid { display: flex; flex-wrap: wrap; gap: 10px; }
.skill-badge { font-size: 14px; padding: 6px 18px; border-radius: 6px; background: #003527; color: #fff; font-weight: 600; display: inline-flex; align-items: center; gap: 6px; }
.skill-level { font-size: 10px; padding: 1px 6px; border-radius: 3px; background: rgba(30,58,138,0.12); font-weight: 700; }
.benefits-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 10px; }
.benefit-item { display: flex; align-items: center; gap: 10px; padding: 10px 14px; border-radius: 8px; background: #f8f9fa; font-size: 13px; font-weight: 500; color: #121c28; svg { color: #003527; } }
.gap-list { display: flex; flex-direction: column; gap: 10px; }
.gap-item { display: flex; align-items: center; justify-content: space-between; padding: 8px 12px; border-radius: 6px; background: #f8f9fa; font-size: 13px; }
.gap-name { font-weight: 600; color: #121c28; }
.gap-level { font-size: 11px; padding: 2px 8px; border-radius: 999px; font-weight: 600; &.must { background: #f8d7da; color: #721c24; } &.nice { background: #fff3cd; color: #856404; } &.bonus { background: #d4edda; color: #155724; } }
.gap-empty { display: flex; flex-direction: column; align-items: center; gap: 10px; padding: 20px 0; color: #bfc9c3; svg { color: #bfc9c3; } p { font-size: 13px; text-align: center; line-height: 1.5; } }
.apply-btn { width: 100%; max-width: 800px; display: flex; align-items: center; justify-content: center; gap: 8px; padding: 14px 0; border-radius: 999px; background: #003527; color: #fff; font-size: 15px; font-weight: 600; border: none; cursor: pointer; transition: all 0.3s; &:hover:not(:disabled) { background: #064e3b; box-shadow: 0 4px 12px rgba(0, 53, 39, 0.3); } &.applied, &:disabled { background: #d4edda; color: #155724; cursor: default; } }
.fixed-footer { position: fixed; bottom: 0; left: 0; right: 0; padding: 12px 24px; background: rgba(255, 255, 255, 0.95); backdrop-filter: blur(10px); border-top: 1px solid #e8e8e8; display: flex; justify-content: center; z-index: 100; }
.detail-page { padding-bottom: 80px; }
@media (max-width: 900px) { .benefits-grid { grid-template-columns: repeat(2, 1fr); } .company-info-bar { flex-wrap: wrap; } }
</style>