<script setup lang="ts">
import { ref } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '@/store/auth'
import {
  LayoutDashboard, Users, ShieldCheck, FileText, Menu,
} from 'lucide-vue-next'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()
const collapsed = ref(false)

const menuItems = [
  { path: '/admin', label: '仪表盘', icon: LayoutDashboard },
  { path: '/admin/users', label: '用户管理', icon: Users },
  { path: '/admin/audit', label: '审核管理', icon: ShieldCheck },
  { path: '/admin/logs', label: '系统日志', icon: FileText },
]

function handleLogout() {
  authStore.logout()
  router.push('/login')
}
</script>

<template>
  <el-container class="admin-layout">
    <el-aside :width="collapsed ? '64px' : '220px'" class="sidebar">
      <div class="sidebar-header">
        <h2 v-show="!collapsed" class="logo">管理后台</h2>
        <el-icon class="collapse-btn" @click="collapsed = !collapsed">
          <Menu :size="20" />
        </el-icon>
      </div>
      <el-menu
        :default-active="route.path"
        :collapse="collapsed"
        router
        class="sidebar-menu"
        background-color="#1a3a5c"
        text-color="#cbd5e1"
        active-text-color="#0ea5e9"
      >
        <el-menu-item v-for="item in menuItems" :key="item.path" :index="item.path">
          <el-icon><component :is="item.icon" :size="18" /></el-icon>
          <template #title>{{ item.label }}</template>
        </el-menu-item>
      </el-menu>
    </el-aside>

    <el-container>
      <el-header class="top-header">
        <div />
        <div class="header-right">
          <el-dropdown @command="router.push">
            <span class="user-info">
              {{ authStore.username }}
              <el-icon><arrow-down /></el-icon>
            </span>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item divided @click="handleLogout">退出登录</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </el-header>
      <el-main class="main-content">
        <router-view />
      </el-main>
    </el-container>
  </el-container>
</template>

<style scoped lang="scss">
.admin-layout { height: 100vh; }
.sidebar {
  background-color: #1a3a5c;
  transition: width 0.3s;
  overflow: hidden;
}
.sidebar-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px;
  color: #fff;
  .logo { font-size: 18px; white-space: nowrap; }
  .collapse-btn { cursor: pointer; color: #cbd5e1; }
}
.sidebar-menu { border-right: none; }
.top-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: #fff;
  border-bottom: 1px solid #e5e7eb;
  padding: 0 24px;
}
.header-right .user-info { cursor: pointer; display: flex; align-items: center; gap: 4px; }
.main-content { background-color: #f5f7fa; padding: 24px; overflow-y: auto; }
</style>
