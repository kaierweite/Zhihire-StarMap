<template>
  <div class="video-page">
    <!-- 顶部导航栏 -->
    <div class="video-header">
      <div class="header-left">
        <h2>{{ roleName }}面试</h2>
        <span class="timer">剩余时间 {{ formatTime(remainingTime) }}</span>
      </div>
      <div class="header-center">
        <div class="interviewer-mini-avatar">
          <User :size="18" />
        </div>
        <span class="interviewer-name">AI 技术面试官</span>
      </div>
      <div class="header-right">
        <span class="recording-badge" :class="{ active: sessionActive }">
          <span class="recording-dot" /> 正在录制
        </span>
        <button class="header-btn" @click="testDevices"><Settings :size="16" /> 设备测试</button>
        <button class="header-btn"><HelpCircle :size="16" /></button>
        <button class="exit-btn" @click="endInterview">退出面试</button>
      </div>
    </div>

    <div class="main-content">
      <!-- 左侧视频区域 -->
      <div class="video-area">
        <!-- 准备阶段 -->
        <div v-if="!sessionActive && !isFinished" class="pre-call">
          <div class="pre-call-content">
            <h2>准备面试</h2>
            <p>请允许摄像头和麦克风权限以开始面试</p>
            
            <div class="device-preview">
              <video ref="localVideo" class="camera-preview" autoplay playsinline muted />
              <div v-if="!cameraReady" class="camera-placeholder">
                <Camera :size="48" />
                <p>摄像头未开启</p>
              </div>
            </div>

            <div class="device-controls">
              <label class="device-item">
                <Camera :size="18" />
                <span>摄像头</span>
                <input type="checkbox" v-model="cameraEnabled" @change="toggleCamera" />
              </label>
              <label class="device-item">
                <Mic :size="18" />
                <span>麦克风</span>
                <input type="checkbox" v-model="micEnabled" @change="toggleMicEnabled" />
              </label>
            </div>

            <button class="start-btn" @click="startCall">
              <Video :size="20" /> 开始面试
            </button>
          </div>
        </div>

        <!-- 面试进行中 -->
        <div v-else-if="!isFinished" class="active-interview">
          <!-- 虚拟办公室背景 -->
          <div class="virtual-background">
            <!-- 墙壁 -->
            <div class="wall" />
            
            <!-- 窗户 -->
            <div class="window">
              <div class="window-frame">
                <div class="window-pane" />
                <div class="window-pane" />
                <div class="window-pane" />
                <div class="window-pane" />
              </div>
              <div class="window-light" />
            </div>
            
            <!-- 书架 -->
            <div class="bookshelf">
              <div class="book-row">
                <div class="book" style="background: #c0392b" />
                <div class="book" style="background: #2c3e50" />
                <div class="book" style="background: #e67e22" />
                <div class="book" style="background: #3498db" />
                <div class="book" style="background: #9b59b6" />
                <div class="book" style="background: #1abc9c" />
              </div>
              <div class="book-row">
                <div class="book" style="background: #f39c12" />
                <div class="book" style="background: #27ae60" />
                <div class="book" style="background: #8e44ad" />
                <div class="book" style="background: #16a085" />
                <div class="book" style="background: #d35400" />
              </div>
            </div>

            <!-- 办公桌上的物品 -->
            <div class="desk-items">
              <div class="computer-monitor">
                <div class="monitor-screen" />
                <div class="monitor-stand" />
              </div>
              <div class="desk-lamp" />
              <div class="notebook" />
            </div>

            <!-- 面试官 -->
            <div class="interviewer-area">
              <InterviewerAvatar :size="420" :isTalking="isSpeaking" :isListening="isRecording" />
            </div>

            <!-- 前景桌面 -->
            <div class="foreground-desk">
              <div class="desk-surface" />
              <div class="keyboard" />
              <div class="mouse" />
              <div class="coffee-cup">
                <div class="cup-body" />
                <div class="cup-handle" />
                <div class="cup-lid" />
              </div>
              <div class="nameplate">
                <span>AI 技术面试官</span>
              </div>
            </div>
          </div>

          <!-- 画中画 - 自己的画面 -->
          <div class="pip-window" :class="{ hidden: !cameraEnabled }">
            <video ref="localVideo" class="pip-video" autoplay playsinline muted />
            <span class="pip-label">我</span>
          </div>

          <!-- 视频覆盖层 -->
          <div class="video-overlay">
            <div class="connection-status" :class="{ stable: connectionStable }">
              <Wifi :size="14" /> 连接{{ connectionStable ? '稳定' : '不稳定' }}
            </div>
          </div>

          <!-- 状态指示器 -->
          <div class="status-indicator">
            <span class="status-text">{{ isSpeaking ? '正在提问...' : isRecording ? '正在聆听...' : '请回答' }}</span>
          </div>

          <!-- 底部控制栏（覆盖层） -->
          <div class="video-controls" v-if="sessionActive && !isFinished">
            <button class="control-btn" :class="{ off: micMuted }" @click="toggleMic">
              <Mic v-if="!micMuted" :size="20" />
              <MicOff v-else :size="20" />
              <span>麦克风</span>
            </button>
            <button class="control-btn" :class="{ off: !cameraEnabled }" @click="toggleCamera">
              <Video v-if="cameraEnabled" :size="20" />
              <VideoOff v-else :size="20" />
              <span>摄像头</span>
            </button>
            <button class="control-btn">
              <Monitor :size="20" />
              <span>屏幕共享</span>
            </button>
            <button class="control-btn" @click="activeTab = 'participants'">
              <Users :size="20" />
              <span>参会人员</span>
            </button>
            <button class="control-btn recording-btn" :class="{ active: isRecording }" @click="toggleRecording">
              <Square v-if="isRecording" :size="18" />
              <Circle v-else :size="18" />
              <span>{{ isRecording ? '停止录制' : '开始录制' }}</span>
            </button>
            <button class="control-btn hangup-btn" @click="endInterview">
              <PhoneOff :size="20" />
              <span>挂断</span>
            </button>
          </div>
        </div>

        <!-- 面试结束 -->
        <div v-else class="finished-screen">
          <div class="finished-content">
            <div class="result-badge">
              <span class="result-score">{{ overallScore ?? '-' }}</span>
              <span class="result-label">综合得分</span>
            </div>
            <h2>面试结束</h2>
            <p>正在生成详细报告</p>
            <div class="finished-actions">
              <button class="action-btn primary" @click="viewReport">
                <FileText :size="16" /> 查看报告
              </button>
              <button class="action-btn" @click="goBack">
                <Home :size="16" /> 返回首页
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- 右侧消息面板 -->
      <div class="side-panel" v-if="sessionActive && !isFinished">
        <div class="panel-tabs">
          <button class="tab-btn active" @click="activeTab = 'chat'"><MessageSquare :size="14" /> 消息</button>
          <button class="tab-btn" @click="activeTab = 'participants'"><Users :size="14" /> 参会人员 ({{ participantCount }})</button>
        </div>

        <!-- 消息列表 -->
        <div v-if="activeTab === 'chat'" class="chat-panel">
          <div class="chat-messages">
            <div class="system-message">
              <span class="msg-time">上午 10:02</span>
              <p>录制已开始，AI 面试官已就位</p>
            </div>
            <div class="chat-message ai">
              <div class="msg-avatar ai">
                <User :size="16" />
              </div>
              <div class="msg-content">
                <span class="msg-name">AI 面试官</span>
                <p>你好！欢迎参加本次面试。我将提出几个问题，请你逐一回答。准备好了吗？</p>
              </div>
            </div>
            <div v-for="(msg, i) in chatMessages" :key="i" class="chat-message" :class="msg.role">
              <div v-if="msg.role === 'user'" class="msg-avatar user">
                <User :size="20" />
              </div>
              <div v-else class="msg-avatar ai">
                <User :size="16" />
              </div>
              <div class="msg-content">
                <span class="msg-name">{{ msg.role === 'user' ? '我' : 'AI 面试官' }}</span>
                <p>{{ msg.text }}</p>
              </div>
            </div>
          </div>
          <div class="chat-input">
            <input v-model="chatInput" type="text" placeholder="输入消息..." @keydown.enter="sendChatMessage" />
            <button class="send-btn" :disabled="!chatInput.trim()" @click="sendChatMessage">
              <Send :size="16" />
            </button>
          </div>
        </div>

        <!-- 参会人员 -->
        <div v-if="activeTab === 'participants'" class="participants-panel">
          <div class="participant-item">
            <div class="participant-mini-avatar">
              <User :size="18" />
            </div>
            <div>
              <span class="participant-name">AI 技术面试官</span>
              <span class="participant-role">面试官</span>
            </div>
            <span class="participant-status online" />
          </div>
          <div class="participant-item">
            <div class="user-avatar">
              <User :size="20" />
            </div>
            <div>
              <span class="participant-name">我</span>
              <span class="participant-role">面试者</span>
            </div>
            <span class="participant-status online" />
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, nextTick, onMounted, onUnmounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { 
  ArrowLeft, Camera, CameraOff, Mic, MicOff, Phone, PhoneOff, Square, Video, 
  Keyboard, Send, FileText, Home, Settings, HelpCircle, Wifi, MessageSquare, 
  Users, User, Monitor, Circle, VideoOff 
} from 'lucide-vue-next'
import { ElMessage } from 'element-plus'
import { startInterview, submitAnswer } from '@/api/interview'
import InterviewerAvatar from '@/components/interview/InterviewerAvatar.vue'
import type { SessionRecord } from '@/types/interview'

const route = useRoute()
const router = useRouter()

const localVideo = ref<HTMLVideoElement>()
let mediaStream: MediaStream | null = null
const cameraReady = ref(false)
const cameraEnabled = ref(true)
const micEnabled = ref(true)
const micMuted = ref(false)
const connectionStable = ref(true)

const sessionId = ref<number | null>(null)
const roleName = ref((route.query.role as string) || '高级软件工程师')
const currentQuestion = ref('')
const currentQuestionId = ref<number | null>(null)
const sessionActive = ref(false)
const isFinished = ref(false)
const isSpeaking = ref(false)
const isRecording = ref(false)
const submitting = ref(false)
const overallScore = ref<number | null>(null)
const answeredCount = ref(0)
const maxQuestions = 5
const remainingTime = ref(45 * 60) // 45分钟

const roleId = computed(() => Number(route.query.role_id) || 0)
const participantCount = ref(2)
const activeTab = ref<'chat' | 'participants'>('chat')
const chatInput = ref('')

interface TranscriptItem { role: 'ai' | 'user'; text: string }
const transcript = ref<TranscriptItem[]>([])
const transcriptRef = ref<HTMLElement>()

interface ChatMessage { role: 'ai' | 'user'; text: string }
const chatMessages = ref<ChatMessage[]>([])

let recognition: SpeechRecognition | null = null
let synth: SpeechSynthesis | null = null
let timerInterval: ReturnType<typeof setInterval> | null = null

function formatTime(seconds: number): string {
  const mins = Math.floor(seconds / 60)
  const secs = seconds % 60
  return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`
}

async function toggleCamera() {
  cameraEnabled.value = !cameraEnabled.value
  if (cameraEnabled.value && !cameraReady.value) await initCamera()
  else if (!cameraEnabled.value && mediaStream) mediaStream.getVideoTracks().forEach((t) => (t.enabled = false))
  else if (cameraEnabled.value && mediaStream) mediaStream.getVideoTracks().forEach((t) => (t.enabled = true))
}

function toggleMicEnabled() {
  micEnabled.value = !micEnabled.value
  if (!micEnabled.value) micMuted.value = true
}

async function initCamera() {
  try {
    mediaStream = await navigator.mediaDevices.getUserMedia({ 
      video: { width: { ideal: 640 }, height: { ideal: 480 }, facingMode: 'user' }, 
      audio: false 
    })
    if (localVideo.value) localVideo.value.srcObject = mediaStream
    cameraReady.value = true
  } catch {
    cameraEnabled.value = false
  }
}

function initSpeech() {
  const SR = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition
  if (SR) {
    recognition = new SR()
    recognition.lang = 'zh-CN'
    recognition.continuous = false
    recognition.interimResults = true
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

async function startCall() {
  sessionActive.value = true
  isRecording.value = true
  startTimer()
  beginInterview()
}

function startTimer() {
  timerInterval = setInterval(() => {
    if (remainingTime.value > 0) {
      remainingTime.value--
    } else {
      endInterview()
    }
  }, 1000)
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
      chatMessages.value.push({ role: 'ai', text: data.first_question.content })
      speakText(data.first_question.content)
    }
    saveSessionToLocal(data.session_id)
  } catch { ElMessage.error('无法开始面试') }
}

function speakText(text: string) {
  if (!synth) return
  isSpeaking.value = true; synth.cancel()
  const u = new SpeechSynthesisUtterance(text)
  u.lang = 'zh-CN'; u.rate = 0.9
  u.onend = () => { isSpeaking.value = false; setTimeout(() => startListening(), 500) }
  u.onerror = () => { isSpeaking.value = false }
  synth.speak(u)
}

function startListening() {
  if (!recognition || micMuted.value) return
  try { isRecording.value = true; recognition.start() } catch { isRecording.value = false }
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
  transcript.value.push({ role: 'user', text }); scrollTranscript()
  chatMessages.value.push({ role: 'user', text })
  try {
    const res = await submitAnswer({ session_id: sessionId.value, question_id: currentQuestionId.value, answer: text })
    const data = res.data.data
    if (data.is_finished) {
      isFinished.value = true; overallScore.value = data.overall_score; updateLocalSession(true)
      stopTimer()
    } else if (data.next_question) {
      currentQuestionId.value = data.next_question.question_id
      currentQuestion.value = data.next_question.content
      answeredCount.value++
      chatMessages.value.push({ role: 'ai', text: data.next_question.content })
      scrollTranscript(); speakText(data.next_question.content)
    }
  } catch { ElMessage.error('提交失败'); if (!micMuted.value) setTimeout(() => startListening(), 1000) }
  finally { submitting.value = false }
}

function sendChatMessage() {
  const text = chatInput.value.trim()
  if (!text) return
  chatMessages.value.push({ role: 'user', text })
  chatInput.value = ''
}

function scrollTranscript() { 
  nextTick(() => { 
    if (transcriptRef.value) transcriptRef.value.scrollTop = transcriptRef.value.scrollHeight 
  }) 
}

function stopTimer() {
  if (timerInterval) {
    clearInterval(timerInterval)
    timerInterval = null
  }
}

function endInterview() { 
  synth?.cancel(); recognition?.stop(); stopTimer()
  updateLocalSession(true); isFinished.value = true; 
  isRecording.value = false; isSpeaking.value = false 
}

function viewReport() { 
  router.push({ path: '/user/interview/report', query: { session_id: String(sessionId.value) } }) 
}

function goBack() { 
  synth?.cancel(); recognition?.stop(); stopTimer()
  if (mediaStream) mediaStream.getTracks().forEach((t) => t.stop())
  router.push('/user/interview') 
}

function testDevices() {
  ElMessage.info('设备测试功能开发中')
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
    if (idx >= 0) { 
      recs[idx].is_finished = finished; recs[idx].score = overallScore.value
      localStorage.setItem('zhihire_interview_records', JSON.stringify(recs)) 
    } 
  } catch { /* ignore */ }
}

onMounted(async () => { 
  if (cameraEnabled.value) await initCamera()
  initSpeech() 
})

onUnmounted(() => { 
  recognition?.abort(); synth?.cancel(); stopTimer()
  if (mediaStream) mediaStream.getTracks().forEach((t) => t.stop()) 
})
</script>

<style scoped lang="scss">
.video-page { 
  display: flex; 
  flex-direction: column; 
  height: 100vh; 
  background: #f5f5f5; 
  color: #333;
}

/* 顶部导航栏 */
.video-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 20px;
  background: #fff;
  border-bottom: 1px solid #e0e0e0;
  flex-shrink: 0;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 16px;
  h2 {
    font-size: 16px;
    font-weight: 600;
    margin: 0;
    color: #1a3a5c;
  }
}

.timer {
  font-size: 13px;
  color: #666;
  background: #f0f0f0;
  padding: 4px 12px;
  border-radius: 999px;
}

.header-center {
  display: flex;
  align-items: center;
  gap: 8px;
}

.interviewer-name {
  font-size: 14px;
  font-weight: 500;
  color: #333;
}

.interviewer-mini-avatar {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background: linear-gradient(135deg, #1a3a5c, #0ea5e9);
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 12px;
}

.recording-badge {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 4px 12px;
  border-radius: 999px;
  background: #f0f0f0;
  font-size: 12px;
  color: #666;
  
  &.active {
    background: rgba(239, 68, 68, 0.1);
    color: #ef4444;
  }
}

.recording-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #999;
  
  .active & {
    background: #ef4444;
    animation: pulse 1.5s infinite;
  }
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}

.header-btn {
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 6px 12px;
  border-radius: 6px;
  border: 1px solid #e0e0e0;
  background: #fff;
  font-size: 12px;
  color: #666;
  cursor: pointer;
  
  &:hover {
    background: #f8f9fa;
  }
}

.exit-btn {
  padding: 6px 16px;
  border-radius: 6px;
  border: none;
  background: #dc3545;
  color: #fff;
  font-size: 12px;
  font-weight: 500;
  cursor: pointer;
  
  &:hover {
    background: #c82333;
  }
}

/* 主内容区域 */
.main-content {
  flex: 1;
  display: flex;
  overflow: hidden;
}

.video-area {
  flex: 1;
  display: flex;
  flex-direction: column;
  position: relative;
  background: #1a1a2e;
}

/* 准备阶段 */
.pre-call {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
}

.pre-call-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 24px;
  padding: 40px;
}

.pre-call-content h2 {
  font-size: 24px;
  font-weight: 700;
  color: #fff;
  margin: 0;
}

.pre-call-content p {
  font-size: 14px;
  color: rgba(255, 255, 255, 0.6);
  margin: 0;
}

.device-preview {
  width: 320px;
  height: 240px;
  border-radius: 12px;
  overflow: hidden;
  background: #2a2a4a;
  position: relative;
}

.camera-preview {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.camera-placeholder {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 12px;
  color: rgba(255, 255, 255, 0.3);
}

.device-controls {
  display: flex;
  gap: 32px;
}

.device-item {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  color: rgba(255, 255, 255, 0.8);
  cursor: pointer;
  
  input {
    width: 18px;
    height: 18px;
    accent-color: #0ea5e9;
  }
}

.start-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 14px 40px;
  border-radius: 999px;
  border: none;
  background: #0ea5e9;
  color: #fff;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  
  &:hover {
    background: #0284c7;
  }
}

/* 面试进行中 */
.active-interview {
  flex: 1;
  display: flex;
  flex-direction: column;
  position: relative;
  overflow: hidden;
}

.main-video {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
}

/* 虚拟办公室背景 */
.virtual-background {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  width: 100%;
  height: 100%;
  overflow: hidden;
}

.wall {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 30%;
  background: linear-gradient(180deg, #e8e8e8 0%, #d5d5d5 40%, #c8c8c8 100%);
}

.wall::before {
  content: '';
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  height: 60px;
  background: linear-gradient(180deg, transparent, rgba(0,0,0,0.05));
}

.window {
  position: absolute;
  top: 30px;
  right: 80px;
  width: 220px;
  height: 180px;
}

.window-frame {
  position: relative;
  width: 100%;
  height: 100%;
  background: #2c3e50;
  border-radius: 8px;
  padding: 8px;
  box-shadow: 0 4px 20px rgba(0,0,0,0.2);
}

.window-pane {
  position: absolute;
  background: linear-gradient(135deg, #87ceeb 0%, #5dade2 50%, #3498db 100%);
  
  &:nth-child(1) {
    top: 8px;
    left: 8px;
    width: calc(50% - 6px);
    height: calc(50% - 6px);
    border-radius: 4px 0 0 0;
  }
  &:nth-child(2) {
    top: 8px;
    right: 8px;
    width: calc(50% - 6px);
    height: calc(50% - 6px);
    border-radius: 0 4px 0 0;
  }
  &:nth-child(3) {
    bottom: 8px;
    left: 8px;
    width: calc(50% - 6px);
    height: calc(50% - 6px);
    border-radius: 0 0 0 4px;
  }
  &:nth-child(4) {
    bottom: 8px;
    right: 8px;
    width: calc(50% - 6px);
    height: calc(50% - 6px);
    border-radius: 0 0 4px 0;
  }
}

.window-frame::before {
  content: '';
  position: absolute;
  top: 8px;
  left: 50%;
  transform: translateX(-50%);
  width: 4px;
  height: calc(100% - 16px);
  background: #2c3e50;
}

.window-frame::after {
  content: '';
  position: absolute;
  left: 8px;
  top: 50%;
  transform: translateY(-50%);
  width: calc(100% - 16px);
  height: 4px;
  background: #2c3e50;
}

.window-light {
  position: absolute;
  top: -10px;
  right: -10px;
  width: 240px;
  height: 200px;
  background: radial-gradient(ellipse at center, rgba(255,255,255,0.15) 0%, transparent 70%);
  pointer-events: none;
}

.bookshelf {
  position: absolute;
  top: 50px;
  left: 40px;
  width: 160px;
  height: 200px;
  background: #8b6914;
  border-radius: 4px;
  padding: 10px;
  box-shadow: 0 4px 15px rgba(0,0,0,0.15);
}

.book-row {
  display: flex;
  gap: 4px;
  margin-bottom: 12px;
  
  &:last-child {
    margin-bottom: 0;
  }
}

.book {
  flex: 1;
  height: 70px;
  border-radius: 2px;
  box-shadow: 2px 0 4px rgba(0,0,0,0.2);
}

.desk-items {
  position: absolute;
  bottom: 25%;
  right: 40px;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.computer-monitor {
  width: 120px;
  height: 80px;
  
  .monitor-screen {
    width: 100%;
    height: 70px;
    background: #1a1a2e;
    border-radius: 6px 6px 0 0;
    border: 3px solid #3d3d3d;
    position: relative;
    
    &::before {
      content: '';
      position: absolute;
      top: 5px;
      left: 5px;
      right: 5px;
      bottom: 5px;
      background: linear-gradient(135deg, rgba(52, 152, 219, 0.1) 0%, rgba(52, 152, 219, 0.05) 100%);
    }
  }
  
  .monitor-stand {
    width: 20px;
    height: 15px;
    background: #3d3d3d;
    margin: 0 auto;
  }
}

.desk-lamp {
  width: 10px;
  height: 40px;
  background: #3d3d3d;
  position: relative;
  left: 80px;
  
  &::before {
    content: '';
    position: absolute;
    top: -15px;
    left: -15px;
    width: 40px;
    height: 15px;
    background: #f39c12;
    border-radius: 5px;
  }
  
  &::after {
    content: '';
    position: absolute;
    top: -50px;
    left: -40px;
    width: 80px;
    height: 60px;
    background: radial-gradient(ellipse at center, rgba(255, 240, 180, 0.3) 0%, transparent 70%);
    pointer-events: none;
  }
}

.notebook {
  width: 60px;
  height: 8px;
  background: #e67e22;
  border-radius: 2px;
  position: relative;
  left: 20px;
  
  &::before {
    content: '';
    position: absolute;
    top: -30px;
    left: 0;
    width: 100%;
    height: 30px;
    background: #fff;
    border-radius: 2px;
    border: 1px solid #ddd;
  }
}

.interviewer-area {
  position: absolute;
  bottom: 28%;
  left: 50%;
  transform: translateX(-50%);
  z-index: 2;
  filter: saturate(0.85) contrast(0.98) brightness(1.01);
}

.foreground-desk {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  height: 22%;
  z-index: 3;
}

.desk-surface {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 100%;
  background: linear-gradient(180deg, #8b7355 0%, #6b5344 40%, #5a4535 100%);
  border-radius: 4px 4px 0 0;
}

.desk-surface::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 8px;
  background: linear-gradient(180deg, #a08060, #8b7355);
  border-radius: 4px 4px 0 0;
}

.keyboard {
  position: absolute;
  top: 20px;
  left: 50%;
  transform: translateX(-50%);
  width: 280px;
  height: 45px;
  background: #2c2c2c;
  border-radius: 4px;
  padding: 5px;
  display: flex;
  flex-wrap: wrap;
  gap: 3px;
}

.keyboard::before {
  content: '';
  position: absolute;
  top: 5px;
  left: 5px;
  right: 5px;
  bottom: 5px;
  display: flex;
  flex-wrap: wrap;
  gap: 2px;
  align-content: flex-start;
  
  &::before {
    content: '';
    width: 100%;
    height: 100%;
    background: repeating-linear-gradient(
      0deg,
      transparent,
      transparent 18px,
      #1a1a1a 18px,
      #1a1a1a 20px
    );
    opacity: 0.5;
  }
}

.mouse {
  position: absolute;
  top: 25px;
  right: 120px;
  width: 40px;
  height: 30px;
  background: #3d3d3d;
  border-radius: 6px;
}

.coffee-cup {
  position: absolute;
  top: 15px;
  right: 40px;
  width: 35px;
  height: 40px;
  
  .cup-body {
    position: absolute;
    bottom: 0;
    left: 2px;
    width: 28px;
    height: 32px;
    background: #f5f5f5;
    border-radius: 4px 4px 8px 8px;
    border: 2px solid #ccc;
  }
  
  .cup-handle {
    position: absolute;
    bottom: 8px;
    right: -8px;
    width: 12px;
    height: 18px;
    border: 3px solid #ccc;
    border-left: none;
    border-radius: 0 6px 6px 0;
  }
  
  .cup-lid {
    position: absolute;
    top: 0;
    left: 0;
    width: 35px;
    height: 8px;
    background: #d5d5d5;
    border-radius: 4px;
  }
}

.nameplate {
  position: absolute;
  top: 20px;
  left: 60px;
  padding: 6px 16px;
  background: #fff;
  border-radius: 4px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.15);
  
  span {
    font-size: 12px;
    font-weight: 600;
    color: #333;
  }
}

.video-overlay {
  position: absolute;
  top: 16px;
  left: 16px;
}

.connection-status {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 6px 12px;
  border-radius: 999px;
  background: rgba(239, 68, 68, 0.2);
  color: #ef4444;
  font-size: 12px;
  
  &.stable {
    background: rgba(34, 197, 94, 0.2);
    color: #22c55e;
  }
}

.pip-window {
  position: absolute;
  top: 16px;
  right: 16px;
  width: 180px;
  height: 135px;
  border-radius: 8px;
  overflow: hidden;
  background: #000;
  border: 2px solid rgba(255, 255, 255, 0.2);
  
  &.hidden {
    display: none;
  }
}

.pip-video {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.pip-label {
  position: absolute;
  bottom: 4px;
  left: 50%;
  transform: translateX(-50%);
  font-size: 10px;
  color: rgba(255, 255, 255, 0.7);
  background: rgba(0, 0, 0, 0.6);
  padding: 2px 8px;
  border-radius: 999px;
}

.question-panel {
  position: absolute;
  bottom: 120px;
  left: 16px;
  right: 220px;
  background: rgba(0, 0, 0, 0.85);
  border-radius: 12px;
  padding: 16px 20px;
}

.question-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

/* 状态指示器 */
.status-indicator {
  position: absolute;
  bottom: 26%;
  left: 50%;
  transform: translateX(-50%);
  padding: 8px 20px;
  background: rgba(0, 0, 0, 0.7);
  border-radius: 999px;
  z-index: 4;
}

.status-text {
  font-size: 14px;
  color: #0ea5e9;
  font-weight: 500;
}

/* 面试结束 */
.finished-screen {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
}

.finished-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 16px;
}

.result-badge {
  width: 120px;
  height: 120px;
  border-radius: 50%;
  background: linear-gradient(135deg, #1a3a5c, #0ea5e9);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  box-shadow: 0 0 30px rgba(14, 165, 233, 0.3);
}

.result-score {
  font-size: 36px;
  font-weight: 700;
  color: #fff;
}

.result-label {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.8);
}

.finished-content h2 {
  font-size: 24px;
  font-weight: 700;
  color: #fff;
  margin: 0;
}

.finished-content p {
  font-size: 14px;
  color: rgba(255, 255, 255, 0.6);
  margin: 0;
}

.finished-actions {
  display: flex;
  gap: 12px;
  margin-top: 8px;
}

.action-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 12px 28px;
  border-radius: 999px;
  border: 1px solid rgba(255, 255, 255, 0.3);
  background: transparent;
  color: #fff;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  
  &:hover {
    background: rgba(255, 255, 255, 0.1);
  }
  
  &.primary {
    background: #1a3a5c;
    border-color: #1a3a5c;
    
    &:hover {
      background: #24507a;
    }
  }
}

/* 右侧消息面板 */
.side-panel {
  width: 320px;
  background: #fff;
  border-left: 1px solid #e0e0e0;
  display: flex;
  flex-direction: column;
}

.panel-tabs {
  display: flex;
  border-bottom: 1px solid #e0e0e0;
}

.tab-btn {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 4px;
  padding: 12px;
  border: none;
  background: #fff;
  font-size: 13px;
  color: #666;
  cursor: pointer;
  border-bottom: 2px solid transparent;
  
  &.active {
    color: #1a3a5c;
    font-weight: 600;
    border-bottom-color: #1a3a5c;
  }
}

/* 聊天面板 */
.chat-panel {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.chat-messages {
  flex: 1;
  overflow-y: auto;
  padding: 12px;
  
  &::-webkit-scrollbar {
    width: 4px;
  }
  
  &::-webkit-scrollbar-thumb {
    background: #e0e0e0;
    border-radius: 4px;
  }
}

.system-message {
  text-align: center;
  margin-bottom: 12px;
  
  .msg-time {
    font-size: 11px;
    color: #999;
  }
  
  p {
    font-size: 12px;
    color: #999;
    margin: 4px 0 0 0;
  }
}

.chat-message {
  display: flex;
  gap: 8px;
  margin-bottom: 12px;
  
  &.ai {
    .msg-content {
      background: #f0f4f8;
      border-radius: 0 12px 12px 12px;
    }
  }
  
  &.user {
    flex-direction: row-reverse;
    
    .msg-content {
      background: #1a3a5c;
      color: #fff;
      border-radius: 12px 0 12px 12px;
      
      .msg-name {
        color: rgba(255, 255, 255, 0.7);
      }
      
      p {
        color: #fff;
      }
    }
  }
}

.msg-avatar {
  flex-shrink: 0;
  
  &.user {
    width: 32px;
    height: 32px;
    border-radius: 50%;
    background: #e0e0e0;
    display: flex;
    align-items: center;
    justify-content: center;
    color: #666;
  }
  
  &.ai {
    width: 32px;
    height: 32px;
    border-radius: 50%;
    background: linear-gradient(135deg, #1a3a5c, #0ea5e9);
    display: flex;
    align-items: center;
    justify-content: center;
    color: #fff;
  }
}

.msg-content {
  max-width: 75%;
  padding: 10px 14px;
  
  .msg-name {
    font-size: 11px;
    font-weight: 600;
    color: #666;
    margin-bottom: 4px;
    display: block;
  }
  
  p {
    font-size: 13px;
    color: #333;
    margin: 0;
    line-height: 1.4;
  }
}

.chat-input {
  display: flex;
  gap: 8px;
  padding: 12px;
  border-top: 1px solid #e0e0e0;
}

.chat-input input {
  flex: 1;
  padding: 10px 14px;
  border-radius: 20px;
  border: 1px solid #e0e0e0;
  font-size: 13px;
  outline: none;
  
  &:focus {
    border-color: #1a3a5c;
  }
  
  &::placeholder {
    color: #999;
  }
}

.send-btn {
  width: 38px;
  height: 38px;
  border-radius: 50%;
  background: #1a3a5c;
  color: #fff;
  border: none;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  
  &:hover:not(:disabled) {
    background: #24507a;
  }
  
  &:disabled {
    opacity: 0.4;
    cursor: not-allowed;
  }
}

/* 参会人员面板 */
.participants-panel {
  flex: 1;
  padding: 12px;
  overflow-y: auto;
}

.participant-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 10px;
  border-radius: 8px;
  
  &:hover {
    background: #f8f9fa;
  }
}

.user-avatar {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background: #e0e0e0;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #666;
}

.participant-mini-avatar {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background: linear-gradient(135deg, #1a3a5c, #0ea5e9);
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
}

.participant-name {
  display: block;
  font-size: 13px;
  font-weight: 500;
  color: #333;
}

.participant-role {
  display: block;
  font-size: 11px;
  color: #999;
}

.participant-status {
  margin-left: auto;
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #ccc;
  
  &.online {
    background: #22c55e;
  }
}

/* 底部控制栏（覆盖层） */
.video-controls {
  position: absolute;
  bottom: 24%;
  left: 0;
  right: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 16px;
  padding: 12px 20px;
  background: rgba(0, 0, 0, 0.5);
  backdrop-filter: blur(8px);
  z-index: 5;
}

.control-btn {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
  padding: 10px 18px;
  border-radius: 12px;
  border: none;
  background: rgba(255, 255, 255, 0.15);
  color: #fff;
  font-size: 11px;
  cursor: pointer;
  transition: all 0.2s;
  
  &:hover {
    background: rgba(255, 255, 255, 0.25);
  }
  
  &.off {
    background: rgba(239, 68, 68, 0.3);
    color: #ef4444;
  }
  
  &.recording-btn {
    background: rgba(239, 68, 68, 0.3);
    color: #ef4444;
    
    &.active {
      background: #ef4444;
      color: #fff;
    }
  }
  
  &.hangup-btn {
    background: rgba(239, 68, 68, 0.3);
    color: #ef4444;
    
    &:hover {
      background: #ef4444;
      color: #fff;
    }
  }
}

/* 响应式布局 */
@media (max-width: 1024px) {
  .side-panel {
    display: none;
  }
  
  .question-panel,
  .transcript-panel {
    right: 16px;
  }
}

@media (max-width: 640px) {
  .video-header {
    padding: 10px 12px;
    
    .header-left h2 {
      font-size: 14px;
    }
    
    .timer {
      display: none;
    }
    
    .interviewer-name {
      display: none;
    }
    
    .header-btn {
      display: none;
    }
  }
  
  .pip-window {
    width: 120px;
    height: 90px;
  }
  
  .control-btn span {
    display: none;
  }
  
  .video-controls {
    gap: 8px;
  }
  
  .question-text {
    font-size: 14px;
  }
}
</style>