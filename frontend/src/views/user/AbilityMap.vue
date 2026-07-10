<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, nextTick } from 'vue'
import * as echarts from 'echarts'
import { BarChart3, Lightbulb, TrendingUp, Briefcase, Loader2 } from 'lucide-vue-next'
import { ElMessage } from 'element-plus'
import { useAuthStore } from '@/store/auth'
import { getUserGraph, listRoles } from '@/api/graph'
import type { GraphNode, GraphEdge, GapSkill, OccupationRole, UserGraphResult, SunburstNode } from '@/types/graph'

const authStore = useAuthStore()
const chartRefSunburst = ref<HTMLElement>()
let chartSunburst: echarts.ECharts | null = null
const activeTab = ref<'graph' | 'gap'>('graph')
const loading = ref(true)
const rolesLoading = ref(true)
const gapLoading = ref(false)
const error = ref('')
const graphData = ref<UserGraphResult>({ nodes: [], edges: [], gap_skills: [], state: 'empty', categories: [] })
const gapGraphData = ref<UserGraphResult>({ nodes: [], edges: [], gap_skills: [], state: 'empty', categories: [] })
const roles = ref<OccupationRole[]>([])
const selectedRoleId = ref(0)

// Category color mapping
const colorMap = computed(() => {
  const m: Record<string, string> = {}
  for (const cat of graphData.value.categories) m[cat.name] = cat.color
  return m
})

function getCategoryColor(cat: string | null): string {
  return (cat && colorMap.value[cat]) || '#9A60B4'
}

// ====== Stats Computed ======
const categoryStats = computed(() => {
  const stats: Record<string, number> = {}
  for (const n of graphData.value.nodes) {
    const cat = n.category || '通用'
    stats[cat] = (stats[cat] || 0) + 1
  }
  return stats
})

const levelDistribution = computed(() => {
  let expert = 0; let proficient = 0; let basic = 0
  for (const n of graphData.value.nodes) {
    if (n.level_label === 'advanced') expert++
    else if (n.level_label === 'intermediate') proficient++
    else if (n.level_label === 'beginner') basic++
  }
  return { '精通': expert, '熟练': proficient, '了解': basic }
})

const gapSkills = computed(() => {
  if (selectedRoleId.value <= 0) return []
  return gapGraphData.value.gap_skills || []
})

const gapMustSkills = computed(() => gapSkills.value.filter((g) => g.requirement_level === 'MUST'))
const gapNiceSkills = computed(() => gapSkills.value.filter((g) => g.requirement_level === 'NICE'))
const gapBonusSkills = computed(() => gapSkills.value.filter((g) => g.requirement_level === 'BONUS'))

const matchCount = computed(() => {
  if (selectedRoleId.value <= 0) return 0
  const gapNames = new Set(gapSkills.value.map((g) => g.skill_name))
  return graphData.value.nodes.filter((n) => !gapNames.has(n.name)).length
})

const coveragePercent = computed(() => {
  const total = matchCount.value + gapSkills.value.length
  if (total === 0) return 0
  return Math.round((matchCount.value / total) * 100)
})

// ====== ECharts Sunburst ======
function initSunburstChart(data: UserGraphResult) {
  if (!chartRefSunburst.value) return
  let instance = chartSunburst
  if (!instance) {
    instance = echarts.init(chartRefSunburst.value, undefined, { renderer: 'canvas' })
    chartSunburst = instance
  }

  const root = data.sunburst_data || {
    name: '能力图谱',
    children: data.categories.map((c) => ({ name: c.name, itemStyle: { color: c.color }, children: [] })),
  }

  instance.setOption({
    tooltip: {
      trigger: 'item',
      backgroundColor: 'rgba(255,255,255,0.96)',
      borderColor: '#e8e8e8',
      borderWidth: 1,
      padding: [12, 16],
      textStyle: { color: '#303133', fontSize: 13 },
      formatter: (params: any) => {
        const name = params.name || ''
        const val = params.value || 0
        // Leaf (skill) – show name and proficiency
        if (params.treePathInfo && params.treePathInfo.length >= 3) {
          const category = params.treePathInfo[1]?.name || ''
          return '<strong style="font-size:15px;color:#1a1a2e;">' + name + '</strong><br/>' +
            '<span style="color:#999">分类</span><span style="float:right">' + category + '</span><br/>' +
            '<span style="color:#999">熟练度</span><span style="float:right">' + val.toFixed(1) + ' / 5.0</span>'
        }
        // Category node
        if (params.treePathInfo && params.treePathInfo.length === 2) {
          const childCount = params.treePathInfo[1]?.children?.length || 0
          return '<strong style="font-size:15px;color:#1a1a2e;">' + name + '</strong><br/>' +
            '<span style="color:#999">技能数</span><span style="float:right">' + childCount + '</span>'
        }
        return name
      },
    },
    series: [
      {
        type: 'sunburst',
        data: [root],
        radius: ['0%', '95%'],
        sort: undefined,
        emphasis: {
          focus: 'ancestor',
        },
        levels: [
          {},
          {
            r0: '15%',
            r: '40%',
            label: { rotate: 'tangential' as const, fontSize: 13, fontWeight: 700, color: '#303133' },
          },
          {
            r0: '40%',
            r: '75%',
            label: { rotate: 'tangential' as const, fontSize: 11, color: '#606266' },
          },
        ],
        label: {
          rotate: 'tangential' as const,
          color: '#ffffff',
          fontSize: 12,
          fontWeight: 600,
          textShadowBlur: 4,
          textShadowColor: 'rgba(0,0,0,0.3)',
        },
        itemStyle: {
          borderRadius: 4,
          borderColor: '#fff',
          borderWidth: 2,
        },
        animationDuration: 1000,
        animationEasing: 'elasticOut' as const,
      },
    ],
  })
  instance.setOption({
    legend: {
      data: data.categories.map((c) => c.name),
      bottom: 0,
      textStyle: { fontSize: 12, color: '#666' },
      icon: 'circle',
    },
  })
}

// ====== Fetch Data ======
async function fetchGraph() {
  loading.value = true
  error.value = ''
  try {
    const res = await getUserGraph()
    const d = res.data.data || {}
    graphData.value = {
      nodes: d.nodes || [],
      edges: d.edges || [],
      gap_skills: d.gap_skills || [],
      state: d.state || (d.nodes && d.nodes.length ? 'ready' : 'empty'),
      categories: d.categories || [],
      sunburst_data: d.sunburst_data,
    }
    await nextTick()
    initSunburstChart(graphData.value)
  } catch (e: any) {
    error.value = e.message || '加载图谱失败'
  } finally {
    loading.value = false
  }
}

async function fetchRoles() {
  rolesLoading.value = true
  try {
    const res = await listRoles()
    roles.value = res.data || []
  } catch {
    roles.value = []
  } finally {
    rolesLoading.value = false
  }
}

async function handleRoleChange(roleId: number | null) {
  if (roleId == null) {
    selectedRoleId.value = null
    gapGraphData.value = { nodes: [], edges: [], gap_skills: [], state: 'empty', categories: [] }
    return
  }
  selectedRoleId.value = roleId
  gapLoading.value = true
  try {
    const res = await getUserGraph(roleId)
    const gd = res.data || {}
    gapGraphData.value = {
      nodes: gd.nodes || [],
      edges: gd.edges || [],
      gap_skills: gd.gap_skills || [],
      state: gd.state || (gd.nodes && gd.nodes.length ? 'ready' : 'empty'),
      categories: gd.categories || [],
    }
  } catch (e: any) {
    ElMessage.error(e.message || '加载缺口分析失败')
  } finally {
    gapLoading.value = false
  }
}

function handleResize() {
  chartSunburst?.resize()
}

// ====== Lifecycle ======
onMounted(() => {
  fetchGraph()
  fetchRoles()
  window.addEventListener('resize', handleResize)
})

onUnmounted(() => {
  chartSunburst?.dispose()
  chartSunburst = null
  window.removeEventListener('resize', handleResize)
})

// ====== Learning Tips ======
const learningTips = computed(() => {
  const tips: string[] = []
  if (graphData.value.nodes.length > 0) {
    const topCat = Object.entries(categoryStats.value).sort((a, b) => b[1] - a[1])[0]
    if (topCat) {
      tips.push('<strong>' + topCat[0] + '</strong>' + '技术栈完整度较高（' + topCat[1] + '项技能），建议横向拓展相邻领域补齐全栈能力。')
    }
  }
  if (tips.length === 0) {
    tips.push('暂无学习建议。添加技能后图谱会自动生成推荐路径。')
  }
  return tips
})
</script>

<template>
  <div class="ability-page">
    <div class="ability-container">
      <h1 class="page-title fade-up">个人能力图谱</h1>
      <p class="page-desc fade-up d1">基于 AI 语义构建的技能知识图谱 — 旭日图</p>

      <!-- Tabs -->
      <div class="tabs fade-up d2">
        <button class="tab-btn" :class="{ active: activeTab === 'graph' }" @click="activeTab = 'graph'">旭日图</button>
        <button class="tab-btn" :class="{ active: activeTab === 'gap' }" @click="activeTab = 'gap'">缺口分析</button>
      </div>

      <!-- ====== Loading ====== -->
      <div v-if="loading && graphData.nodes.length === 0" class="loading-state">
        <Loader2 :size="32" class="spin" />
        <p>加载能力图谱中...</p>
      </div>

      <!-- ====== Error ====== -->
      <div v-else-if="error && graphData.nodes.length === 0" class="error-state">
        <p>{{ error }}</p>
        <button class="tab-btn" @click="fetchGraph">重新加载</button>
      </div>

      <!-- ====== Sunburst Tab ====== -->
      <div v-show="activeTab === 'graph'" class="tab-content">
        <div class="graph-layout">
          <!-- Sunburst Chart -->
          <div class="graph-main card">
            <div class="card-header">
              <h3>技能旭日图</h3>
            </div>
            <div v-if="!loading && graphData.nodes.length === 0" class="empty-graph">
              <div class="empty-content">
                <svg class="empty-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                  <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
                  <polyline points="14 2 14 8 20 8"/>
                  <line x1="16" y1="13" x2="8" y2="13"/>
                  <line x1="16" y1="17" x2="8" y2="17"/>
                  <polyline points="10 9 9 9 8 9"/>
                </svg>
                <h3 class="empty-title">暂无能力图谱</h3>
                <p class="empty-desc">您还没有上传简历或添加技能信息，系统无法生成个人能力图谱。</p>
                <p class="empty-desc">上传简历后，系统会自动解析您的技能并构建知识图谱。</p>
                <router-link to="/user/resume" class="empty-btn">
                  <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="17 8 12 3 7 8"/><line x1="12" y1="3" x2="12" y2="15"/></svg>
                  上传简历
                </router-link>
              </div>
            </div>
            <div v-show="graphData.nodes.length > 0" ref="chartRefSunburst" class="echarts-container" />
            <!-- Legend -->
            <div class="legend">
              <div class="legend-group">
                <span class="legend-label">分类：</span>
                <span v-for="cat in (graphData.categories || [])" :key="cat.name" class="legend-item">
                  <span class="dot" :style="{ background: cat.color }" /> {{ cat.name }}
                </span>
              </div>
            </div>
          </div>

          <!-- Right: Stats -->
          <div class="graph-sidebar">
            <div class="card">
              <div class="card-header"><BarChart3 :size="18" /><h3>技能概览</h3></div>
              <div class="stat-big">{{ graphData.nodes.length }} <span class="stat-unit">项技能</span></div>
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
              <div class="level-bars">
                <div v-for="(count, label) in levelDistribution" :key="label" class="level-row">
                  <div class="level-header">
                    <span>{{ label }}</span>
                    <span class="level-count">{{ count }}项 ({{ graphData.state === 'ready' ? Math.round(count / graphData.nodes.length * 100) : 0 }}%)</span>
                  </div>
                  <div class="bar-track"><div class="bar-fill" :style="{ width: (graphData.state === 'ready' ? (count / graphData.nodes.length * 100) : 0) + '%' }" /></div>
                </div>
              </div>
            </div>

            <div class="card">
              <div class="card-header"><Lightbulb :size="18" /><h3>学习建议</h3></div>
              <div v-for="(tip, idx) in learningTips" :key="idx" class="tip tip-primary" v-html="tip" />
            </div>
          </div>
        </div>
      </div>

      <!-- ====== Gap Analysis Tab ====== -->
      <div v-show="activeTab === 'gap'" class="tab-content">
        <div class="card gap-card">
          <h3 class="gap-title">缺口分析视图</h3>
          <p class="gap-desc">选择目标岗位角色，对比当前技能与岗位要求，识别差距与重叠</p>

          <!-- Role Selector -->
          <div class="role-selector">
            <span class="role-label">目标角色：</span>
            <el-select
              v-model="selectedRoleId"
              placeholder="请选择目标岗位角色"
              :loading="rolesLoading"
              style="width: 320px"
              @change="handleRoleChange"
            >
              <el-option
                v-for="role in roles"
                :key="role.id"
                :label="role.name"
                :value="role.id"
              >
                <span>{{ role.name }}</span>
                <span v-if="role.category" class="role-category-tag">{{ role.category }}</span>
              </el-option>
            </el-select>
          </div>

          <!-- No role selected -->
          <div v-if="selectedRoleId <= 0" class="no-role-hint">
            <Briefcase :size="48" class="hint-icon" />
            <p>请先选择一个目标岗位角色<br/>系统将自动对比技能差距</p>
          </div>

          <!-- Gap Loading -->
          <div v-else-if="gapLoading" class="loading-state">
            <Loader2 :size="24" class="spin" />
            <p>正在分析技能差距...</p>
          </div>

          <!-- Gap Results -->
          <template v-else>
            <div class="target-job">
              <Briefcase :size="16" />
              <span>目标岗位：</span>
              <span class="target-tag">{{ roles.find((r) => r.id === selectedRoleId)?.name || '未知岗位' }}</span>
              <span class="target-match">匹配度 {{ coveragePercent }}%</span>
            </div>

            <!-- Coverage Bar -->
            <div class="coverage-section">
              <div class="coverage-cards">
                <div class="cov-card cov-green"><div class="cov-num">{{ matchCount }}</div><div class="cov-label">已匹配</div></div>
                <div class="cov-card cov-red"><div class="cov-num">{{ gapSkills.length }}</div><div class="cov-label">技能缺口</div></div>
              </div>
              <div class="coverage-bar-header">
                <span>覆盖度</span>
                <span class="coverage-pct">{{ coveragePercent }}%</span>
              </div>
              <div class="bar-track bar-thick"><div class="bar-fill" :style="{ width: coveragePercent + '%' }" /></div>
            </div>

            <!-- Gap Skills Detail -->
            <div v-if="gapSkills.length > 0" class="gap-detail">
              <h4>缺口技能</h4>
              <div class="gap-section">
                <div v-if="gapMustSkills.length > 0" class="gap-group">
                  <div class="gap-group-header"><span class="req-badge req-must">必备</span> 必须掌握的技能</div>
                  <div class="skill-tags">
                    <span v-for="s in gapMustSkills" :key="s.skill_name" class="tag tag-gap">
                      {{ s.skill_name }}
                    </span>
                  </div>
                </div>
                <div v-if="gapNiceSkills.length > 0" class="gap-group">
                  <div class="gap-group-header"><span class="req-badge req-nice">加分</span> 建议掌握的技能</div>
                  <div class="skill-tags">
                    <span v-for="s in gapNiceSkills" :key="s.skill_name" class="tag tag-gap-nice">{{ s.skill_name }}</span>
                  </div>
                </div>
                <div v-if="gapBonusSkills.length > 0" class="gap-group">
                  <div class="gap-group-header"><span class="req-badge req-bonus">可选</span> 可选的拓展技能</div>
                  <div class="skill-tags">
                    <span v-for="s in gapBonusSkills" :key="s.skill_name" class="tag tag-gap-bonus">{{ s.skill_name }}</span>
                  </div>
                </div>
              </div>
            </div>

            <div v-else class="no-gap">
              <p>恭喜！您的技能已覆盖该岗位所有要求</p>
            </div>

            <!-- Gap hint -->
            <div v-if="gapSkills.length > 0" class="tip tip-primary gap-hint">
              <Lightbulb :size="16" />
              <span><strong>AI 建议</strong> 重点补齐 <strong>{{ gapMustSkills.slice(0, 3).map((s) => s.skill_name).join('、') }}</strong> 等必备技能，可显著提升岗位匹配度。</span>
            </div>
          </template>
        </div>

        <!-- Gap graph -->
        <div v-if="selectedRoleId != null && !gapLoading && gapGraphData.nodes.length > 0" class="card gap-graph-card">
          <div class="card-header">
            <h3>技能旭日图（缺口视图）</h3>
            <span class="gap-legend-hint">红色节点为缺口技能</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped lang="scss">
.ability-page { padding: 24px 20px; min-height: 100vh; background: #f5f6f8; }
.ability-container { max-width: 1200px; margin: 0 auto; }

@keyframes fadeUp { from { opacity: 0; transform: translateY(20px); } to { opacity: 1; transform: translateY(0); } }
@keyframes spin { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }
.fade-up { opacity: 0; animation: fadeUp 0.5s cubic-bezier(0.22,1,0.36,1) forwards; }
.d1 { animation-delay: 0.08s; } .d2 { animation-delay: 0.15s; }
.spin { animation: spin 1s linear infinite; }

.page-title { font-size: 28px; font-weight: 700; color: #1a1a2e; letter-spacing: -0.3px; margin-bottom: 4px; }
.page-desc { font-size: 14px; color: #aaa; margin-bottom: 28px; }

/* Loading & Empty & Error */
.loading-state { display: flex; flex-direction: column; align-items: center; gap: 12px; padding: 80px 0; color: #909399; }
.error-state { text-align: center; padding: 60px 0; color: #f56c6c; }
.error-state .tab-btn { margin-top: 16px; }
.empty-graph { height: 480px; display: flex; align-items: center; justify-content: center; }
.empty-content { text-align: center; max-width: 400px; }
.empty-icon { width: 64px; height: 64px; color: #c0c4cc; margin-bottom: 16px; }
.empty-title { font-size: 18px; font-weight: 600; color: #303133; margin-bottom: 12px; }
.empty-desc { font-size: 14px; color: #909399; line-height: 1.8; margin-bottom: 4px; }
.empty-btn { display: inline-flex; align-items: center; gap: 6px; margin-top: 20px; padding: 10px 28px; border-radius: 8px; font-size: 14px; font-weight: 600; color: #fff; background: #1a3a5c; text-decoration: none; transition: background 0.25s; }
.empty-btn:hover { background: #2a5a8c; text-decoration: none; color: #fff; }
.empty-btn svg { width: 16px; height: 16px; }

/* Tabs */
.tabs { display: flex; gap: 6px; margin-bottom: 28px; }
.tab-btn {
  padding: 8px 20px; border-radius: 6px; font-size: 14px; font-weight: 500;
  cursor: pointer; transition: all 0.25s; border: 1px solid #e8e8e8; background: #fff; color: #666;
  &:hover { border-color: #1a3a5c; color: #1a3a5c; }
  &.active { background: #1a3a5c; color: #fff; border-color: #1a3a5c; }
}

/* Cards */
.card { background: #fff; border-radius: 12px; padding: 20px; border: 1px solid #eee; box-shadow: 0 1px 3px rgba(0,0,0,0.04); }
.card-header { display: flex; align-items: center; gap: 8px; margin-bottom: 14px; h3 { font-size: 14px; font-weight: 600; color: #303133; } svg { color: #1a3a5c; width: 16px; height: 16px; } }

/* Graph layout */
.graph-layout { display: grid; grid-template-columns: 1fr 340px; gap: 24px; }
.graph-main { min-height: 0; }
.echarts-container { width: 100%; height: 560px; border-radius: 10px; background: #fafbfc; border: 1px solid #f0f0f0; }

/* Legend */
.legend { margin-top: 12px; display: flex; flex-direction: column; gap: 8px; }
.legend-group { display: flex; align-items: center; gap: 14px; flex-wrap: wrap; }
.legend-label { font-size: 12px; color: #909399; font-weight: 600; }
.legend-item { display: inline-flex; align-items: center; gap: 4px; font-size: 12px; color: #606266; }
.dot { display: inline-block; width: 10px; height: 10px; border-radius: 50%; }

/* Sidebar */
.graph-sidebar { display: flex; flex-direction: column; gap: 20px; }
.stat-big { font-size: 32px; font-weight: 700; color: #1a1a2e; letter-spacing: -1px; margin-bottom: 16px; }
.stat-unit { font-size: 14px; font-weight: 500; color: #909399; }

.category-list { display: flex; flex-direction: column; gap: 10px; }
.category-row { display: flex; align-items: center; gap: 8px; }
.category-dot { width: 10px; height: 10px; border-radius: 50%; flex-shrink: 0; }
.category-name { flex: 1; font-size: 13px; color: #606266; }
.category-count { font-size: 13px; font-weight: 600; color: #303133; }

.level-bars { display: flex; flex-direction: column; gap: 14px; }
.level-header { display: flex; justify-content: space-between; margin-bottom: 6px; font-size: 13px; color: #303133; }
.level-count { color: #909399; font-size: 12px; }
.bar-track { height: 6px; border-radius: 999px; background: #e9ecef; overflow: hidden; }
.bar-fill { height: 100%; border-radius: 999px; background: linear-gradient(90deg, #1a3a5c, #0ea5e9); transition: width 0.8s ease; }

.tip {
  padding: 12px 16px; border-radius: 8px; font-size: 13px; line-height: 1.6; margin-top: 8px;
  &:first-of-type { margin-top: 0; }
}
.tip-primary { background: rgba(14,165,233,0.08); border: 1px solid rgba(14,165,233,0.15); color: #303133; }

/* Gap analysis */
.gap-card { padding: 28px 32px; }
.gap-title { font-size: 20px; font-weight: 700; color: #1a1a2e; margin-bottom: 4px; letter-spacing: -0.3px; }
.gap-desc { font-size: 14px; color: #909399; margin-bottom: 24px; }

.role-selector { display: flex; align-items: center; gap: 12px; margin-bottom: 24px; }
.role-label { font-size: 14px; font-weight: 600; color: #303133; white-space: nowrap; }
.role-category-tag { margin-left: 8px; font-size: 11px; color: #909399; background: #f3f4f5; padding: 1px 8px; border-radius: 3px; }

.no-role-hint { text-align: center; padding: 60px 0; color: #909399; }
.hint-icon { color: #c0c4cc; margin-bottom: 16px; }
.no-role-hint p { font-size: 14px; line-height: 1.8; }

.target-job {
  display: flex; align-items: center; gap: 8px; margin-bottom: 20px;
  font-size: 14px; color: #606266;
  svg { color: #1a3a5c; }
}
.target-tag { padding: 4px 14px; border-radius: 4px; background: #dbeafe; color: #1e3a8a; font-size: 13px; font-weight: 600; }
.target-match { font-size: 13px; color: #909399; margin-left: 4px; }

.coverage-section { padding-top: 20px; border-top: 1px solid #e5e7eb; }
.coverage-cards { display: grid; grid-template-columns: repeat(2, 1fr); gap: 12px; margin-bottom: 20px; }
.cov-card { padding: 16px; border-radius: 10px; text-align: center; }
.cov-green { background: rgba(34,197,94,0.08); }
.cov-red { background: rgba(239,68,68,0.08); }
.cov-num { font-size: 24px; font-weight: 700; }
.cov-green .cov-num { color: #155724; }
.cov-red .cov-num { color: #721c24; }
.cov-label { font-size: 12px; color: #909399; margin-top: 4px; }
.coverage-bar-header { display: flex; justify-content: space-between; margin-bottom: 8px; font-size: 13px; color: #606266; }
.coverage-pct { font-weight: 700; color: #1a3a5c; }
.bar-thick { height: 10px; }

/* Gap detail */
.gap-detail { margin-top: 24px; }
.gap-detail h4 { font-size: 15px; font-weight: 600; color: #303133; margin-bottom: 16px; }
.gap-group { margin-bottom: 16px; }
.gap-group:last-child { margin-bottom: 0; }
.gap-group-header { display: flex; align-items: center; gap: 8px; margin-bottom: 10px; font-size: 13px; color: #606266; }
.req-badge { display: inline-block; padding: 2px 10px; border-radius: 3px; font-size: 11px; font-weight: 700; color: #fff; }
.req-must { background: #e74c3c; }
.req-nice { background: #e67e22; }
.req-bonus { background: #95a5a6; }

.skill-tags { display: flex; flex-wrap: wrap; gap: 8px; }
.tag { padding: 4px 14px; border-radius: 4px; font-size: 12px; font-weight: 600; }
.tag-gap { background: #f8d7da; color: #721c24; }
.tag-gap-nice { background: #fdebd0; color: #935e0c; }
.tag-gap-bonus { background: #f3f4f5; color: #6b7280; }

.no-gap { text-align: center; padding: 40px 0; color: #67c23a; font-size: 15px; font-weight: 600; }

.gap-hint { display: flex; align-items: flex-start; gap: 8px; margin-top: 20px; svg { flex-shrink: 0; margin-top: 2px; } }

.gap-graph-card { margin-top: 20px; }
.gap-legend-hint { font-size: 12px; color: #FF4D4F; margin-left: auto; }

@media (max-width: 1024px) {
  .graph-layout { grid-template-columns: 1fr; }
  .echarts-container { height: 360px; }
  .role-selector { flex-direction: column; align-items: stretch; }
  .role-selector .el-select { width: 100% !important; }
}
</style>




