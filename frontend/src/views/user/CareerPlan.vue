<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, nextTick } from 'vue'
import * as echarts from 'echarts'
import {
  Sparkles, Loader2, RefreshCw, TrendingUp, Award,
  BookOpen, Users, Target, ArrowUpRight, Star,
  Plus, Minus, Download, Eye, Code, Upload, FileText,
  GraduationCap, MessageSquare, CheckCircle, AlertCircle,
  Lightbulb, ChevronRight, Briefcase, BarChart3,
} from 'lucide-vue-next'
import { ElMessage } from 'element-plus'
import { aiGenerateCareerPlan } from '@/api/career'
import type { AiPlanResponse, MindMapNode } from '@/api/career'

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
const radarChartRef = ref<HTMLElement>()
const growthChartRef = ref<HTMLElement>()
let chartInstance: echarts.ECharts | null = null
let radarInstance: echarts.ECharts | null = null
let growthInstance: echarts.ECharts | null = null
const zoomLevel = ref(1)
const MIN_ZOOM = 0.5
const MAX_ZOOM = 3

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
  if (s >= 80) return '#10b981'
  if (s >= 60) return '#3b82f6'
  if (s >= 40) return '#f59e0b'
  return '#ef4444'
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

function initMindMap() {
  zoomLevel.value = 1
  if (!chartRef.value || !planData.value?.mind_map) return

  if (!chartInstance) {
    chartInstance = echarts.init(chartRef.value, undefined, { renderer: 'canvas' })
  }
  chartInstance.clear()

  const nodes = deepCount(planData.value.mind_map)
  const chartHeight = Math.max(nodes * 45 + 100, 500)

  chartInstance.setOption({
    tooltip: {
      trigger: 'item',
      backgroundColor: 'rgba(255,255,255,0.96)',
      borderColor: '#e8e8e8',
      borderWidth: 1,
      padding: [8, 14],
      textStyle: { color: '#121c28', fontSize: 13 },
      formatter: (params: any) => {
        const name = params.name || ''
        const depth = params.treePathInfo?.length || 0
        if (depth <= 2) return '<strong style="font-size:15px;color:#003527;">' + name + '</strong>'
        return '<span style="color:#404944;font-size:13px;">' + name + '</span>'
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
        color: '#121c28',
        width: 200,
        overflow: 'break',
        formatter: (params: any) => {
          const name = params.name || ''
          const depth = params.treePathInfo?.length || 0
          if (depth <= 2) return '{bold|' + name + '}'
          return name
        },
        rich: {
          bold: { fontSize: 16, fontWeight: 700, color: '#003527' },
        },
      },
      leaves: {
        label: {
          position: 'bottom',
          fontSize: 13,
          color: '#404944',
          width: 180,
          overflow: 'break',
        },
      },
      lineStyle: {
        color: '#003527',
        width: 1.5,
        curveness: 0.5,
      },
      animationDuration: 800,
      animationEasing: 'cubicOut',
    }],
  }, true)

  chartRef.value.style.height = chartHeight + 'px'
  chartInstance.resize()
}

function initRadarChart() {
  if (!radarChartRef.value || !planData.value?.gap_skills) return

  if (!radarInstance) {
    radarInstance = echarts.init(radarChartRef.value, undefined, { renderer: 'canvas' })
  }
  radarInstance.clear()

  const skills = planData.value.gap_skills.slice(0, 6)
  const indicators = skills.map(s => ({ name: s.skill_name, max: 100 }))
  const currentValues = skills.map(s => s.current_level || 0)
  const targetValues = skills.map(s => s.target_level || 100)

  radarInstance.setOption({
    tooltip: {
      trigger: 'item',
    },
    radar: {
      indicator: indicators,
      shape: 'polygon',
      splitNumber: 4,
      axisName: {
        color: '#404944',
        fontSize: 12,
      },
      splitLine: {
        lineStyle: {
          color: ['#bfc9c3', '#bfc9c3', '#bfc9c3', '#bfc9c3'],
        },
      },
      splitArea: {
        show: true,
        areaStyle: {
          color: ['rgba(26,58,92,0.02)', 'rgba(26,58,92,0.04)'],
        },
      },
      axisLine: {
        lineStyle: {
          color: '#bfc9c3',
        },
      },
    },
    series: [{
      type: 'radar',
      data: [
        {
          value: currentValues,
          name: '当前水平',
          symbol: 'circle',
          symbolSize: 6,
          lineStyle: {
            width: 2,
            color: '#3b82f6',
          },
          areaStyle: {
            color: 'rgba(59,130,246,0.2)',
          },
          itemStyle: {
            color: '#3b82f6',
          },
        },
        {
          value: targetValues,
          name: '目标水平',
          symbol: 'circle',
          symbolSize: 6,
          lineStyle: {
            width: 2,
            color: '#10b981',
            type: 'dashed',
          },
          areaStyle: {
            color: 'rgba(16,185,129,0.1)',
          },
          itemStyle: {
            color: '#10b981',
          },
        },
      ],
    }],
  }, true)
}

function initGrowthChart() {
  if (!growthChartRef.value || !planData.value?.growth_curve) return

  if (!growthInstance) {
    growthInstance = echarts.init(growthChartRef.value, undefined, { renderer: 'canvas' })
  }
  growthInstance.clear()

  const curve = planData.value.growth_curve
  const xData = curve.map(c => c.label)
  const yData = curve.map(c => c.value)

  growthInstance.setOption({
    tooltip: {
      trigger: 'axis',
      backgroundColor: 'rgba(255,255,255,0.96)',
      borderColor: '#e8e8e8',
      borderWidth: 1,
      textStyle: { color: '#121c28' },
      formatter: (params: any) => {
        const item = params[0]
        return `<strong>${item.name}</strong><br/>能力值: <span style="color:#3b82f6;font-weight:bold;">${item.value}</span>`
      },
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      top: '10%',
      containLabel: true,
    },
    xAxis: {
      type: 'category',
      data: xData,
      axisLine: { lineStyle: { color: '#bfc9c3' } },
      axisLabel: { color: '#404944', fontSize: 12 },
      axisTick: { show: false },
    },
    yAxis: {
      type: 'value',
      min: 0,
      max: 100,
      splitLine: { lineStyle: { color: '#f8f9ff', type: 'dashed' } },
      axisLabel: { color: '#404944', fontSize: 12 },
    },
    series: [{
      type: 'line',
      data: yData,
      smooth: true,
      symbol: 'circle',
      symbolSize: 8,
      lineStyle: {
        width: 3,
        color: '#3b82f6',
      },
      itemStyle: {
        color: '#fff',
        borderColor: '#3b82f6',
        borderWidth: 3,
      },
      areaStyle: {
        color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
          { offset: 0, color: 'rgba(59,130,246,0.3)' },
          { offset: 1, color: 'rgba(59,130,246,0.05)' },
        ]),
      },
    }],
  }, true)
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
  radarInstance?.resize()
  growthInstance?.resize()
}

onMounted(() => {
  window.addEventListener('resize', handleResize)
})

onUnmounted(() => {
  chartInstance?.dispose()
  chartInstance = null
  radarInstance?.dispose()
  radarInstance = null
  growthInstance?.dispose()
  growthInstance = null
  window.removeEventListener('resize', handleResize)
})

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
    initRadarChart()
    initGrowthChart()
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
      <header class="page-header">
        <div class="header-left">
          <h1 class="page-title">AI 智能职业规划</h1>
          <p class="page-desc">为你量身定制学习路径，让职业目标清晰可达</p>
        </div>
        <div class="header-right">
          <div class="ai-avatar">
            <div class="avatar-icon">
              <Sparkles :size="20" />
            </div>
            <span class="ai-label">AI</span>
          </div>
        </div>
      </header>

      <section class="input-section">
        <div class="input-header">
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
              <Upload :size="16" />
              招聘链接
            </button>
          </div>
        </div>

        <div class="input-area">
          <template v-if="inputType === 'PROFESSION'">
            <label class="input-label">我的职业目标是</label>
            <div class="input-row">
              <input
                v-model="professionText"
                type="text"
                class="text-input"
                placeholder="例如：教师、软件工程师、产品经理..."
                @keyup.enter="handleGenerate"
              />
              <button class="generate-btn" :disabled="!canGenerate || generating" @click="handleGenerate">
                <Loader2 v-if="generating" :size="18" class="spin-icon" />
                <Sparkles v-else :size="18" />
                {{ generating ? 'AI 分析中...' : 'AI 开始规划' }}
              </button>
            </div>
          </template>

          <template v-else-if="inputType === 'JOB_DESCRIPTION'">
            <label class="input-label">粘贴目标公司的招聘岗位 JD</label>
            <textarea
              v-model="jobDescriptionText"
              class="text-area"
              rows="4"
              placeholder="将招聘岗位的职位描述和要求粘贴到这里..."
            ></textarea>
            <button class="generate-btn" :disabled="!canGenerate || generating" @click="handleGenerate">
              <Loader2 v-if="generating" :size="18" class="spin-icon" />
              <Sparkles v-else :size="18" />
              {{ generating ? 'AI 分析中...' : 'AI 开始规划' }}
            </button>
          </template>

          <template v-else>
            <label class="input-label">输入目标公司的招聘岗位链接</label>
            <div class="input-row">
              <input
                v-model="jobUrlText"
                type="url"
                class="text-input"
                placeholder="例如：https://www.zhipin.com/job/..."
                @keyup.enter="handleGenerate"
              />
              <button class="generate-btn" :disabled="!canGenerate || generating" @click="handleGenerate">
                <Loader2 v-if="generating" :size="18" class="spin-icon" />
                <Sparkles v-else :size="18" />
                {{ generating ? 'AI 分析中...' : 'AI 开始规划' }}
              </button>
            </div>
          </template>
        </div>

        <div v-if="errorMsg" class="error-banner">{{ errorMsg }}</div>
      </section>

      <template v-if="hasPlan && planData">
        <div class="main-content">
          <div class="content-left">
            <div class="grid-row">
              <div class="match-card">
                <div class="card-header">
                  <Target :size="18" class="card-icon" />
                  <span class="card-title">职业匹配度</span>
                </div>
                <div class="score-display">
                  <svg width="120" height="120" viewBox="0 0 120 120">
                    <circle cx="60" cy="60" r="48" fill="none" stroke="#e9ecef" stroke-width="8" />
                    <circle
                      cx="60" cy="60" r="48" fill="none"
                      :stroke="scoreColor" stroke-width="8"
                      stroke-linecap="round"
                      :stroke-dasharray="2 * Math.PI * 48"
                      :stroke-dashoffset="2 * Math.PI * 48 * (1 - planData.match_score / 100)"
                      transform="rotate(-90 60 60)"
                      class="score-arc"
                    />
                    <text x="60" y="56" text-anchor="middle" fill="#121c28" font-size="28" font-weight="700">{{ planData.match_score }}</text>
                    <text x="60" y="74" text-anchor="middle" fill="#404944" font-size="12">%</text>
                  </svg>
                </div>
                <div class="score-stars">
                  <Star v-for="n in 5" :key="n" :size="14" :class="{ filled: n <= Math.ceil(planData.match_score / 20) }" />
                </div>
                <p class="score-tip">匹配度较低，建议提升核心技能</p>
              </div>

              <div class="swot-card">
                <div class="card-header">
                  <MessageSquare :size="18" class="card-icon" />
                  <span class="card-title">优势 & 不足分析</span>
                </div>
                <div class="swot-content">
                  <div class="swot-left">
                    <h4 class="swot-title strengths"><CheckCircle :size="14" /> 优势</h4>
                    <ul class="swot-list">
                      <li v-for="(item, idx) in planData.strength_weakness.strengths.slice(0, 4)" :key="idx">{{ item }}</li>
                    </ul>
                  </div>
                  <div class="swot-right">
                    <h4 class="swot-title weaknesses"><AlertCircle :size="14" /> 不足</h4>
                    <ul class="swot-list">
                      <li v-for="(item, idx) in planData.strength_weakness.weaknesses.slice(0, 4)" :key="idx">{{ item }}</li>
                    </ul>
                  </div>
                </div>
              </div>

              <div class="career-path-card">
                <div class="card-header">
                  <Users :size="18" class="card-icon" />
                  <span class="card-title">职业发展路径</span>
                </div>
                <div class="career-stages">
                  <div
                    v-for="(stage, idx) in planData.career_stages"
                    :key="idx"
                    class="stage-item"
                  >
                    <div class="stage-icon">
                      <Briefcase :size="16" />
                    </div>
                    <div class="stage-info">
                      <span class="stage-name">{{ stage.title }}</span>
                      <span class="stage-label">{{ stage.stage }}</span>
                    </div>
                    <ChevronRight v-if="idx < planData.career_stages.length - 1" :size="14" class="stage-arrow" />
                  </div>
                </div>
                <p class="path-desc">学前教育行业需求稳定增长，国家政策支持，职业发展空间大。</p>
              </div>
            </div>

            <div class="grid-row">
              <div class="skill-gap-card">
                <div class="card-header">
                  <BarChart3 :size="18" class="card-icon" />
                  <span class="card-title">技能差距分析</span>
                </div>
                <div class="skill-tabs">
                  <button class="skill-tab" :class="{ active: gapMustSkills.length > 0 }">MUST 必备</button>
                  <button class="skill-tab" :class="{ active: gapNiceSkills.length > 0 }">NICE 加分</button>
                  <button class="skill-tab" :class="{ active: gapBonusSkills.length > 0 }">BONUS 锦上添花</button>
                </div>
                <div class="skill-list">
                  <div v-for="skill in gapMustSkills" :key="skill.skill_name" class="skill-item">
                    <div class="skill-header">
                      <span class="skill-name">{{ skill.skill_name }}</span>
                      <span class="skill-percent">{{ skill.current_level }}% → {{ skill.target_level }}%</span>
                    </div>
                    <div class="skill-bar">
                      <div class="skill-bar-fill" :style="{ width: skill.current_level + '%' }"></div>
                    </div>
                  </div>
                </div>
              </div>

              <div class="radar-card">
                <div class="card-header">
                  <TrendingUp :size="18" class="card-icon" />
                  <span class="card-title">能力成长曲线</span>
                </div>
                <div ref="radarChartRef" class="radar-chart"></div>
              </div>

              <div class="growth-card">
                <div class="card-header">
                  <TrendingUp :size="18" class="card-icon" />
                  <span class="card-title">能力成长曲线</span>
                </div>
                <div ref="growthChartRef" class="growth-chart"></div>
              </div>
            </div>

            <div class="grid-row">
              <div class="resources-card">
                <div class="card-header">
                  <BookOpen :size="18" class="card-icon" />
                  <span class="card-title">推荐学习资源</span>
                  <button class="view-more">查看更多</button>
                </div>
                <div class="resources-list">
                  <div
                    v-for="resource in planData.learning_resources"
                    :key="resource.id"
                    class="resource-item"
                  >
                    <div class="resource-cover">
                      <BookOpen :size="24" />
                    </div>
                    <div class="resource-info">
                      <h4 class="resource-title">{{ resource.title }}</h4>
                      <div class="resource-rating">
                        <Star v-for="n in 5" :key="n" :size="12" :class="{ filled: n <= Math.ceil(resource.rating) }" />
                        <span class="rating-num">{{ resource.rating }}</span>
                      </div>
                    </div>
                    <button class="resource-btn">
                      <ArrowUpRight :size="14" />
                      学习
                    </button>
                  </div>
                </div>
              </div>

              <div class="outlook-card">
                <div class="card-header">
                  <TrendingUp :size="18" class="card-icon" />
                  <span class="card-title">就业前景预测</span>
                </div>
                <div class="outlook-content">
                  <div class="salary-info">
                    <span class="salary-label">预计薪资</span>
                    <span class="salary-value">{{ planData.employment_outlook.salary_range }}</span>
                  </div>
                  <div class="demand-info">
                    <span class="demand-label">需求等级</span>
                    <div class="demand-stars">
                      <Star v-for="n in 5" :key="n" :size="14" :class="{ filled: n <= 4 }" />
                    </div>
                  </div>
                  <div class="growth-info">
                    <span class="growth-label">增长率</span>
                    <span class="growth-value positive">{{ planData.employment_outlook.growth_rate }}</span>
                  </div>
                </div>
              </div>

              <div class="stats-card">
                <div class="card-header">
                  <Award :size="18" class="card-icon" />
                  <span class="card-title">学习数据概览</span>
                </div>
                <div class="stats-grid">
                  <div class="stat-item">
                    <span class="stat-value">{{ planData.learning_stats.total_hours }}</span>
                    <span class="stat-label">累计学时</span>
                  </div>
                  <div class="stat-item">
                    <span class="stat-value">{{ planData.learning_stats.completed_courses }}</span>
                    <span class="stat-label">已学课程</span>
                  </div>
                  <div class="stat-item">
                    <span class="stat-value">{{ planData.learning_stats.planned_courses }}</span>
                    <span class="stat-label">预计学习课程</span>
                  </div>
                  <div class="stat-item">
                    <span class="stat-value">{{ planData.learning_stats.certificates }}</span>
                    <span class="stat-label">证书完成</span>
                  </div>
                </div>
                <div class="progress-section">
                  <div class="progress-row">
                    <span class="progress-label">完成度</span>
                    <span class="progress-value">{{ planData.learning_stats.completion_rate }}%</span>
                  </div>
                  <div class="progress-bar">
                    <div class="progress-fill" :style="{ width: planData.learning_stats.completion_rate + '%' }"></div>
                  </div>
                  <div class="progress-row">
                    <span class="progress-label">目标完成度</span>
                    <span class="progress-value">{{ planData.learning_stats.target_completion_rate }}%</span>
                  </div>
                </div>
              </div>
            </div>

            <div class="mindmap-section">
              <div class="card-header">
                <span class="card-title">学习路径思维导图</span>
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
              </div>
              <div v-show="mindMapMode === 'code'" class="mindmap-code">
                <pre class="code-block"><code>{{ formattedJson }}</code></pre>
              </div>
            </div>
          </div>

          <div class="content-right">
            <div class="ai-suggestions-card">
              <div class="card-header">
                <Sparkles :size="18" class="card-icon" />
                <span class="card-title">AI 建议</span>
              </div>
              <div class="suggestions-list">
                <div
                  v-for="(suggestion, idx) in planData.ai_suggestions"
                  :key="idx"
                  class="suggestion-item"
                >
                  <span class="suggestion-number">{{ idx + 1 }}</span>
                  <span class="suggestion-text">{{ suggestion.title }}</span>
                </div>
              </div>
              <div class="suggestion-summary">
                <div class="summary-row">
                  <span class="summary-label">预计学习时长</span>
                  <span class="summary-value">6 个月</span>
                </div>
                <div class="summary-row">
                  <span class="summary-label">匹配度提升</span>
                  <span class="summary-value positive">0% → +72%</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div class="action-bar">
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
.career-page { padding: 24px 16px; background: linear-gradient(180deg, #f8fafc 0%, #f1f5f9 100%); min-height: 100vh; }
.career-container { max-width: 1400px; margin: 0 auto; }

@keyframes fadeUp {
  from { opacity: 0; transform: translateY(20px); }
  to { opacity: 1; transform: translateY(0); }
}
@keyframes spin { to { transform: rotate(360deg); } }
.fade-up { opacity: 0; animation: fadeUp 0.5s cubic-bezier(0.22,1,0.36,1) forwards; }
.spin-icon { animation: spin 1s linear infinite; }

.page-header {
  display: flex; justify-content: space-between; align-items: flex-start;
  margin-bottom: 28px; padding: 20px 0;
}
.header-left { flex: 1; }
.page-title { font-size: 36px; font-weight: 700; color: #1e293b; letter-spacing: -1px; margin-bottom: 6px; }
.page-desc { font-size: 16px; color: #64748b; margin: 0; }
.header-right { flex-shrink: 0; }
.ai-avatar {
  display: flex; align-items: center; gap: 10px;
  padding: 12px 20px; background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
  border-radius: 12px; box-shadow: 0 8px 32px rgba(99,102,241,0.25);
}
.avatar-icon {
  width: 40px; height: 40px; background: rgba(255,255,255,0.2);
  border-radius: 50%; display: flex; align-items: center; justify-content: center;
  color: #fff;
}
.ai-label { color: #fff; font-size: 14px; font-weight: 600; }

.input-section {
  background: #fff; border-radius: 16px; padding: 28px 32px;
  border: 1px solid #e2e8f0; margin-bottom: 28px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.04);
}
.input-header { margin-bottom: 16px; }
.input-tabs {
  display: flex; gap: 6px; margin-bottom: 20px;
  background: #f1f5f9; border-radius: 10px; padding: 4px;
}
.input-tab {
  flex: 1; display: flex; align-items: center; justify-content: center; gap: 6px;
  padding: 10px 16px; border: none; border-radius: 8px;
  background: transparent; color: #64748b; font-size: 14px; font-weight: 500;
  cursor: pointer; transition: all 0.2s;
  &:hover { color: #334155; }
  &.active {
    background: #fff; color: #1e293b; font-weight: 600;
    box-shadow: 0 2px 8px rgba(0,0,0,0.06);
  }
}
.input-area { margin-bottom: 16px; }
.input-label {
  display: block; font-size: 14px; font-weight: 600; color: #334155; margin-bottom: 10px;
}
.input-row { display: flex; gap: 12px; }
.text-input {
  flex: 1; padding: 12px 16px; border: 2px solid #e2e8f0; border-radius: 10px;
  font-size: 15px; color: #1e293b; outline: none; transition: border-color 0.2s;
  box-sizing: border-box;
  &:focus { border-color: #3b82f6; }
  &::placeholder { color: #94a3b8; }
}
.text-area {
  width: 100%; padding: 12px 16px; border: 2px solid #e2e8f0; border-radius: 10px;
  font-size: 14px; color: #1e293b; outline: none; resize: vertical; transition: border-color 0.2s;
  font-family: inherit; line-height: 1.6; box-sizing: border-box;
  &:focus { border-color: #3b82f6; }
  &::placeholder { color: #94a3b8; }
}
.generate-btn {
  display: inline-flex; align-items: center; gap: 8px;
  padding: 12px 28px; border: none; border-radius: 10px;
  background: linear-gradient(135deg, #3b82f6 0%, #6366f1 100%);
  color: #fff; font-size: 15px; font-weight: 600;
  cursor: pointer; transition: all 0.2s; white-space: nowrap;
  &:hover:not(:disabled) { transform: translateY(-1px); box-shadow: 0 4px 16px rgba(59,130,246,0.25); }
  &:disabled { opacity: 0.5; cursor: not-allowed; }
}
.error-banner {
  background: #fef2f2; border: 1px solid #fecaca; border-radius: 8px; padding: 12px 16px;
  color: #dc2626; font-size: 14px; margin-bottom: 16px;
}

.main-content { display: flex; gap: 24px; }
.content-left { flex: 1; }
.content-right { width: 320px; flex-shrink: 0; }

.grid-row { display: grid; grid-template-columns: repeat(3, 1fr); gap: 20px; margin-bottom: 20px; }

.card-header {
  display: flex; align-items: center; justify-content: space-between; margin-bottom: 16px;
}
.card-icon { color: #3b82f6; }
.card-title { font-size: 16px; font-weight: 600; color: #1e293b; }
.view-more {
  border: none; background: transparent; color: #3b82f6; font-size: 13px; font-weight: 500;
  cursor: pointer; transition: color 0.2s; &:hover { color: #2563eb; }
}

.match-card {
  background: #fff; border-radius: 16px; padding: 24px;
  border: 1px solid #e2e8f0; box-shadow: 0 2px 8px rgba(0,0,0,0.04);
  text-align: center;
}
.score-display { margin: 16px auto; width: 120px; }
.score-arc { transition: stroke-dashoffset 0.8s ease; }
.score-stars { display: flex; justify-content: center; gap: 2px; margin: 12px 0; }
.score-stars .filled { color: #fbbf24; }
.score-tip { font-size: 13px; color: #64748b; margin: 0; }

.swot-card {
  background: #fff; border-radius: 16px; padding: 24px;
  border: 1px solid #e2e8f0; box-shadow: 0 2px 8px rgba(0,0,0,0.04);
}
.swot-content { display: flex; gap: 20px; }
.swot-left, .swot-right { flex: 1; }
.swot-title { font-size: 13px; font-weight: 600; margin-bottom: 12px; display: flex; align-items: center; gap: 6px; }
.swot-title.strengths { color: #10b981; }
.swot-title.weaknesses { color: #ef4444; }
.swot-list { list-style: none; padding: 0; margin: 0; }
.swot-list li {
  font-size: 13px; color: #475569; padding: 6px 0; border-bottom: 1px dashed #f1f5f9;
  &:last-child { border-bottom: none; }
}

.career-path-card {
  background: #fff; border-radius: 16px; padding: 24px;
  border: 1px solid #e2e8f0; box-shadow: 0 2px 8px rgba(0,0,0,0.04);
}
.career-stages { display: flex; flex-direction: column; gap: 12px; }
.stage-item {
  display: flex; align-items: center; gap: 12px; padding: 10px;
  background: #f8fafc; border-radius: 10px; transition: background 0.2s;
  &:hover { background: #f1f5f9; }
}
.stage-icon {
  width: 32px; height: 32px; background: #3b82f6; border-radius: 8px;
  display: flex; align-items: center; justify-content: center; color: #fff;
}
.stage-info { flex: 1; }
.stage-name { display: block; font-size: 13px; font-weight: 600; color: #1e293b; }
.stage-label { font-size: 11px; color: #64748b; }
.stage-arrow { color: #cbd5e1; }
.path-desc { font-size: 12px; color: #64748b; margin-top: 12px; line-height: 1.6; }

.skill-gap-card {
  background: #fff; border-radius: 16px; padding: 24px;
  border: 1px solid #e2e8f0; box-shadow: 0 2px 8px rgba(0,0,0,0.04);
}
.skill-tabs { display: flex; gap: 4px; margin-bottom: 16px; }
.skill-tab {
  padding: 4px 12px; border: none; border-radius: 6px;
  background: #f1f5f9; color: #64748b; font-size: 12px; font-weight: 500;
  cursor: pointer; transition: all 0.2s;
  &.active { background: #dc2626; color: #fff; }
}
.skill-list { display: flex; flex-direction: column; gap: 14px; }
.skill-item { }
.skill-header { display: flex; justify-content: space-between; margin-bottom: 6px; }
.skill-name { font-size: 13px; font-weight: 500; color: #334155; }
.skill-percent { font-size: 12px; color: #64748b; }
.skill-bar {
  height: 6px; background: #f1f5f9; border-radius: 3px; overflow: hidden;
}
.skill-bar-fill { height: 100%; background: linear-gradient(90deg, #3b82f6, #6366f1); border-radius: 3px; transition: width 0.5s ease; }

.radar-card {
  background: #fff; border-radius: 16px; padding: 24px;
  border: 1px solid #e2e8f0; box-shadow: 0 2px 8px rgba(0,0,0,0.04);
}
.radar-chart { width: 100%; height: 200px; }

.growth-card {
  background: #fff; border-radius: 16px; padding: 24px;
  border: 1px solid #e2e8f0; box-shadow: 0 2px 8px rgba(0,0,0,0.04);
}
.growth-chart { width: 100%; height: 200px; }

.resources-card {
  background: #fff; border-radius: 16px; padding: 24px;
  border: 1px solid #e2e8f0; box-shadow: 0 2px 8px rgba(0,0,0,0.04);
}
.resources-list { display: flex; flex-direction: column; gap: 14px; }
.resource-item {
  display: flex; align-items: center; gap: 14px; padding: 12px;
  background: #f8fafc; border-radius: 10px; transition: background 0.2s;
  &:hover { background: #f1f5f9; }
}
.resource-cover {
  width: 48px; height: 48px; background: linear-gradient(135deg, #3b82f6, #6366f1);
  border-radius: 10px; display: flex; align-items: center; justify-content: center;
  color: #fff;
}
.resource-info { flex: 1; }
.resource-title { font-size: 13px; font-weight: 600; color: #1e293b; margin-bottom: 4px; }
.resource-rating { display: flex; align-items: center; gap: 4px; }
.resource-rating .filled { color: #fbbf24; }
.rating-num { font-size: 12px; color: #64748b; }
.resource-btn {
  padding: 6px 14px; border: 2px solid #3b82f6; border-radius: 6px;
  background: transparent; color: #3b82f6; font-size: 12px; font-weight: 500;
  cursor: pointer; transition: all 0.2s; display: flex; align-items: center; gap: 4px;
  &:hover { background: #3b82f6; color: #fff; }
}

.outlook-card {
  background: #fff; border-radius: 16px; padding: 24px;
  border: 1px solid #e2e8f0; box-shadow: 0 2px 8px rgba(0,0,0,0.04);
}
.outlook-content { display: flex; flex-direction: column; gap: 16px; }
.salary-info, .demand-info, .growth-info { display: flex; justify-content: space-between; align-items: center; }
.salary-label, .demand-label, .growth-label { font-size: 13px; color: #64748b; }
.salary-value { font-size: 20px; font-weight: 700; color: #1e293b; }
.demand-stars { display: flex; gap: 2px; }
.demand-stars .filled { color: #fbbf24; }
.growth-value { font-size: 14px; font-weight: 600; }
.growth-value.positive { color: #10b981; }

.stats-card {
  background: #fff; border-radius: 16px; padding: 24px;
  border: 1px solid #e2e8f0; box-shadow: 0 2px 8px rgba(0,0,0,0.04);
}
.stats-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 16px; margin-bottom: 20px; }
.stat-item { text-align: center; padding: 12px; background: #f8fafc; border-radius: 10px; }
.stat-value { display: block; font-size: 24px; font-weight: 700; color: #1e293b; }
.stat-label { font-size: 12px; color: #64748b; }
.progress-section { }
.progress-row { display: flex; justify-content: space-between; margin-bottom: 6px; }
.progress-label { font-size: 12px; color: #64748b; }
.progress-value { font-size: 12px; font-weight: 600; color: #1e293b; }
.progress-bar {
  height: 8px; background: #f1f5f9; border-radius: 4px; overflow: hidden;
  margin-bottom: 12px;
}
.progress-fill {
  height: 100%; background: linear-gradient(90deg, #10b981, #34d399);
  border-radius: 4px; transition: width 0.5s ease;
}

.mindmap-section {
  background: #fff; border-radius: 16px; padding: 24px;
  border: 1px solid #e2e8f0; box-shadow: 0 2px 8px rgba(0,0,0,0.04);
  margin-top: 20px;
}
.mode-toggle {
  display: flex; gap: 4px;
  background: #f1f5f9; border-radius: 8px; padding: 3px;
}
.mode-btn {
  display: inline-flex; align-items: center; gap: 4px;
  padding: 6px 14px; border: none; border-radius: 6px;
  background: transparent; color: #64748b; font-size: 13px; font-weight: 500;
  cursor: pointer; transition: all 0.2s;
  &:hover { color: #334155; }
  &.active {
    background: #fff; color: #1e293b; font-weight: 600;
    box-shadow: 0 2px 6px rgba(0,0,0,0.08);
  }
}
.mindmap-render {
  position: relative; overflow: auto;
  background: #f8fafc; border-radius: 12px; padding: 16px;
}
.chart-box {
  width: 100%; min-height: 500px; border-radius: 8px;
  transition: height 0.3s ease;
}
.empty-mindmap {
  display: flex; flex-direction: column; align-items: center; gap: 12px;
  padding: 60px 0; color: #94a3b8;
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

.ai-suggestions-card {
  background: #fff; border-radius: 16px; padding: 24px;
  border: 1px solid #e2e8f0; box-shadow: 0 2px 8px rgba(0,0,0,0.04);
  position: sticky; top: 24px;
}
.suggestions-list { display: flex; flex-direction: column; gap: 12px; margin-bottom: 20px; }
.suggestion-item {
  display: flex; align-items: flex-start; gap: 10px; padding: 10px;
  background: #f8fafc; border-radius: 10px;
}
.suggestion-number {
  width: 22px; height: 22px; background: #6366f1; color: #fff;
  border-radius: 50%; display: flex; align-items: center; justify-content: center;
  font-size: 11px; font-weight: 600; flex-shrink: 0;
}
.suggestion-text { font-size: 13px; color: #334155; line-height: 1.5; }
.suggestion-summary {
  padding-top: 16px; border-top: 1px solid #e2e8f0;
}
.summary-row { display: flex; justify-content: space-between; margin-bottom: 8px; }
.summary-label { font-size: 13px; color: #64748b; }
.summary-value { font-size: 13px; font-weight: 600; color: #1e293b; }
.summary-value.positive { color: #10b981; }

.action-bar { text-align: center; padding: 20px 0; }
.regen-btn {
  display: inline-flex; align-items: center; gap: 8px;
  padding: 10px 24px; border: 2px solid #3b82f6; border-radius: 10px;
  background: #fff; color: #3b82f6; font-size: 14px; font-weight: 600;
  cursor: pointer; transition: all 0.2s;
  &:hover:not(:disabled) { background: #eff6ff; transform: translateY(-1px); }
  &:disabled { opacity: 0.5; cursor: not-allowed; }
}

.mindmap-toolbar {
  position: absolute; top: 12px; right: 12px; z-index: 10;
  display: flex; align-items: center; gap: 4px;
  background: rgba(255,255,255,0.95); border: 1px solid #e2e8f0;
  border-radius: 8px; padding: 4px 6px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.08);
}
.toolbar-btn {
  display: flex; align-items: center; justify-content: center;
  width: 30px; height: 30px; border: none; border-radius: 6px;
  background: transparent; color: #64748b; cursor: pointer;
  transition: all 0.15s;
  &:hover { background: #f1f5f9; color: #1e293b; }
}
.zoom-label {
  font-size: 12px; font-weight: 600; color: #64748b;
  min-width: 36px; text-align: center; user-select: none;
}
.toolbar-divider { width: 1px; height: 18px; background: #e2e8f0; margin: 0 2px; }

@media (max-width: 1200px) {
  .grid-row { grid-template-columns: repeat(2, 1fr); }
  .content-right { display: none; }
}
@media (max-width: 768px) {
  .grid-row { grid-template-columns: 1fr; }
  .input-row { flex-direction: column; }
  .swot-content { flex-direction: column; }
  .page-header { flex-direction: column; gap: 16px; }
}
</style>