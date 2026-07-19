<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, nextTick, watch } from 'vue'
import * as echarts from 'echarts'
import { BarChart3, Lightbulb, Briefcase, Loader2 } from 'lucide-vue-next'
import { ElMessage } from 'element-plus'
import { getUserGraph, listRoles } from '@/api/graph'
import type { OccupationRole, UserGraphResult } from '@/types/graph'

const chartRefSunburst = ref<HTMLElement>()
let chartSunburst: echarts.ECharts | null = null
const loading = ref(true)
const rolesLoading = ref(true)
const gapLoading = ref(false)
const chartFullscreen = ref(false)
const error = ref('')
const graphData = ref<UserGraphResult>({ nodes: [], edges: [], gap_skills: [], state: 'empty', categories: [] })
const gapGraphData = ref<UserGraphResult>({ nodes: [], edges: [], gap_skills: [], state: 'empty', categories: [] })
const roles = ref<OccupationRole[]>([])
const selectedRoleId = ref(0)
const gapExpanded = ref(false)

const colorMap = computed(() => {
  const m: Record<string, string> = {}
  for (const cat of graphData.value.categories) m[cat.name] = cat.color
  return m
})
const categoryStats = computed(() => {
  const stats: Record<string, number> = {}
  for (const n of graphData.value.nodes) {
    const cat = n.category || '通用'
    stats[cat] = (stats[cat] || 0) + 1
  }
  return stats
})
function getCategoryColor(cat: string | null): string {
  return (cat && colorMap.value[cat]) || '#9A60B4'
}

const gapSkills = computed(() => selectedRoleId.value <= 0 ? [] : gapGraphData.value.gap_skills || [])
const gapMustSkills = computed(() => gapSkills.value.filter(g => g.requirement_level === 'MUST'))
const gapNiceSkills = computed(() => gapSkills.value.filter(g => g.requirement_level === 'NICE'))
const gapBonusSkills = computed(() => gapSkills.value.filter(g => g.requirement_level === 'BONUS'))
const matchCount = computed(() => selectedRoleId.value <= 0 ? 0 : graphData.value.nodes.filter((n) => !new Set(gapSkills.value.map(g => g.skill_name)).has(n.name)).length)
const coveragePercent = computed(() => { const t = matchCount.value + gapSkills.value.length; return t === 0 ? 0 : Math.round((matchCount.value / t) * 100) })

const topCategory = computed(() => Object.entries(categoryStats.value).sort((a, b) => b[1] - a[1])[0])

function initSunburstChart(data: UserGraphResult) {
  if (!chartRefSunburst.value) return
  let inst = chartSunburst
  if (!inst) {
    inst = echarts.init(chartRefSunburst.value)
    chartSunburst = inst
  } else {
    inst.clear()
  }

  const root = data.sunburst_data || {
    name: '能力图谱',
    itemStyle: { color: '#003527' },
    children: data.categories.map((c) => ({ name: c.name, itemStyle: { color: c.color }, children: [] })),
  }

  inst.setOption({
    tooltip: {
      trigger: 'item',
      backgroundColor: 'rgba(255,255,255,0.96)',
      borderColor: '#e8e8e8',
      borderWidth: 1,
      padding: [12, 16],
      textStyle: { color: '#121c28', fontSize: 13 },
      formatter: function(params: any) {
        const name = params.name || '';
        const val = params.value || 0;
        if (params.treePathInfo && params.treePathInfo.length >= 3) {
          const category = params.treePathInfo[1]?.name || '';
          return '<strong style="font-size:15px;color:#1a1a2e;">' + name + '</strong><br/>' +
            '<span style="color:#999">分类</span><span style="float:right">' + category + '</span><br/>' +
            '<span style="color:#999">熟练度</span><span style="float:right">' + val.toFixed(1) + ' / 5.0</span>';
        }
        if (params.treePathInfo && params.treePathInfo.length === 2) {
          const childCount = params.treePathInfo[1]?.children?.length || 0;
          return '<strong style="font-size:15px;color:#1a1a2e;">' + name + '</strong><br/>' +
            '<span style="color:#999">技能数</span><span style="float:right">' + childCount + '</span>';
        }
        return name;
      },
    },
    series: [{
      type: 'sunburst',
      data: [root],
      radius: ['0%', '95%'],
      sort: 'asc',
      emphasis: { focus: 'ancestor' },
      levels: [{}, {
        r0: '12%',
        r: '35%',
        label: { rotate: 'tangential', fontSize: 14, fontWeight: 700, color: '#fff', textShadowBlur: 3, textShadowColor: 'rgba(0,0,0,0.5)' },
      }, {
        r0: '35%',
        r: '80%',
        label: { rotate: 'tangential', fontSize: 12, color: '#fff', textShadowBlur: 3, textShadowColor: 'rgba(0,0,0,0.5)' },
      }],
      label: {
        rotate: 'tangential', color: '#fff', fontSize: 12, fontWeight: 600,
        textShadowBlur: 4, textShadowColor: 'rgba(0,0,0,0.3)',
      },
      itemStyle: { borderRadius: 4, borderColor: '#fff', borderWidth: 2 },
      animationDuration: 1000,
      animationEasing: 'elasticOut',
    }],
  })
}

async function fetchGraph() {
  loading.value = true; error.value = ''
  try {
    const res = await getUserGraph()
    const d = res.data.data || {}
    graphData.value = { nodes: d.nodes || [], edges: d.edges || [], gap_skills: d.gap_skills || [], state: d.state || (d.nodes && d.nodes.length ? 'ready' : 'empty'), categories: d.categories || [], sunburst_data: d.sunburst_data }
    await nextTick()
    initSunburstChart(graphData.value)
  } catch (e) {
    error.value = (e as any).message || '加载图谱失败'
  } finally {
    loading.value = false
  }
}

async function fetchRoles() {
  rolesLoading.value = true
  try {
    const res = await listRoles()
    roles.value = res.data || []
  } catch { roles.value = [] }
  finally { rolesLoading.value = false }
}

async function handleRoleChange(roleId: number | null) {
  if (roleId <= 0) {
    selectedRoleId.value = null
    gapGraphData.value = { nodes: [], edges: [], gap_skills: [], state: 'empty', categories: [] }
    return
  }
  selectedRoleId.value = roleId; gapLoading.value = true
  try {
    const res = await getUserGraph(roleId)
    const gd = res.data || {}
    gapGraphData.value = { nodes: gd.nodes || [], edges: gd.edges || [], gap_skills: gd.gap_skills || [], state: gd.state || (gd.nodes && gd.nodes.length ? 'ready' : 'empty'), categories: gd.categories || [] }
    await nextTick()
  } catch { ElMessage.error('加载差距分析失败') }
  finally { gapLoading.value = false }
}

function toggleChartSize() {
  chartFullscreen.value = !chartFullscreen.value
  nextTick(() => { chartSunburst?.resize() })
}

function handleResize() { chartSunburst?.resize() }

onMounted(() => { fetchGraph(); fetchRoles(); window.addEventListener('resize', handleResize) })
onUnmounted(() => {
  chartSunburst?.dispose(); chartSunburst = null
  window.removeEventListener('resize', handleResize)
})

watch(() => gapExpanded.value, (val) => {
  if (val) { nextTick(() => chartSunburst?.resize()) }
})
</script>

<template>
  <div class="ability-section" :class="{ 'is-fullscreen': chartFullscreen }">
    <div class="section-header">
      <h2 class="section-title"><BarChart3 :size="18" /> 能力图谱</h2>
      <span class="section-summary" v-if="graphData.nodes.length">
        {{ graphData.nodes.length }} 项技能
        <template v-for="(count, name) in categoryStats" :key="name">
          · {{ name }} <strong>{{ count }}</strong>
        </template>
      </span>
    </div>

    <div v-if="loading && !graphData.nodes.length" class="center-state">
      <Loader2 :size="28" class="spin" />
      <p>加载中...</p>
    </div>
    <div v-else-if="error && !graphData.nodes.length" class="center-state err">
      <p>{{ error }}</p>
      <button class="retry-btn" @click="fetchGraph">重新加载</button>
    </div>

    <div v-else-if="graphData.nodes.length" class="chart-area" @dblclick="toggleChartSize">
      <div ref="chartRefSunburst" class="chart-box" :class="{ 'maximized': chartFullscreen }"></div>
      <div class="legend-row">
        <span v-for="cat in (graphData.categories || [])" :key="cat.name" class="legend-chip">
          <span class="legend-dot" :style="{ background: cat.color }" /> {{ cat.name }}
        </span>
        <span class="legend-hint">双击全屏 · 悬停查看技能详情</span>
      </div>
    </div>

    <div v-else class="empty-chart">
      <p>暂无图谱数据。请先在简历中心上传简历，系统将自动解析并生成能力图谱。</p>
    </div>

    <div v-if="topCategory && graphData.nodes.length" class="tip-row">
      <Lightbulb :size="14" class="tip-icon" />
      <span class="tip-text">
        <strong>{{ topCategory[0] }}</strong> 技术栈完整度较高（{{ topCategory[1] }}项技能），建议横向拓展相邻领域补齐全栈能力。
      </span>
    </div>

    <div class="gap-toggle" v-if="graphData.nodes.length" @click="gapExpanded = !gapExpanded">
      <Briefcase :size="15" />
      <span>技能缺口分析</span>
      <span class="toggle-arrow" :class="{ open: gapExpanded }">&#9654;</span>
    </div>

    <div v-show="gapExpanded" class="gap-body">
      <div class="gap-row">
        <span class="gap-label">目标角色：</span>
        <el-select v-model="selectedRoleId" placeholder="请选择目标岗位角色" :loading="rolesLoading" style="width: 220px" @change="handleRoleChange">
          <el-option v-for="role in roles" :key="role.id" :label="role.name" :value="role.id">
            <span>{{ role.name }}</span>
            <span v-if="role.category" class="role-cat-tag">{{ role.category }}</span>
          </el-option>
        </el-select>
      </div>

      <div v-if="selectedRoleId <= 0" class="gap-placeholder">
        <Briefcase :size="32" class="hint-icon" />
        <p>选择目标岗位后自动分析技能差距</p>
      </div>

      <div v-else-if="gapLoading" class="center-state">
        <Loader2 :size="20" class="spin" />
        <p>正在分析...</p>
      </div>

      <template v-else>
        <div class="gap-stats">
          <div class="target-job">
            <strong>{{ roles.find(r => r.id === selectedRoleId)?.name || '未知岗位' }}</strong>
            <span class="match-badge">匹配度 {{ coveragePercent }}%</span>
          </div>
          <div class="gap-cards">
            <div class="cov-card matched"><span class="cov-num">{{ matchCount }}</span> 已匹配</div>
            <div class="cov-card miss"><span class="cov-num">{{ gapSkills.length }}</span> 缺口</div>
          </div>
        </div>

        <div v-if="gapSkills.length" class="gap-lists">
          <div v-if="gapMustSkills.length" class="gap-group">
            <div class="gap-group-title"><span class="req-badge must">必备</span></div>
            <div class="skill-tags">
              <span v-for="s in gapMustSkills" :key="s.skill_name" class="skill-tag must">{{ s.skill_name }}</span>
            </div>
          </div>
          <div v-if="gapNiceSkills.length" class="gap-group">
            <div class="gap-group-title"><span class="req-badge nice">加分</span></div>
            <div class="skill-tags">
              <span v-for="s in gapNiceSkills" :key="s.skill_name" class="skill-tag nice">{{ s.skill_name }}</span>
            </div>
          </div>
        </div>

        <div v-if="gapMustSkills.length" class="gap-ai-tip">
          <Lightbulb :size="14" />
          <span><strong>AI 建议</strong> 重点补齐 <strong>{{ gapMustSkills.slice(0, 3).map(s => s.skill_name).join('、') }}</strong> 等必备技能。</span>
        </div>
      </template>
    </div>

    <button v-if="chartFullscreen" class="fullscreen-close" @click="toggleChartSize">&#10005;</button>

  </div>
</template>

<style scoped lang="scss">
@keyframes spin { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }
.spin { animation: spin 1s linear infinite; color: #003527; }

.ability-section {
  position: relative;
  background: #fff;
  border-radius: 12px;
  border: 1px solid #bfc9c3;
  padding: 16px 20px;
  margin-bottom: 16px;
  transition: all 0.3s;
}
.ability-section.is-fullscreen {
  position: fixed; top: 0; left: 0; right: 0; bottom: 0;
  z-index: 1000; padding: 12px 24px;
  background: #fff; border: none; border-radius: 0;
}

.section-header {
  display: flex; align-items: center; gap: 10px;
  margin-bottom: 12px;
}
.section-title { display: flex; align-items: center; gap: 8px; font-size: 17px; font-weight: 700; color: #121c28; margin: 0; flex-shrink: 0; svg { color: #003527; } }
.section-summary { font-size: 12px; color: #404944; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; flex: 1; }
.section-summary strong { color: #003527; }

.center-state { text-align: center; padding: 32px 0; color: #404944; font-size: 14px; display: flex; flex-direction: column; align-items: center; gap: 10px; &.err { color: #f56c6c; } }
.retry-btn { padding: 6px 16px; border-radius: 6px; border: 1px solid #003527; background: none; color: #003527; font-size: 13px; cursor: pointer; &:hover { background: #003527; color: #fff; } }

.chart-area { margin-bottom: 10px; }
.chart-box { width: 100%; min-height: 500px; height: calc(100vh - 420px); max-height: 750px; border-radius: 10px; background: #fafbfc; border: 1px solid #f0f0f0; transition: all 0.3s; }
.chart-box.maximized { height: calc(100vh - 120px); max-height: none; }
.empty-chart { height: 120px; display: flex; align-items: center; justify-content: center; color: #404944; font-size: 14px; background: #fafbfc; border-radius: 8px; border: 1px solid #eef0f2; }

.legend-row { display: flex; flex-wrap: wrap; align-items: center; gap: 12px; margin-top: 8px; font-size: 12px; color: #404944; }
.legend-chip { display: inline-flex; align-items: center; gap: 4px; }
.legend-dot { width: 9px; height: 9px; border-radius: 50%; display: inline-block; flex-shrink: 0; }
.legend-hint { font-size: 11px; color: #bfc9c3; margin-left: auto; }

.tip-row { display: flex; align-items: center; gap: 6px; padding: 8px 14px; margin-bottom: 10px; border-radius: 6px; background: rgba(245,158,11,0.06); border-left: 3px solid #f59e0b; font-size: 13px; color: #404944; }
.tip-icon { color: #f59e0b; flex-shrink: 0; }
.tip-text strong { color: #121c28; }

.gap-toggle { display: flex; align-items: center; gap: 8px; padding: 10px 14px; margin-bottom: 8px; border-radius: 6px; background: #f8f9fa; border: 1px solid #eef0f2; cursor: pointer; font-size: 14px; font-weight: 600; color: #121c28; transition: all 0.2s; user-select: none; }
.gap-toggle:hover { border-color: #003527; color: #003527; }
.gap-toggle svg { color: #003527; }
.toggle-arrow { font-size: 10px; margin-left: auto; transition: transform 0.25s; }
.toggle-arrow.open { transform: rotate(90deg); }

.gap-body { padding: 4px 0 10px; }
.gap-row { display: flex; align-items: center; gap: 10px; margin-bottom: 14px; }
.gap-label { font-size: 13px; font-weight: 600; color: #121c28; white-space: nowrap; }
.role-cat-tag { font-size: 11px; color: #404944; margin-left: 6px; }
.gap-placeholder { text-align: center; padding: 28px 0; color: #404944; }
.gap-placeholder p { font-size: 13px; margin-top: 8px; }

.gap-stats { margin-bottom: 12px; }
.target-job { display: flex; align-items: center; gap: 10px; font-size: 14px; color: #121c28; margin-bottom: 10px; }
.match-badge { padding: 2px 10px; border-radius: 999px; background: #003527; color: #fff; font-size: 12px; font-weight: 600; }
.gap-cards { display: flex; gap: 16px; }
.cov-card { font-size: 13px; color: #404944; }
.cov-card .cov-num { font-size: 22px; font-weight: 700; margin-right: 4px; }
.cov-card.matched .cov-num { color: #155724; }
.cov-card.miss .cov-num { color: #991b1b; }

.gap-lists { display: flex; flex-direction: column; gap: 10px; margin-bottom: 12px; }
.gap-group-title { margin-bottom: 6px; }
.req-badge { font-size: 11px; font-weight: 700; padding: 1px 8px; border-radius: 4px; }
.req-badge.must { background: #fde8e8; color: #991b1b; }
.req-badge.nice { background: #fef3cd; color: #856404; }
.skill-tags { display: flex; flex-wrap: wrap; gap: 4px; }
.skill-tag { padding: 3px 10px; border-radius: 4px; font-size: 12px; }
.skill-tag.must { background: #fef2f2; color: #991b1b; border: 1px solid #fecaca; }
.skill-tag.nice { background: #fffbeb; color: #856404; border: 1px solid #fde68a; }

.gap-ai-tip { display: flex; align-items: flex-start; gap: 8px; padding: 8px 14px; border-radius: 8px; background: rgba(14,165,233,0.04); border-left: 3px solid #064e3b; font-size: 13px; color: #404944; }
.gap-ai-tip svg { color: #064e3b; flex-shrink: 0; margin-top: 1px; }
.gap-ai-tip strong { color: #121c28; }

.hint-icon { color: #bfc9c3; }
.fullscreen-close { position: fixed; top: 16px; right: 24px; z-index: 1001; width: 40px; height: 40px; border-radius: 50%; border: none; background: rgba(0,0,0,0.06); color: #121c28; font-size: 20px; cursor: pointer; display: flex; align-items: center; justify-content: center; }

@media (max-width: 640px) {
  .chart-box { min-height: 320px; height: 50vh; }
  .section-summary { display: none; }
}
</style>
