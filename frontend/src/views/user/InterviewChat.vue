<template>
  <div class="chat-page">
    <div class="chat-header">
      <button class="back-btn" @click="router.push('/user/interview')"><ArrowLeft :size="18" /></button>
      <div class="header-info">
        <div class="ai-avatar"><Bot :size="18" /></div>
        <div>
          <h2>AI 面试官</h2>
          <span class="header-sub">{{ roleName }} · 第 {{ questionCount }}/{{ maxQuestions }} 题</span>
        </div>
      </div>
      <div class="header-actions">
        <button v-if="sessionActive && !isFinished" class="end-btn" @click="endInterview">
          <PhoneOff :size="14" /> 结束
        </button>
        <router-link v-if="sessionId" :to="'/user/interview/report?session_id=' + sessionId" class="report-link">
          <FileText :size="16" /> 报告
        </router-link>
      </div>
    </div>

    <div ref="chatContainer" class="chat-body">
      <div v-for="(msg, i) in messages" :key="i" class="chat-msg" :class="msg.role">
        <div class="msg-avatar">
          <Bot v-if="msg.role === 'ai'" :size="16" />
          <User v-else :size="16" />
        </div>
        <div class="msg-bubble">
          <p>{{ msg.content }}</p>
          <span class="msg-time"><Clock :size="11" /> {{ msg.time }}</span>
        </div>
      </div>
      <div v-if="isTyping" class="chat-msg ai">
        <div class="msg-avatar"><Bot :size="16" /></div>
        <div class="msg-bubble typing"><span class="dot" /><span class="dot" /><span class="dot" /></div>
      </div>
    </div>

    <div class="chat-input">
      <input
        v-model="inputText"
        type="text"
        :placeholder="isFinished ? '面试已结束' : '输入你的回答...'"
        @keydown.enter="sendMessage"
        :disabled="isTyping || isFinished"
      />
      <button class="send-btn" :disabled="!inputText.trim() || isTyping || isFinished" @click="sendMessage">
        <Send :size="18" />
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, nextTick, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { Send, Bot, User, Clock, ArrowLeft, FileText, PhoneOff } from 'lucide-vue-next'
import { ElMessage } from 'element-plus'
import { startInterview, submitAnswer } from '@/api/interview'
import type { SessionRecord } from '@/types/interview'

const route = useRoute()
const router = useRouter()

interface Message { role: 'ai' | 'user'; content: string; time: string }

const messages = ref<Message[]>([])
const inputText = ref('')
const isTyping = ref(false)
const questionCount = ref(0)
const maxQuestions = 5
const chatContainer = ref<HTMLElement>()
const sessionId = ref<number | null>(null)
const roleName = ref((route.query.role as string) || '目标岗位')
const currentQuestionId = ref<number | null>(null)
const isFinished = ref(false)
const overallScore = ref<number | null>(null)
const sessionActive = ref(false)

const roleId = computed(() => Number(route.query.role_id) || 0)

function scrollToBottom() {
  nextTick(() => { if (chatContainer.value) chatContainer.value.scrollTop = chatContainer.value.scrollHeight })
}

function addMessage(role: 'ai' | 'user', content: string) {
  const now = new Date()
  const time = `${String(now.getHours()).padStart(2, '0')}:${String(now.getMinutes()).padStart(2, '0')}`
  messages.value.push({ role, content, time })
  scrollToBottom()
}

function saveRecord(sid: number, role: string) {
  try {
    const rec: SessionRecord = { session_id: sid, role_name: role, score: null, created_at: new Date().toISOString(), is_finished: false }
    const raw = localStorage.getItem('zhihire_interview_records') || '[]'
    const recs: SessionRecord[] = JSON.parse(raw)
    recs.unshift(rec)
    localStorage.setItem('zhihire_interview_records', JSON.stringify(recs.slice(0, 20)))
  } catch { /* ignore */ }
}

function updateRecord(sid: number, finished: boolean, score: number | null) {
  try {
    const raw = localStorage.getItem('zhihire_interview_records') || '[]'
    const recs: SessionRecord[] = JSON.parse(raw)
    const idx = recs.findIndex((r) => r.session_id === sid)
    if (idx >= 0) { recs[idx].is_finished = finished; recs[idx].score = score; localStorage.setItem('zhihire_interview_records', JSON.stringify(recs)) }
  } catch { /* ignore */ }
}

async function beginInterview() {
  isTyping.value = true
  sessionActive.value = true
  try {
    const res = await startInterview({ occupation_role_id: roleId.value })
    const data = res.data.data
    sessionId.value = data.session_id
    if (data.first_question) {
      currentQuestionId.value = data.first_question.question_id
      addMessage('ai', data.first_question.content)
      questionCount.value = 1
    }
    saveRecord(data.session_id, roleName.value)
  } catch {
    ElMessage.error('无法开始面试，请稍后重试')
  } finally {
    isTyping.value = false
  }
}

async function sendMessage() {
  const text = inputText.value.trim()
  if (!text || isTyping.value || !sessionId.value || !currentQuestionId.value || isFinished.value) return
  addMessage('user', text)
  inputText.value = ''

  isTyping.value = true
  try {
    const res = await submitAnswer({
      session_id: sessionId.value,
      question_id: currentQuestionId.value,
      answer: text,
    })
    const data = res.data.data

    if (data.is_finished) {
      isFinished.value = true
      sessionActive.value = false
      overallScore.value = data.overall_score
      addMessage('ai', `面试结束！你的综合评分：${data.overall_score ?? '待计算'} 分`)
      updateRecord(sessionId.value, true, data.overall_score)
      setTimeout(() => {
        router.push({ path: '/user/interview/report', query: { session_id: String(sessionId.value) } })
      }, 2000)
    } else if (data.next_question) {
      currentQuestionId.value = data.next_question.question_id
      addMessage('ai', data.next_question.content)
      questionCount.value++
    }
  } catch {
    ElMessage.error('提交失败，请重试')
  } finally {
    isTyping.value = false
  }
}

function endInterview() {
  if (sessionId.value) updateRecord(sessionId.value, true, overallScore.value)
  isFinished.value = true
  sessionActive.value = false
  router.push('/user/interview')
}

onMounted(async () => {
  const sid = route.query.session_id
  if (sid) {
    sessionId.value = Number(sid)
    sessionActive.value = true
    addMessage('ai', '欢迎回来！请继续回答下一题。')
    isTyping.value = true
    try {
      const res = await startInterview({ occupation_role_id: roleId.value })
      const data = res.data.data
      if (data.first_question) {
        currentQuestionId.value = data.first_question.question_id
        addMessage('ai', data.first_question.content)
        questionCount.value = 1
      }
    } catch {
      addMessage('ai', '无法恢复面试，请重新开始。')
    } finally {
      isTyping.value = false
    }
  } else {
    await beginInterview()
  }
})
</script>

<style scoped lang="scss">
.chat-page { display: flex; flex-direction: column; height: 100vh; background: #f8f9fa; }

.chat-header {
  display: flex; align-items: center; gap: 16px; padding: 12px 20px;
  background: #fff; border-bottom: 1px solid #e5e7eb; flex-shrink: 0;
}
.back-btn { width: 36px; height: 36px; border-radius: 8px; border: 1px solid #dcdfe6; background: #fff; color: #606266; display: flex; align-items: center; justify-content: center; cursor: pointer; &:hover { border-color: #1a3a5c; color: #1a3a5c; } }
.header-info { display: flex; align-items: center; gap: 10px; flex: 1; h2 { font-size: 15px; font-weight: 600; color: #303133; } }
.header-actions { display: flex; align-items: center; gap: 8px; }
.ai-avatar { width: 36px; height: 36px; border-radius: 50%; background: linear-gradient(135deg, #1a3a5c, #0ea5e9); color: #fff; display: flex; align-items: center; justify-content: center; }
.header-sub { font-size: 12px; color: #909399; }

.end-btn {
  display: flex; align-items: center; gap: 4px;
  padding: 4px 10px; border-radius: 6px;
  background: rgba(239,68,68,0.08); color: #ef4444;
  border: 1px solid rgba(239,68,68,0.25);
  font-size: 12px; cursor: pointer; white-space: nowrap;
  &:hover { background: rgba(239,68,68,0.15); }
}

.report-link { display: flex; align-items: center; gap: 4px; font-size: 13px; color: #0ea5e9; text-decoration: none; font-weight: 600; &:hover { text-decoration: underline; } }

.chat-body { flex: 1; overflow-y: auto; padding: 20px; display: flex; flex-direction: column; gap: 16px; }
.chat-msg { display: flex; gap: 10px; max-width: 70%; &.user { align-self: flex-end; flex-direction: row-reverse; } }
.msg-avatar { width: 32px; height: 32px; border-radius: 50%; display: flex; align-items: center; justify-content: center; flex-shrink: 0; }
.chat-msg.ai .msg-avatar { background: rgba(26,58,92,0.1); color: #1a3a5c; }
.chat-msg.user .msg-avatar { background: rgba(14,165,233,0.1); color: #0ea5e9; }
.msg-bubble {
  padding: 14px 18px; border-radius: 14px; font-size: 14px; line-height: 1.6;
  p { margin-bottom: 6px; }
}
.chat-msg.ai .msg-bubble { background: #fff; color: #303133; border: 1px solid #e5e7eb; border-bottom-left-radius: 4px; }
.chat-msg.user .msg-bubble { background: #1a3a5c; color: #fff; border-bottom-right-radius: 4px; }
.msg-time { display: flex; align-items: center; gap: 3px; font-size: 11px; color: #c0c4cc; }
.chat-msg.user .msg-time { color: rgba(255,255,255,0.5); }
.typing { display: flex; gap: 4px; padding: 14px 22px; }
.dot { width: 8px; height: 8px; border-radius: 50%; background: #c0c4cc; animation: bounce 1.4s infinite; &:nth-child(2) { animation-delay: 0.2s; } &:nth-child(3) { animation-delay: 0.4s; } }
@keyframes bounce { 0%, 80%, 100% { transform: translateY(0); } 40% { transform: translateY(-6px); } }

.chat-input {
  display: flex; gap: 10px; padding: 16px 20px; background: #fff; border-top: 1px solid #e5e7eb;
  input { flex: 1; padding: 12px 16px; border: 1px solid #dcdfe6; border-radius: 10px; font-size: 14px; outline: none; &:focus { border-color: #1a3a5c; } &:disabled { background: #f5f7fa; } }
}
.send-btn {
  width: 44px; height: 44px; border-radius: 10px; background: #1a3a5c; color: #fff;
  border: none; display: flex; align-items: center; justify-content: center;
  cursor: pointer; transition: all 0.2s;
  &:hover:not(:disabled) { background: #24507a; }
  &:disabled { opacity: 0.4; cursor: default; }
}
</style>
