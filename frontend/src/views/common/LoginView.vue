<script setup lang="ts">
import { reactive, ref } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import { login } from '@/api/auth'
import { useAuthStore } from '@/store/auth'
import type { LoginForm, UserRole } from '@/types/auth'
import {
  Phone, Lock, Briefcase, Building2, ShieldCheck, Sparkles, Network, Route,
} from 'lucide-vue-next'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()
const loading = ref(false)
const selectedRole = ref<UserRole>('USER')

const form = reactive<LoginForm>({ username: '', password: '' })

const roleOptions = [
  { value: 'USER' as UserRole, label: '求职者', icon: Briefcase },
  { value: 'COMPANY' as UserRole, label: '企业', icon: Building2 },
  { value: 'ADMIN' as UserRole, label: '管理员', icon: ShieldCheck },
]

async function handleLogin() {
  if (!form.username || !form.password) {
    ElMessage.warning('请输入账号和密码')
    return
  }
  loading.value = true
  try {
    const { data: res } = await login(form)
    authStore.setAuth(res.data.token, res.data.role, res.data.username)
    ElMessage.success('登录成功')
    const redirect = route.query.redirect as string
    const roleRoutes: Record<UserRole, string> = { ADMIN: '/admin', USER: '/user', COMPANY: '/company' }
    router.push(redirect || roleRoutes[res.data.role] || '/')
  } catch { /* interceptor handles */ } finally { loading.value = false }
}
</script>

<template>
  <div class="login-page" @keydown.enter="handleLogin">
    <!-- 左侧表单 -->
    <div class="form-side">
      <div class="form-inner">
        <router-link to="/" class="logo fade-up d1">智聘星图</router-link>
        <p class="subtitle fade-up d2">登录你的账户，探索无限机遇</p>

        <div class="role-selector fade-up d3">
          <div
            v-for="opt in roleOptions"
            :key="opt.value"
            class="role-card"
            :class="{ active: selectedRole === opt.value }"
            @click="selectedRole = opt.value"
          >
            <component :is="opt.icon" :size="22" />
            <span>{{ opt.label }}</span>
          </div>
        </div>

        <el-form @submit.prevent="handleLogin">
          <el-form-item class="fade-up d4">
            <el-input v-model="form.username" size="large" placeholder="请输入账号" :prefix-icon="Phone" />
          </el-form-item>
          <el-form-item class="fade-up d5">
            <el-input v-model="form.password" type="password" size="large" placeholder="请输入密码" show-password :prefix-icon="Lock" />
          </el-form-item>
          <div class="form-meta fade-up d6">
            <el-checkbox>记住我</el-checkbox>
            <a href="#" class="forgot-link">忘记密码?</a>
          </div>
          <el-button type="primary" size="large" :loading="loading" class="submit-btn fade-up d7" @click="handleLogin">
            登录
          </el-button>
        </el-form>

        <p class="switch-text fade-up d8">
          还没有账号？<router-link to="/register" class="switch-link">立即注册</router-link>
        </p>
      </div>
    </div>

    <!-- 右侧英雄区 -->
    <div class="hero-side">
      <div class="decor-circle c1" /><div class="decor-circle c2" /><div class="decor-circle c3" />
      <div class="decor-square s1" /><div class="decor-square s2" />
      <div class="feature-cards">
        <div class="feature-card fc1">
          <div class="fc-icon"><Network :size="20" /></div>
          <div><div class="fc-title">能力图谱</div><div class="fc-desc">AI 语义驱动的技能知识网络</div></div>
        </div>
        <div class="feature-card fc2">
          <div class="fc-icon"><Sparkles :size="20" /></div>
          <div><div class="fc-title">AI 智能匹配</div><div class="fc-desc">精准对接理想岗位与人才</div></div>
        </div>
        <div class="feature-card fc3">
          <div class="fc-icon"><Route :size="20" /></div>
          <div><div class="fc-title">AI 职业规划</div><div class="fc-desc">个性化职业发展路径推荐</div></div>
        </div>
      </div>
      <div class="hero-footer">Powered by 银河麒麟 · 人大金仓 · DeepSeek</div>
    </div>
  </div>
</template>

<style scoped lang="scss">
.login-page { display: flex; min-height: 100vh; overflow: hidden; }

/* ====== 入场动画 ====== */
@keyframes fadeUp { from { opacity: 0; transform: translateY(24px); } to { opacity: 1; transform: translateY(0); } }
.fade-up { opacity: 0; animation: fadeUp 0.55s cubic-bezier(0.22, 1, 0.36, 1) forwards; }
.d1 { animation-delay: 0.1s; } .d2 { animation-delay: 0.18s; } .d3 { animation-delay: 0.26s; }
.d4 { animation-delay: 0.34s; } .d5 { animation-delay: 0.40s; } .d6 { animation-delay: 0.46s; }
.d7 { animation-delay: 0.52s; } .d8 { animation-delay: 0.58s; }

/* ====== 左侧表单 ====== */
.form-side { width: 520px; flex-shrink: 0; display: flex; flex-direction: column; justify-content: center; padding: 48px 64px; background: #fff; }
.form-inner { max-width: 380px; }
.logo { font-size: 28px; font-weight: 700; color: #1a3a5c; text-decoration: none; display: block; margin-bottom: 32px; &:hover { text-decoration: none; } }
.subtitle { color: #909399; font-size: 15px; margin-bottom: 28px; }

.role-selector { display: grid; grid-template-columns: repeat(3, 1fr); gap: 10px; margin-bottom: 24px; }
.role-card {
  display: flex; flex-direction: column; align-items: center; gap: 6px;
  padding: 14px 8px; border: 2px solid #e5e7eb; border-radius: 10px;
  cursor: pointer; transition: all 0.25s cubic-bezier(0.4,0,0.2,1);
  background: #fafbfc; color: #909399;
  span { font-size: 13px; font-weight: 600; }
  &:hover { border-color: #1a3a5c; color: #1a3a5c; transform: translateY(-2px); box-shadow: 0 4px 12px rgba(26,58,92,0.1); }
  &.active { border-color: #1a3a5c; background: rgba(26,58,92,0.06); color: #1a3a5c; box-shadow: 0 4px 12px rgba(26,58,92,0.12); }
}

:deep(.el-input__wrapper) { border-radius: 10px; padding: 4px 12px; transition: box-shadow 0.3s; &:focus-within { box-shadow: 0 0 0 3px rgba(14,165,233,0.15); } }
.form-meta { display: flex; align-items: center; justify-content: space-between; margin-bottom: 20px; }
.forgot-link { font-size: 13px; color: #1a3a5c; font-weight: 600; transition: color 0.2s; &:hover { color: #0ea5e9; } }

.submit-btn {
  width: 100%; height: 44px; border-radius: 999px; font-size: 15px; font-weight: 600;
  background: #1a3a5c; border-color: #1a3a5c; letter-spacing: 2px;
  position: relative; overflow: hidden; transition: all 0.3s;
  &::after {
    content: ''; position: absolute; top: 0; left: -150%; width: 100%; height: 100%;
    background: linear-gradient(90deg, transparent, rgba(255,255,255,0.15), transparent);
    transform: skewX(-20deg); animation: shimmer 4s infinite;
  }
  &:hover { background: #24507a; border-color: #24507a; transform: translateY(-1px); box-shadow: 0 8px 20px rgba(26,58,92,0.25); }
}
@keyframes shimmer { 0% { left: -150%; } 30% { left: 150%; } 100% { left: 150%; } }

.switch-text { text-align: center; margin-top: 20px; color: #909399; font-size: 14px; }
.switch-link { color: #1a3a5c; font-weight: 600; text-decoration: none; transition: color 0.2s; &:hover { color: #0ea5e9; } }

/* ====== 右侧英雄区 ====== */
.hero-side { flex: 1; position: relative; overflow: hidden; display: flex; align-items: center; justify-content: center; background: linear-gradient(135deg, #1a3a5c 0%, #1e5a8a 40%, #0ea5e9 100%); }

.decor-circle {
  position: absolute; border-radius: 50%; background: rgba(255,255,255,0.06); pointer-events: none;
  &.c1 { width: 320px; height: 320px; top: -60px; left: -80px; animation: breathe 6s ease-in-out infinite; }
  &.c2 { width: 200px; height: 200px; bottom: 60px; right: 40px; animation: breathe 6s ease-in-out 2s infinite; }
  &.c3 { width: 120px; height: 120px; top: 40%; left: 20%; animation: breathe 6s ease-in-out 4s infinite; }
}
@keyframes breathe { 0%, 100% { transform: scale(1); } 50% { transform: scale(1.06); } }

.decor-square {
  position: absolute; border: 1px solid rgba(255,255,255,0.1); pointer-events: none;
  &.s1 { width: 80px; height: 80px; top: 60px; right: 60px; border-radius: 12px; animation: spin-slow 40s linear infinite; }
  &.s2 { width: 50px; height: 50px; bottom: 120px; left: 80px; border-radius: 50%; animation: float-y 7s ease-in-out 1s infinite; }
}
@keyframes spin-slow { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }
@keyframes float-y { 0%, 100% { transform: translateY(0); } 50% { transform: translateY(-10px); } }

.feature-cards { position: relative; z-index: 2; display: flex; flex-direction: column; gap: 20px; width: 300px; }
.feature-card {
  display: flex; align-items: center; gap: 14px; padding: 16px 20px; border-radius: 12px;
  background: rgba(255,255,255,0.1); backdrop-filter: blur(20px); border: 1px solid rgba(255,255,255,0.15);
  &.fc1 { animation: float-y 4s ease-in-out infinite; }
  &.fc2 { margin-left: 32px; animation: float-y 4s ease-in-out 1.3s infinite; }
  &.fc3 { animation: float-y 4s ease-in-out 2.6s infinite; }
}
.fc-icon { width: 44px; height: 44px; border-radius: 10px; background: rgba(255,255,255,0.15); display: flex; align-items: center; justify-content: center; color: #fff; flex-shrink: 0; }
.fc-title { color: #fff; font-weight: 600; font-size: 14px; margin-bottom: 2px; }
.fc-desc { color: rgba(255,255,255,0.6); font-size: 12px; }
.hero-footer { position: absolute; bottom: 36px; left: 0; right: 0; text-align: center; color: rgba(255,255,255,0.35); font-size: 12px; letter-spacing: 3px; text-transform: uppercase; font-weight: 600; }

@media (max-width: 1024px) { .hero-side { display: none; } .form-side { width: 100%; } }
</style>
