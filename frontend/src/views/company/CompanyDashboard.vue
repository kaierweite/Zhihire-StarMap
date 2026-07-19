<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { Briefcase, CircleCheck, FileText, Send, Eye, Clock, MapPin, DollarSign, TrendingUp } from 'lucide-vue-next'
import { getCompanyDashboard, type CompanyDashboard, type DashboardJobItem, type DashboardApplicationItem } from '@/api/company'
import { ElMessage } from 'element-plus'
import { useRouter } from 'vue-router'

const router = useRouter()
const dashboard = ref<CompanyDashboard | null>(null)
const loading = ref(true)

const statusLabels: Record<string, string> = {
  OPEN: '招聘中',
  CLOSED: '已关闭',
  DRAFT: '草稿',
}

const statusType: Record<string, string> = {
  OPEN: 'success',
  CLOSED: 'info',
  DRAFT: 'warning',
}

const appStatusLabels: Record<string, string> = {
  APPLIED: '已投递',
  REVIEWING: '筛选中',
  ACCEPTED: '已通过',
  REJECTED: '未通过',
}

const appStatusType: Record<string, string> = {
  APPLIED: 'primary',
  REVIEWING: 'warning',
  ACCEPTED: 'success',
  REJECTED: 'danger',
}

async function loadDashboard() {
  loading.value = true
  try {
    const res = await getCompanyDashboard()
    if (res.data.code === 200 && res.data.data) {
      dashboard.value = res.data.data
    } else {
      ElMessage.error(res.data.message || '加载仪表盘失败')
    }
  } catch {
    ElMessage.error('网络异常，请稍后重试')
  } finally {
    loading.value = false
  }
}

function goTo(path: string) {
  router.push(path)
}

function formatSalary(min: number | null, max: number | null): string {
  const minK = min && min > 0 ? Math.round(min / 1000) : null
  const maxK = max && max > 0 ? Math.round(max / 1000) : null
  
  if (minK != null && maxK != null) {
    if (minK === maxK) return `${minK}K`
    return `${minK}K-${maxK}K`
  }
  if (minK != null) return `${minK}K起`
  if (maxK != null) return `至${maxK}K`
  return '面议'
}

onMounted(loadDashboard)
</script>

<template>
  <div class="dashboard-page">
    <div class="page-header">
      <h1>企业首页</h1>
      <span class="subtitle">企业运营概览</span>
    </div>

    <!-- Stats Cards -->
    <div class="stats-grid" v-if="!loading">
      <div class="stat-card" @click="goTo('/company/jobs')">
        <div class="stat-icon bg-blue"><Briefcase :size="22" /></div>
        <div class="stat-body">
          <span class="stat-value">{{ dashboard?.stats.total_jobs ?? 0 }}</span>
          <span class="stat-label">岗位总数</span>
        </div>
      </div>
      <div class="stat-card" @click="goTo('/company/jobs')">
        <div class="stat-icon bg-green"><TrendingUp :size="22" /></div>
        <div class="stat-body">
          <span class="stat-value">{{ dashboard?.stats.active_jobs ?? 0 }}</span>
          <span class="stat-label">招聘中</span>
        </div>
      </div>
      <div class="stat-card" @click="goTo('/company/notifications')">
        <div class="stat-icon bg-orange"><FileText :size="22" /></div>
        <div class="stat-body">
          <span class="stat-value">{{ dashboard?.stats.total_applications ?? 0 }}</span>
          <span class="stat-label">收到投递</span>
        </div>
      </div>
    </div>
    <div v-else class="loading-hint">加载中...</div>

    <!-- Recent Jobs -->
    <div class="section">
      <div class="section-header">
        <h2>最近岗位</h2>
        <el-button text type="primary" @click="goTo('/company/jobs')">查看全部</el-button>
      </div>
      <el-table v-if="dashboard?.recent_jobs.length" :data="dashboard.recent_jobs" stripe style="width: 100%">
        <el-table-column prop="title" label="岗位名称" min-width="160" />
        <el-table-column label="城市" width="100">
          <template #default="{ row }: { row: DashboardJobItem }">
            <span v-if="row.city"><MapPin :size="14" /> {{ row.city }}</span>
            <span v-else class="muted">不限</span>
          </template>
        </el-table-column>
        <el-table-column label="薪资" width="140">
          <template #default="{ row }: { row: DashboardJobItem }">
            {{ formatSalary(row.salary_min, row.salary_max) }}
          </template>
        </el-table-column>
        <el-table-column label="状态" width="100">
          <template #default="{ row }: { row: DashboardJobItem }">
            <el-tag :type="statusType[row.status] || 'info'" size="small">
              {{ statusLabels[row.status] || row.status }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="views" label="浏览" width="70" />
        <el-table-column label="发布时间" width="160">
          <template #default="{ row }: { row: DashboardJobItem }">
            <Clock :size="12" /> {{ row.created_at.slice(0, 10) }}
          </template>
        </el-table-column>
      </el-table>
      <el-empty v-else-if="!loading" description="暂无岗位数据" :image-size="80" />
    </div>

    <!-- Recent Applications -->
    <div class="section">
      <div class="section-header">
        <h2>最近投递</h2>
        <el-button text type="primary" @click="goTo('/company/notifications')">查看全部</el-button>
      </div>
      <el-table v-if="dashboard?.recent_applications.length" :data="dashboard.recent_applications" stripe style="width: 100%">
        <el-table-column label="候选人" width="120">
          <template #default="{ row }: { row: DashboardApplicationItem }">
            <span v-if="row.applicant_name">{{ row.applicant_name }}</span>
            <span v-else class="muted">匿名</span>
          </template>
        </el-table-column>
        <el-table-column label="岗位" min-width="160">
          <template #default="{ row }: { row: DashboardApplicationItem }">
            <span v-if="row.job_title">{{ row.job_title }}</span>
            <span v-else class="muted">岗位#{{ row.job_id }}</span>
          </template>
        </el-table-column>
        <el-table-column label="状态" width="100">
          <template #default="{ row }: { row: DashboardApplicationItem }">
            <el-tag :type="appStatusType[row.status] || 'info'" size="small">
              {{ appStatusLabels[row.status] || row.status }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="投递时间" width="160">
          <template #default="{ row }: { row: DashboardApplicationItem }">
            <Clock :size="12" /> {{ row.created_at.slice(0, 10) }}
          </template>
        </el-table-column>
      </el-table>
      <el-empty v-else-if="!loading" description="暂无投递记录" :image-size="80" />
    </div>
  </div>
</template>

<style scoped lang="scss">
.dashboard-page {
  max-width: 1000px;
  margin: 0 auto;
}
.page-header {
  display: flex;
  align-items: baseline;
  gap: 12px;
  margin-bottom: 24px;
  h1 { font-size: 28px; font-weight: 700; color: #121c28; margin: 0; }
  .subtitle { font-size: 14px; color: #404944; }
}
.loading-hint {
  text-align: center; padding: 40px; color: #404944; font-size: 14px;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16px;
  margin-bottom: 28px;
}
.stat-card {
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 20px;
  background: #fff;
  border-radius: 12px;
  border: 1px solid #bfc9c3;
  cursor: pointer;
  transition: all 0.2s;
  &:hover { box-shadow: 0 4px 16px rgba(0,0,0,0.04); border-color: #003527; }
}
.stat-icon {
  width: 48px; height: 48px; border-radius: 12px;
  display: flex; align-items: center; justify-content: center;
  flex-shrink: 0; color: #fff;
  &.bg-blue { background: #003527; }
  &.bg-green { background: #2d7d46; }
  &.bg-orange { background: #d97706; }
}
.stat-body {
  display: flex; flex-direction: column;
}
.stat-value {
  font-size: 28px; font-weight: 700; color: #121c28; line-height: 1.2;
}
.stat-label {
  font-size: 13px; color: #404944;
}

.section {
  margin-bottom: 28px;
}
.section-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 12px;
  h2 { font-size: 18px; font-weight: 600; color: #121c28; margin: 0; }
}
.muted { color: #bfc9c3; font-style: italic; }
</style>