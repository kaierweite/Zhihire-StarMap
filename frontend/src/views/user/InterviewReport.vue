<script setup lang="ts">
import { ref, onMounted, onUnmounted, nextTick, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import * as echarts from 'echarts'
import { ChevronRight, Brain, Lightbulb, ThumbsUp, AlertTriangle, ArrowLeft, Sparkles } from 'lucide-vue-next'
import { getReport } from '@/api/interview'
import type { InterviewReportData, InterviewRadar } from '@/types/interview'

const route = useRoute()
const router = useRouter()

const chartRef = ref<HTMLElement>()
let chart: echarts.ECharts | null = null
const loading = ref(true)
const reportData = ref<InterviewReportData | null>(null)
const errorMsg = ref('')

const sessionId = computed(() => Number(route.query.session_id))

const DIM_LABELS: Record<keyof InterviewRadar, string> = {
  communication: '沟通表达',
  technical: '专业技能',
  problem_solving: '问题解决',
  culture_fit: '文化匹配',
  depth: '思维深度',
}

const DIM_KEYS = ['communication', 'technical', 'problem_solving', 'culture_fit', 'depth'] as const

function getRadarEntries(): { name: string; score: number; key: string }[] {
  const radar = reportData.value?.radar
  if (!radar) return []
  return DIM_KEYS.map((k) => ({
    key: k,
    name: DIM_LABELS[k],
    score: radar[k],
  }))
}

function initChart() {
  if (!chartRef.value) return
  chart = echarts.init(chartRef.value)
  const entries = getRadarEntries()
  chart.setOption({
    radar: {
      indicator: entries.map((d) => ({ name: d.name, max: 100 })),
      shape: 'circle',
      splitNumber: 4,
      axisName: { color: '#606266', fontSize: 12 },
      splitLine: { lineStyle: { color: '#e5e7eb' } },
      splitArea: { show: true, areaStyle: { color: ['rgba(14,165,233,0.02)', 'rgba(14,165,233,0.04)'] } },
      axisLine: { lineStyle: { color: '#e5e7eb' } },
    },
    series: [{
      type: 'radar',
      data: [{
        value: entries.map((d) => d.score),
        areaStyle: { color: 'rgba(26,58,92,0.15)' },
        lineStyle: { color: '#1a3a5c', width: 2 },
        itemStyle: { color: '#1a3a5c' },
      }],
    }],
  })
}

function handleResize() { chart?.resize() }

onMounted(async () => {
  if (!sessionId.value) {
    errorMsg.value = '缺少面试会话 ID'
    loading.value = false
    return
  }
  try {
    const res = await getReport(sessionId.value)
    reportData.value = res.data.data
    nextTick(() => { initChart(); loading.value = false })
  } catch {
    errorMsg.value = '获取报告失败，请稍后重试'
    loading.value = false
  }
  window.addEventListener('resize', handleResize)
})

onUnmounted(() => { chart?.dispose(); window.removeEventListener('resize', handleResize) })

function scoreClass(s: number): string {
  if (s >= 80) return 'high'
  if (s >= 60) return 'mid'
  return 'low'
}

const feedback = computed(() => reportData.value?.feedback)
const strengths = computed(() => feedback.value?.strengths ?? [])
const weaknesses = computed(() => feedback.value?.weaknesses ?? [])
</script>

<template>
  <div class="report-page">
    <div class="report-container">
      <div class="breadcrumb">
        <button class="breadcrumb-btn" @click="router.push('/user/interview')"><ArrowLeft :size="14" /></button>
        <router-link to="/user/interview">模拟面试</router-link>
        <ChevronRight :size="14" /><span>面试报告</span>
      </div>

      <div v-if="loading" class="loading-state">
        <div class="loading-spinner" />
        <p>正在加载报告...</p>
      </div>

      <div v-else-if="errorMsg" class="error-state">
        <AlertTriangle :size="32" />
        <p>{{ errorMsg }}</p>
        <router-link to="/user/interview" class="back-link">返回面试首页</router-link>
      </div>

      <template v-else-if="reportData">
        <div class="report-header fade-up">
          <div>
            <h1>面试报告</h1>
            <p v-if="reportData.created_at">面试时间：{{ reportData.created_at.replace('T', ' ').slice(0, 16) }}</p>
          </div>
          <div class="header-actions">
            <router-link to="/user/resume/optimize" class="primary-btn">
              <Sparkles :size="15" /> 简历优化
            </router-link>
          </div>
        </div>

        <div class="report-layout">
          <div class="report-left">
            <div class="card fade-up d1">
              <h2>综合评分</h2>
              <div class="score-ring">
                <span class="score-num">{{ reportData.overall_score ?? '-' }}</span>
                <span class="score-unit">/100</span>
              </div>
              <div ref="chartRef" class="radar-chart" />
            </div>
          </div>

          <div class="report-right">
            <div
              v-for="(entry, i) in getRadarEntries()"
              :key="entry.key"
              class="dim-card fade-up"
              :style="{ animationDelay: (0.15 + i * 0.08) + 's' }"
            >
              <div class="dim-header">
                <h3>{{ entry.name }}</h3>
                <span class="dim-score" :class="scoreClass(entry.score)">{{ entry.score }}</span>
              </div>
              <div class="bar-track">
                <div class="bar-fill" :style="{ width: entry.score + '%' }" />
              </div>
            </div>

            <div v-if="strengths.length > 0" class="card feedback-card fade-up d6">
              <div class="feedback-header positive">
                <ThumbsUp :size="18" />
                <h3>优势</h3>
              </div>
              <ul class="feedback-list">
                <li v-for="(s, si) in strengths" :key="si">
                  <Lightbulb :size="14" /> {{ s }}
                </li>
              </ul>
            </div>

            <div v-if="weaknesses.length > 0" class="card feedback-card fade-up d7">
              <div class="feedback-header negative">
                <AlertTriangle :size="18" />
                <h3>待改进</h3>
              </div>
              <ul class="feedback-list">
                <li v-for="(w, wi) in weaknesses" :key="wi">
                  <Lightbulb :size="14" /> {{ w }}
                </li>
              </ul>
            </div>

            <div v-if="feedback?.suggestions" class="card ai-card fade-up d8">
              <div class="ai-header"><Brain :size="18" /><h3>AI 改进建议</h3></div>
              <p class="ai-text">{{ feedback.suggestions }}</p>
            </div>
          </div>
        </div>
      </template>
    </div>
  </div>
</template>

<style scoped lang="scss">
.report-page { padding: 24px 16px; }
.report-container { max-width: 1100px; margin: 0 auto; }

@keyframes fadeUp { from { opacity: 0; transform: translateY(20px); } to { opacity: 1; transform: translateY(0); } }
.fade-up { opacity: 0; animation: fadeUp 0.5s cubic-bezier(0.22,1,0.36,1) forwards; }
.d1 { animation-delay: 0.08s; } .d2 { animation-delay: 0.15s; } .d3 { animation-delay: 0.22s; }
.d4 { animation-delay: 0.3s; } .d5 { animation-delay: 0.38s; } .d6 { animation-delay: 0.46s; }
.d7 { animation-delay: 0.52s; } .d8 { animation-delay: 0.58s; }

.breadcrumb { display: flex; align-items: center; gap: 6px; margin-bottom: 16px; font-size: 13px; color: #909399; a { color: #909399; text-decoration: none; &:hover { color: #1a3a5c; } } span:last-child { color: #303133; font-weight: 500; } }
.breadcrumb-btn { width: 28px; height: 28px; border-radius: 6px; border: 1px solid #dcdfe6; background: #fff; color: #606266; display: flex; align-items: center; justify-content: center; cursor: pointer; &:hover { border-color: #1a3a5c; color: #1a3a5c; } }

.report-header { display: flex; align-items: flex-end; justify-content: space-between; margin-bottom: 28px; h1 { font-size: 32px; font-weight: 700; color: #303133; margin-bottom: 4px; } p { font-size: 15px; color: #909399; } }
.header-actions { display: flex; gap: 10px; }
.primary-btn { display: flex; align-items: center; gap: 6px; padding: 8px 20px; border-radius: 999px; background: #1a3a5c; color: #fff; font-size: 13px; font-weight: 600; text-decoration: none; &:hover { background: #24507a; } }

.report-layout { display: grid; grid-template-columns: 380px 1fr; gap: 24px; }
.card { background: #fff; border-radius: 12px; padding: 24px; border: 1px solid #e5e7eb; margin-bottom: 16px; }

.report-left .card { text-align: center; h2 { font-size: 18px; font-weight: 600; color: #303133; margin-bottom: 16px; } }
.score-ring { margin-bottom: 12px; }
.score-num { font-size: 48px; font-weight: 700; color: #1a3a5c; line-height: 1; }
.score-unit { font-size: 16px; color: #909399; }
.radar-chart { width: 100%; height: 300px; }

.dim-card { background: #fff; border-radius: 12px; padding: 18px 20px; border: 1px solid #e5e7eb; margin-bottom: 12px; }
.dim-header { display: flex; align-items: center; justify-content: space-between; margin-bottom: 8px; h3 { font-size: 15px; font-weight: 600; color: #303133; } }
.dim-score { font-size: 20px; font-weight: 700; &.high { color: #198754; } &.mid { color: #b8860b; } &.low { color: #dc3545; } }
.bar-track { height: 6px; border-radius: 999px; background: #e9ecef; overflow: hidden; margin-bottom: 10px; }
.bar-fill { height: 100%; border-radius: 999px; background: linear-gradient(90deg, #1a3a5c, #0ea5e9); transition: width 0.8s ease; }

.feedback-header { display: flex; align-items: center; gap: 8px; margin-bottom: 14px; &.positive svg { color: #198754; } &.negative svg { color: #dc3545; } h3 { font-size: 16px; font-weight: 600; color: #303133; } }
.feedback-list { list-style: none; display: flex; flex-direction: column; gap: 10px; li { display: flex; align-items: flex-start; gap: 8px; font-size: 13px; color: #606266; line-height: 1.6; svg { color: #f59e0b; flex-shrink: 0; margin-top: 3px; } } }

.ai-header { display: flex; align-items: center; gap: 8px; margin-bottom: 14px; svg { color: #1a3a5c; } h3 { font-size: 16px; font-weight: 600; color: #303133; } }
.ai-text { font-size: 14px; color: #606266; line-height: 1.8; white-space: pre-wrap; }

.loading-state, .error-state { display: flex; flex-direction: column; align-items: center; gap: 12px; padding: 60px 0; color: #909399; }
.loading-spinner { width: 36px; height: 36px; border: 3px solid #e5e7eb; border-top-color: #1a3a5c; border-radius: 50%; animation: spin 0.8s linear infinite; }
@keyframes spin { to { transform: rotate(360deg); } }
.error-state svg { color: #dc3545; }
.back-link { color: #0ea5e9; text-decoration: none; font-weight: 600; &:hover { text-decoration: underline; } }

@media (max-width: 900px) { .report-layout { grid-template-columns: 1fr; } .report-header { flex-direction: column; align-items: flex-start; gap: 12px; } }
</style>
