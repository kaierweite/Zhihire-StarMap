<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { FileText, Search, Clock, User, Activity } from 'lucide-vue-next'
import { listOperationLogs } from '@/api/admin'
import type { LogItem } from '@/types/admin'

const activeTab = ref<'operation' | 'login'>('operation')
const keyword = ref('')
const logs = ref<LogItem[]>([])
const page = ref(1)
const size = ref(20)
const total = ref(0)
const loading = ref(false)

async function fetchLogs() {
  loading.value = true
  try {
    const logType = activeTab.value === 'operation' ? 'operation' : 'login'
    const res = await listOperationLogs(logType, keyword.value || undefined, page.value, size.value)
    const data = res.data.data
    logs.value = data.records
    total.value = data.total
  } catch {
    // handled by interceptor
  } finally {
    loading.value = false
  }
}

function onSearch() {
  page.value = 1
  fetchLogs()
}

function formatDetail(detail: Record<string, unknown> | null): string {
  if (!detail) return '-'
  if (typeof detail === 'string') return detail
  try {
    return JSON.stringify(detail)
  } catch {
    return '-'
  }
}

function formatTime(t: string | null): string {
  if (!t) return '-'
  // Keep full ISO timestamp from backend
  return t
}

function actionTagClass(action: string | null): string {
  if (!action) return 'ok'
  if (action.includes('失败')) return 'fail'
  if (action.includes('封禁')) return 'ban'
  return 'ok'
}

onMounted(fetchLogs)
</script>

<template>
  <div class="page">
    <h1 class="page-title fade-up">系统日志</h1>
    <p class="page-desc fade-up d1">操作日志与登录日志查询</p>

    <div class="tabs fade-up d2">
      <button class="tab" :class="{ active: activeTab === 'operation' }" @click="activeTab = 'operation'; onSearch()"><Activity :size="15" /> 操作日志</button>
      <button class="tab" :class="{ active: activeTab === 'login' }" @click="activeTab = 'login'; onSearch()"><User :size="15" /> 登录日志</button>
    </div>

    <div class="filter-bar fade-up d2">
      <div class="search-box"><Search :size="16" /><input v-model="keyword" placeholder="搜索用户ID / 操作 / 模块..." @keyup.enter="onSearch" /></div>
      <span class="count">共<strong>{{ total }}</strong> 条记录</span>
    </div>

    <div class="log-table fade-up d3">
      <div class="th"><span class="c-user">用户ID</span><span class="c-action">操作</span><span class="c-detail">详情</span><span class="c-ip">IP</span><span class="c-time">时间</span></div>
      <div v-for="l in logs" :key="l.id" class="tr">
        <span class="c-user">{{ l.user_id }}</span>
        <span class="c-action"><span class="action-tag" :class="actionTagClass(l.action)">{{ l.action || '-' }}</span></span>
        <span class="c-detail">{{ l.module ? '[' + l.module + '] ' : '' }}{{ formatDetail(l.detail) }}</span>
        <span class="c-ip">{{ l.ip || '-' }}</span>
        <span class="c-time"><Clock :size="12" /> {{ formatTime(l.created_at) }}</span>
      </div>
    </div>

    <div class="pagination-wrap fade-up d3">
      <el-pagination
        v-model:current-page="page"
        v-model:page-size="size"
        :total="total"
        :page-sizes="[10, 20, 50]"
        layout="total, sizes, prev, pager, next"
        background
        @current-change="fetchLogs"
        @size-change="fetchLogs"
      />
    </div>
  </div>
</template>

<style scoped lang="scss">
.page { max-width: 1000px; margin: 0 auto; }
@keyframes fadeUp { from { opacity: 0; transform: translateY(20px); } to { opacity: 1; transform: translateY(0); } }
.fade-up { opacity: 0; animation: fadeUp 0.5s cubic-bezier(0.22,1,0.36,1) forwards; }
.d1 { animation-delay: 0.08s; } .d2 { animation-delay: 0.15s; } .d3 { animation-delay: 0.22s; }
.page-title { font-size: 28px; font-weight: 700; color: #121c28; margin-bottom: 4px; }
.page-desc { font-size: 14px; color: #404944; margin-bottom: 20px; }

.tabs { display: flex; gap: 0; border-bottom: 1px solid #bfc9c3; margin-bottom: 16px; }
.tab { display: flex; align-items: center; gap: 6px; padding: 10px 20px; font-size: 14px; font-weight: 500; color: #404944; background: none; border: none; border-bottom: 2px solid transparent; cursor: pointer; &:hover { color: #003527; } &.active { color: #003527; font-weight: 700; border-bottom-color: #003527; } }

.filter-bar { display: flex; gap: 8px; align-items: center; margin-bottom: 16px; }
.search-box { flex: 1; display: flex; align-items: center; gap: 8px; padding: 8px 12px; border: 1px solid #bfc9c3; border-radius: 8px; background: #fff; input { flex: 1; border: none; outline: none; font-size: 13px; } svg { color: #404944; } &:focus-within { border-color: #003527; } }
.count { font-size: 13px; color: #404944; white-space: nowrap; }

.log-table { background: #fff; border-radius: 12px; border: 1px solid #bfc9c3; overflow: hidden; }
.th, .tr { display: flex; align-items: center; padding: 10px 16px; font-size: 13px; }
.th { background: #f8f9fa; font-weight: 600; color: #404944; border-bottom: 1px solid #bfc9c3; }
.tr { border-bottom: 1px solid #f0f0f0; color: #404944; transition: background 0.2s; &:hover { background: #f8f9fa; } &:last-child { border-bottom: none; } }
.c-user { flex: 1; font-weight: 500; color: #121c28; }
.c-action { flex: 1; }
.c-detail { flex: 2; font-size: 12px; }
.c-ip { flex: 1; font-family: monospace; font-size: 12px; color: #404944; }
.c-time { flex: 1.2; display: flex; align-items: center; gap: 4px; font-size: 12px; color: #bfc9c3; }

.action-tag { font-size: 11px; padding: 2px 10px; border-radius: 4px; font-weight: 600; &.ok { background: #d4edda; color: #155724; } &.fail { background: #f8d7da; color: #721c24; } &.ban { background: #fff3cd; color: #856404; } }

.pagination-wrap { display: flex; justify-content: center; margin-top: 16px; }

@media (max-width: 768px) { .log-table { overflow-x: auto; } .th, .tr { min-width: 700px; } }
</style>
