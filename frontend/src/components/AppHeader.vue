﻿<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from "vue"
import { useRouter, useRoute } from "vue-router"
import { useAuthStore } from "@/store/auth"
import { Bell, ChevronDown } from "lucide-vue-next"
import { getUnreadCount } from "@/api/notification"

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()

function handleLogout() {
  authStore.logout()
  router.push("/login")
}

const activeLink = computed(() => {
  const path = route.path
  if (path === "/") return "explore"
  if (path.startsWith("/user/jobs/search")) return "search"
  if (path.startsWith("/user/jobs")) return "jobs"
  if (path.startsWith("/user/career-plan")) return "career-plan"
  if (path.startsWith("/user/resume")) return "resume"
  if (path.startsWith("/user/social")) return "social"
  if (path.startsWith("/user/interview")) return "interview"
  return ""
})

const navItems = [
  { key: "explore", label: "探索", to: "/" },
  { key: "jobs", label: "职位推荐", to: "/user/jobs" },
  { key: "search", label: "职位搜索", to: "/user/jobs/search" },
  { key: "career-plan", label: "职业规划", to: "/user/career-plan" },
  { key: "resume", label: "简历中心", to: "/user/resume" },
]

const interviewItems = [
  { label: "智能面试", to: "/user/interview" },
  { label: "面试题目", to: "/user/interview/question-bank" },
  { label: "面试记录", to: "/user/interview/report" },
]

// ---- Unread notification count with polling ----
const unreadCount = ref(0)
let pollTimer: ReturnType<typeof setInterval> | null = null

async function fetchUnreadCount() {
  if (!authStore.isLoggedIn || authStore.role !== "USER") return
  try {
    const res = await getUnreadCount()
    unreadCount.value = res.data.data.count
  } catch {
    unreadCount.value = 0
  }
}

onMounted(() => {
  fetchUnreadCount()
  pollTimer = setInterval(fetchUnreadCount, 30000)
})

onUnmounted(() => {
  if (pollTimer) clearInterval(pollTimer)
})
</script>

<template>
  <nav class="app-header">
    <div class="header-inner">
      <router-link to="/" class="header-logo">智聘星图</router-link>
      <div class="header-links">
        <router-link
          v-for="item in navItems"
          :key="item.key"
          :to="item.to"
          class="header-link"
          :class="{ active: activeLink === item.key }"
        >
          {{ item.label }}
        </router-link>
        <!-- 面试功能下拉 -->
        <el-dropdown trigger="click">
          <span class="header-link interview-trigger" :class="{ active: activeLink === 'interview' }">
            面试功能 <ChevronDown :size="14" />
          </span>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item v-for="item in interviewItems" :key="item.to" @click="router.push(item.to)">
                {{ item.label }}
              </el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
      </div>
      <div class="header-actions">
        <template v-if="authStore.isLoggedIn">
          <router-link to="/user/notifications" class="icon-btn notif-btn" title="通知中心">
            <Bell :size="18" />
            <span v-if="unreadCount" class="notif-dot">{{ unreadCount > 99 ? "99+" : unreadCount }}</span>
          </router-link>
          <el-dropdown>
            <div class="user-badge">
              <div class="avatar">{{ authStore.username?.charAt(0).toUpperCase() || "U" }}</div>
              <span class="username">{{ authStore.username }}</span>
              <ChevronDown :size="14" class="chevron" />
            </div>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item @click="router.push('/user/profile')">个人中心</el-dropdown-item>
                <el-dropdown-item divided @click="handleLogout">退出登录</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </template>
        <template v-else>
          <router-link to="/login" class="nav-text-btn">登录</router-link>
          <router-link to="/register" class="nav-primary-btn">注册</router-link>
        </template>
      </div>
    </div>
  </nav>
</template>

<style scoped lang="scss">
.app-header {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  z-index: 100;
  height: 60px;
  background: rgba(255, 255, 255, 0.8);
  backdrop-filter: blur(16px);
  border-bottom: 1px solid rgba(0, 0, 0, 0.08);
  box-shadow: 0 1px 8px rgba(0, 0, 0, 0.06);
}

.header-inner {
  max-width: 1440px;
  margin: 0 auto;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 40px;
}

.header-logo {
  font-size: 16px;
  font-weight: 700;
  color: #000;
  text-decoration: none;
  flex-shrink: 0;
  &:hover { text-decoration: none; }
}

.header-links {
  display: flex;
  align-items: center;
  gap: 24px;
}

.header-link {
  font-size: 16px;
  font-weight: 500;
  color: #333;
  text-decoration: none;
  padding-bottom: 2px;
  border-bottom: 2px solid transparent;
  transition: all 0.2s;
  cursor: pointer;
  white-space: nowrap;
  &:hover {
    color: #000;
    text-decoration: none;
  }
  &.active {
    color: #003527;
    border-bottom-color: #064e3b;
  }
}

/* Remove extra spacing from el-dropdown inside header */
.header-links .el-dropdown,
.header-links .el-dropdown__trigger { display: inline-flex; align-items: center; padding: 0; margin: 0; }

.interview-trigger {
  display: inline-flex;
  align-items: center;
  gap: 2px;
  user-select: none;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 12px;
}

.icon-btn {
  width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 8px;
  color: #666;
  transition: all 0.2s;
  &:hover { background: #eee; color: #000; }
}

.notif-btn {
  position: relative;
}

.notif-dot {
  position: absolute;
  top: 0;
  right: -2px;
  min-width: 16px;
  height: 16px;
  border-radius: 8px;
  background: #e74c3c;
  color: #fff;
  font-size: 11px;
  font-weight: 700;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0 4px;
  line-height: 1;
  box-shadow: 0 0 0 2px #fff;
}

.user-badge {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  padding: 4px 8px;
  border-radius: 8px;
  transition: background 0.2s;
  &:hover { background: #eee; }
}

.avatar {
  width: 30px;
  height: 30px;
  border-radius: 50%;
  background: #003527;
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 13px;
  font-weight: 700;
}

.username {
  font-size: 16px;
  font-weight: 500;
  color: #333;
}

.chevron {
  color: #999;
}

.nav-text-btn {
  font-size: 16px;
  font-weight: 500;
  color: #666;
  text-decoration: none;
  padding: 6px 14px;
  transition: all 0.2s;
  &:hover { color: #000; background: #f5f5f5; border-radius: 6px; }
}

.nav-primary-btn {
  font-size: 16px;
  font-weight: 600;
  color: #fff;
  background: #003527;
  padding: 6px 18px;
  border-radius: 6px;
  text-decoration: none;
  transition: all 0.2s;
  &:hover { background: #064e3b; }
}
</style>