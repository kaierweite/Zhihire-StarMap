<script setup lang="ts">
import { reactive, ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { register } from '@/api/auth'
import { searchCompanies } from '@/api/company'
import type { RegisterForm } from '@/types/auth'
import { User, Lock, Building2, FileUp, Network, TrendingUp } from 'lucide-vue-next'

const router = useRouter()
const loading = ref(false)
const activeRole = ref<'USER' | 'COMPANY'>('USER')
const agreed = ref(false)

const form = reactive<RegisterForm>({ username: '', password: '', role: 'USER', company_name: '' })
const confirmPassword = ref('')

function switchRole(role: 'USER' | 'COMPANY') { activeRole.value = role; form.role = role }
const isCompany = computed(() => activeRole.value === 'COMPANY')

const querySearch = async (queryString: string, cb: any) => {
  if (!queryString) { cb([]); return }
  try {
    const res = await searchCompanies(queryString)
    cb((res.data || []).map((name: string) => ({ value: name })))
  } catch { cb([]) }
}

async function handleRegister() {
  if (!form.username || !form.password) { ElMessage.warning('请填写完整信息'); return }
  if (form.password.length < 6) { ElMessage.warning('密码至少 6 位'); return }
  if (form.password !== confirmPassword.value) { ElMessage.warning('两次密码不一致'); return }
  if (!agreed.value) { ElMessage.warning('请阅读并同意服务条款'); return }
  loading.value = true
  try { await register(form); ElMessage.success('注册成功，请登录'); router.push('/login') }
  catch { /* interceptor */ } finally { loading.value = false }
}
</script>

<template>
  <div class="register-page" @keydown.enter="handleRegister">
    <div class="form-side">
      <div class="form-inner">
        <router-link to="/" class="logo fade-up d1">智聘星图</router-link>
        <div class="role-tabs fade-up d2">
          <button class="tab-btn" :class="{ active: activeRole === 'USER' }" @click="switchRole('USER')">求职者</button>
          <button class="tab-btn" :class="{ active: activeRole === 'COMPANY' }" @click="switchRole('COMPANY')">企业</button>
        </div>
        <el-form @submit.prevent="handleRegister">
          <el-form-item v-if="isCompany" class="fade-up d3"><el-autocomplete v-model="form.company_name" :fetch-suggestions="querySearch" size="large" placeholder="请输入企业全称（支持关键字搜索）" :prefix-icon="Building2" :debounce="300" clearable /></el-form-item>
          <el-form-item class="fade-up d3"><el-input v-model="form.username" size="large" placeholder="请输入手机号码" :prefix-icon="User" /></el-form-item>
          <el-form-item class="fade-up d4"><el-input v-model="form.password" type="password" size="large" placeholder="请设置密码（至少 6 位）" show-password :prefix-icon="Lock" /></el-form-item>
          <el-form-item class="fade-up d5"><el-input v-model="confirmPassword" type="password" size="large" placeholder="请再次输入密码" show-password :prefix-icon="Lock" /></el-form-item>
          <div class="terms-row fade-up d6">
            <el-checkbox v-model="agreed">我已阅读并同意 <a href="#" class="terms-link">服务条款</a> 和 <a href="#" class="terms-link">隐私政策</a></el-checkbox>
          </div>
          <el-button type="primary" size="large" :loading="loading" class="submit-btn fade-up d7" @click="handleRegister">创建账号</el-button>
        </el-form>
        <p class="switch-text fade-up d8">已有账号？<router-link to="/login" class="switch-link">立即登录</router-link></p>
      </div>
    </div>
    <div class="hero-side">
      <div class="decor-circle c1" /><div class="decor-circle c2" />
      <div class="decor-square s1" /><div class="decor-square s2" />
      <div class="feature-cards">
        <div class="feature-card fc1"><div class="fc-icon"><FileUp :size="20" /></div><div><div class="fc-title">智能简历解析</div><div class="fc-desc">AI 自动提取技能与经验</div></div></div>
        <div class="feature-card fc2"><div class="fc-icon"><Hub :size="20" /></div><div><div class="fc-title">知识图谱分析</div><div class="fc-desc">构建个人技能网络拓扑</div></div></div>
        <div class="feature-card fc3"><div class="fc-icon"><TrendingUp :size="20" /></div><div><div class="fc-title">职业发展预测</div><div class="fc-desc">数据驱动的成长路径规划</div></div></div>
      </div>
      <div class="hero-footer">Powered by 银河麒麟 · 人大金仓 · DeepSeek</div>
    </div>
  </div>
</template>

<style scoped lang="scss">
.register-page { display: flex; min-height: 100vh; overflow: hidden; }

@keyframes fadeUp { from { opacity: 0; transform: translateY(24px); } to { opacity: 1; transform: translateY(0); } }
.fade-up { opacity: 0; animation: fadeUp 0.55s cubic-bezier(0.22,1,0.36,1) forwards; }
.d1 { animation-delay: 0.1s; } .d2 { animation-delay: 0.18s; } .d3 { animation-delay: 0.26s; }
.d4 { animation-delay: 0.34s; } .d5 { animation-delay: 0.40s; } .d6 { animation-delay: 0.46s; }
.d7 { animation-delay: 0.52s; } .d8 { animation-delay: 0.58s; }

.form-side { width: 560px; flex-shrink: 0; display: flex; flex-direction: column; justify-content: center; padding: 48px 64px; background: #fff; }
.form-inner { max-width: 400px; }
.logo { font-size: 28px; font-weight: 700; color: #003527; text-decoration: none; display: block; margin-bottom: 28px; &:hover { text-decoration: none; } }

.role-tabs { display: flex; gap: 8px; margin-bottom: 24px; }
.tab-btn {
  padding: 8px 20px; border-radius: 999px; font-size: 13px; font-weight: 600;
  cursor: pointer; transition: all 0.25s; border: 1px solid #bfc9c3; background: #fff; color: #404944;
  &:hover { border-color: #003527; color: #003527; }
  &.active { background: #003527; color: #fff; border-color: #003527; box-shadow: 0 4px 12px rgba(26,58,92,0.2); }
}

:deep(.el-input__wrapper) { border-radius: 10px; padding: 4px 12px; transition: box-shadow 0.3s; &:focus-within { box-shadow: 0 0 0 3px rgba(14,165,233,0.15); } }
.terms-row { margin-bottom: 20px; }
.terms-link { color: #003527; font-weight: 600; &:hover { color: #064e3b; } }

.submit-btn {
  width: 100%; height: 44px; border-radius: 999px; font-size: 15px; font-weight: 600;
  background: #003527; border-color: #003527; letter-spacing: 2px;
  position: relative; overflow: hidden; transition: all 0.3s;
  &::after { content: ''; position: absolute; top: 0; left: -150%; width: 100%; height: 100%; background: linear-gradient(90deg, transparent, rgba(255,255,255,0.15), transparent); transform: skewX(-20deg); animation: shimmer 4s infinite; }
  &:hover { background: #064e3b; border-color: #064e3b; transform: translateY(-1px); box-shadow: 0 8px 20px rgba(26,58,92,0.25); }
}
@keyframes shimmer { 0% { left: -150%; } 30% { left: 150%; } 100% { left: 150%; } }

.switch-text { text-align: center; margin-top: 20px; color: #404944; font-size: 14px; }
.switch-link { color: #003527; font-weight: 600; text-decoration: none; &:hover { color: #064e3b; } }

.hero-side { flex: 1; position: relative; overflow: hidden; display: flex; align-items: center; justify-content: center; background: linear-gradient(135deg, #003527 0%, #064e3b 40%, #064e3b 100%); }
.decor-circle { position: absolute; border-radius: 50%; background: rgba(255,255,255,0.06); pointer-events: none; &.c1 { width: 360px; height: 360px; top: -40px; left: -40px; animation: breathe 6s ease-in-out infinite; } &.c2 { width: 240px; height: 240px; bottom: 40px; right: 60px; animation: breathe 6s ease-in-out 2s infinite; } }
@keyframes breathe { 0%, 100% { transform: scale(1); } 50% { transform: scale(1.06); } }
.decor-square { position: absolute; border: 1px solid rgba(255,255,255,0.1); pointer-events: none; &.s1 { width: 70px; height: 70px; top: 80px; right: 80px; border-radius: 16px; animation: spin-slow 40s linear infinite; } &.s2 { width: 90px; height: 90px; bottom: 100px; left: 60px; border-radius: 50%; animation: float-y 7s ease-in-out 1s infinite; } }
@keyframes spin-slow { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }
@keyframes float-y { 0%, 100% { transform: translateY(0); } 50% { transform: translateY(-10px); } }

.feature-cards { position: relative; z-index: 2; display: flex; flex-direction: column; gap: 20px; width: 300px; }
.feature-card { display: flex; align-items: center; gap: 14px; padding: 16px 20px; border-radius: 12px; background: rgba(255,255,255,0.1); backdrop-filter: blur(20px); border: 1px solid rgba(255,255,255,0.15); &.fc1 { animation: float-y 4s ease-in-out infinite; } &.fc2 { margin-left: 40px; animation: float-y 4s ease-in-out 1.3s infinite; } &.fc3 { animation: float-y 4s ease-in-out 2.6s infinite; } }
.fc-icon { width: 44px; height: 44px; border-radius: 10px; background: rgba(255,255,255,0.15); display: flex; align-items: center; justify-content: center; color: #fff; flex-shrink: 0; }
.fc-title { color: #fff; font-weight: 600; font-size: 14px; margin-bottom: 2px; }
.fc-desc { color: rgba(255,255,255,0.6); font-size: 12px; }
.hero-footer { position: absolute; bottom: 36px; left: 0; right: 0; text-align: center; color: rgba(255,255,255,0.35); font-size: 12px; letter-spacing: 3px; text-transform: uppercase; font-weight: 600; }

@media (max-width: 1024px) { .hero-side { display: none; } .form-side { width: 100%; } }
</style>


