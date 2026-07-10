<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, nextTick } from 'vue'
import * as echarts from 'echarts'
import { BarChart3, Lightbulb, TrendingUp, Briefcase, Loader2 } from 'lucide-vue-next'
import { getUserGraph, listRoles } from '@/api/graph'
import type { GraphNode, GraphEdge, GapSkill, OccupationRole, UserGraphResult } from '@/types/graph'

const chartRef = ref<HTMLElement>()
let chart: echarts.ECharts | null = null
const loading = ref(true)
const rolesLoading = ref(true)
const gapLoading = ref(false)
const error = ref('')
const graphData = ref<UserGraphResult>({ nodes: [], edges: [], gap_skills: [] })
const gapGraphData = ref<UserGraphResult>({ nodes: [], edges: [], gap_skills: [] })
const roles = ref<OccupationRole[]>([])
const selectedRoleId = ref<number | null>(null)

const categoryColors: Record<string, string> = {
  "后端": '#5470C6', "前端": '#91CC75', "测试": '#FAC858',
  "运维": '#EE6666', "数据": '#73C0DE', "算法": '#3BA272',
  "移动端": '#FC8452', "通用": '#9A60B4',
}

const edgeStyleMap: Record<string, { type: string; color: string; curveness: number }> = {
  'PREREQUISITE': { type: 'solid', color: '#5470C6', curveness: 0.1 },
  'INCLUDES': { type: 'dashed', color: '#91CC75', curveness: 0.2 },
  'SIMILAR': { type: 'dotted', color: '#FAC858', curveness: 0.15 },
  'COMPLEMENTARY': { type: 'solid', color: '#9A60B4', curveness: 0.3 },
}

function getCategoryColor(cat: string | null): string {
  return (cat && categoryColors[cat]) || '#9A60B4'
}

const categoryStats = computed(() => {
  const stats: Record<string, number> = {}
  for (const n of graphData.value.nodes) {
    const cat = n.category || "通用"
    stats[cat] = (stats[cat] || 0) + 1
  }
  return stats
})

const levelDistribution = computed(() => {
  let expert = 0, proficient = 0, basic = 0
  for (const n of graphData.value.nodes) {
    if (n.level >= 4) expert++
    else if (n.level >= 2.5) proficient++
    else basic++
  }
  return { "精通": expert, "熟练": proficient, "了解": basic }
})

const gapSkills = computed(() => {
  if (selectedRoleId.value == null) return []
  return gapGraphData.value.gap_skills || []
})

const gapMustSkills = computed(() => gapSkills.value.filter(g => g.requirement_level === 'MUST'))
const gapBetterSkills = computed(() => gapSkills.value.filter(g => g.requirement_level === 'BETTER'))
const gapOptionalSkills = computed(() => gapSkills.value.filter(g => g.requirement_level === 'OPTIONAL'))

const matchCount = computed(() => {
  if (selectedRoleId.value == null) return 0
  const gapNames = new Set(gapSkills.value.map(g => g.skill_name))
  return graphData.value.nodes.filter(n => !gapNames.has(n.name)).length
})

const coveragePercent = computed(() => {
  const total = matchCount.value + gapSkills.value.length
  return total === 0 ? 0 : Math.round((matchCount.value / total) * 100)
})

onMounted(async () => {
  await Promise.all([loadGraph(), loadRoles()])
  loading.value = false
  nextTick(() => renderGraph())
})

onUnmounted(() => { chart?.dispose() })

async function loadGraph() {
  try {
    const resp = await getUserGraph()
    graphData.value = resp.data.data
  } catch { error.value = "加载技能图谱失败" }
}

async function loadRoles() {
  try {
    const resp = await listRoles()
    roles.value = resp.data.data
  } catch {} finally { rolesLoading.value = false }
}

async function selectRole(roleId: number | null) {
  selectedRoleId.value = roleId
  if (roleId == null) {
    await loadGraph()
    nextTick(() => renderGraph())
    return
  }
  gapLoading.value = true
  try {
    const resp = await getUserGraph(roleId)
    gapGraphData.value = resp.data.data
    graphData.value = resp.data.data
    nextTick(() => renderGraph(graphData.value, gapGraphData.value.gap_skills))
  } catch { ElMessage.error("加载差距分析失败") }
  finally { gapLoading.value = false }
}

function renderGraph(data?: UserGraphResult, highlightGaps: GapSkill[] = []) {
  if (!chartRef.value) return
  const d = data || graphData.value
  const gapNames = new Set(highlightGaps.map(g => g.skill_name))
  const catSet = new Set<string>()
  for (const n of d.nodes) catSet.add(n.category || "通用")
  const categories = Array.from(catSet).map(name => ({ name }))

  const nodes = d.nodes.map(n => ({
    id: n.id, name: n.name,
    value: n.category || "通用",
    category: n.category || "通用",
    symbolSize: Math.max(20, Math.min(n.symbolSize || 30, 60)),
    itemStyle: {
      color: highlightGaps.length > 0
        ? (gapNames.has(n.name) ? '#f56c6c' : getCategoryColor(n.category))
        : getCategoryColor(n.category),
    },
    label: {
      show: n.level >= 3 || gapNames.has(n.name),
      formatter: n.name,
      fontSize: 11, color: gapNames.has(n.name) ? '#f56c6c' : '#303133',
    },
  }))

  const edges = d.edges.map(e => {
    const style = edgeStyleMap[e.relation_type] || { type: 'solid', color: '#ccc', curveness: 0.1 }
    return {
      source: e.source, target: e.target,
      lineStyle: { color: style.color, width: e.weight || 1.5, type: style.type as any, curveness: style.curveness },
      label: { show: true, formatter: e.relation_type, fontSize: 9, color: style.color },
    }
  })

  if (!chart) chart = echarts.init(chartRef.value)
  chart.setOption({
    backgroundColor: 'transparent',
    tooltip: {},
    legend: [{ data: categories.map(c => c.name), bottom: 0, textStyle: { fontSize: 11 } }],
    series: [{
      type: 'graph', layout: 'force',
      categories, data: nodes, edges,
      roam: true, draggable: true, focusNodeAdjacency: true,
      force: { repulsion: 500, edgeLength: [120, 250], gravity: 0.1, friction: 0.1 },
      lineStyle: { width: 1.5, opacity: 0.7 },
      label: { show: false },
      emphasis: { focus: 'adjacency', lineStyle: { width: 3 } },
      zoom: 0.85,
    }],
  })
  chart.resize()
}

import { ElMessage } from 'element-plus'
</script>

<template>
  <div class="ability-section">
    <div class="section-header">
      <div class="section-title">
        <BarChart3 :size="20" />
        <span>能力图谱</span>
      </div>
      <div class="role-selector" v-if="roles.length">
        <select v-model="selectedRoleId" @change="selectRole(selectedRoleId)" class="role-select">
          <option :value="null">全部技能</option>
          <option v-for="r in roles" :key="r.id" :value="r.id">{{ r.name }}</option>
        </select>
      </div>
    </div>

    <div v-if="loading" class="chart-loading"><Loader2 :size="28" class="spin" /></div>
    <div v-else-if="error" class="chart-error">{{ error }}</div>
    <template v-else>
      <!-- Stats Row -->
      <div class="stats-row">
        <div class="stat-card" v-for="(count, name) in categoryStats" :key="name">
          <span class="stat-dot" :style="{ background: getCategoryColor(name) }"></span>
          <span class="stat-name">{{ name }}</span>
          <span class="stat-count">{{ count }}</span>
        </div>
      </div>

      <!-- Level Distribution -->
      <div class="level-row">
        <div class="level-item" v-for="(count, name) in levelDistribution" :key="name">
          <span class="level-name">{{ name }}</span>
          <span class="level-count">{{ count }}</span>
        </div>
        <div class="level-item" v-if="selectedRoleId != null">
          <span class="level-name">岗位匹配</span>
          <span class="level-count highlight">{{ coveragePercent }}%</span>
        </div>
      </div>

      <!-- ECharts Graph -->
      <div ref="chartRef" class="chart-container"></div>

      <!-- Gap Skills -->
      <div v-if="gapSkills.length && selectedRoleId != null" class="gap-section">
        <div class="gap-title"><Lightbulb :size="16" /> 技能缺口分析</div>
        <div class="gap-columns">
          <div class="gap-col">
            <h4 class="gap-col-title must">必需</h4>
            <span v-for="g in gapMustSkills" :key="g.skill_name" class="gap-tag must">{{ g.skill_name }}</span>
            <p v-if="!gapMustSkills.length" class="gap-empty">无</p>
          </div>
          <div class="gap-col">
            <h4 class="gap-col-title better">加分</h4>
            <span v-for="g in gapBetterSkills" :key="g.skill_name" class="gap-tag better">{{ g.skill_name }}</span>
            <p v-if="!gapBetterSkills.length" class="gap-empty">无</p>
          </div>
          <div class="gap-col">
            <h4 class="gap-col-title optional">可选</h4>
            <span v-for="g in gapOptionalSkills" :key="g.skill_name" class="gap-tag optional">{{ g.skill_name }}</span>
            <p v-if="!gapOptionalSkills.length" class="gap-empty">无</p>
          </div>
        </div>
      </div>
    </template>
  </div>
</template>

<style scoped lang="scss">
.ability-section { background: #fff; border-radius: 12px; border: 1px solid #e5e7eb; padding: 20px 24px; margin-bottom: 16px; }

.section-header { display: flex; align-items: center; justify-content: space-between; margin-bottom: 16px; }
.section-title { display: flex; align-items: center; gap: 8px; font-size: 17px; font-weight: 700; color: #303133; svg { color: #1a3a5c; } }
.role-select { padding: 6px 12px; border: 1px solid #dcdfe6; border-radius: 8px; font-size: 13px; color: #303133; background: #fff; outline: none; cursor: pointer; &:focus { border-color: #1a3a5c; } }

.chart-loading { display: flex; justify-content: center; padding: 40px 0; }
.chart-error { text-align: center; padding: 40px 0; color: #f56c6c; font-size: 14px; }

.stats-row { display: flex; flex-wrap: wrap; gap: 6px; margin-bottom: 12px; }
.stat-card { display: flex; align-items: center; gap: 6px; padding: 4px 12px 4px 8px; border-radius: 6px; background: #f8f9fa; font-size: 12px; }
.stat-dot { width: 8px; height: 8px; border-radius: 50%; flex-shrink: 0; }
.stat-name { color: #606266; }
.stat-count { color: #303133; font-weight: 700; margin-left: auto; }

.level-row { display: flex; gap: 16px; margin-bottom: 14px; flex-wrap: wrap; }
.level-item { display: flex; align-items: center; gap: 6px; font-size: 13px; }
.level-name { color: #909399; }
.level-count { font-weight: 700; color: #303133; &.highlight { color: #1a3a5c; font-size: 15px; } }

.chart-container { width: 100%; height: 380px; border-radius: 8px; background: #fafbfc; border: 1px solid #eef0f2; }

.gap-section { margin-top: 16px; padding-top: 16px; border-top: 1px solid #eef0f2; }
.gap-title { display: flex; align-items: center; gap: 6px; font-size: 14px; font-weight: 600; color: #303133; margin-bottom: 12px; }
.gap-columns { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 12px; }
.gap-col { }
.gap-col-title { font-size: 12px; font-weight: 600; margin-bottom: 6px; padding: 2px 8px; border-radius: 4px; display: inline-block; }
.gap-col-title.must { background: #fde8e8; color: #991b1b; }
.gap-col-title.better { background: #fef3cd; color: #856404; }
.gap-col-title.optional { background: #e8e8f5; color: #5a5a8a; }
.gap-tag { display: inline-block; padding: 3px 8px; border-radius: 4px; font-size: 12px; margin: 2px 4px 2px 0; }
.gap-tag.must { background: #fef2f2; color: #991b1b; border: 1px solid #fecaca; }
.gap-tag.better { background: #fffbeb; color: #856404; border: 1px solid #fde68a; }
.gap-tag.optional { background: #f5f3ff; color: #5a5a8a; border: 1px solid #ddd6fe; }
.gap-empty { font-size: 12px; color: #c0c4cc; }

@keyframes spin { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }
.spin { animation: spin 1s linear infinite; color: #1a3a5c; }

@media (max-width: 640px) { .gap-columns { grid-template-columns: 1fr; } .chart-container { height: 300px; } }
</style>
