<script setup lang="ts">
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { register } from '@/api/auth'
import type { RegisterForm, UserRole } from '@/types/auth'

const router = useRouter()
const loading = ref(false)

const form = reactive<RegisterForm>({ username: '', password: '', role: 'USER' })
const confirmPassword = ref('')

async function handleRegister() {
  if (!form.username || !form.password) {
    ElMessage.warning('请填写完整信息')
    return
  }
  if (form.password !== confirmPassword.value) {
    ElMessage.warning('两次密码不一致')
    return
  }
  loading.value = true
  try {
    await register(form)
    ElMessage.success('注册成功，请登录')
    router.push('/login')
  } catch {
    // error handled by interceptor
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="register-page">
    <div class="register-card">
      <h2>注册 智聘星图</h2>
      <el-form @submit.prevent="handleRegister">
        <el-form-item>
          <el-input v-model="form.username" placeholder="用户名" size="large" />
        </el-form-item>
        <el-form-item>
          <el-input v-model="form.password" type="password" placeholder="密码" size="large" show-password />
        </el-form-item>
        <el-form-item>
          <el-input v-model="confirmPassword" type="password" placeholder="确认密码" size="large" show-password />
        </el-form-item>
        <el-form-item label="角色">
          <el-radio-group v-model="form.role">
            <el-radio value="USER">求职者</el-radio>
            <el-radio value="COMPANY">企业</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-button type="primary" size="large" :loading="loading" @click="handleRegister" style="width: 100%">
          注册
        </el-button>
      </el-form>
      <p class="login-link">
        已有账号？<router-link to="/login">立即登录</router-link>
      </p>
    </div>
  </div>
</template>

<style scoped lang="scss">
.register-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f5f7fa;
}
.register-card {
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
.login-link {
  text-align: center;
  margin-top: 16px;
  color: #909399;
}
</style>
