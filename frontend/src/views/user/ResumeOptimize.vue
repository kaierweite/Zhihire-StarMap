<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Sparkles, ChevronRight, FileText, RefreshCw, Lightbulb, Target } from 'lucide-vue-next'
import { listResumes, optimizeResume } from '@/api/resume'
import type { ResumeListItem, 开始优化Suggestion } from '@/api/resume'

const route = useRoute()
const generating = ref(false)
const loaded = ref(false)
const resumeList = ref<ResumeListItem[]>([])
const selectedResumeId = ref<number | null>(null)
const jobDescription = ref('')
const suggestions = ref<开始优化Suggestion[]>([])
const errorMsg = ref('')

onMounted(async () => {
  // Check URL param from ResumeCenter navigation
  const rid = Number(route.query.resume_id)
  if (rid) selectedResumeId.value = rid
  await loadResumes()
})

async function loadResumes() {
  try {
    const resp = await listResumes(1, 50)
    resumeList.value = resp.data.data.records
  } catch {} finally { loaded.value = true }
}

async function generate开始优化() {
  if (!selectedResumeId.value) {
    ElMessage.warning('Please select a resume first')
    return
  }
  generating.value = true
  errorMsg.value = ''
  suggestions.value = []
  try {
    const resp = await optimizeResume(
      selectedResumeId.value,
      jobDescription.value.trim() || null
    )
    suggestions.value = resp.data.data.suggestions
  } catch {
    errorMsg.value = '优化请求失败，请稍后重试'
  } finally { generating.value = false }
}

const sectionIcons: Record<string, string> = {
  'personal': '👤', 'summary': '📋', 'skills': '🛠', 'experience': '💼',
  'project': '🚀', 'education': '🎓', 'certificate': '📜',
}
function sectionIcon(section: string): string {
  const key = section.toLowerCase().slice(0, 8)
  for (const [k, v] of Object.entries(sectionIcons)) {
    if (key.includes(k)) return v
  }
  return '📄'
}
</script>

<template>
  <div class="optimize-page">
    <div class="optimize-container">
      <!-- Breadcrumb -->
      <div class="breadcrumb">
        <router-link to="/user/resume">面试准备</router-link>
        <ChevronRight :size="14" /><span>AI 简历优化</span>
      </div>

      <div class="page-header">
        <div>
          <h1>AI 简历优化</h1>
          <p>针对目标岗位获取简历优化建议</p>
        </div>
      </div>

      <!-- Controls -->
      <div class="controls-card">
        <div class="control-row">
          <div class="control-group">
            <label>选择简历</label>
            <select v-model="selectedResumeId" class="control-select">
              <option :value="null" disabled>-- 请选择简历 --</option>
              <option v-for="r in resumeList" :key="r.id" :value="r.id">{{ r.title || 'Untitled' }}</option>
            </select>
          </div>
          <div class="control-group">
            <label>目标职位（选填）</label>
            <input v-model="jobDescription" placeholder="例如：高级前端工程师 @ 腾讯" class="control-input" />
          </div>
          <button class="generate-btn" :disabled="generating || !selectedResumeId" @click="generate开始优化">
            <Sparkles :size="16" /> {{ generating ? '优化中...' : '开始优化' }}
          </button>
        </div>
      </div>

      <!-- Loading -->
      <div v-if="generating" class="loading-card">
        <RefreshCw :size="24" class="spinning" />
        <p>AI 正在分析你的简历并生成建议...</p>
      </div>

      <!-- Error -->
      <div v-if="errorMsg" class="error-msg">{{ errorMsg }}</div>

      <!-- Suggestions -->
      <div v-if="!generating && suggestions.length" class="suggestion-list">
        <div v-for="(s, i) in suggestions" :key="i" class="suggestion-card">
          <div class="card-header">
            <span class="section-badge"><FileText :size="15" /> {{ s.section }}</span>
            <span v-if="s.relates_to_skill" class="skill-tag"><Target :size="12" /> {{ s.relates_to_skill }}</span>
          </div>
          <div class="content-row">
            <div class="content-col original">
              <h4>当前内容</h4>
              <p>{{ s.current }}</p>
            </div>
            <div class="content-col suggestion">
              <h4><Sparkles :size="14" /> AI 建议</h4>
              <p>{{ s.suggestion }}</p>
            </div>
          </div>
          <div v-if="s.relates_to_skill" class="reason-box">
            <Lightbulb :size="14" />
            <span>关联技能： <strong>{{ s.relates_to_skill }}</strong></span>
          </div>
        </div>
      </div>

      <!-- Empty -->
      <div v-if="!generating && !suggestions.length && loaded && selectedResumeId" class="empty-state">
        <p>Click "开始优化" to generate suggestions for your resume.</p>
      </div>
    </div>
  </div>
</template>

<style scoped lang="scss">
.optimize-page { padding: 24px 16px; }
.optimize-container { max-width: 900px; margin: 0 auto; }

.breadcrumb { display: flex; align-items: center; gap: 6px; margin-bottom: 16px; font-size: 13px; color: #909399; }
.breadcrumb a { color: #909399; text-decoration: none; }
.breadcrumb a:hover { color: #1a3a5c; }
.breadcrumb span:last-child { color: #303133; font-weight: 500; }

.page-header { margin-bottom: 24px; }
.page-header h1 { font-size: 28px; font-weight: 700; color: #303133; margin-bottom: 4px; }
.page-header p { font-size: 14px; color: #909399; }

.controls-card { background: #fff; border-radius: 12px; padding: 20px 24px; border: 1px solid #e5e7eb; margin-bottom: 20px; }
.control-row { display: flex; align-items: flex-end; gap: 16px; flex-wrap: wrap; }
.control-group { display: flex; flex-direction: column; gap: 4px; flex: 1; min-width: 180px; }
.control-group label { font-size: 12px; color: #909399; font-weight: 500; }
.control-select, .control-input { padding: 8px 12px; border: 1px solid #dcdfe6; border-radius: 8px; font-size: 13px; color: #303133; background: #fff; outline: none; }
.control-select:focus, .control-input:focus { border-color: #1a3a5c; }
.generate-btn { display: flex; align-items: center; gap: 6px; padding: 10px 24px; border-radius: 999px; background: linear-gradient(135deg, #0ea5e9, #1a3a5c); color: #fff; font-size: 14px; font-weight: 600; border: none; cursor: pointer; transition: all .3s; white-space: nowrap; }
.generate-btn:hover:not(:disabled) { transform: translateY(-1px); box-shadow: 0 6px 20px rgba(14,165,233,0.25); }
.generate-btn:disabled { opacity: 0.5; cursor: not-allowed; }

.loading-card { text-align: center; padding: 60px 24px; color: #909399; }
.loading-card p { margin-top: 12px; font-size: 14px; }

.error-msg { background: #fef2f2; border: 1px solid #fca5a5; color: #b91c1c; border-radius: 8px; padding: 12px 16px; margin-bottom: 16px; font-size: 13px; }

.suggestion-list { display: flex; flex-direction: column; gap: 16px; }
.suggestion-card { background: #fff; border-radius: 12px; padding: 20px 24px; border: 1px solid #e5e7eb; }
.card-header { display: flex; align-items: center; justify-content: space-between; margin-bottom: 14px; flex-wrap: wrap; gap: 8px; }
.section-badge { display: flex; align-items: center; gap: 6px; font-size: 15px; font-weight: 600; color: #303133; }
.section-badge svg { color: #1a3a5c; }
.skill-tag { display: flex; align-items: center; gap: 4px; padding: 3px 10px; border-radius: 999px; background: rgba(14,165,233,0.08); color: #0ea5e9; font-size: 12px; font-weight: 600; }
.content-row { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; margin-bottom: 12px; }
.content-col { padding: 14px; border-radius: 8px; }
.content-col h4 { font-size: 12px; font-weight: 600; margin-bottom: 8px; }
.content-col p { font-size: 13px; color: #606266; line-height: 1.7; white-space: pre-wrap; }
.original { background: #f8f9fa; }
.original h4 { color: #909399; }
.suggestion { background: rgba(14,165,233,0.04); border: 1px solid rgba(14,165,233,0.1); }
.suggestion h4 { display: flex; align-items: center; gap: 4px; color: #0ea5e9; }
.reason-box { display: flex; align-items: center; gap: 8px; padding: 10px 14px; border-radius: 8px; background: rgba(245,158,11,0.06); border-left: 3px solid #f59e0b; }
.reason-box svg { color: #f59e0b; flex-shrink: 0; }
.reason-box span { font-size: 13px; color: #606266; }
.reason-box strong { color: #303133; }
.empty-state { text-align: center; padding: 60px 24px; color: #909399; font-size: 14px; }

@keyframes spin { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }
.spinning { color: #0ea5e9; animation: spin 1s linear infinite; }

@media (max-width: 640px) { .content-row { grid-template-columns: 1fr; } .control-row { flex-direction: column; align-items: stretch; } .control-group { min-width: unset; } }
</style>
