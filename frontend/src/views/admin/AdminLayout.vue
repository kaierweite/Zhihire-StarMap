<script setup lang="ts">
import { ref } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '@/store/auth'
import { LayoutDashboard, Users, Building2, ShieldCheck, FileText, Brain, Menu, Bell, ChevronDown, LogOut } from 'lucide-vue-next'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()
const collapsed = ref(false)

const menuItems = [
  { path: '/admin', label: '仪表盘', icon: LayoutDashboard },
  { path: '/admin/users', label: '用户管理', icon: Users },
  { path: '/admin/companies', label: '企业管理', icon: Building2 },
  { path: '/admin/audit', label: '审核管理', icon: ShieldCheck },
  { path: '/admin/logs', label: '系统日志', icon: FileText },
  { path: '/admin/ai-model', label: '大模型配置', icon: Brain },
]

function handleLogout() { authStore.logout(); router.push('/login') }
</script>

<template>
  <el-container class="admin-layout">
    <el-aside :width="collapsed ? '64px' : '220px'" class="sidebar">
      <div class="sidebar-header">
        <h2 v-show="!collapsed" class="logo">管理后台</h2>
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
        <div />
        <div class="header-right">
          <el-dropdown>
            <div class="user-badge">
              <div class="avatar">{{ authStore.username?.charAt(0).toUpperCase() || 'A' }}</div>
              <span class="username">{{ authStore.username }}</span>
              <ChevronDown :size="14" />
            </div>
            <template #dropdown>
              <el-dropdown-menu><el-dropdown-item @click="handleLogout"><LogOut :size="14" /> 退出登录</el-dropdown-item></el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </el-header>
      <el-main class="main-content"><router-view /></el-main>
    </el-container>
  </el-container>
</template>

<style scoped lang="scss">
.admin-layout { height: 100vh; }
.sidebar { background-color: #1a3a5c; transition: width 0.3s; overflow: hidden; }
.sidebar-header { display: flex; align-items: center; justify-content: space-between; padding: 16px; color: #fff; }
.logo { font-size: 18px; font-weight: 700; white-space: nowrap; }
.collapse-btn { background: none; border: none; color: #cbd5e1; cursor: pointer; padding: 4px; border-radius: 6px; &:hover { background: rgba(255,255,255,0.1); } }
.sidebar-menu { border-right: none; }
.top-header { display: flex; align-items: center; justify-content: space-between; background: #fff; border-bottom: 1px solid #e5e7eb; padding: 0 24px; }
.header-right { display: flex; align-items: center; gap: 12px; }
.user-badge { display: flex; align-items: center; gap: 8px; cursor: pointer; padding: 4px 8px; border-radius: 8px; transition: background 0.2s; &:hover { background: #f5f7fa; } }
.avatar { width: 30px; height: 30px; border-radius: 50%; background: #1a3a5c; color: #fff; display: flex; align-items: center; justify-content: center; font-size: 13px; font-weight: 700; }
.username { font-size: 13px; font-weight: 500; color: #303133; }
.main-content { background-color: #f8f9fa; padding: 24px; overflow-y: auto; }
</style>
