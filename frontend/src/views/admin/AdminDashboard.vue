<script setup lang="ts">
import { ref, onMounted, type Component } from 'vue'
import { Users, Briefcase, Building2, TrendingUp, FileText, Send } from 'lucide-vue-next'
import { getAdminStat } from '@/api/admin'
import type { AdminStat } from '@/types/admin'

interface StatCard {
  label: string
  value: string
  icon: Component
  color: string
}

const stats = ref<StatCard[]>([])

async function fetchStat() {
  try {
    const res = await getAdminStat()
    const data: AdminStat = res.data.data
    stats.value = [
      { label: '注册用户', value: data.user_count.toLocaleString(), icon: Users, color: '#064e3b' },
      { label: '注册企业', value: data.company_count.toLocaleString(), icon: Building2, color: '#8b5cf6' },
      { label: '发布岗位', value: data.job_count.toLocaleString(), icon: Briefcase, color: '#198754' },
      { label: '智能匹配', value: data.match_count.toLocaleString(), icon: TrendingUp, color: '#f59e0b' },
      { label: '简历解析', value: data.parse_count.toLocaleString(), icon: FileText, color: '#6366f1' },
      { label: '投递申请', value: data.application_count.toLocaleString(), icon: Send, color: '#ec4899' },
    ]
  } catch {
    // Error handling handled by request interceptor
  }
}

onMounted(() => {
  fetchStat()
})
</script>

<template>
  <div class="dashboard">
    <h1 class="page-title fade-up">管理员仪表盘</h1>
    <p class="page-desc fade-up d1">系统运行概况与数据统计</p>

    <div class="stat-grid fade-up d2">
      <div v-for="s in stats" :key="s.label" class="stat-card">
        <div class="stat-icon" :style="{ background: s.color + '15', color: s.color }"><component :is="s.icon" :size="22" /></div>
        <div class="stat-info"><div class="stat-val">{{ s.value }}</div><div class="stat-label">{{ s.label }}</div></div>
      </div>
    </div>
  </div>
</template>

<style scoped lang="scss">
@keyframes fadeUp { from { opacity: 0; transform: translateY(20px); } to { opacity: 1; transform: translateY(0); } }
.fade-up { opacity: 0; animation: fadeUp 0.5s cubic-bezier(0.22,1,0.36,1) forwards; }
.d1 { animation-delay: 0.08s; } .d2 { animation-delay: 0.15s; }
.page-title { font-size: 28px; font-weight: 700; color: #121c28; margin-bottom: 4px; }
.page-desc { font-size: 14px; color: #404944; margin-bottom: 24px; }

.stat-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 14px; margin-bottom: 20px; }
.stat-card { display: flex; align-items: center; gap: 14px; padding: 18px; background: #fff; border-radius: 12px; border: 1px solid #bfc9c3; position: relative; }
.stat-icon { width: 48px; height: 48px; border-radius: 12px; display: flex; align-items: center; justify-content: center; flex-shrink: 0; }
.stat-info { flex: 1; }
.stat-val { font-size: 24px; font-weight: 700; color: #121c28; line-height: 1; }
.stat-label { font-size: 13px; color: #404944; margin-top: 4px; }

@media (max-width: 768px) { .stat-grid { grid-template-columns: repeat(2, 1fr); } }
</style>
