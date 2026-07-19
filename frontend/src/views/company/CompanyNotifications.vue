<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from "vue"
import { Bell, CheckCircle, Send, Calendar, Sparkles, Clock } from "lucide-vue-next"
import type { NotificationItem } from "@/types/notification"
import { NOTIFICATION_TYPE_LABELS } from "@/types/notification"
import {
  listNotifications,
  getUnreadCount,
  markRead as markReadApi,
  markAllRead as markAllReadApi,
} from "@/api/notification"
import Pagination from "@/components/common/Pagination.vue"

// ---- State ----
const records = ref<NotificationItem[]>([])
const total = ref(0)
const page = ref(1)
const pageSize = ref(20)
const loading = ref(false)
const unreadCount = ref(0)
const activeFilter = ref<string>("all")

// ---- Type icon/color mapping ----
const typeMeta: Record<string, { icon: any; iconColor: string; tagClass: string }> = {
  APPLICATION: { icon: Send, iconColor: "#d4edda", tagClass: "tag-application" },
  INTERVIEW_INVITE: { icon: Calendar, iconColor: "#dbeafe", tagClass: "tag-interview" },
  SYSTEM: { icon: Sparkles, iconColor: "#e8d5f5", tagClass: "tag-system" },
}

// ---- API calls ----
async function fetchNotifications() {
  loading.value = true
  try {
    const res = await listNotifications(page.value, pageSize.value)
    const d = res.data.data
    records.value = d.records
    total.value = d.total
  } catch {
    records.value = []
    total.value = 0
  } finally {
    loading.value = false
  }
}

async function fetchUnreadCount() {
  try {
    const res = await getUnreadCount()
    unreadCount.value = res.data.data.count
  } catch {
    unreadCount.value = 0
  }
}

async function handleMarkRead(id: number) {
  try {
    await markReadApi(id)
    const n = records.value.find((r) => r.id === id)
    if (n) {
      n.is_read = true
      unreadCount.value = Math.max(0, unreadCount.value - 1)
    }
  } catch {
    // silent
  }
}

async function handleMarkAllRead() {
  try {
    await markAllReadApi()
    records.value.forEach((r) => {
      r.is_read = true
    })
    unreadCount.value = 0
  } catch {
    // silent
  }
}

function onPageChange(p: number) {
  page.value = p
  fetchNotifications()
}

// ---- Relative time ----
function relativeTime(iso: string): string {
  const diff = Date.now() - new Date(iso).getTime()
  const minutes = Math.floor(diff / 60000)
  if (minutes < 1) return "刚刚"
  if (minutes < 60) return `${minutes}分钟前`
  const hours = Math.floor(minutes / 60)
  if (hours < 24) return `${hours}小时前`
  const days = Math.floor(hours / 24)
  if (days < 30) return `${days}天前`
  const months = Math.floor(days / 30)
  return `${months}个月前`
}

// ---- Filter tabs ----
const filterTabs = [
  { key: "all", label: "全部" },
  { key: "APPLICATION", label: "投递相关" },
  { key: "INTERVIEW_INVITE", label: "面试邀请" },
  { key: "SYSTEM", label: "系统通知" },
]

const filtered = computed(() => {
  if (activeFilter.value === "all") return records.value
  return records.value.filter((n) => n.type === activeFilter.value)
})

function switchFilter(key: string) {
  activeFilter.value = key
}

// ---- Polling ----
let pollTimer: ReturnType<typeof setInterval> | null = null

onMounted(() => {
  fetchNotifications()
  fetchUnreadCount()
  pollTimer = setInterval(fetchUnreadCount, 30000)
})

onUnmounted(() => {
  if (pollTimer) clearInterval(pollTimer)
})
</script>

<template>
  <div class="notif-page">
    <div class="notif-container">
      <!-- 标题 -->
      <div class="page-header">
        <div class="header-left">
          <h1 class="page-title">通知中心</h1>
          <span v-if="unreadCount" class="unread-badge">{{ unreadCount }}</span>
        </div>
        <button class="mark-btn" @click="handleMarkAllRead"><CheckCircle :size="16" /> 全部标记为已读</button>
      </div>

      <!-- 筛选 Tab -->
      <div class="filter-tabs">
        <button
          v-for="tab in filterTabs"
          :key="tab.key"
          class="filter-tab"
          :class="{ active: activeFilter === tab.key }"
          @click="switchFilter(tab.key)"
        >
          {{ tab.label }}
        </button>
      </div>

      <!-- Loading -->
      <div v-if="loading" class="loading-state">
        <span class="loader-text">加载中...</span>
      </div>

      <!-- 通知列表 -->
      <div v-else class="notif-list">
        <div
          v-for="n in filtered"
          :key="n.id"
          class="notif-card"
          :class="{ unread: !n.is_read }"
          @click="handleMarkRead(n.id)"
        >
          <div class="notif-icon" :style="{ background: typeMeta[n.type]?.iconColor || '#f3f4f5' }">
            <component :is="typeMeta[n.type]?.icon || Bell" :size="20" />
          </div>
          <div class="notif-body">
            <div class="notif-title-row">
              <h3>{{ n.title }}</h3>
              <span v-if="!n.is_read" class="unread-dot" />
            </div>
            <p class="notif-content">{{ n.content }}</p>
            <div class="notif-footer">
              <span class="notif-time"><Clock :size="13" /> {{ relativeTime(n.created_at) }}</span>
              <span class="notif-tag" :class="typeMeta[n.type]?.tagClass || 'tag-system'">
                {{ NOTIFICATION_TYPE_LABELS[n.type] || n.type }}
              </span>
            </div>
          </div>
        </div>

        <!-- 空态 -->
        <div v-if="filtered.length === 0" class="empty-state">
          <Bell :size="48" class="empty-icon" />
          <p>暂无通知</p>
        </div>
      </div>

      <!-- 分页 -->
      <Pagination
        v-if="total > pageSize"
        :page="page"
        :total="total"
        :page-size="pageSize"
        @update:page="onPageChange"
      />
    </div>
  </div>
</template>

<style scoped lang="scss">
.notif-page { padding: 24px 16px; }
.notif-container { max-width: 800px; margin: 0 auto; }

.page-header { display: flex; align-items: center; justify-content: space-between; margin-bottom: 20px; }
.header-left { display: flex; align-items: center; gap: 12px; }
.page-title { font-size: 32px; font-weight: 700; color: #121c28; letter-spacing: -0.5px; }
.unread-badge {
  display: inline-flex; align-items: center; justify-content: center;
  width: 28px; height: 28px; border-radius: 50%; background: #003527; color: #fff;
  font-size: 13px; font-weight: 700;
}
.mark-btn {
  display: inline-flex; align-items: center; gap: 6px;
  padding: 6px 16px; border-radius: 6px; border: 1px solid #bfc9c3;
  background: #fff; color: #404944; font-size: 13px; cursor: pointer;
  transition: all 0.2s;
  &:hover { border-color: #003527; color: #003527; }
}

.filter-tabs {
  display: flex; gap: 0; border-bottom: 1px solid #bfc9c3; margin-bottom: 20px;
}
.filter-tab {
  padding: 10px 20px; font-size: 14px; font-weight: 500; color: #404944;
  background: none; border: none; border-bottom: 2px solid transparent;
  cursor: pointer; transition: all 0.2s;
  &:hover { color: #003527; }
  &.active { color: #003527; font-weight: 700; border-bottom-color: #003527; }
}

.loading-state { display: flex; justify-content: center; padding: 60px 0; }
.loader-text { font-size: 14px; color: #404944; }

.notif-list { display: flex; flex-direction: column; gap: 12px; }
.notif-card {
  display: flex; gap: 14px; padding: 18px 20px;
  background: #fff; border-radius: 12px; border: 1px solid #bfc9c3;
  cursor: pointer; transition: all 0.25s;
  &:hover { box-shadow: 0 6px 20px rgba(0,0,0,0.05); transform: translateY(-1px); }
  &.unread { border-left: 3px solid #003527; }
}
.notif-icon { width: 44px; height: 44px; border-radius: 10px; display: flex; align-items: center; justify-content: center; flex-shrink: 0; color: #121c28; }
.notif-body { flex: 1; min-width: 0; }
.notif-title-row { display: flex; align-items: center; gap: 8px; margin-bottom: 6px; h3 { font-size: 15px; font-weight: 600; color: #121c28; } }
.unread-dot { width: 8px; height: 8px; border-radius: 50%; background: #003527; flex-shrink: 0; }
.notif-content { font-size: 13px; color: #404944; line-height: 1.6; margin-bottom: 10px; }
.notif-footer { display: flex; align-items: center; gap: 12px; }
.notif-time { display: flex; align-items: center; gap: 4px; font-size: 12px; color: #bfc9c3; }
.notif-tag { font-size: 11px; padding: 2px 10px; border-radius: 4px; font-weight: 600; }
.tag-interview { background: #003527; color: #fff; }
.tag-application { background: #d4edda; color: #155724; }
.tag-system { background: #f3f4f5; color: #404944; }

.empty-state { text-align: center; padding: 60px 20px; color: #bfc9c3; p { font-size: 16px; margin-top: 12px; } }
.empty-icon { color: #bfc9c3; }
</style>
