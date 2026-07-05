<script setup lang="ts">
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/store/auth'
import { Bell, ChevronDown } from 'lucide-vue-next'

const router = useRouter()
const authStore = useAuthStore()

defineProps<{
  activeLink?: string
}>()

function goDashboard() {
  const routes: Record<string, string> = { ADMIN: '/admin', USER: '/user', COMPANY: '/company' }
  router.push(routes[authStore.role as string] || '/login')
}

function handleLogout() {
  authStore.logout()
  router.push('/login')
}

const navItems = [
  { key: 'explore', label: '探索', to: '/' },
  { key: 'jobs', label: '职位推荐', to: '/user/jobs' },
  { key: 'search', label: '职位搜索', to: '/user/jobs/search' },
  { key: 'resume', label: '简历中心', to: '/user/resume' },
  { key: 'social', label: '社交', to: '/user/social' },
]

const interviewItems = [
  { label: '智能面试', to: '/user/interview' },
  { label: '面试记录', to: '/user/interview/report' },
  { label: '面试题库', to: '/user/interview/question-bank' },
]
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
        <router-link to="/user/notifications" class="icon-btn" title="通知中心">
          <Bell :size="18" />
        </router-link>

        <el-dropdown @command="goDashboard">
          <div class="user-badge">
            <div class="avatar">{{ authStore.username?.charAt(0).toUpperCase() || 'U' }}</div>
            <span class="username">{{ authStore.username }}</span>
            <ChevronDown :size="14" class="chevron" />
          </div>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item @click="router.push('/user')">个人中心</el-dropdown-item>
              <el-dropdown-item @click="goDashboard">我的工作台</el-dropdown-item>
              <el-dropdown-item divided @click="handleLogout">退出登录</el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
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
  height: 56px;
  background: #fff;
  border-bottom: 1px solid #e5e7eb;
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
  font-size: 22px;
  font-weight: 700;
  color: #1a3a5c;
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
  font-size: 13px;
  font-weight: 500;
  color: #606266;
  text-decoration: none;
  padding-bottom: 2px;
  border-bottom: 2px solid transparent;
  transition: all 0.2s;
  cursor: pointer;
  white-space: nowrap;

  &:hover {
    color: #1a3a5c;
    text-decoration: none;
  }

  &.active {
    color: #1a3a5c;
    font-weight: 700;
    border-bottom-color: #1a3a5c;
  }
}

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
  color: #606266;
  transition: all 0.2s;
  &:hover { background: #f5f7fa; color: #1a3a5c; }
}

.user-badge {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  padding: 4px 8px;
  border-radius: 8px;
  transition: background 0.2s;
  &:hover { background: #f5f7fa; }
}

.avatar {
  width: 30px;
  height: 30px;
  border-radius: 50%;
  background: #1a3a5c;
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 13px;
  font-weight: 700;
}

.username {
  font-size: 13px;
  font-weight: 500;
  color: #303133;
}

.chevron {
  color: #909399;
}
</style>
