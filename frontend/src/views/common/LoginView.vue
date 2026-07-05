<script setup lang="ts">
import { reactive, ref } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import { login } from '@/api/auth'
import { useAuthStore } from '@/store/auth'
import type { LoginForm } from '@/types/auth'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()
const loading = ref(false)

const form = reactive<LoginForm>({ username: '', password: '' })

async function handleLogin() {
  if (!form.username || !form.password) {
    ElMessage.warning('请输入用户名和密码')
    return
  }
  loading.value = true
  try {
    const { data: res } = await login(form)
    authStore.setAuth(res.data.token, res.data.role, res.data.username)
    ElMessage.success('登录成功')
    const redirect = route.query.redirect as string
    const roleRoutes: Record<string, string> = {
      ADMIN: '/admin',
      USER: '/user',
      COMPANY: '/company',
    }
    router.push(redirect || roleRoutes[res.data.role] || '/')
  } catch {
    // error already handled by interceptor
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="login-page">
    <div class="login-card">
      <h2>登录 智聘星图</h2>
      <el-form @submit.prevent="handleLogin">
        <el-form-item>
          <el-input v-model="form.username" placeholder="用户名" size="large" />
        </el-form-item>
        <el-form-item>
          <el-input v-model="form.password" type="password" placeholder="密码" size="large" show-password />
        </el-form-item>
        <el-button type="primary" size="large" :loading="loading" @click="handleLogin" style="width: 100%">
          登录
        </el-button>
      </el-form>
      <p class="register-link">
        还没有账号？<router-link to="/register">立即注册</router-link>
      </p>
    </div>
  </div>
</template>

<style scoped lang="scss">
.login-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f5f7fa;
}
.login-card {
  width: 400px;
  padding: 40px;
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
  h2 {
    text-align: center;
    margin-bottom: 32px;
    color: #1a3a5c;
  }
}
.register-link {
  text-align: center;
  margin-top: 16px;
  color: #909399;
}
</style>
