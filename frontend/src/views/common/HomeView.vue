<script setup lang="ts">
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/store/auth'

const router = useRouter()
const authStore = useAuthStore()

function goLogin() {
  router.push('/login')
}
function goDashboard() {
  const routes: Record<string, string> = {
    ADMIN: '/admin',
    USER: '/user',
    COMPANY: '/company',
  }
  router.push(routes[authStore.role as string] || '/login')
}
</script>

<template>
  <div class="home">
    <header class="home-header">
      <h1 class="logo">智聘星图</h1>
      <div class="header-actions">
        <el-button v-if="authStore.isLoggedIn" type="primary" @click="goDashboard">
          进入工作台
        </el-button>
        <template v-else>
          <el-button @click="goLogin">登录</el-button>
          <el-button type="primary" @click="router.push('/register')">注册</el-button>
        </template>
      </div>
    </header>
    <main class="home-hero">
      <h2>AI 智能匹配与能力图谱</h2>
      <p>基于银河麒麟操作系统的面试能力培养平台</p>
      <el-button type="primary" size="large" @click="goLogin">
        开始使用
      </el-button>
    </main>
  </div>
</template>

<style scoped lang="scss">
.home {
  min-height: 100vh;
  background: linear-gradient(135deg, #1a3a5c 0%, #0ea5e9 100%);
  color: #fff;
}
.home-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 20px 40px;
}
.logo {
  font-size: 24px;
  font-weight: 700;
}
.home-hero {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  text-align: center;
  padding-top: 20vh;
  gap: 16px;
  h2 {
    font-size: 40px;
    font-weight: 700;
  }
  p {
    font-size: 18px;
    opacity: 0.85;
    margin-bottom: 12px;
  }
}
</style>
