<script setup lang="ts">
import { ref, onMounted, onUnmounted } from "vue"
import { useRouter, useRoute } from "vue-router"
import { useAuthStore } from "@/store/auth"
import { Home, Briefcase, PlusCircle, Filter, UserPlus, Bell, Menu, LogOut, ChevronDown, Building2 } from "lucide-vue-next"
import { getUnreadCount } from "@/api/notification"

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()
const collapsed = ref(false)

const menuItems = [
  { path: "/company", label: "企业首页", icon: Home },
  { path: "/company/profile", label: "企业信息", icon: Building2 },
  { path: "/company/jobs", label: "岗位管理", icon: Briefcase },
  { path: "/company/jobs/publish", label: "发布岗位", icon: PlusCircle },
  { path: "/company/screening", label: "智能筛选", icon: Filter },
  { path: "/company/candidates", label: "候选人推荐", icon: UserPlus },
  { path: "/company/notifications", label: "通知中心", icon: Bell },
]

function handleLogout() { authStore.logout(); router.push("/login") }

// ---- Unread notification count with polling ----
const unreadCount = ref(0)
let pollTimer: ReturnType<typeof setInterval> | null = null

async function fetchUnreadCount() {
  if (!authStore.isLoggedIn || authStore.role !== "COMPANY") return
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
  <el-container class="company-layout">
    <el-aside :width="collapsed ? '64px' : '220px'" class="sidebar">
      <div class="sidebar-header">
        <h2 v-show="!collapsed" class="logo">智聘星图</h2>
        <button class="collapse-btn" @click="collapsed = !collapsed"><Menu :size="18" /></button>
      </div>
      <el-menu :default-active="route.path" :collapse="collapsed" router class="sidebar-menu" background-color="#1a3a5c" text-color="#cbd5e1" active-text-color="#0ea5e9">
        <el-menu-item v-for="item in menuItems" :key="item.path" :index="item.path">
          <el-icon><component :is="item.icon" :size="18" /></el-icon>
          <template #title>{{ item.label }}</template>
        </el-menu-item>
      </el-menu>
    </el-aside>
    <el-container>
      <el-header class="top-header">
        <div></div>
        <div class="header-right">
          <router-link to="/company/notifications" class="icon-btn notif-btn">
            <Bell :size="18" />
            <span v-if="unreadCount" class="notif-dot">{{ unreadCount > 99 ? "99+" : unreadCount }}</span>
          </router-link>
          <el-dropdown>
            <div class="user-badge">
              <div class="avatar">{{ authStore.username?.charAt(0).toUpperCase() || "E" }}</div>
              <span class="username">{{ authStore.username }}</span>
              <ChevronDown :size="14" />
            </div>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item @click="handleLogout"><LogOut :size="14" /> 退出登录</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </el-header>
      <el-main class="main-content"><router-view /></el-main>
    </el-container>
  </el-container>
</template>

<style scoped lang="scss">
.company-layout { height: 100vh; }
.sidebar { background-color: #1a3a5c; transition: width 0.3s; overflow: hidden; }
.sidebar-header { display: flex; align-items: center; justify-content: space-between; padding: 16px; color: #fff; }
.logo { font-size: 18px; font-weight: 700; white-space: nowrap; }
.collapse-btn { background: none; border: none; color: #cbd5e1; cursor: pointer; padding: 4px; border-radius: 6px; &:hover { background: rgba(255,255,255,0.1); } }
.sidebar-menu { border-right: none; }
.top-header { display: flex; align-items: center; justify-content: space-between; background: #fff; border-bottom: 1px solid #e5e7eb; padding: 0 24px; }
.header-right { display: flex; align-items: center; gap: 12px; }
.icon-btn { width: 36px; height: 36px; display: flex; align-items: center; justify-content: center; border-radius: 8px; color: #606266; transition: all 0.2s; &:hover { background: #f5f7fa; color: #1a3a5c; } }

.notif-btn { position: relative; }
.notif-dot {
  position: absolute; top: 0; right: -2px;
  min-width: 16px; height: 16px; border-radius: 8px;
  background: #e74c3c; color: #fff;
  font-size: 11px; font-weight: 700;
  display: flex; align-items: center; justify-content: center;
  padding: 0 4px; line-height: 1;
  box-shadow: 0 0 0 2px #fff;
}

.user-badge { display: flex; align-items: center; gap: 8px; cursor: pointer; padding: 4px 8px; border-radius: 8px; transition: background 0.2s; &:hover { background: #f5f7fa; } }
.avatar { width: 30px; height: 30px; border-radius: 50%; background: #1a3a5c; color: #fff; display: flex; align-items: center; justify-content: center; font-size: 13px; font-weight: 700; }
.username { font-size: 13px; font-weight: 500; color: #303133; }
.main-content { background-color: #f8f9fa; padding: 24px; overflow-y: auto; }
</style>
