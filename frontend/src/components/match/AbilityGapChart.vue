<script setup lang="ts">
import { ref, onMounted, onUnmounted, computed, watch, nextTick } from 'vue'
import * as echarts from 'echarts'
import { X, Target, Award, AlertTriangle, MinusCircle, Sparkles } from 'lucide-vue-next'
import { getUserGraph, getJobGraph } from '@/api/graph'
import type { GraphNode, GapSkill } from '@/types/graph'

const props = defineProps<{
  visible: boolean
  jobId: number
}>()

const emit = defineEmits<{
  (e: 'close'): void
}>()

const chartRef = ref<HTMLElement>()
let chartInstance: echarts.ECharts | null = null
const loading = ref(true)
const error = ref('')
const userSkills = ref<GraphNode[]>([])
const jobSkills = ref<{ name: string; importance: number; required_level: string }[]>([])
const gapSkills = ref<GapSkill[]>([])

interface BubbleData {
  name: string
  x: number
  y: number
  size: number
  category: string
  requirement_level: string
  quadrant: 'core' | 'fatal' | 'redundant' | 'irrelevant'
}

function mergeSimilarSkills(skills: { name: string; importance: number; required_level: string }[]): typeof skills {
  const merged = new Map<string, typeof skills[0]>()
  const levelOrder = { MUST: 3, NICE: 2, BONUS: 1 }
  
  for (const skill of skills) {
    let baseName = skill.name
    if (skill.name.endsWith(' NN')) baseName = skill.name.replace(' NN', '')
    
    if (!merged.has(baseName) || levelOrder[skill.required_level] > levelOrder[merged.get(baseName)!.required_level]) {
      merged.set(baseName, skill)
    }
  }
  
  return Array.from(merged.values())
}

const bubbleData = computed<BubbleData[]>(() => {
  const data: BubbleData[] = []
  const mergedSkills = mergeSimilarSkills(jobSkills.value)
  
  for (let i = 0; i < mergedSkills.length; i++) {
    const jobSkill = mergedSkills[i]
    const userSkill = userSkills.value.find(u => u.name === jobSkill.name)
    const userLevel = userSkill ? userSkill.level : 0
    const importance = jobSkill.importance
    
    const baseGap = jobSkill.required_level === 'MUST' ? 5 : jobSkill.required_level === 'NICE' ? 4 : 3
    const gap = Math.max(0, baseGap - userLevel)
    const difficulty = gap * (jobSkill.required_level === 'MUST' ? 1.5 : jobSkill.required_level === 'NICE' ? 1.0 : 0.5)
    
    let quadrant: BubbleData['quadrant'] = 'irrelevant'
    if (importance >= 3 && userLevel >= 3) quadrant = 'core'
    else if (importance >= 3 && userLevel < 3) quadrant = 'fatal'
    else if (importance < 3 && userLevel >= 3) quadrant = 'redundant'
    else quadrant = 'irrelevant'
    
    const angle = (i / jobSkills.value.length) * Math.PI * 2
    const radius = 1.0 + Math.random() * 1.5
    let x = importance + Math.cos(angle) * radius
    
    let yOffset = Math.sin(angle) * radius
    if (userLevel < 1.0) {
      yOffset = Math.abs(yOffset)
    }
    let y = userLevel + yOffset
    
    data.push({
      name: jobSkill.name,
      x: Math.max(0.5, Math.min(5.5, x)),
      y: Math.max(0.8, Math.min(5.3, y)),
      size: Math.max(25, Math.min(70, difficulty * 15)),
      category: userSkill?.category || '通用',
      requirement_level: jobSkill.required_level,
      quadrant,
    })
  }
  
  return data
})

const quadrantStats = computed(() => ({
  core: bubbleData.value.filter(d => d.quadrant === 'core').length,
  fatal: bubbleData.value.filter(d => d.quadrant === 'fatal').length,
  redundant: bubbleData.value.filter(d => d.quadrant === 'redundant').length,
  irrelevant: bubbleData.value.filter(d => d.quadrant === 'irrelevant').length,
}))

const fatalSkills = computed(() => bubbleData.value.filter(d => d.quadrant === 'fatal'))
const coreSkills = computed(() => bubbleData.value.filter(d => d.quadrant === 'core'))

function initChart() {
  if (!chartRef.value) return
  if (chartInstance) chartInstance.dispose()
  
  chartInstance = echarts.init(chartRef.value)
  
  const option: echarts.EChartsOption = {
    backgroundColor: '#fff',
    tooltip: {
        trigger: 'item',
        backgroundColor: 'rgba(255,255,255,0.96)',
        borderColor: '#e8e8e8',
        borderWidth: 1,
        padding: [12, 16],
        textStyle: { color: '#121c28', fontSize: 13 },
        formatter: (params: any) => {
          const d = params.data
          const labels: Record<string, string> = {
            core: '核心卖点',
            fatal: '致命差距',
            redundant: '冗余优势',
            irrelevant: '无关差距',
          }
          const reqLabels: Record<string, string> = {
            MUST: '必备',
            NICE: '加分',
            BONUS: '可选',
          }
          const x = d.value ? d.value[0] : 0
          const y = d.value ? d.value[1] : 0
          return `<strong style="font-size:15px;color:#121c28;">${d.name}</strong><br/>` +
            `<span style="color:#999">岗位重要性</span><span style="float:right">${x.toFixed(1)} / 5</span><br/>` +
            `<span style="color:#999">当前能力</span><span style="float:right">${y.toFixed(1)} / 5</span><br/>` +
            `<span style="color:#999">要求等级</span><span style="float:right">${reqLabels[d.requirement_level] || d.requirement_level}</span><br/>` +
            `<span style="color:#999">象限</span><span style="float:right">${labels[d.quadrant]}</span>`
        },
      },
    grid: {
      top: 60,
      right: 40,
      bottom: 60,
      left: 80,
    },
    xAxis: {
      type: 'value',
      name: '岗位重要性',
      nameLocation: 'middle',
      nameGap: 35,
      nameTextStyle: { fontSize: 14, fontWeight: 600, color: '#404944' },
      min: 0.5,
      max: 5.5,
      interval: 1,
      axisLine: { lineStyle: { color: '#bfc9c3' } },
      axisTick: { show: false },
      axisLabel: { color: '#404944', fontSize: 12 },
      splitLine: { lineStyle: { color: '#f0f0f0', type: 'dashed' } },
    },
    yAxis: {
      type: 'value',
      name: '当前能力得分',
      nameLocation: 'middle',
      nameGap: 50,
      nameTextStyle: { fontSize: 14, fontWeight: 600, color: '#404944' },
      min: 0,
      max: 5.5,
      interval: 1,
      axisLine: { lineStyle: { color: '#bfc9c3' } },
      axisTick: { show: false },
      axisLabel: { color: '#404944', fontSize: 12 },
      splitLine: { lineStyle: { color: '#f0f0f0', type: 'dashed' } },
    },
    graphic: [
      {
        type: 'line',
        coordinateSystem: 'cartesian2d',
        xAxisIndex: 0,
        yAxisIndex: 0,
        x: 3, y: 0, x2: 3, y2: 5.5,
        lineStyle: { color: '#f56c6c', type: 'dashed', width: 2, opacity: 0.5 },
      },
      {
        type: 'line',
        coordinateSystem: 'cartesian2d',
        xAxisIndex: 0,
        yAxisIndex: 0,
        x: 0.5, y: 3, x2: 5.5, y2: 3,
        lineStyle: { color: '#f56c6c', type: 'dashed', width: 2, opacity: 0.5 },
      },
      {
        type: 'text',
        left: '75%',
        top: '15%',
        style: { text: '核心卖点', fontSize: 14, fontWeight: 700, fill: '#198754' },
      },
      {
        type: 'text',
        left: '25%',
        top: '15%',
        style: { text: '冗余优势', fontSize: 14, fontWeight: 700, fill: '#8b5cf6' },
      },
      {
        type: 'text',
        left: '75%',
        top: '70%',
        style: { text: '致命差距', fontSize: 14, fontWeight: 700, fill: '#dc3545' },
      },
      {
        type: 'text',
        left: '25%',
        top: '70%',
        style: { text: '无关差距', fontSize: 14, fontWeight: 700, fill: '#6c757d' },
      },
    ],
    series: [{
      type: 'scatter',
      data: bubbleData.value.map(d => ({
        name: d.name,
        value: [d.x, d.y, d.size],
        symbolSize: d.size,
        itemStyle: {
          color: d.quadrant === 'core' ? '#198754' :
                 d.quadrant === 'fatal' ? '#dc3545' :
                 d.quadrant === 'redundant' ? '#8b5cf6' : '#6c757d',
          opacity: 0.75,
          borderWidth: 2,
          borderColor: '#fff',
          shadowBlur: 10,
          shadowColor: 'rgba(0,0,0,0.15)',
        },
        emphasis: {
          itemStyle: {
            shadowBlur: 10,
            shadowColor: 'rgba(0,0,0,0.3)',
            scale: 1.2,
          },
        },
        quadrant: d.quadrant,
        requirement_level: d.requirement_level,
      })),
      label: {
        show: true,
        formatter: (params: any) => params.name,
        fontSize: 9,
        fontWeight: 500,
        color: '#333',
        position: 'right',
        distance: 5,
        alignTo: 'edge',
        edgeDistance: 10,
      },
    }],
  }
  
  chartInstance.setOption(option)
}

async function fetchData() {
  loading.value = true
  error.value = ''
  try {
    const [userRes, jobRes] = await Promise.all([
      getUserGraph(),
      getJobGraph(props.jobId),
    ])
    
    const userData = userRes.data.data || {}
    userSkills.value = userData.nodes || []
    
    const jobData = jobRes.data.data || {}
    const jobNodes = jobData.nodes || []
    jobSkills.value = jobNodes.map((n: any) => ({
      name: n.name,
      importance: n.importance || 3,
      required_level: n.required_level || 'NICE',
    }))
  } catch (e: any) {
    error.value = e.message || '加载差距分析失败'
  } finally {
    loading.value = false
    await nextTick()
    initChart()
  }
}

function handleResize() {
  chartInstance?.resize()
}

function handleClose() {
  emit('close')
}

watch(() => props.visible, (val) => {
  if (val) {
    fetchData()
    setTimeout(() => handleResize(), 100)
  }
})

onMounted(() => {
  window.addEventListener('resize', handleResize)
  if (props.visible) {
    fetchData()
    setTimeout(() => handleResize(), 100)
  }
})

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
  chartInstance?.dispose()
  chartInstance = null
})
</script>

<template>
  <div v-if="visible" class="gap-chart-container">
    <div v-if="loading" class="loading-state">
      <div class="loader">
        <div class="loader-ring"></div>
      </div>
      <p>正在分析能力差距...</p>
    </div>

    <div v-else-if="error" class="error-state">
      <p>{{ error }}</p>
      <button class="retry-btn" @click="fetchData">重新加载</button>
    </div>

    <template v-else>
      <div class="chart-section">
        <div ref="chartRef" class="chart-container" />
      </div>

      <div class="stats-section">
        <div class="stats-grid">
          <div class="stat-card core">
            <Award :size="16" />
            <div class="stat-info">
              <span class="stat-num">{{ quadrantStats.core }}</span>
              <span class="stat-label">核心卖点</span>
            </div>
          </div>
          <div class="stat-card fatal">
            <AlertTriangle :size="16" />
            <div class="stat-info">
              <span class="stat-num">{{ quadrantStats.fatal }}</span>
              <span class="stat-label">致命差距</span>
            </div>
          </div>
          <div class="stat-card redundant">
            <Sparkles :size="16" />
            <div class="stat-info">
              <span class="stat-num">{{ quadrantStats.redundant }}</span>
              <span class="stat-label">冗余优势</span>
            </div>
          </div>
          <div class="stat-card irrelevant">
            <MinusCircle :size="16" />
            <div class="stat-info">
              <span class="stat-num">{{ quadrantStats.irrelevant }}</span>
              <span class="stat-label">无关差距</span>
            </div>
          </div>
        </div>

        <div v-if="fatalSkills.length" class="warning-box">
          <AlertTriangle :size="14" class="warning-icon" />
          <div class="warning-content">
            <strong>警告</strong>
            <p>以下技能属于<strong>致命差距</strong>，如果是必备项建议直接放弃或调剂岗位：</p>
            <div class="fatal-skill-tags">
              <span v-for="skill in fatalSkills" :key="skill.name" class="fatal-tag" :class="skill.requirement_level.toLowerCase()">
                {{ skill.name }}
                <span class="tag-badge">{{ skill.requirement_level === 'MUST' ? '必备' : skill.requirement_level === 'NICE' ? '加分' : '可选' }}</span>
              </span>
            </div>
          </div>
        </div>

        <div v-if="coreSkills.length" class="suggestion-box">
          <Award :size="14" class="suggestion-icon" />
          <div class="suggestion-content">
            <strong>优势</strong>
            <p>以下技能是你的<strong>核心卖点</strong>，面试时重点讲：</p>
            <div class="core-skill-tags">
              <span v-for="skill in coreSkills" :key="skill.name" class="core-tag">
                {{ skill.name }}
              </span>
            </div>
          </div>
        </div>

        <div class="legend-box">
          <h4>象限说明</h4>
          <div class="legend-items">
            <div class="legend-item">
              <span class="legend-dot core" />
              <span class="legend-text">
                <strong>核心卖点</strong>（重要+高分）：面试时重点讲
              </span>
            </div>
            <div class="legend-item">
              <span class="legend-dot fatal" />
              <span class="legend-text">
                <strong>致命差距</strong>（重要+低分）：必备项建议放弃或调剂
              </span>
            </div>
            <div class="legend-item">
              <span class="legend-dot redundant" />
              <span class="legend-text">
                <strong>冗余优势</strong>（不重要+高分）：可以提，但不解决主要矛盾
              </span>
            </div>
            <div class="legend-item">
              <span class="legend-dot irrelevant" />
              <span class="legend-text">
                <strong>无关差距</strong>（不重要+低分）：无需浪费精力弥补
              </span>
            </div>
          </div>
          <div class="legend-note">
            <span class="note-label">横轴：</span>岗位重要性（1-5）
            <span class="note-label">纵轴：</span>当前能力得分（0-5）
            <span class="note-label">气泡大小：</span>弥补难度
          </div>
        </div>
      </div>
    </template>
  </div>
</template>

<style scoped lang="scss">
.gap-chart-container {
  width: 100%;
}

.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 0;
  color: #404944;
}

.loader {
  width: 48px;
  height: 48px;
  margin-bottom: 16px;
}

.loader-ring {
  width: 100%;
  height: 100%;
  border: 3px solid #e8e8e8;
  border-top-color: #003527;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.error-state {
  text-align: center;
  padding: 40px 0;
  color: #f56c6c;
}

.retry-btn {
  margin-top: 16px;
  padding: 8px 20px;
  border-radius: 6px;
  background: #003527;
  color: #fff;
  border: none;
  cursor: pointer;
  font-size: 13px;
  &:hover { background: #064e3b; }
}

.chart-section {
  margin-bottom: 20px;
}

.chart-container {
  width: 100%;
  height: 500px;
  border-radius: 12px;
  background: #fafbfc;
  border: 1px solid #eef0f2;
}

.stats-section {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 12px;
}

.stat-card {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 14px 16px;
  border-radius: 10px;
  background: #f8f9fa;
  border-left: 4px solid;
  
  &.core { border-left-color: #198754; svg { color: #198754; } }
  &.fatal { border-left-color: #dc3545; svg { color: #dc3545; } }
  &.redundant { border-left-color: #8b5cf6; svg { color: #8b5cf6; } }
  &.irrelevant { border-left-color: #6c757d; svg { color: #6c757d; } }
}

.stat-info {
  display: flex;
  flex-direction: column;
}

.stat-num {
  font-size: 24px;
  font-weight: 700;
  color: #121c28;
}

.stat-label {
  font-size: 12px;
  color: #404944;
}

.warning-box {
  display: flex;
  gap: 12px;
  padding: 16px;
  border-radius: 10px;
  background: #fef2f2;
  border: 1px solid #fecaca;
}

.warning-icon {
  color: #dc3545;
  flex-shrink: 0;
  margin-top: 2px;
}

.warning-content {
  flex: 1;
}

.warning-content strong {
  font-size: 14px;
  color: #dc3545;
}

.warning-content p {
  margin: 4px 0 8px 0;
  font-size: 13px;
  color: #404944;
}

.fatal-skill-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.fatal-tag {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 4px 10px;
  border-radius: 4px;
  font-size: 12px;
  background: #fde8e8;
  color: #991b1b;
  
  &.must { border: 1px solid #fca5a5; font-weight: 600; }
  &.nice { border: 1px solid #fecaca; }
}

.tag-badge {
  font-size: 10px;
  padding: 1px 6px;
  border-radius: 999px;
  background: rgba(220, 53, 69, 0.2);
}

.suggestion-box {
  display: flex;
  gap: 12px;
  padding: 16px;
  border-radius: 10px;
  background: #ecfdf5;
  border: 1px solid #a7f3d0;
}

.suggestion-icon {
  color: #198754;
  flex-shrink: 0;
  margin-top: 2px;
}

.suggestion-content {
  flex: 1;
}

.suggestion-content strong {
  font-size: 14px;
  color: #198754;
}

.suggestion-content p {
  margin: 4px 0 8px 0;
  font-size: 13px;
  color: #404944;
}

.core-skill-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.core-tag {
  display: inline-flex;
  align-items: center;
  padding: 4px 10px;
  border-radius: 4px;
  font-size: 12px;
  background: #d1fae5;
  color: #065f46;
  border: 1px solid #a7f3d0;
}

.legend-box {
  padding: 16px;
  border-radius: 10px;
  background: #f8f9fa;
  border: 1px solid #eef0f2;
}

.legend-box h4 {
  font-size: 14px;
  font-weight: 600;
  color: #121c28;
  margin: 0 0 12px 0;
}

.legend-items {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.legend-item {
  display: flex;
  align-items: flex-start;
  gap: 8px;
}

.legend-dot {
  width: 12px;
  height: 12px;
  border-radius: 50%;
  flex-shrink: 0;
  margin-top: 2px;
  
  &.core { background: #198754; }
  &.fatal { background: #dc3545; }
  &.redundant { background: #8b5cf6; }
  &.irrelevant { background: #6c757d; }
}

.legend-text {
  font-size: 13px;
  color: #404944;
  line-height: 1.5;
}

.legend-text strong {
  color: #121c28;
}

.legend-note {
  display: flex;
  flex-wrap: wrap;
  gap: 16px;
  margin-top: 12px;
  padding-top: 12px;
  border-top: 1px solid #eef0f2;
  font-size: 12px;
  color: #6c757d;
}

.note-label {
  font-weight: 600;
  color: #404944;
}

@media (max-width: 768px) {
  .stats-grid { grid-template-columns: repeat(2, 1fr); }
  .chart-container { height: 350px; }
  .subtitle { display: none; }
}
</style>