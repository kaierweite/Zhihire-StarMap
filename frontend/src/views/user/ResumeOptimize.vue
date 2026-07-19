<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Sparkles, ChevronRight, FileText, RefreshCw, Lightbulb, Target } from 'lucide-vue-next'
import { listResumes, optimizeResume, getResumeDetail } from '@/api/resume'
import type { ResumeListItem, OptimizeSuggestion, OptimizeResult } from '@/api/resume'

const route = useRoute()
const generating = ref(false)
const loaded = ref(false)
const resumeList = ref<ResumeListItem[]>([])
const selectedResumeId = ref<number | null>(null)
const jobDescription = ref('')
const suggestions = ref<OptimizeSuggestion[]>([])
const originalContent = ref('')
const optimizedContent = ref('')
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
  originalContent.value = ''
  optimizedContent.value = ''
  try {
    // Fetch original resume content
    const detailResp = await getResumeDetail(selectedResumeId.value)
    const detail = detailResp.data.data
    originalContent.value = formatResumeToText(detail.parsed || {})

    // Fetch optimization
    const resp = await optimizeResume(
      selectedResumeId.value,
      jobDescription.value.trim() || null
    )
    suggestions.value = resp.data.data.suggestions
    optimizedContent.value = combineSuggestions(resp.data.data.suggestions)
  } catch {
    errorMsg.value = '优化请求失败，请稍后重试'
  } finally { generating.value = false }
}

// === Fullscreen and copy ===
const fullscreenCard = ref<number | null>(null)
function toggleFullscreen(idx: number | null) {
  fullscreenCard.value = fullscreenCard.value === idx ? null : idx
}

async function copyContent(text: string, label: string) {
  try {
    await navigator.clipboard.writeText(text)
    ElMessage.success(label + '已复制')
  } catch {
    ElMessage.error('复制失败')
  }
}

function tryParseSuggestion(text: string): string {
  if (!text) return ""
  
  // Step 1: Strip markdown code block markers
  let cleaned = text.trim()
  const tripleTickRegex = new RegExp("```(?:json)?\n?([\\s\\S]*?)\n?```", "g")
  cleaned = cleaned.replace(tripleTickRegex, "$1").trim()
  cleaned = cleaned.replace(/\`+/g, "").trim()
  cleaned = cleaned.replace(/\*\*/g, "").replace(/__/g, "").trim()
  
  // Step 2: Find JSON array anywhere in the text
  let jsonStart = cleaned.indexOf("[")
  let jsonEnd = cleaned.lastIndexOf("]")
  if (jsonStart >= 0 && jsonEnd > jsonStart) {
    const jsonStr = cleaned.substring(jsonStart, jsonEnd + 1)
    try {
      const parsed = JSON.parse(jsonStr)
      if (Array.isArray(parsed)) {
        const parts: string[] = []
        for (const item of parsed) {
          if (typeof item === "object" && item !== null) {
            if (item.suggestion && typeof item.suggestion === "string") {
              const section = item.section ? "【" + item.section + "】" : ""
              if (section) parts.push(section)
              parts.push(item.suggestion)
            } else {
              const values = Object.values(item).filter(function(v: any): boolean { return typeof v === "string" })
              if (values.length) parts.push(values.join("\n"))
            }
          } else if (typeof item === "string") {
            parts.push(item)
          }
        }
        if (parts.length) return parts.join("\n\n")
      } else if (typeof parsed === "object" && parsed !== null) {
        if (parsed.suggestion && typeof parsed.suggestion === "string") {
          return parsed.suggestion
        }
        const values = Object.values(parsed).filter(function(v: any): boolean { return typeof v === "string" })
        if (values.length) return values.join("\n")
      } else if (typeof parsed === "string") {
        return parsed
      }
      if (cleaned !== text.trim()) return cleaned
    } catch {
      // JSON parse failed, continue
    }
  }
  
  // Step 3: Try JSON object (if no array found)
  jsonStart = cleaned.indexOf("{")
  jsonEnd = cleaned.lastIndexOf("}")
  if (jsonStart >= 0 && jsonEnd > jsonStart) {
    const jsonStr = cleaned.substring(jsonStart, jsonEnd + 1)
    try {
      const parsed = JSON.parse(jsonStr)
      if (typeof parsed === "object" && parsed !== null) {
        if (parsed.suggestion && typeof parsed.suggestion === "string") {
          return parsed.suggestion
        }
        const values = Object.values(parsed).filter(function(v: any): boolean { return typeof v === "string" })
        if (values.length) return values.join("\n")
      }
    } catch {
      // JSON parse failed
    }
  }
  
  // Step 4: If cleaning produced different text, return cleaned
  if (cleaned !== text.trim()) return cleaned
  
  // Step 5: Final cleanup - strip remaining marker patterns
  let result = cleaned
  // Remove 【??】 markers from any remaining section headers
  result = result.split("【??】").join( "").trim()
  // Remove empty 【】 
  result = result.replace(/【】/g, "").trim()
  if (result) return result
  
  // Step 6: Return as-is (already clean text)
  return text.trim()
}
function formatResumeToText(parsed: any): string {
  const parts: string[] = []

  // Handle case where content_text is a JSON string (not yet parsed)
  if (typeof parsed === 'string') {
    try {
      parsed = JSON.parse(parsed)
    } catch {
      return parsed as string
    }
  }
  if (!parsed || typeof parsed !== 'object') return ''

  if (parsed.name) parts.push('姓名：' + parsed.name)
  if (parsed.education) parts.push('学历：' + parsed.education)
  if (parsed.years !== undefined && parsed.years !== null && parsed.years !== '') {
    parts.push('工作年限：' + parsed.years + ' 年')
  }
  if (parsed.targetJob) parts.push('目标职位：' + parsed.targetJob)
  if (parsed.city) parts.push('城市：' + parsed.city)
  if (parsed.school) parts.push('学校：' + parsed.school)
  if (parsed.major) parts.push('专业：' + parsed.major)
  parts.push('')

  // Skills
  if (Array.isArray(parsed.skills) && parsed.skills.length) {
    parts.push('技能：')
    for (const s of parsed.skills) {
      const name = typeof s === 'string' ? s : (s.name || '')
      if (name) parts.push('  - ' + name)
    }
    parts.push('')
  }

  // Work experience
  if (Array.isArray(parsed.experience) && parsed.experience.length) {
    parts.push('工作经历：')
    for (const exp of parsed.experience) {
      const company = exp.company || ''
      const title = exp.title || ''
      const period = exp.period || ''
      const desc = exp.description || ''
      const heading = [company, title].filter(Boolean).join(' - ')
      if (heading || period) {
        parts.push('  ' + heading + (period ? ' (' + period + ')' : ''))
      }
      if (desc) {
        for (const d of desc.split('\n')) {
          if (d.trim()) parts.push('    ' + d.trim())
        }
      }
    }
  }

  return parts.join('\n')
}

function combineSuggestions(suggestions: OptimizeSuggestion[]): string {
  if (!suggestions || !suggestions.length) return ''
  const parts: string[] = []
  for (const s of suggestions) {
    const sectionHeading = (s.section && s.section !== '??') ? s.section : ''
    if (sectionHeading) parts.push('【' + sectionHeading + '】')
    parts.push('')
    // Parse suggestion to strip any JSON formatting
    const text = tryParseSuggestion(s.suggestion || '')
    parts.push(text)
    parts.push('')
  }
  return parts.join('\n')
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

      <!-- Compare View -->
      <div v-if="!generating && suggestions.length" class="compare-view">
        <div class="compare-header">
          <span class="section-badge"><FileText :size="15" /> 简历对比</span>
          <div class="compare-actions">
            <button class="copy-col-btn" @click="copyContent(originalContent, '原始内容')">复制原始</button>
            <button class="copy-col-btn" @click="copyContent(optimizedContent, '优化后内容')">复制优化</button>
            <button class="fullscreen-btn" @click="toggleFullscreen(0)" title="全屏查看">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M8 3H5a2 2 0 0 0-2 2v3"/><path d="M21 8V5a2 2 0 0 0-2-2h-3"/><path d="M16 21h3a2 2 0 0 0 2-2v-3"/><path d="M3 16v3a2 2 0 0 0 2 2h3"/></svg>
            </button>
          </div>
        </div>
        <div class="compare-body">
          <div class="content-col original">
            <div class="col-header">
              <h4>原始简历</h4>
              <button class="copy-col-btn" @click="copyContent(originalContent, '原始内容')" title="复制">复制</button>
            </div>
            <p class="resume-text">{{ originalContent }}</p>
          </div>
          <div class="content-col suggestion">
            <div class="col-header">
              <h4><Sparkles :size="14" /> AI 优化</h4>
              <button class="copy-col-btn" @click="copyContent(optimizedContent, '优化后内容')" title="复制">复制</button>
            </div>
            <p class="resume-text">{{ optimizedContent }}</p>
          </div>
        </div>
      </div>

      <!-- Fullscreen Overlay -->
      <div v-if="fullscreenCard !== null" class="fullscreen-overlay" @click.self="toggleFullscreen(null)">
        <div class="fullscreen-card">
          <div class="fullscreen-header">
            <span>简历对比——全屏查看</span>
            <div class="fullscreen-actions">
              <button class="copy-col-btn" @click="copyContent(originalContent, '原始内容')">复制原始</button>
              <button class="copy-col-btn" @click="copyContent(optimizedContent, '优化后内容')">复制优化</button>
              <button class="fullscreen-close-btn" @click="toggleFullscreen(null)">✕</button>
            </div>
          </div>
          <div class="fullscreen-body fullscreen-compare">
            <div class="fullscreen-col original">
              <h4>原始简历</h4>
              <p class="resume-text">{{ originalContent }}</p>
            </div>
            <div class="fullscreen-col suggestion">
              <h4><Sparkles :size="14" /> AI 优化</h4>
              <p class="resume-text">{{ optimizedContent }}</p>
            </div>
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

.breadcrumb { display: flex; align-items: center; gap: 6px; margin-bottom: 16px; font-size: 13px; color: #404944; }
.breadcrumb a { color: #404944; text-decoration: none; }
.breadcrumb a:hover { color: #003527; }
.breadcrumb span:last-child { color: #121c28; font-weight: 500; }

.page-header { margin-bottom: 24px; }
.page-header h1 { font-size: 28px; font-weight: 700; color: #121c28; margin-bottom: 4px; }
.page-header p { font-size: 14px; color: #404944; }

.controls-card { background: #fff; border-radius: 12px; padding: 20px 24px; border: 1px solid #bfc9c3; margin-bottom: 20px; }
.control-row { display: flex; align-items: flex-end; gap: 16px; flex-wrap: wrap; }
.control-group { display: flex; flex-direction: column; gap: 4px; flex: 1; min-width: 180px; }
.control-group label { font-size: 12px; color: #404944; font-weight: 500; }
.control-select, .control-input { padding: 8px 12px; border: 1px solid #bfc9c3; border-radius: 8px; font-size: 13px; color: #121c28; background: #fff; outline: none; }
.control-select:focus, .control-input:focus { border-color: #003527; }
.generate-btn { display: flex; align-items: center; gap: 6px; padding: 10px 24px; border-radius: 999px; background: linear-gradient(135deg, #064e3b, #003527); color: #fff; font-size: 14px; font-weight: 600; border: none; cursor: pointer; transition: all .3s; white-space: nowrap; }
.generate-btn:hover:not(:disabled) { transform: translateY(-1px); box-shadow: 0 6px 20px rgba(14,165,233,0.25); }
.generate-btn:disabled { opacity: 0.5; cursor: not-allowed; }

.loading-card { text-align: center; padding: 60px 24px; color: #404944; }
.loading-card p { margin-top: 12px; font-size: 14px; }

.error-msg { background: #fef2f2; border: 1px solid #fca5a5; color: #b91c1c; border-radius: 8px; padding: 12px 16px; margin-bottom: 16px; font-size: 13px; }

.compare-view { background: #fff; border-radius: 16px; border: 1px solid #bfc9c3; overflow: hidden; }
.suggestion-card { display: none; }
.card-header { display: none; }
.compare-header { display: flex; align-items: center; justify-content: space-between; padding: 16px 24px; border-bottom: 1px solid #bfc9c3; }
.compare-actions { display: flex; gap: 8px; align-items: center; }
.section-badge { display: flex; align-items: center; gap: 6px; font-size: 15px; font-weight: 600; color: #121c28; }
.section-badge svg { color: #003527; }
.skill-tag { display: flex; align-items: center; gap: 4px; padding: 3px 10px; border-radius: 999px; background: rgba(14,165,233,0.08); color: #064e3b; font-size: 12px; font-weight: 600; }
.compare-body { display: grid; grid-template-columns: 1fr 1fr; gap: 0; }
.content-col { padding: 20px 24px; }
.content-col h4 { font-size: 12px; font-weight: 600; margin-bottom: 8px; }
.col-header { display: flex; align-items: center; justify-content: space-between; margin-bottom: 4px; }
.content-col p { font-size: 13px; color: #404944; line-height: 1.7; white-space: pre-wrap; }
.resume-text { font-size: 13px; color: #404944; line-height: 1.8; white-space: pre-wrap; font-family: 'Microsoft YaHei', 'PingFang SC', sans-serif; }
.original { background: #f8f9fa; border-right: 1px solid #bfc9c3; }
.original h4 { color: #404944; }
.suggestion { background: rgba(251,191,36,0.06); border: 1px solid rgba(251,191,36,0.15); }
.suggestion h4 { display: flex; align-items: center; gap: 4px; color: #b45309; }

.empty-state { text-align: center; padding: 60px 24px; color: #404944; font-size: 14px; }

/* Fullscreen */
.suggestion-card.is-fullscreen { position: relative; z-index: 1; }
.fullscreen-overlay {
  position: fixed; inset: 0; z-index: 1000;
  background: rgba(0,0,0,0.6); display: flex;
  align-items: center; justify-content: center;
  padding: 32px; animation: fadeIn 0.2s ease;
}
.fullscreen-card {
  background: #fff; border-radius: 16px; width: 100%; max-width: 1100px;
  max-height: 90vh; display: flex; flex-direction: column;
  box-shadow: 0 24px 80px rgba(0,0,0,0.3); animation: scaleIn 0.2s ease;
}
.fullscreen-header {
  display: flex; align-items: center; justify-content: space-between;
  padding: 18px 24px; border-bottom: 1px solid #bfc9c3; font-weight: 600; font-size: 16px; color: #121c28;
}
.fullscreen-actions { display: flex; gap: 8px; align-items: center; }
.fullscreen-close-btn {
  width: 32px; height: 32px; border-radius: 8px; border: 1px solid #bfc9c3;
  background: #fff; color: #404944; cursor: pointer; display: flex;
  align-items: center; justify-content: center; font-size: 14px;
  transition: all .15s;
}
.fullscreen-close-btn:hover { border-color: #f56c6c; color: #f56c6c; background: #fef2f2; }
.fullscreen-body.fullscreen-compare {
  display: grid; grid-template-columns: 1fr 1fr; gap: 20px;
  padding: 24px; overflow-y: auto; flex: 1;
}
.fullscreen-col { padding: 16px; border-radius: 8px; }
.fullscreen-col h4 { font-size: 13px; font-weight: 600; margin-bottom: 10px; }
.fullscreen-col p { font-size: 14px; color: #404944; line-height: 1.8; white-space: pre-wrap; font-family: 'Microsoft YaHei', 'PingFang SC', sans-serif; }
.fullscreen-col.original { background: #f8f9fa; border-right: 1px solid #bfc9c3; }
.fullscreen-col.original h4 { color: #404944; }
.fullscreen-col.suggestion { background: rgba(251,191,36,0.06); border: 1px solid rgba(251,191,36,0.15); }
.fullscreen-col.suggestion h4 { display: flex; align-items: center; gap: 4px; color: #b45309; }

/* Copy button */
.copy-col-btn {
  padding: 2px 10px; border-radius: 4px; border: 1px solid #bfc9c3;
  background: #fff; color: #404944; font-size: 11px; cursor: pointer;
  transition: all .15s; white-space: nowrap;
}
.copy-col-btn:hover { border-color: #003527; color: #003527; }

/* Fullscreen button on suggestion card */
.fullscreen-btn {
  flex-shrink: 0; width: 32px; height: 32px; border-radius: 8px;
  border: 1px solid #bfc9c3; background: #fff; color: #404944;
  display: flex; align-items: center; justify-content: center; cursor: pointer;
  transition: all .15s; margin-left: auto;
}
.fullscreen-btn:hover { border-color: #003527; color: #003527; background: #f8f9ff; }

@keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }
@keyframes scaleIn { from { opacity: 0; transform: scale(0.95); } to { opacity: 1; transform: scale(1); } }

.spinning { color: #064e3b; animation: spin 1s linear infinite; }
.spinning { color: #064e3b; animation: spin 1s linear infinite; }

@media (max-width: 640px) { .content-row { grid-template-columns: 1fr; } .control-row { flex-direction: column; align-items: stretch; } .control-group { min-width: unset; } }
</style>
