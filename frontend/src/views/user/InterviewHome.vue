<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/store/auth'
import { MessageSquare, Phone, Video, User, Briefcase, ChevronRight } from 'lucide-vue-next'
import { listOccupRoles } from '@/api/interview'
import type { OccupRole, SessionRecord } from '@/types/interview'

const router = useRouter()
const authStore = useAuthStore()

const roles = ref<OccupRole[]>([])
const selectedRole = ref<number | null>(null)
const records = ref<SessionRecord[]>([])

function loadRecords() {
  try {
    const raw = localStorage.getItem('zhihire_interview_records')
    records.value = raw ? JSON.parse(raw) : []
  } catch {
    records.value = []
  }
}

onMounted(async () => {
  loadRecords()
  try {
    const res = await listOccupRoles()
    roles.value = res.data.data
    if (roles.value.length > 0) {
      selectedRole.value = roles.value[0].id
    }
  } catch {
    // fallback: keep empty list
  }
})

const modes = [
  { key: 'chat', label: '文字聊天面试', desc: '文字问答，AI 模拟面试官实时出题、评分', icon: MessageSquare, route: '/user/interview/chat' },
  { key: 'phone', label: '语音面试', desc: '语音识别+合成，模拟电话面试场景', icon: Phone, route: '/user/interview/phone' },
  { key: 'video', label: '视频面试', desc: '摄像头+虚拟形象，全方位模拟真实面试', icon: Video, route: '/user/interview/video' },
]

function goMode(mode: string) {
  if (!selectedRole.value) return
  const roleName = roles.value.find((r) => r.id === selectedRole.value)?.name || ''
  const m = modes.find((m) => m.key === mode)
  router.push({ path: m?.route || '/user/interview/chat', query: { role_id: String(selectedRole.value), role: roleName } })
}
</script>

<template>
  <div class="interview-home">
    <div class="container">
      <h1 class="page-title fade-up">模拟面试训练</h1>
      <p class="page-desc fade-up d1">AI 扮演面试官，针对你的专业和岗位实时出题、评分与反馈</p>

      <div class="info-grid fade-up d2">
        <div class="info-card">
          <div class="info-icon"><User :size="22" /></div>
          <div>
            <h3>求职者信息</h3>
            <p class="info-val">{{ authStore.username }}</p>
          </div>
        </div>
        <div class="info-card">
          <div class="info-icon"><Briefcase :size="22" /></div>
          <div>
            <h3>目标职业</h3>
            <select v-model="selectedRole" class="job-select">
              <option v-for="r in roles" :key="r.id" :value="r.id">{{ r.name }}</option>
            </select>
            <p v-if="selectedRole" class="info-sub">
              {{ roles.find((r) => r.id === selectedRole)?.category || '' }}
            </p>
          </div>
        </div>
      </div>

      <h2 class="section-heading fade-up d3">选择面试模式</h2>
      <div class="mode-grid fade-up d3">
        <div v-for="m in modes" :key="m.key" class="mode-card" @click="goMode(m.key)">
          <div class="mode-icon" :class="m.key"><component :is="m.icon" :size="28" /></div>
          <h3>{{ m.label }}</h3>
          <p>{{ m.desc }}</p>
          <button class="start-btn">开始面试</button>
        </div>
      </div>

      <h2 class="section-heading fade-up d4">最近面试记录</h2>
      <div v-if="records.length === 0" class="empty-hint fade-up d4">暂无面试记录</div>
      <div v-else class="records fade-up d4">
        <div v-for="r in records" :key="r.session_id" class="record-row">
          <span class="record-job">{{ r.role_name }}</span>
          <span class="record-date">{{ r.created_at.slice(0, 10) }}</span>
          <span v-if="r.is_finished" class="record-score" :class="r.score !== null && r.score >= 70 ? 'high' : 'mid'">
            {{ r.score ?? '-' }} 分
          </span>
          <span v-else class="record-status">进行中</span>
          <router-link v-if="r.is_finished" :to="'/user/interview/report?session_id=' + r.session_id" class="record-link">
            查看报告 <ChevronRight :size="14" />
          </router-link>
          <router-link v-else :to="'/user/interview/chat?session_id=' + r.session_id" class="record-link">
            继续面试
          </router-link>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped lang="scss">
.interview-home { padding: 24px 16px; }
.container { max-width: 900px; margin: 0 auto; }

@keyframes fadeUp { from { opacity: 0; transform: translateY(20px); } to { opacity: 1; transform: translateY(0); } }
.fade-up { opacity: 0; animation: fadeUp 0.5s cubic-bezier(0.22,1,0.36,1) forwards; }
.d1 { animation-delay: 0.08s; } .d2 { animation-delay: 0.15s; } .d3 { animation-delay: 0.22s; } .d4 { animation-delay: 0.3s; }

.page-title { font-size: 32px; font-weight: 700; color: #303133; margin-bottom: 6px; }
.page-desc { font-size: 15px; color: #909399; margin-bottom: 28px; }
.section-heading { font-size: 20px; font-weight: 600; color: #303133; margin-bottom: 16px; }

.info-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; margin-bottom: 32px; }
.info-card {
  display: flex; align-items: center; gap: 14px; padding: 20px;
  background: #fff; border-radius: 12px; border: 1px solid #e5e7eb;
  h3 { font-size: 13px; color: #909399; margin-bottom: 4px; }
}
.info-icon { width: 44px; height: 44px; border-radius: 10px; background: rgba(14,165,233,0.08); color: #1a3a5c; display: flex; align-items: center; justify-content: center; flex-shrink: 0; }
.info-val { font-size: 16px; font-weight: 600; color: #303133; }
.info-sub { font-size: 13px; color: #606266; margin-top: 2px; }
.job-select {
  padding: 6px 10px; border: 1px solid #dcdfe6; border-radius: 6px;
  font-size: 15px; font-weight: 600; color: #303133; background: #fff; outline: none;
  min-width: 180px;
  &:focus { border-color: #1a3a5c; }
}

.mode-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 20px; margin-bottom: 36px; }
.mode-card {
  display: flex; flex-direction: column; align-items: center; text-align: center; gap: 10px;
  padding: 32px 20px; background: #fff; border-radius: 12px; border: 1px solid #e5e7eb;
  cursor: pointer; transition: all 0.3s;
  &:hover { transform: translateY(-4px); box-shadow: 0 12px 28px rgba(0,0,0,0.08); border-color: #1a3a5c; }
  h3 { font-size: 16px; font-weight: 600; color: #303133; }
  p { font-size: 13px; color: #909399; }
}
.mode-icon {
  width: 56px; height: 56px; border-radius: 14px;
  background: linear-gradient(135deg, #1a3a5c, #0ea5e9); color: #fff;
  display: flex; align-items: center; justify-content: center;
  &.chat { background: linear-gradient(135deg, #2563eb, #60a5fa); }
  &.phone { background: linear-gradient(135deg, #059669, #34d399); }
  &.video { background: linear-gradient(135deg, #dc2626, #f87171); }
}
.start-btn {
  margin-top: 4px; padding: 8px 24px; border-radius: 999px;
  font-size: 13px; font-weight: 600; border: none; cursor: pointer;
  transition: all 0.2s;
}
.mode-card:nth-child(1) .start-btn { background: #2563eb; color: #fff; &:hover { background: #1d4ed8; } }
.mode-card:nth-child(2) .start-btn { background: #059669; color: #fff; &:hover { background: #047857; } }
.mode-card:nth-child(3) .start-btn { background: #dc2626; color: #fff; &:hover { background: #b91c1c; } }

.records { display: flex; flex-direction: column; gap: 10px; }
.empty-hint { text-align: center; color: #c0c4cc; padding: 32px 0; font-size: 14px; }
.record-row {
  display: flex; align-items: center; gap: 16px; padding: 14px 20px;
  background: #fff; border-radius: 10px; border: 1px solid #e5e7eb;
}
.record-job { font-size: 14px; font-weight: 600; color: #303133; flex: 1; }
.record-date { font-size: 13px; color: #909399; }
.record-score { font-size: 14px; font-weight: 700; &.high { color: #198754; } &.mid { color: #b8860b; } }
.record-status { font-size: 13px; color: #909399; font-style: italic; }
.record-link { display: inline-flex; align-items: center; gap: 2px; font-size: 13px; color: #0ea5e9; text-decoration: none; font-weight: 600; &:hover { text-decoration: underline; } }

@media (max-width: 640px) { .info-grid { grid-template-columns: 1fr; } .mode-grid { grid-template-columns: 1fr; } }
</style>
