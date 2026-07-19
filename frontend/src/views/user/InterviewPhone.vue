<template>
  <div class="phone-page">
    <div class="phone-header">
      <button class="back-btn" @click="goBack"><ArrowLeft :size="18" /></button>
      <div class="header-info">
        <div class="status-dot" :class="{ active: isRecording || isSpeaking, idle: !isRecording && !isSpeaking && sessionActive }" />
        <div>
          <h2>{{ isSpeaking ? '正在朗读问题...' : isRecording ? '正在聆听...' : sessionActive ? '面试中' : '待接听' }}</h2>
          <span class="header-sub">{{ roleName }} · 第 {{ answeredCount }}/{{ maxQuestions }} 题</span>
        </div>
      </div>
      <button v-if="sessionActive && !isFinished" class="end-btn" @click="endInterview">
        <PhoneOff :size="16" /> 结束
      </button>
    </div>

    <div v-if="!sessionActive && !isFinished" class="dialing-screen">
      <div class="caller-avatar">
        <div class="avatar-ring">
          <Bot :size="48" />
        </div>
      </div>
      <h2 class="caller-name">AI 面试官</h2>
      <p class="caller-status">正在拨号...</p>
      <div class="dialing-pulse">
        <span /><span /><span />
      </div>
      <button class="answer-btn" @click="startCall">
        <Phone :size="24" /> 接听面试
      </button>
    </div>

    <div v-else-if="!isFinished" class="call-screen">
      <div class="avatar-section">
        <div class="avatar-wrapper">
          <InterviewerAvatar :size="160" :speaking="isSpeaking" />
          <div class="avatar-speech" v-if="currentQuestion">
            <p>{{ currentQuestion }}</p>
          </div>
        </div>
        <div class="caller-label">AI 面试官</div>
      </div>

      <div class="transcript-area" ref="transcriptRef">
        <div v-for="(msg, i) in transcript" :key="i" class="transcript-item" :class="msg.role">
          <span class="transcript-label">{{ msg.role === 'ai' ? '面试官' : '我' }}</span>
          <p>{{ msg.text }}</p>
        </div>
        <div v-if="isRecording" class="transcript-item user">
          <span class="transcript-label">我</span>
          <p class="listening"><span class="pulse-dot" /> 正在聆听...</p>
        </div>
      </div>

      <div class="call-controls">
        <button class="ctrl-btn" :class="{ active: micMuted }" @click="toggleMic" :disabled="submitting">
          <MicOff v-if="micMuted" :size="20" />
          <Mic v-else :size="20" />
        </button>
        <button class="ctrl-btn answer-btn big" :class="{ recording: isRecording }" @click="toggleRecording" :disabled="submitting || !currentQuestion">
          <Square v-if="isRecording" :size="20" />
          <Phone v-else :size="20" />
        </button>
        <button class="ctrl-btn" @click="showTranscript = !showTranscript">
          <MessageSquare :size="20" />
        </button>
      </div>
    </div>

    <div v-else class="finished-screen">
      <div class="result-ring">
        <span class="result-score">{{ overallScore ?? '-' }}</span>
        <span class="result-label">综合评分</span>
      </div>
      <h2>面试结束</h2>
      <p>感谢你的参与，正在生成详细报告...</p>
      <div class="result-actions">
        <button class="action-btn primary" @click="viewReport">
          <FileText :size="16" /> 查看报告
        </button>
        <button class="action-btn" @click="goBack">
          <ArrowLeft :size="16" /> 返回首页
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, nextTick, onMounted, onUnmounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import {
  ArrowLeft, Bot, Phone, PhoneOff, Mic, MicOff, Square,
  MessageSquare, FileText,
} from 'lucide-vue-next'
import { ElMessage } from 'element-plus'
import { startInterview, submitAnswer } from '@/api/interview'
import InterviewerAvatar from '@/components/interview/InterviewerAvatar.vue'
import type { SessionRecord } from '@/types/interview'

const route = useRoute()
const router = useRouter()

const sessionId = ref<number | null>(null)
const roleName = ref((route.query.role as string) || '目标岗位')
const currentQuestion = ref('')
const currentQuestionId = ref<number | null>(null)
const sessionActive = ref(false)
const isFinished = ref(false)
const isSpeaking = ref(false)
const isRecording = ref(false)
const submitting = ref(false)
const micMuted = ref(false)
const showTranscript = ref(true)
const overallScore = ref<number | null>(null)
const answeredCount = ref(0)
const maxQuestions = 5

const roleId = computed(() => Number(route.query.role_id) || 0)

interface TranscriptItem { role: 'ai' | 'user'; text: string }
const transcript = ref<TranscriptItem[]>([])
const transcriptRef = ref<HTMLElement>()

let recognition: SpeechRecognition | null = null
let synth: SpeechSynthesis | null = null

function initSpeech() {
  const SpeechRecognition = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition
  if (SpeechRecognition) {
    recognition = new SpeechRecognition()
    recognition.lang = 'zh-CN'
    recognition.continuous = false
    recognition.interimResults = true
    recognition.maxAlternatives = 1
    recognition.onresult = (e: SpeechRecognitionEvent) => {
      const last = e.results[e.results.length - 1]
      if (last.isFinal) {
        const text = last[0].transcript.trim()
        if (text) sendAnswer(text)
      }
    }
    recognition.onerror = () => { isRecording.value = false }
    recognition.onend = () => { isRecording.value = false }
  }
  synth = window.speechSynthesis
}

function startCall() {
  sessionActive.value = true
  beginInterview()
}

async function beginInterview() {
  try {
    const res = await startInterview({ occupation_role_id: roleId.value })
    const data = res.data.data
    sessionId.value = data.session_id
    if (data.first_question) {
      currentQuestionId.value = data.first_question.question_id
      currentQuestion.value = data.first_question.content
      answeredCount.value = 1
      transcript.value.push({ role: 'ai', text: data.first_question.content })
      speakText(data.first_question.content)
    }
    saveSessionToLocal(data.session_id)
  } catch {
    ElMessage.error('无法开始面试')
  }
}

function speakText(text: string) {
  if (!synth || micMuted.value) return
  isSpeaking.value = true
  synth.cancel()
  const utterance = new SpeechSynthesisUtterance(text)
  utterance.lang = 'zh-CN'
  utterance.rate = 0.9
  utterance.onend = () => {
    isSpeaking.value = false
    startListening()
  }
  utterance.onerror = () => { isSpeaking.value = false }
  synth.speak(utterance)
}

function startListening() {
  if (!recognition || micMuted.value) return
  try {
    isRecording.value = true
    recognition.start()
  } catch { isRecording.value = false }
}

function toggleMic() {
  micMuted.value = !micMuted.value
  if (micMuted.value && isRecording.value) { recognition?.stop(); isRecording.value = false }
}

function toggleRecording() {
  if (isRecording.value) { recognition?.stop(); return }
  if (!submitting.value && currentQuestion.value) startListening()
}

async function sendAnswer(text: string) {
  if (!sessionId.value || !currentQuestionId.value || submitting.value) return
  submitting.value = true
  transcript.value.push({ role: 'user', text })
  scrollTranscript()
  try {
    const res = await submitAnswer({ session_id: sessionId.value, question_id: currentQuestionId.value, answer: text })
    const data = res.data.data
    if (data.is_finished) {
      isFinished.value = true
      overallScore.value = data.overall_score
      updateLocalSession(true)
    } else if (data.next_question) {
      currentQuestionId.value = data.next_question.question_id
      currentQuestion.value = data.next_question.content
      answeredCount.value++
      transcript.value.push({ role: 'ai', text: data.next_question.content })
      scrollTranscript()
      speakText(data.next_question.content)
    }
  } catch {
    ElMessage.error('提交失败')
    if (!micMuted.value) setTimeout(() => startListening(), 1000)
  } finally { submitting.value = false }
}

function scrollTranscript() {
  nextTick(() => { if (transcriptRef.value) transcriptRef.value.scrollTop = transcriptRef.value.scrollHeight })
}

function endInterview() {
  synth?.cancel(); recognition?.stop()
  updateLocalSession(true)
  isFinished.value = true; isRecording.value = false; isSpeaking.value = false
}

function viewReport() {
  router.push({ path: '/user/interview/report', query: { session_id: String(sessionId.value) } })
}

function goBack() {
  synth?.cancel(); recognition?.stop()
  router.push('/user/interview')
}

function saveSessionToLocal(sid: number) {
  const rec: SessionRecord = { session_id: sid, role_name: roleName.value, score: null, created_at: new Date().toISOString(), is_finished: false }
  try {
    const raw = localStorage.getItem('zhihire_interview_records') || '[]'
    const recs: SessionRecord[] = JSON.parse(raw)
    recs.unshift(rec)
    localStorage.setItem('zhihire_interview_records', JSON.stringify(recs.slice(0, 20)))
  } catch { /* ignore */ }
}

function updateLocalSession(finished: boolean) {
  try {
    const raw = localStorage.getItem('zhihire_interview_records') || '[]'
    const recs: SessionRecord[] = JSON.parse(raw)
    const idx = recs.findIndex((r) => r.session_id === sessionId.value)
    if (idx >= 0) { recs[idx].is_finished = finished; recs[idx].score = overallScore.value; localStorage.setItem('zhihire_interview_records', JSON.stringify(recs)) }
  } catch { /* ignore */ }
}

onMounted(() => { initSpeech() })
onUnmounted(() => { recognition?.abort(); synth?.cancel() })
</script>

<style scoped lang="scss">
.phone-page { display: flex; flex-direction: column; height: 100vh; background: linear-gradient(180deg, #0f1923 0%, #1a2a3a 100%); color: #fff; }
.phone-header { display: flex; align-items: center; gap: 12px; padding: 12px 16px; background: rgba(0,0,0,0.3); flex-shrink: 0; }
.back-btn { width: 36px; height: 36px; border-radius: 50%; background: rgba(255,255,255,0.1); color: #fff; border: none; display: flex; align-items: center; justify-content: center; cursor: pointer; &:hover { background: rgba(255,255,255,0.2); } }
.header-info { display: flex; align-items: center; gap: 10px; flex: 1; h2 { font-size: 14px; font-weight: 600; } }
.status-dot { width: 10px; height: 10px; border-radius: 50%; flex-shrink: 0; background: #555; &.active { background: #22c55e; box-shadow: 0 0 8px rgba(34,197,94,0.5); animation: pulse 1.5s infinite; } &.idle { background: #eab308; } }
@keyframes pulse { 0%, 100% { opacity: 1; } 50% { opacity: 0.5; } }
.header-sub { font-size: 12px; color: rgba(255,255,255,0.5); }
.end-btn { display: flex; align-items: center; gap: 4px; padding: 4px 10px; border-radius: 6px; background: rgba(239,68,68,0.15); color: #ef4444; border: 1px solid rgba(239,68,68,0.3); font-size: 12px; cursor: pointer; &:hover { background: rgba(239,68,68,0.25); } }
.dialing-screen { flex: 1; display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 16px; padding: 40px 20px; }
.avatar-ring { width: 100px; height: 100px; border-radius: 50%; background: linear-gradient(135deg, #003527, #064e3b); display: flex; align-items: center; justify-content: center; box-shadow: 0 0 40px rgba(14,165,233,0.3); }
.caller-name { font-size: 22px; font-weight: 700; margin-top: 8px; }
.caller-status { font-size: 14px; color: rgba(255,255,255,0.6); }
.dialing-pulse { display: flex; gap: 8px; margin: 12px 0; span { width: 10px; height: 10px; border-radius: 50%; background: #064e3b; animation: dialPulse 1.4s infinite; &:nth-child(2) { animation-delay: 0.2s; } &:nth-child(3) { animation-delay: 0.4s; } } }
@keyframes dialPulse { 0%, 100% { transform: scale(0.5); opacity: 0.3; } 50% { transform: scale(1); opacity: 1; } }
.answer-btn { display: flex; align-items: center; gap: 10px; padding: 14px 36px; border-radius: 999px; border: none; background: #22c55e; color: #fff; font-size: 16px; font-weight: 600; cursor: pointer; margin-top: 20px; &:hover { background: #16a34a; } }
.call-screen { flex: 1; display: flex; flex-direction: column; align-items: center; padding: 20px 16px 24px; gap: 16px; overflow: hidden; }
.avatar-section { display: flex; flex-direction: column; align-items: center; gap: 8px; flex-shrink: 0; }
.caller-label { font-size: 13px; color: rgba(255,255,255,0.5); }
.avatar-wrapper { position: relative; display: inline-flex; }
.avatar-speech {
  position: absolute; top: -10px; left: 110%;
  min-width: 200px; max-width: 300px;
  padding: 10px 14px; border-radius: 12px;
  background: rgba(255,255,255,0.12); backdrop-filter: blur(8px);
  border: 1px solid rgba(255,255,255,0.15);
  font-size: 13px; line-height: 1.6;
  p { margin: 0; color: rgba(255,255,255,0.95); }
  &::before {
    content: ''; position: absolute; top: 20px; left: -8px;
    width: 0; height: 0;
    border-top: 8px solid transparent;
    border-bottom: 8px solid transparent;
    border-right: 8px solid rgba(255,255,255,0.12);
  }
}
.transcript-area { flex: 1; width: 100%; max-width: 500px; overflow-y: auto; display: flex; flex-direction: column; gap: 8px; padding: 8px 0; &::-webkit-scrollbar { width: 3px; } &::-webkit-scrollbar-thumb { background: rgba(255,255,255,0.2); border-radius: 3px; } }
.transcript-item { padding: 10px 14px; border-radius: 12px; background: rgba(255,255,255,0.05); max-width: 90%; &.user { align-self: flex-end; background: rgba(14,165,233,0.15); } }
.transcript-label { font-size: 11px; color: rgba(255,255,255,0.4); display: block; margin-bottom: 4px; }
.transcript-item p { margin: 0; font-size: 13px; line-height: 1.5; color: rgba(255,255,255,0.9); }
.listening { display: flex; align-items: center; gap: 6px; }
.pulse-dot { width: 6px; height: 6px; border-radius: 50%; background: #22c55e; animation: pulse 1s infinite; }
.call-controls { display: flex; align-items: center; gap: 24px; padding: 12px 0; flex-shrink: 0; }
.ctrl-btn { width: 48px; height: 48px; border-radius: 50%; background: rgba(255,255,255,0.1); color: #fff; border: none; display: flex; align-items: center; justify-content: center; cursor: pointer; transition: all 0.2s; &:hover { background: rgba(255,255,255,0.2); } &:disabled { opacity: 0.3; cursor: not-allowed; } &.active { background: rgba(239,68,68,0.3); color: #ef4444; } &.big { width: 56px; height: 56px; } &.recording { background: rgba(239,68,68,0.4); color: #ef4444; box-shadow: 0 0 20px rgba(239,68,68,0.3); } }
.ctrl-btn.answer-btn.big { background: #22c55e; color: #fff; &:hover { background: #16a34a; } &.recording:hover { background: #dc2626; } }
.finished-screen { flex: 1; display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 16px; padding: 40px 20px; }
.result-ring { width: 120px; height: 120px; border-radius: 50%; background: linear-gradient(135deg, #003527, #064e3b); display: flex; flex-direction: column; align-items: center; justify-content: center; box-shadow: 0 0 40px rgba(14,165,233,0.3); }
.result-score { font-size: 36px; font-weight: 700; }
.result-label { font-size: 12px; color: rgba(255,255,255,0.7); }
.finished-screen h2 { font-size: 22px; font-weight: 700; }
.finished-screen p { font-size: 14px; color: rgba(255,255,255,0.6); }
.result-actions { display: flex; gap: 12px; margin-top: 8px; }
.action-btn { display: flex; align-items: center; gap: 6px; padding: 10px 24px; border-radius: 999px; border: 1px solid rgba(255,255,255,0.2); background: transparent; color: #fff; font-size: 14px; cursor: pointer; &:hover { background: rgba(255,255,255,0.1); } &.primary { background: #003527; border-color: #003527; &:hover { background: #064e3b; } } }
</style>
