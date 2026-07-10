<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, nextTick } from 'vue'
import * as echarts from 'echarts'
import { BarChart3, Lightbulb, TrendingUp, Briefcase, Loader2, ArrowLeft } from 'lucide-vue-next'
import { ElMessage } from 'element-plus'
import { useRoute, useRouter } from 'vue-router'
import { getJobGraph } from '@/api/graph'
import { getJobDetail, type JobDetail } from '@/api/job'
import type { GraphNode, GraphEdge, GraphResult } from '@/types/graph'

const route = useRoute()
const router = useRouter()
const jobId = Number(route.params.id)

const chartRef = ref<HTMLElement>()
let chartInstance: echarts.ECharts | null = null
const loading = ref(true)
const error = ref('')
const graphData = ref<GraphResult>({ nodes: [], edges: [], state: 'empty', categories: [] })
const jobDetail = ref<JobDetail | null>(null)

const colorMap = computed(() => {
  const m: Record<string, string> = {}
  for (const cat of graphData.value.categories) m[cat.name] = cat.color
  return m
})

function getCategoryColor(cat: string | null): string {
  return (cat && colorMap.value[cat]) || '#9A60B4'
}

const categoryStats = computed(() => {
  const stats: Record<string, number> = {}
  for (const n of graphData.value.nodes) {
    const cat = n.category || '通用'
    stats[cat] = (stats[cat] || 0) + 1
  }
  return stats
})

const skillCount = computed(() => graphData.value.nodes.length)

function buildSunburstData(data: GraphResult): any {
  const root = data.sunburst_data || {
    name: '技能图谱',
    children: data.categories.map((c) => ({ name: c.name, itemStyle: { color: c.color }, children: [] })),
  }
  return root
}

function initChart(data: GraphResult, container: HTMLElement | undefined) {
  if (!container) return null
  let instance = chartInstance
  if (!instance) {
    instance = echarts.init(container)
    chartInstance = instance
  }

  const root = buildSunburstData(data)

  instance.setOption({
    tooltip: {
      trigger: 'item',
      formatter: (params: any) => {
        const name = params.name || ''
        const val = params.value || 0
        if (params.treePathInfo && params.treePathInfo.length >= 3) {
          const category = params.treePathInfo[1]?.name || ''
          return '<strong>' + name + '</strong><br/>分类: ' + category
        }
        if (params.treePathInfo && params.treePathInfo.length === 2) {
          const childCount = params.treePathInfo[1]?.children?.length || 0
          return '<strong>' + name + '</strong><br/>技能数: ' + childCount
        }
        return name
      },
    },
    series: [{
      type: 'sunburst',
      data: [root],
      radius: ['0%', '90%'],
      emphasis: { focus: 'ancestor' },
      levels: [
        {},
        { r0: '6%', r: '18%', label: { rotate: 'tangential', fontSize: 12, fontWeight: 700 } },
        { r0: '18%', r: '88%', label: { rotate: 0, fontSize: 10 } },
      ],
      minShowLabelAngle: 5,
      label: { rotate: 'tangential', color: '#fff', fontSize: 12, fontWeight: 600, textShadowBlur: 3, textShadowColor: 'rgba(0,0,0,0.3)' },
      itemStyle: { borderRadius: 4, borderColor: '#fff', borderWidth: 2 },
      animationDuration: 800,
    }],
  })
  return instance
}

function handleResize() { chartInstance?.resize() }

async function fetchData() {
  loading.value = true
  error.value = ''
  try {
    const [graphRes, detailRes] = await Promise.all([
      getJobGraph(jobId),
      getJobDetail(jobId),
    ])
    const gd = graphRes.data.data || {}
    graphData.value = {
      nodes: gd.nodes || [],
      edges: gd.edges || [],
      state: gd.state || (gd.nodes && gd.nodes.length ? 'ready' : 'empty'),
      categories: gd.categories || [],
      sunburst_data: gd.sunburst_data,
    }
    if (detailRes.data.code === 200) {
      jobDetail.value = detailRes.data.data
    }
    loading.value = false
    await nextTick()
    initChart(graphData.value, chartRef.value)
  } catch (e: any) {
    error.value = e.message || '加载图谱失败'
  } finally {
    loading.value = false
  }
}

function goBack() {
  router.push('/company/jobs')
}

onMounted(() => {
  fetchData()
  window.addEventListener('resize', handleResize)
})

onUnmounted(() => {
  chartInstance?.dispose()
  chartInstance = null
  window.removeEventListener('resize', handleResize)
})
</script>

<template>
  <div class="ability-page">
    <div class="ability-container">
      <div class="page-header fade-up">
        <button class="back-btn" @click="goBack"><ArrowLeft :size="18" /></button>
        <div class="header-text">
          <h1>岗位能力图谱</h1>
          <span class="subtitle">基于岗位技能要求构建的知识图谱 — 旭日图</span>
        </div>
      </div>

      <div v-if="jobDetail" class="job-info-card fade-up d1">
        <div class="job-header">
          <Briefcase :size="20" />
          <h3>{{ jobDetail.title }}</h3>
        </div>
        <div class="job-meta">
          <span v-if="jobDetail.city" class="meta-item">{{ jobDetail.city }}</span>
          <span v-if="jobDetail.education_requirement" class="meta-item">{{ jobDetail.education_requirement }}</span>
          <span v-if="jobDetail.experience_min" class="meta-item">{{ jobDetail.experience_min }}年经验</span>
          <span v-if="jobDetail.salary_min && jobDetail.salary_max" class="meta-item">
            {{ (jobDetail.salary_min / 1000).toFixed(0) }}k-{{ (jobDetail.salary_max / 1000).toFixed(0) }}k
          </span>
        </div>
      </div>

      <div v-if="loading && graphData.nodes.length === 0" class="loading-state">
        <Loader2 :size="32" class="spin" />
        <p>加载能力图谱中...</p>
      </div>

      <div v-else-if="error && graphData.nodes.length === 0" class="error-state">
        <p>{{ error }}</p>
        <button class="retry-btn" @click="fetchData">重新加载</button>
      </div>

      <div v-show="!loading && graphData.nodes.length > 0" class="graph-layout fade-up d2">
        <div class="graph-main card">
          <div class="card-header">
            <h3>技能旭日图</h3>
          </div>
          <div ref="chartRef" class="echarts-container" />
          <div class="legend">
            <div class="legend-group">
              <span class="legend-label">分类：</span>
              <span v-for="cat in (graphData.categories || [])" :key="cat.name" class="legend-item">
                <span class="dot" :style="{ background: cat.color }" /> {{ cat.name }}
              </span>
            </div>
        </div>
          </div>
        </div>
      </div>

      <div class="graph-sidebar">
          <div class="card">
            <div class="card-header"><BarChart3 :size="18" /><h3>技能概览</h3></div>
            <div class="stat-big">{{ skillCount }} <span class="stat-unit">项技能</span></div>
            <div class="category-list">
              <div v-for="(count, name) in categoryStats" :key="name" class="category-row">
                <span class="category-dot" :style="{ background: getCategoryColor(name) }" />
                <span class="category-name">{{ name }}</span>
                <span class="category-count">{{ count }}项</span>
              </div>
            </div>
          </div>

          <div class="card">
            <div class="card-header"><TrendingUp :size="18" /><h3>技能分布</h3></div>
            <div class="distribution-bars">
              <div v-for="(count, name) in categoryStats" :key="name" class="dist-row">
                <div class="dist-header">
                  <span>{{ name }}</span>
                  <span class="dist-count">{{ Math.round(count / skillCount * 100) }}%</span>
                </div>
                <div class="bar-track">
                  <div class="bar-fill" :style="{ width: (count / skillCount * 100) + '%', background: getCategoryColor(name) }" />
                </div>
              </div>
            </div>
          </div>

          <div class="card">
            <div class="card-header"><Lightbulb :size="18" /><h3>招聘建议</h3></div>
            <div v-if="skillCount === 0" class="empty-hint">暂无技能数据</div>
            <div v-else class="suggestions">
              <div class="suggestion-item">
                <span class="suggestion-icon">&#8226;</span>
                <span>建议优先筛选具备<strong>{{ Object.keys(categoryStats).slice(0, 2).join('、') }}</strong> 技术栈的候选人</span>
              </div>
              <div class="suggestion-item">
                <span class="suggestion-icon">&#8226;</span>
                <span>关注技能图谱中<strong>核心技能</strong>，这些是岗位的基础能力</span>
              </div>
              <div class="suggestion-item">
                <span class="suggestion-icon">&#8226;</span>
                <span>可在智能筛选中设置技能匹配度阈值，精准定位候选人</span>
              </div>
            </div>
          </div>

      <div v-show="!loading && graphData.nodes.length === 0 && !error" class="empty-graph-card fade-up d2">
        <div class="empty-content">
          <Briefcase :size="64" class="empty-icon" />
          <h3>暂无能力图谱</h3>
          <p>该岗位尚未添加技能要求，无法生成能力图谱。</p>
          <p>请在岗位管理中为该岗位添加技能要求。</p>
          <router-link to="/company/jobs/detail/" class="empty-btn">
            管理技能要求
          </router-link>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped lang="scss">
.ability-page { padding: 24px 16px; }
.ability-container { max-width: 1200px; margin: 0 auto; }

@keyframes fadeUp { from { opacity: 0; transform: translateY(20px); } to { opacity: 1; transform: translateY(0); } }
@keyframes spin { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }
.fade-up { opacity: 0; animation: fadeUp 0.5s cubic-bezier(0.22,1,0.36,1) forwards; }
.d1 { animation-delay: 0.08s; } .d2 { animation-delay: 0.15s; }
.spin { animation: spin 1s linear infinite; }

.page-header {
  display: flex;
  align-items: center;
  gap: 14px;
  margin-bottom: 24px;
}

.back-btn {
  width: 38px; height: 38px;
  display: flex; align-items: center; justify-content: center;
  border-radius: 10px;
  border: 1px solid #e5e7eb;
  background: #fff;
  color: #606266;
  cursor: pointer;
  transition: all 0.2s;
  &:hover { border-color: #1a3a5c; color: #1a3a5c; }
}

.header-text {
  h1 { font-size: 28px; font-weight: 700; color: #303133; margin: 0 0 2px 0; }
  .subtitle { font-size: 14px; color: #909399; }
}

.job-info-card {
  background: #fff;
  border-radius: 12px;
  padding: 20px;
  border: 1px solid #e5e7eb;
  margin-bottom: 20px;

  .job-header {
    display: flex; align-items: center; gap: 8px; margin-bottom: 12px;
    h3 { font-size: 18px; font-weight: 600; color: #303133; margin: 0; }
    svg { color: #1a3a5c; }
  }

  .job-meta {
    display: flex; flex-wrap: wrap; gap: 12px;
    .meta-item {
      padding: 4px 12px; border-radius: 4px; background: #f0f4f9; color: #606266; font-size: 13px;
    }
  }
}

.loading-state { display: flex; flex-direction: column; align-items: center; gap: 12px; padding: 80px 0; color: #909399; }
.error-state { text-align: center; padding: 60px 0; color: #f56c6c; }
.error-state .retry-btn { margin-top: 16px; padding: 10px 24px; border-radius: 8px; background: #1a3a5c; color: #fff; border: none; cursor: pointer; }

.card { background: #fff; border-radius: 12px; padding: 20px; border: 1px solid #e5e7eb; }
.card-header { display: flex; align-items: center; gap: 8px; margin-bottom: 16px; h3 { font-size: 15px; font-weight: 600; color: #303133; } svg { color: #1a3a5c; } }

.graph-layout { width: 100%; margin-bottom: 20px; }
.graph-main { min-height: 0; }
.echarts-container { width: 100%; height: 640px; border-radius: 8px; background: #f8f9fa; }

.legend { margin-top: 12px; display: flex; flex-direction: column; gap: 8px; }
.legend-group { display: flex; align-items: center; gap: 14px; flex-wrap: wrap; }
.legend-label { font-size: 12px; color: #909399; font-weight: 600; }
.legend-item { display: inline-flex; align-items: center; gap: 4px; font-size: 12px; color: #606266; }
.dot { display: inline-block; width: 10px; height: 10px; border-radius: 50%; }

.graph-sidebar { display: grid; grid-template-columns: repeat(3, 1fr); gap: 16px; }
.stat-big { font-size: 36px; font-weight: 700; color: #303133; letter-spacing: -1px; margin-bottom: 16px; }
.stat-unit { font-size: 14px; font-weight: 500; color: #909399; }

.category-list { display: flex; flex-direction: column; gap: 10px; }
.category-row { display: flex; align-items: center; gap: 8px; }
.category-dot { width: 10px; height: 10px; border-radius: 50%; flex-shrink: 0; }
.category-name { flex: 1; font-size: 13px; color: #606266; }
.category-count { font-size: 13px; font-weight: 600; color: #303133; }

.distribution-bars { display: flex; flex-direction: column; gap: 14px; }
.dist-row { display: flex; flex-direction: column; gap: 6px; }
.dist-header { display: flex; justify-content: space-between; font-size: 13px; color: #303133; }
.dist-count { color: #909399; font-size: 12px; }
.bar-track { height: 6px; border-radius: 999px; background: #e9ecef; overflow: hidden; }
.bar-fill { height: 100%; border-radius: 999px; transition: width 0.8s ease; }

.suggestions { display: flex; flex-direction: column; gap: 12px; }
.suggestion-item { display: flex; gap: 8px; font-size: 13px; color: #606266; line-height: 1.6; }
.suggestion-icon { color: #1a3a5c; font-weight: 700; }
.empty-hint { font-size: 13px; color: #909399; }

.empty-graph-card {
  background: #fff; border-radius: 12px; padding: 40px; border: 1px solid #e5e7eb; text-align: center;

  .empty-content { max-width: 400px; margin: 0 auto; }
  .empty-icon { width: 64px; height: 64px; color: #c0c4cc; margin-bottom: 16px; }
  h3 { font-size: 18px; font-weight: 600; color: #303133; margin: 0 0 12px 0; }
  p { font-size: 14px; color: #909399; line-height: 1.8; margin: 0 0 4px 0; }
  .empty-btn {
    display: inline-block; margin-top: 20px; padding: 10px 28px; border-radius: 8px; font-size: 14px; font-weight: 600;
    color: #fff; background: #1a3a5c; text-decoration: none; transition: background 0.25s;
    &:hover { background: #2a5a8c; }
  }
}

@media (max-width: 1024px) {
  .graph-sidebar { grid-template-columns: 1fr; }
  .echarts-container { height: 360px; }
}
</style>

