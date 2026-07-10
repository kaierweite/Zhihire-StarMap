<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { User, BarChart3, FileText, Compass, Briefcase, Loader2, ChevronRight } from 'lucide-vue-next'
import { getProfile } from '@/api/user'
import { getUserGraph } from '@/api/graph'
import { listResumes } from '@/api/resume'
import { getCareerPlan } from '@/api/career'
import type { UserProfileData } from '@/api/user'
import type { UserGraphResult } from '@/types/graph'
import type { CareerPlanData } from '@/api/career'

const loading = ref(true)
const profile = ref<UserProfileData | null>(null)
const graph = ref<UserGraphResult | null>(null)
const resumeCount = ref(0)
const plan = ref<CareerPlanData | null>(null)
const hasPlan = ref(false)

onMounted(async () => {
  try {
    const [profileRes, graphRes, resumeRes, planRes] = await Promise.allSettled([
      getProfile(), getUserGraph(), listResumes(1, 1), getCareerPlan(),
    ])
    if (profileRes.status === 'fulfilled') profile.value = profileRes.value.data.data
    if (graphRes.status === 'fulfilled') graph.value = graphRes.value.data.data
    if (resumeRes.status === 'fulfilled') resumeCount.value = resumeRes.value.data.data.total
    if (planRes.status === 'fulfilled') {
      const d = planRes.value.data.data
      if (d) { plan.value = d; hasPlan.value = true }
    }
  } catch {} finally { loading.value = false }
})

const skillCount = () => graph.value?.nodes.length ?? 0
</script>

<template>
  <div class="social-page">
    <div class="social-container">
      <h1 class="page-title">个人概览</h1>

      <div v-if="loading" class="loading-state"><Loader2 :size="28" class="spin" /> <p>加载中...</p></div>

      <template v-else>
        <!-- Profile Card -->
        <div class="card profile-card" v-if="profile">
          <div class="avatar-circle">{{ profile.real_name?.charAt(0) || profile.username.charAt(0).toUpperCase() }}</div>
          <div class="profile-info">
            <h2 class="profile-name">{{ profile.real_name || profile.username }}</h2>
            <p class="profile-bio">{{ profile.bio || '暂无个人简介' }}</p>
            <div class="profile-tags">
              <span v-if="profile.education" class="tag">{{ profile.education }}</span>
              <span v-if="profile.school" class="tag">{{ profile.school }}</span>
              <span v-if="profile.current_city" class="tag">{{ profile.current_city }}</span>
              <span v-if="profile.work_years" class="tag">{{ profile.work_years }}年经验</span>
            </div>
          </div>
        </div>

        <!-- Stats Grid -->
        <div class="stats-grid">
          <router-link to="/user/resume" class="stat-card">
            <FileText :size="22" class="stat-icon resume" />
            <div><div class="stat-num">{{ resumeCount }}</div><div class="stat-label">简历</div></div>
            <ChevronRight :size="16" class="stat-arrow" />
          </router-link>
          <router-link to="/user/resume" class="stat-card">
            <BarChart3 :size="22" class="stat-icon graph" />
            <div><div class="stat-num">{{ skillCount() }}</div><div class="stat-label">技能</div></div>
            <ChevronRight :size="16" class="stat-arrow" />
          </router-link>
          <router-link to="/user/career-plan" class="stat-card">
            <Compass :size="22" class="stat-icon plan" />
            <div>
              <div class="stat-num" :class="hasPlan ? '' : 'muted'">{{ hasPlan ? plan!.score : '--' }}</div>
              <div class="stat-label">{{ hasPlan ? '匹配度' : '暂无规划' }}</div>
            </div>
            <ChevronRight :size="16" class="stat-arrow" />
          </router-link>
          <router-link to="/user/jobs" class="stat-card">
            <Briefcase :size="22" class="stat-icon job" />
            <div><div class="stat-num">{{ profile?.expected_salary_min || '--' }}</div><div class="stat-label">期望薪资</div></div>
            <ChevronRight :size="16" class="stat-arrow" />
          </router-link>
        </div>

        <!-- Quick Links -->
        <div class="quick-links">
          <h3 class="section-title"><Compass :size="18" /> 快捷入口</h3>
          <div class="link-grid">
            <router-link to="/user/resume" class="link-item"><FileText :size="18" /> 简历中心</router-link>
            <router-link to="/user/resume/optimize" class="link-item"><FileText :size="18" /> AI 优化简历</router-link>
            <router-link to="/user/career-plan" class="link-item"><Compass :size="18" /> 职业规划</router-link>
            <router-link to="/user/interview" class="link-item"><Briefcase :size="18" /> 模拟面试</router-link>
            <router-link to="/user/jobs" class="link-item"><Briefcase :size="18" /> 职位推荐</router-link>
            <router-link to="/user/notifications" class="link-item"><User :size="18" /> 通知中心</router-link>
          </div>
        </div>

        <!-- Career Plan Summary -->
        <div v-if="hasPlan && plan" class="card plan-card">
          <h3 class="section-title"><Compass :size="18" /> 职业规划摘要</h3>
          <div class="plan-target">
            <Briefcase :size="16" /> 目标：<strong>{{ plan.target_role }}</strong>
            <span class="plan-score" :style="{ color: plan.score >= 80 ? '#198754' : plan.score >= 60 ? '#1a3a5c' : '#e67e22' }">{{ plan.score }}%</span>
          </div>
          <p class="plan-rationale">{{ plan.rationale?.slice(0, 120) }}...</p>
          <router-link to="/user/career-plan" class="plan-link">查看完整规划 <ChevronRight :size="14" /></router-link>
        </div>
      </template>
    </div>
  </div>
</template>

<style scoped lang="scss">
.social-page { padding: 24px 16px; }
.social-container { max-width: 800px; margin: 0 auto; }
.page-title { font-size: 24px; font-weight: 700; color: #303133; margin-bottom: 20px; }

.loading-state { display: flex; flex-direction: column; align-items: center; gap: 12px; padding: 80px 0; color: #909399; }
@keyframes spin { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }
.spin { animation: spin 1s linear infinite; color: #1a3a5c; }

.card { background: #fff; border-radius: 12px; border: 1px solid #e5e7eb; padding: 20px 24px; margin-bottom: 16px; }

/* Profile Card */
.profile-card { display: flex; align-items: center; gap: 20px; }
.avatar-circle { width: 56px; height: 56px; border-radius: 50%; background: linear-gradient(135deg, #1a3a5c, #0ea5e9); color: #fff; display: flex; align-items: center; justify-content: center; font-size: 22px; font-weight: 700; flex-shrink: 0; }
.profile-info { flex: 1; min-width: 0; }
.profile-name { font-size: 20px; font-weight: 700; color: #303133; margin: 0 0 2px; }
.profile-bio { font-size: 13px; color: #909399; margin: 0 0 8px; }
.profile-tags { display: flex; flex-wrap: wrap; gap: 4px; }
.tag { font-size: 11px; padding: 2px 8px; border-radius: 4px; background: #f0f2f5; color: #606266; }

/* Stats Grid */
.stats-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; margin-bottom: 16px; }
.stat-card { display: flex; align-items: center; gap: 12px; background: #fff; border-radius: 12px; border: 1px solid #e5e7eb; padding: 16px 18px; text-decoration: none; transition: all .2s; &:hover { border-color: #1a3a5c; transform: translateY(-1px); } }
.stat-icon { flex-shrink: 0; }
.stat-icon.resume { color: #1a3a5c; }
.stat-icon.graph { color: #0ea5e9; }
.stat-icon.plan { color: #f59e0b; }
.stat-icon.job { color: #10b981; }
.stat-num { font-size: 22px; font-weight: 700; color: #303133; }
.stat-num.muted { color: #c0c4cc; }
.stat-label { font-size: 12px; color: #909399; }
.stat-arrow { margin-left: auto; color: #c0c4cc; }

/* Quick Links */
.quick-links { margin-bottom: 16px; }
.section-title { display: flex; align-items: center; gap: 6px; font-size: 15px; font-weight: 600; color: #303133; margin: 0 0 12px; }
.link-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 8px; }
.link-item { display: flex; align-items: center; gap: 8px; padding: 10px 14px; border-radius: 8px; background: #fff; border: 1px solid #e5e7eb; font-size: 13px; color: #606266; text-decoration: none; transition: all .2s; &:hover { border-color: #1a3a5c; color: #1a3a5c; } }

/* Plan Card */
.plan-card { }
.plan-target { display: flex; align-items: center; gap: 8px; font-size: 14px; color: #303133; margin-bottom: 8px; }
.plan-score { margin-left: auto; font-weight: 700; font-size: 18px; }
.plan-rationale { font-size: 13px; color: #606266; line-height: 1.6; margin: 0 0 10px; }
.plan-link { display: inline-flex; align-items: center; gap: 4px; font-size: 13px; color: #1a3a5c; font-weight: 600; text-decoration: none; &:hover { text-decoration: underline; } }

@media (max-width: 640px) {
  .stats-grid, .link-grid { grid-template-columns: 1fr; }
  .profile-card { flex-direction: column; text-align: center; }
}
</style>