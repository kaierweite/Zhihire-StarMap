<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, nextTick } from 'vue'
import * as echarts from 'echarts'
import {
  Route, Lightbulb, CheckCircle, RefreshCw,
  Sparkles, AlertTriangle, Info, Gift, Loader2, Eye, Code,
  FileText, Link, GraduationCap, BookOpen,
  ZoomIn, ZoomOut, Download, Plus, Minus,
} from 'lucide-vue-next'
import { ElMessage } from 'element-plus'
import { aiGenerateCareerPlan } from '@/api/career'
import type { AiPlanResponse, MindMapNode } from '@/api/career'

// ====== State ======
const inputType = ref<'PROFESSION' | 'JOB_DESCRIPTION' | 'JOB_URL'>('PROFESSION')
const professionText = ref('')
const jobDescriptionText = ref('')
const jobUrlText = ref('')
const generating = ref(false)
const planData = ref<AiPlanResponse | null>(null)
const errorMsg = ref('')
const hasPlan = ref(false)
const mindMapMode = ref<'render' | 'code'>('render')
const chartRef = ref<HTMLElement>()
let chartInstance: echarts.ECharts | null = null
const zoomLevel = ref(1)
const MIN_ZOOM = 0.5
const MAX_ZOOM = 3

// ====== Computed ======
const targetText = computed(() => {
  switch (inputType.value) {
    case 'PROFESSION': return professionText.value.trim()
    case 'JOB_DESCRIPTION': return jobDescriptionText.value.trim()
    case 'JOB_URL': return jobUrlText.value.trim()
  }
})

const canGenerate = computed(() => targetText.value.length > 0)

const gapMustSkills = computed(() =>
  (planData.value?.gap_skills || []).filter((g) => g.requirement_level === 'MUST'),
)
const gapNiceSkills = computed(() =>
  (planData.value?.gap_skills || []).filter((g) => g.requirement_level === 'NICE'),
)
const gapBonusSkills = computed(() =>
  (planData.value?.gap_skills || []).filter((g) => g.requirement_level === 'BONUS'),
)

const scoreColor = computed(() => {
  const s = planData.value?.match_score ?? 0
  if (s >= 80) return '#198754'
  if (s >= 60) return '#1a3a5c'
  if (s >= 40) return '#e67e22'
  return '#e74c3c'
})

const CIRCUMFERENCE = 2 * Math.PI * 54
const scoreOffset = computed(() => {
  const s = planData.value?.match_score ?? 0
  return CIRCUMFERENCE * (1 - s / 100)
})

const formattedJson = computed(() => {
  if (!planData.value?.mind_map) return '{}'
  return JSON.stringify(planData.value.mind_map, null, 2)
})

// ====== ECharts Mind Map ======
function initMindMap() {
  zoomLevel.value = 1
  if (!chartRef.value || !planData.value?.mind_map) return

  if (!chartInstance) {
    chartInstance = echarts.init(chartRef.value, undefined, { renderer: 'canvas' })
  }
  chartInstance.clear()

  const nodes = deepCount(planData.value.mind_map)
  const chartHeight = Math.max(nodes * 52 + 120, 500)

  chartInstance.setOption({
    tooltip: {
      trigger: 'item',
      backgroundColor: 'rgba(255,255,255,0.96)',
      borderColor: '#e8e8e8',
      borderWidth: 1,
      padding: [8, 14],
      textStyle: { color: '#303133', fontSize: 13 },
      formatter: (params: any) => {
        const name = params.name || ''
        const depth = params.treePathInfo?.length || 0
        if (depth <= 2) return '<strong style="font-size:15px;color:#1a3a5c;">' + name + '</strong>'
        return '<span style="color:#606266;font-size:13px;">' + name + '</span>'
      },
    },
    series: [{
      type: 'tree',
      data: [planData.value.mind_map],
      top: 5,
      left: 5,
      bottom: 5,
      right: 5,
      symbolSize: 8,
      orient: 'LR',
      expandAndCollapse: true,
      initialTreeDepth: 3,
      label: {
        position: 'bottom',
        fontSize: 14,
        fontWeight: 500,
        color: '#303133',
        width: 200,
        overflow: 'break',
        formatter: (params: any) => {
          const name = params.name || ''
          const depth = params.treePathInfo?.length || 0
          if (depth <= 2) return '{bold|' + name + '}'
          return name
        },
        rich: {
          bold: { fontSize: 16, fontWeight: 700, color: '#1a3a5c' },
        },
      },
      leaves: {
        label: {
          position: 'bottom',
          fontSize: 13,
          color: '#606266',
          width: 180,
          overflow: 'break',
        },
      },
      lineStyle: {
        color: '#1a3a5c',
        width: 1.5,
        curveness: 0.5,
      },
      animationDuration: 800,
      animationEasing: 'cubicOut',
    }],
  }, true)

  chartRef.value.style.height = chartHeight + 'px'
  chartInstance.resize()
  baseChartWidth = chartRef.value.clientWidth
  baseChartHeight = chartRef.value.clientHeight
}

function deepCount(node: MindMapNode): number {
  let count = 1
  if (node.children) {
    for (const child of node.children) {
      count += deepCount(child)
    }
  }
  return count
}

function handleResize() {
  chartInstance?.resize()
}

// ====== Lifecycle ======
onMounted(() => {
  window.addEventListener('resize', handleResize)
})

onUnmounted(() => {
  chartInstance?.dispose()
  chartInstance = null
  window.removeEventListener('resize', handleResize)
})

// ====== Actions ======
async function handleGenerate() {
  const text = targetText.value
  if (!text) {
    ElMessage.warning('请输入目标专业名称或招聘 JD')
    return
  }

  generating.value = true
  errorMsg.value = ''
  try {
    const res = await aiGenerateCareerPlan({
      input_type: inputType.value,
      target_text: text,
    })
    planData.value = res.data.data
    hasPlan.value = true

    await nextTick()
    initMindMap()
  } catch (err: any) {
    errorMsg.value = err?.response?.data?.message || 'AI 分析失败，请稍后重试'
  } finally {
    generating.value = false
  }
}

function handleRegenerate() {
  handleGenerate()
}

function switchMindMapMode(mode: 'render' | 'code') {
  mindMapMode.value = mode
  if (mode === 'render') {
    nextTick(() => initMindMap())
  }
}

// ====== Zoom & Download ======
let baseChartWidth = 800
let baseChartHeight = 400

function applyZoom() {
  if (!chartRef.value || !chartInstance) return
  if (zoomLevel.value === 1) {
    chartRef.value.style.width = ''
    chartRef.value.style.height = baseChartHeight + 'px'
  } else {
    chartRef.value.style.width = Math.round(baseChartWidth * zoomLevel.value) + 'px'
    chartRef.value.style.height = Math.round(baseChartHeight * zoomLevel.value) + 'px'
  }
  nextTick(() => chartInstance?.resize())
}

function zoomIn() {
  if (zoomLevel.value < MAX_ZOOM) {
    zoomLevel.value = Math.round((zoomLevel.value + 0.25) * 100) / 100
    applyZoom()
  }
}

function zoomOut() {
  if (zoomLevel.value > MIN_ZOOM) {
    zoomLevel.value = Math.round((zoomLevel.value - 0.25) * 100) / 100
    applyZoom()
  }
}

function resetZoom() {
  zoomLevel.value = 1
  applyZoom()
}

function downloadChart() {
  if (!chartInstance) return
  const url = chartInstance.getDataURL({
    type: 'png',
    pixelRatio: 2,
    backgroundColor: '#fff',
  })
  const link = document.createElement('a')
  link.href = url
  link.download = 'career-plan-mindmap.png'
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
}
</script>

<template>
  <div class="career-page">
    <div class="career-container">
      <!-- Header -->
      <h1 class="page-title">AI 智能职业规划</h1>
      <p class="page-desc">输入你感兴趣的专业方向或目标公司岗位，AI 分析能力差距并生成专属学习思维导图</p>

      <!-- ====== Input Section ====== -->
      <section class="input-section fade-up">
        <!-- Input type tabs -->
        <div class="input-tabs">
          <button
            class="input-tab"
            :class="{ active: inputType === 'PROFESSION' }"
            @click="inputType = 'PROFESSION'"
          >
            <GraduationCap :size="16" />
            对口专业
          </button>
          <button
            class="input-tab"
            :class="{ active: inputType === 'JOB_DESCRIPTION' }"
            @click="inputType = 'JOB_DESCRIPTION'"
          >
            <FileText :size="16" />
            招聘 JD
          </button>
          <button
            class="input-tab"
            :class="{ active: inputType === 'JOB_URL' }"
            @click="inputType = 'JOB_URL'"
          >
            <Link :size="16" />
            招聘链接
          </button>
        </div>

        <!-- Input area -->
        <div class="input-area">
          <template v-if="inputType === 'PROFESSION'">
            <label class="input-label">你想学习什么专业或从事什么方向？</label>
            <div class="input-with-hint">
              <input
                v-model="professionText"
                type="text"
                class="text-input"
                placeholder="例如：软件工程、人工智能、数据分析、产品经理..."
                @keyup.enter="handleGenerate"
              />
            </div>
          </template>

          <template v-else-if="inputType === 'JOB_DESCRIPTION'">
            <label class="input-label">粘贴目标公司的招聘岗位 JD</label>
            <textarea
              v-model="jobDescriptionText"
              class="text-area"
              rows="6"
              placeholder="将招聘岗位的职位描述和要求粘贴到这里..."
            ></textarea>
          </template>

          <template v-else>
            <label class="input-label">输入目标公司的招聘岗位链接</label>
            <div class="input-with-hint">
              <input
                v-model="jobUrlText"
                type="url"
                class="text-input"
                placeholder="例如：https://www.zhipin.com/job/..."
                @keyup.enter="handleGenerate"
              />
            </div>
          </template>
        </div>

        <div v-if="errorMsg" class="error-banner">{{ errorMsg }}</div>

        <button
          class="generate-btn"
          :disabled="!canGenerate || generating"
          @click="handleGenerate"
        >
          <Loader2 v-if="generating" :size="18" class="spin-icon" />
          <Sparkles v-else :size="18" />
          {{ generating ? 'AI 分析中...' : 'AI 生成规划' }}
        </button>
      </section>

      <!-- ====== Results (after generation) ====== -->
      <template v-if="hasPlan && planData">
        <!-- Score + Target role hero -->
        <div class="score-section fade-up">
          <div class="score-ring-wrap">
            <svg width="140" height="140" viewBox="0 0 140 140">
              <circle cx="70" cy="70" r="54" fill="none" stroke="#e9ecef" stroke-width="10" />
              <circle
                cx="70" cy="70" r="54" fill="none"
                :stroke="scoreColor" stroke-width="10"
                stroke-linecap="round"
                :stroke-dasharray="CIRCUMFERENCE"
                :stroke-dashoffset="scoreOffset"
                transform="rotate(-90 70 70)"
                class="score-arc"
              />
              <text x="70" y="62" text-anchor="middle" fill="#303133" font-size="32" font-weight="700">{{ planData.match_score }}</text>
              <text x="70" y="82" text-anchor="middle" fill="#909399" font-size="13">分</text>
            </svg>
          </div>
          <div class="score-meta">
            <h2 class="target-role">{{ planData.target_role }}</h2>
            <div class="score-tags">
              <span class="source-badge">AI 分析</span>
              <span class="match-label" v-if="planData.has_resume">已结合简历分析</span>
              <span class="match-label" v-else>仅基于技能评估</span>
            </div>
            <p class="score-desc">{{ planData.analysis_summary }}</p>
          </div>
        </div>

        <!-- Gap Skills -->
        <section class="fade-up gap-section">
          <h2 class="section-heading"><Lightbulb :size="22" /> 技能差距分析</h2>

          <div v-if="gapMustSkills.length" class="skill-group">
            <div class="group-head"><AlertTriangle :size="16" class="must-icon" /> MUST — 必备</div>
            <div class="skill-chips">
              <span
                v-for="s in gapMustSkills"
                :key="s.skill_name"
                class="skill-chip must"
                :title="s.description"
              >{{ s.skill_name }}</span>
            </div>
          </div>

          <div v-if="gapNiceSkills.length" class="skill-group">
            <div class="group-head"><Info :size="16" class="nice-icon" /> NICE — 加分</div>
            <div class="skill-chips">
              <span
                v-for="s in gapNiceSkills"
                :key="s.skill_name"
                class="skill-chip nice"
                :title="s.description"
              >{{ s.skill_name }}</span>
            </div>
          </div>

          <div v-if="gapBonusSkills.length" class="skill-group">
            <div class="group-head"><Gift :size="16" class="bonus-icon" /> BONUS — 锦上添花</div>
            <div class="skill-chips">
              <span
                v-for="s in gapBonusSkills"
                :key="s.skill_name"
                class="skill-chip bonus"
                :title="s.description"
              >{{ s.skill_name }}</span>
            </div>
          </div>

          <div v-if="planData.gap_skills.length === 0" class="no-gap">
            <CheckCircle :size="20" /> 太棒了！你已掌握目标所需的核心技能。
          </div>
        </section>

        <!-- ====== Mind Map ====== -->
        <section class="fade-up mindmap-section">
          <div class="mindmap-header">
            <h2 class="section-heading"><Route :size="22" /> 学习路径思维导图</h2>
            <div class="mode-toggle">
              <button
                class="mode-btn"
                :class="{ active: mindMapMode === 'render' }"
                @click="switchMindMapMode('render')"
              >
                <Eye :size="14" /> 渲染
              </button>
              <button
                class="mode-btn"
                :class="{ active: mindMapMode === 'code' }"
                @click="switchMindMapMode('code')"
              >
                <Code :size="14" /> 代码
              </button>
            </div>
          </div>

          <!-- Render mode: ECharts -->
          <div v-show="mindMapMode === 'render'" class="mindmap-render">
            <div class="mindmap-toolbar">
              <button class="toolbar-btn" @click="zoomOut" title="缩小">
                <Minus :size="16" />
              </button>
              <span class="zoom-label">{{ Math.round(zoomLevel * 100) }}%</span>
              <button class="toolbar-btn" @click="zoomIn" title="放大">
                <Plus :size="16" />
              </button>
              <span class="toolbar-divider"></span>
              <button class="toolbar-btn" @click="downloadChart" title="下载为图片">
                <Download :size="16" />
              </button>
            </div>
            <div v-if="planData.mind_map" ref="chartRef" class="chart-box"></div>
            <div v-else class="empty-mindmap">
              <BookOpen :size="40" />
              <p>暂无思维导图数据</p>
            </div>
            <div class="mindmap-tip">
              <Lightbulb :size="12" />
              <span>点击节点展开/收起子分支 · 滚轮缩放</span>
            </div>
          </div>

          <!-- Code mode: JSON -->
          <div v-show="mindMapMode === 'code'" class="mindmap-code">
            <pre class="code-block"><code>{{ formattedJson }}</code></pre>
          </div>
        </section>

        <!-- Actions -->
        <div class="action-bar fade-up">
          <button class="regen-btn" :disabled="generating" @click="handleRegenerate">
            <Loader2 v-if="generating" :size="16" class="spin-icon" />
            <RefreshCw v-else :size="16" />
            {{ generating ? '重新分析中...' : '重新生成' }}
          </button>
        </div>
      </template>
    </div>
  </div>
</template>

<style scoped lang="scss">
.career-page { padding: 24px 16px; }
.career-container { max-width: 960px; margin: 0 auto; }

@keyframes fadeUp {
  from { opacity: 0; transform: translateY(20px); }
  to { opacity: 1; transform: translateY(0); }
}
@keyframes spin { to { transform: rotate(360deg); } }
.fade-up { opacity: 0; animation: fadeUp 0.5s cubic-bezier(0.22,1,0.36,1) forwards; }
.fade-up:nth-child(2) { animation-delay: 0.08s; }
.fade-up:nth-child(3) { animation-delay: 0.15s; }
.fade-up:nth-child(4) { animation-delay: 0.22s; }
.fade-up:nth-child(5) { animation-delay: 0.3s; }

.spin-icon { animation: spin 1s linear infinite; }

.page-title {
  font-size: 36px; font-weight: 700; color: #303133; letter-spacing: -1px; margin-bottom: 6px;
}
.page-desc {
  font-size: 16px; color: #909399; margin-bottom: 32px;
}
.section-heading {
  display: flex; align-items: center; gap: 10px; font-size: 22px; font-weight: 600;
  color: #303133; margin: 0;
  svg { color: #1a3a5c; }
}

// ====== Input Section ======
.input-section {
  background: #fff; border-radius: 16px; padding: 28px 32px;
  border: 1px solid #e5e7eb; margin-bottom: 28px;
}
.input-tabs {
  display: flex; gap: 6px; margin-bottom: 20px;
  background: #f3f4f5; border-radius: 10px; padding: 4px;
}
.input-tab {
  flex: 1; display: flex; align-items: center; justify-content: center; gap: 6px;
  padding: 10px 16px; border: none; border-radius: 8px;
  background: transparent; color: #606266; font-size: 14px; font-weight: 500;
  cursor: pointer; transition: all 0.2s;
  &:hover { color: #303133; }
  &.active {
    background: #fff; color: #1a3a5c; font-weight: 600;
    box-shadow: 0 2px 8px rgba(0,0,0,0.06);
  }
}
.input-area { margin-bottom: 16px; }
.input-label {
  display: block; font-size: 14px; font-weight: 600; color: #303133; margin-bottom: 10px;
}
.text-input {
  width: 100%; padding: 12px 16px; border: 2px solid #e5e7eb; border-radius: 10px;
  font-size: 15px; color: #303133; outline: none; transition: border-color 0.2s;
  box-sizing: border-box;
  &:focus { border-color: #1a3a5c; }
  &::placeholder { color: #c0c4cc; }
}
.text-area {
  width: 100%; padding: 12px 16px; border: 2px solid #e5e7eb; border-radius: 10px;
  font-size: 14px; color: #303133; outline: none; resize: vertical; transition: border-color 0.2s;
  font-family: inherit; line-height: 1.6; box-sizing: border-box;
  &:focus { border-color: #1a3a5c; }
  &::placeholder { color: #c0c4cc; }
}
.error-banner {
  background: #fdf0ef; border: 1px solid #f56c6c; border-radius: 8px; padding: 12px 16px;
  color: #e74c3c; font-size: 14px; margin-bottom: 16px;
}
.generate-btn {
  display: inline-flex; align-items: center; gap: 8px;
  padding: 12px 28px; border: none; border-radius: 10px;
  background: linear-gradient(135deg, #1a3a5c 0%, #2c5282 100%);
  color: #fff; font-size: 15px; font-weight: 600;
  cursor: pointer; transition: all 0.2s;
  &:hover:not(:disabled) { transform: translateY(-1px); box-shadow: 0 4px 16px rgba(26,58,92,0.25); }
  &:disabled { opacity: 0.5; cursor: not-allowed; }
}

// ====== Score Section ======
.score-section {
  display: flex; align-items: center; gap: 28px;
  background: #fff; border-radius: 16px; padding: 28px 32px;
  border: 1px solid #e5e7eb; margin-bottom: 28px;
}
.score-ring-wrap { flex-shrink: 0; }
.score-arc { transition: stroke-dashoffset 0.8s ease; }
.score-meta { flex: 1; }
.target-role { font-size: 26px; font-weight: 700; color: #303133; margin-bottom: 6px; }
.score-tags { display: flex; align-items: center; gap: 8px; margin-bottom: 8px; }
.source-badge {
  font-size: 11px; padding: 2px 10px; border-radius: 4px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: #fff; font-weight: 600;
}
.match-label { font-size: 13px; color: #909399; background: #f3f4f5; padding: 2px 10px; border-radius: 4px; }
.score-desc { font-size: 14px; color: #606266; margin: 0; line-height: 1.7; }

// ====== Gap Skills ======
.gap-section { margin-bottom: 28px; }
.skill-group { margin-bottom: 16px; &:last-child { margin-bottom: 0; } }
.group-head {
  display: flex; align-items: center; gap: 6px; font-size: 13px;
  font-weight: 600; color: #606266; margin-bottom: 8px;
  .must-icon { color: #e74c3c; }
  .nice-icon { color: #3498db; }
  .bonus-icon { color: #95a5a6; }
}
.skill-chips { display: flex; flex-wrap: wrap; gap: 8px; }
.skill-chip {
  display: inline-flex; align-items: center; gap: 4px;
  padding: 6px 14px; border-radius: 6px; font-size: 13px; font-weight: 500;
  cursor: default;
  &.must { background: #fdf0ef; color: #c0392b; border: 1px solid #f5c6cb; }
  &.nice { background: #ebf5fb; color: #2980b9; border: 1px solid #aed6f1; }
  &.bonus { background: #f8f9fa; color: #7f8c8d; border: 1px solid #dee2e6; }
}
.no-gap {
  display: flex; align-items: center; gap: 8px;
  padding: 16px 20px; background: #d4edda; border-radius: 8px;
  color: #155724; font-size: 14px; font-weight: 500;
}

// ====== Mind Map ======
.mindmap-section { margin-bottom: 28px; }
.mindmap-header {
  display: flex; align-items: center; justify-content: space-between; margin-bottom: 16px;
}
.mode-toggle {
  display: flex; gap: 4px;
  background: #f3f4f5; border-radius: 8px; padding: 3px;
}
.mode-btn {
  display: inline-flex; align-items: center; gap: 4px;
  padding: 6px 14px; border: none; border-radius: 6px;
  background: transparent; color: #606266; font-size: 13px; font-weight: 500;
  cursor: pointer; transition: all 0.2s;
  &:hover { color: #303133; }
  &.active {
    background: #fff; color: #1a3a5c; font-weight: 600;
    box-shadow: 0 2px 6px rgba(0,0,0,0.08);
  }
}
.mindmap-render {
  position: relative;
  overflow: auto;
  background: #fff; border-radius: 12px; border: 1px solid #e5e7eb; padding: 16px;
}
.chart-box {
  width: 100%; min-height: 400px; border-radius: 8px;
  transition: height 0.3s ease;
}
.mindmap-tip {
  display: flex; align-items: center; gap: 6px; margin-top: 10px;
  font-size: 12px; color: #c0c4cc; justify-content: center;
  svg { color: #c0c4cc; }
}
.empty-mindmap {
  display: flex; flex-direction: column; align-items: center; gap: 12px;
  padding: 60px 0; color: #c0c4cc;
  svg { opacity: 0.4; }
  p { font-size: 14px; margin: 0; }
}
.mindmap-code {
  background: #1e1e2e; border-radius: 12px; overflow: hidden;
  border: 1px solid #313244;
}
.code-block {
  margin: 0; padding: 20px 24px; overflow-x: auto;
  font-family: 'JetBrains Mono', 'Fira Code', 'Courier New', monospace;
  font-size: 13px; line-height: 1.6; color: #cdd6f4;
  code { white-space: pre; }
}

// ====== Action Bar ======
.action-bar { text-align: center; padding: 8px 0 32px; }
.regen-btn {
  display: inline-flex; align-items: center; gap: 8px;
  padding: 10px 24px; border: 2px solid #1a3a5c; border-radius: 10px;
  background: #fff; color: #1a3a5c; font-size: 14px; font-weight: 600;
  cursor: pointer; transition: all 0.2s;
  &:hover:not(:disabled) { background: #f0f4f9; transform: translateY(-1px); }
  &:disabled { opacity: 0.5; cursor: not-allowed; }
}


// ====== Mind Map Toolbar ======
.mindmap-toolbar {
  position: absolute;
  top: 12px;
  right: 12px;
  z-index: 10;
  display: flex;
  align-items: center;
  gap: 4px;
  background: rgba(255, 255, 255, 0.95);
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  padding: 4px 6px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
}
.toolbar-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 30px;
  height: 30px;
  border: none;
  border-radius: 6px;
  background: transparent;
  color: #606266;
  cursor: pointer;
  transition: all 0.15s;
  &:hover { background: #f3f4f5; color: #1a3a5c; }
  &:active { background: #e5e7eb; }
}
.zoom-label {
  font-size: 12px;
  font-weight: 600;
  color: #606266;
  min-width: 36px;
  text-align: center;
  user-select: none;
}
.toolbar-divider {
  width: 1px;
  height: 18px;
  background: #e5e7eb;
  margin: 0 2px;
}

// ====== Responsive ======
@media (max-width: 768px) {
  .score-section { flex-direction: column; text-align: center; }
  .mindmap-header { flex-direction: column; align-items: flex-start; gap: 12px; }
}
@media (max-width: 480px) {
  .input-tabs { flex-direction: column; }
}
</style>
