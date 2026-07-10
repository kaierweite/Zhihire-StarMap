<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import {
  Route, Briefcase, Lightbulb, CheckCircle, ArrowRight, RefreshCw,
  Sparkles, Target, AlertTriangle, Info, Gift, Loader2,
} from 'lucide-vue-next'
import { ElMessage } from 'element-plus'
import { listRoles } from '@/api/graph'
import { getCareerPlan, generateCareerPlan } from '@/api/career'
import type { OccupationRole } from '@/types/graph'
import type { CareerPlanData } from '@/api/career'

// ====== State ======
const roles = ref<OccupationRole[]>([])
const selectedRoleId = ref<number | null>(null)
const pageLoading = ref(true)
const generating = ref(false)
const planData = ref<CareerPlanData | null>(null)
const hasPlan = ref(false)
const errorMsg = ref('')

// ====== Computed ======
const gapMustSkills = computed(() =>
  (planData.value?.gap_skills || []).filter((g) => g.requirement_level === 'MUST'),
)
const gapNiceSkills = computed(() =>
  (planData.value?.gap_skills || []).filter((g) => g.requirement_level === 'NICE'),
)
const gapBonusSkills = computed(() =>
  (planData.value?.gap_skills || []).filter((g) => g.requirement_level === 'BONUS'),
)

const selectedRoleName = computed(() => {
  if (!planData.value) return ''
  return planData.value.target_role
})

const scoreColor = computed(() => {
  const s = planData.value?.score ?? 0
  if (s >= 80) return '#198754'
  if (s >= 60) return '#1a3a5c'
  if (s >= 40) return '#e67e22'
  return '#e74c3c'
})

// SVG circular progress — circumference for r=54 is 2*pi*54 ≈ 339.292
const CIRCUMFERENCE = 2 * Math.PI * 54
const scoreOffset = computed(() => {
  const s = planData.value?.score ?? 0
  return CIRCUMFERENCE * (1 - s / 100)
})

// ====== Lifecycle ======
onMounted(async () => {
  pageLoading.value = true
  try {
    const [rolesRes, planRes] = await Promise.all([listRoles(), getCareerPlan()])
    roles.value = rolesRes.data.data || []
    const planResp = planRes.data
    if (planResp.data) {
      planData.value = planResp.data
      hasPlan.value = true
      selectedRoleId.value = planResp.data.target_role_id ?? null
    }
  } catch {
    // errors handled by request interceptor
  } finally {
    pageLoading.value = false
  }
})

// ====== Actions ======
async function handleGenerate() {
  if (selectedRoleId.value == null) {
    ElMessage.warning('请先选择一个目标职业角色')
    return
  }
  generating.value = true
  errorMsg.value = ''
  try {
    const res = await generateCareerPlan(selectedRoleId.value)
    planData.value = res.data.data
    hasPlan.value = true
  } catch (err: any) {
    if (err?.response?.status === 400 || err?.response?.status === 404) {
      errorMsg.value = err.response.data?.message || '该角色暂无可用数据'
    } else {
      errorMsg.value = '生成失败，请稍后重试'
    }
  } finally {
    generating.value = false
  }
}

async function handleRegenerate() {
  if (selectedRoleId.value == null) {
    ElMessage.warning('请先选择一个目标职业角色')
    return
  }
  await handleGenerate()
}
</script>

<template>
  <div class="career-page">
    <div class="career-container">
      <!-- Header -->
      <h1 class="page-title">AI 智能职业规划</h1>
      <p class="page-desc">基于技能图谱的拓扑排序算法，生成可复现、可解释的学习路径</p>

      <!-- Loading state -->
      <div v-if="pageLoading" class="loading-state">
        <Loader2 :size="36" class="spin-icon" />
        <p>加载中...</p>
      </div>

      <!-- ====== No plan yet: Role selector ====== -->
      <template v-else-if="!hasPlan">
        <section class="fade-up">
          <h2 class="section-heading"><Briefcase :size="22" /> 选择目标职业角色</h2>
          <div v-if="roles.length === 0" class="empty-role">
            <p>暂无可用的职业角色数据</p>
          </div>
          <div v-else class="role-grid">
            <div
              v-for="role in roles"
              :key="role.id"
              class="role-card"
              :class="{ active: selectedRoleId === role.id }"
              @click="selectedRoleId = role.id"
            >
              <div class="role-info">
                <h3>{{ role.name }}</h3>
                <p v-if="role.description" class="role-desc">{{ role.description }}</p>
              </div>
              <CheckCircle v-if="selectedRoleId === role.id" :size="20" class="check-icon" />
            </div>
          </div>

          <div v-if="errorMsg" class="error-banner">{{ errorMsg }}</div>

          <button
            class="generate-btn"
            :disabled="selectedRoleId == null || generating"
            @click="handleGenerate"
          >
            <Loader2 v-if="generating" :size="18" class="spin-icon" />
            <Sparkles v-else :size="18" />
            {{ generating ? '生成中...' : '生成职业规划' }}
          </button>
        </section>
      </template>

      <!-- ====== Plan exists: Show result ====== -->
      <template v-else-if="planData">
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
              <text x="70" y="62" text-anchor="middle" fill="#303133" font-size="32" font-weight="700">{{ planData.score }}</text>
              <text x="70" y="82" text-anchor="middle" fill="#909399" font-size="13">分</text>
            </svg>
          </div>
          <div class="score-meta">
            <h2 class="target-role">{{ planData.target_role }}</h2>
            <div class="score-tags">
              <span class="source-badge">{{ planData.source }}</span>
              <span class="match-label">技能匹配度</span>
            </div>
            <p class="score-desc">
              与目标岗位匹配度为 <strong>{{ planData.score }}%</strong>，
              需补充 {{ planData.gap_skills.length }} 项技能。
            </p>
          </div>
        </div>

        <!-- Gap Skills -->
        <section class="fade-up gap-section">
          <h2 class="section-heading"><Lightbulb :size="22" /> 缺口技能</h2>

          <div v-if="gapMustSkills.length" class="skill-group">
            <div class="group-head"><AlertTriangle :size="16" class="must-icon" /> MUST — 必备</div>
            <div class="skill-chips">
              <span v-for="s in gapMustSkills" :key="s.skill_name" class="skill-chip must">{{ s.skill_name }}</span>
            </div>
          </div>

          <div v-if="gapNiceSkills.length" class="skill-group">
            <div class="group-head"><Info :size="16" class="nice-icon" /> NICE — 加分</div>
            <div class="skill-chips">
              <span v-for="s in gapNiceSkills" :key="s.skill_name" class="skill-chip nice">{{ s.skill_name }}</span>
            </div>
          </div>

          <div v-if="gapBonusSkills.length" class="skill-group">
            <div class="group-head"><Gift :size="16" class="bonus-icon" /> BONUS — 锦上添花</div>
            <div class="skill-chips">
              <span v-for="s in gapBonusSkills" :key="s.skill_name" class="skill-chip bonus">{{ s.skill_name }}</span>
            </div>
          </div>

          <div v-if="planData.gap_skills.length === 0" class="no-gap">
            <CheckCircle :size="20" /> 已掌握所有必需技能，无需额外补充！
          </div>
        </section>

        <!-- Learning Path -->
        <section class="fade-up">
          <h2 class="section-heading">
            <Route :size="22" /> 学习路径
            <span class="role-tag">{{ planData.target_role }}</span>
          </h2>

          <div class="path-steps">
            <div
              v-for="(step, idx) in planData.learning_path"
              :key="idx"
              class="path-step-card"
            >
              <div class="step-index">{{ idx + 1 }}</div>
              <div class="step-body">
                <div class="step-skills">
                  <span
                    v-for="(skill, si) in step.skills"
                    :key="si"
                    class="skill-node"
                  >
                    {{ skill }}
                    <ArrowRight v-if="si < step.skills.length - 1" :size="14" class="arrow-icon" />
                  </span>
                </div>
              </div>
            </div>
          </div>
        </section>

        <!-- Graph Hints -->
        <section v-if="planData.graph_hints.length" class="fade-up">
          <h2 class="section-heading"><Lightbulb :size="22" /> 图谱关联提示</h2>
          <div class="hints-grid">
            <div v-for="(hint, idx) in planData.graph_hints" :key="idx" class="hint-card">
              <Lightbulb :size="18" class="hint-icon" />
              <p>{{ hint }}</p>
            </div>
          </div>
        </section>

        <!-- Rationale -->
        <section v-if="planData.rationale" class="fade-up">
          <h2 class="section-heading"><Sparkles :size="22" /> 规划说明</h2>
          <div class="rationale-card">
            <p class="rationale-text">{{ planData.rationale }}</p>
            <div v-if="planData.created_at" class="rationale-footer">
              生成时间：{{ planData.created_at }}
            </div>
          </div>
        </section>

        <!-- Actions -->
        <div class="action-bar fade-up">
          <button class="regen-btn" :disabled="generating" @click="handleRegenerate">
            <Loader2 v-if="generating" :size="16" class="spin-icon" />
            <RefreshCw v-else :size="16" />
            {{ generating ? '重新生成中...' : '重新生成' }}
          </button>
        </div>
      </template>
    </div>
  </div>
</template>

<style scoped lang="scss">
.career-page { padding: 24px 16px; }
.career-container { max-width: 900px; margin: 0 auto; }

// ====== Animation ======
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
.fade-up:nth-child(6) { animation-delay: 0.37s; }

.spin-icon { animation: spin 1s linear infinite; }

.page-title {
  font-size: 36px; font-weight: 700; color: #303133; letter-spacing: -1px; margin-bottom: 6px;
}
.page-desc {
  font-size: 16px; color: #909399; margin-bottom: 32px;
}
.section-heading {
  display: flex; align-items: center; gap: 10px; font-size: 22px; font-weight: 600;
  color: #303133; margin-bottom: 20px;
  svg { color: #1a3a5c; }
}
.role-tag {
  font-size: 13px; padding: 3px 12px; border-radius: 4px; background: #dbeafe;
  color: #1e3a8a; font-weight: 600;
}

// ====== Loading ======
.loading-state {
  display: flex; flex-direction: column; align-items: center; gap: 12px;
  padding: 80px 0; color: #909399;
}

// ====== Role Selector ======
.role-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 12px; margin-bottom: 24px; }
.role-card {
  display: flex; align-items: center; justify-content: space-between; gap: 12px;
  padding: 16px; background: #fff; border-radius: 12px;
  border: 2px solid #e5e7eb; cursor: pointer; transition: all 0.25s;
  &:hover { border-color: #1a3a5c; transform: translateY(-2px); box-shadow: 0 6px 20px rgba(0,0,0,0.06); }
  &.active { border-color: #1a3a5c; box-shadow: 0 6px 20px rgba(26,58,92,0.1); }
}
.role-info { flex: 1; min-width: 0;
  h3 { font-size: 15px; font-weight: 600; color: #303133; margin-bottom: 3px; }
}
.role-desc { font-size: 12px; color: #909399; margin: 0; line-height: 1.4; }
.check-icon { color: #1a3a5c; flex-shrink: 0; }
.empty-role { text-align: center; padding: 40px 0; color: #909399; }

.error-banner {
  background: #fdf0ef; border: 1px solid #f56c6c; border-radius: 8px; padding: 12px 16px;
  color: #e74c3c; font-size: 14px; margin-bottom: 16px;
}

.generate-btn {
  display: inline-flex; align-items: center; gap: 8px;
  padding: 12px 28px; border: none; border-radius: 10px;
  background: #1a3a5c; color: #fff; font-size: 15px; font-weight: 600;
  cursor: pointer; transition: all 0.2s;
  &:hover:not(:disabled) { background: #0f2b47; transform: translateY(-1px); }
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
  background: #dbeafe; color: #1e3a8a; font-weight: 600; text-transform: uppercase;
}
.match-label { font-size: 13px; color: #909399; }
.score-desc { font-size: 14px; color: #606266; margin: 0; line-height: 1.6; }

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
  &.must { background: #fdf0ef; color: #c0392b; border: 1px solid #f5c6cb; }
  &.nice { background: #ebf5fb; color: #2980b9; border: 1px solid #aed6f1; }
  &.bonus { background: #f8f9fa; color: #7f8c8d; border: 1px solid #dee2e6; }
}
.no-gap {
  display: flex; align-items: center; gap: 8px;
  padding: 16px 20px; background: #d4edda; border-radius: 8px;
  color: #155724; font-size: 14px; font-weight: 500;
}

// ====== Learning Path ======
.path-steps { margin-bottom: 28px; }
.path-step-card {
  display: flex; align-items: flex-start; gap: 16px;
  margin-bottom: 14px; position: relative;
  &:not(:last-child)::after {
    content: ''; position: absolute; left: 18px; top: 44px;
    width: 2px; height: calc(100% + 14px);
    background: linear-gradient(180deg, #1a3a5c 60%, #e9ecef 100%);
  }
}
.step-index {
  width: 38px; height: 38px; border-radius: 50%;
  background: #1a3a5c; color: #fff; font-size: 16px; font-weight: 700;
  display: flex; align-items: center; justify-content: center; flex-shrink: 0;
  z-index: 1;
}
.step-body {
  flex: 1; background: #fff; border-radius: 12px;
  padding: 14px 18px; border: 1px solid #e5e7eb;
}
.step-skills {
  display: flex; flex-wrap: wrap; align-items: center; gap: 8px;
}
.skill-node {
  display: inline-flex; align-items: center; gap: 4px;
  font-size: 13px; font-weight: 500; color: #303133;
  background: #f3f4f5; padding: 4px 12px; border-radius: 6px;
}
.arrow-icon { color: #909399; flex-shrink: 0; }

// ====== Graph Hints ======
.hints-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; margin-bottom: 28px; }
.hint-card {
  display: flex; align-items: flex-start; gap: 12px;
  background: #f0f9ff; border: 1px solid #bae6fd; border-radius: 10px;
  padding: 16px;
  .hint-icon { color: #1a3a5c; flex-shrink: 0; margin-top: 1px; }
  p { font-size: 13px; color: #303133; line-height: 1.6; margin: 0; }
}

// ====== Rationale ======
.rationale-card {
  background: #fff; border-radius: 12px; padding: 24px 28px;
  border: 1px solid #e5e7eb; margin-bottom: 28px;
}
.rationale-text {
  font-size: 14px; color: #606266; line-height: 1.8; margin: 0; white-space: pre-wrap;
}
.rationale-footer {
  margin-top: 16px; padding-top: 12px; border-top: 1px solid #f0f0f0;
  font-size: 12px; color: #c0c4cc;
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

// ====== Responsive ======
@media (max-width: 768px) {
  .role-grid { grid-template-columns: 1fr 1fr; }
  .hints-grid { grid-template-columns: 1fr; }
  .score-section { flex-direction: column; text-align: center; }
}
@media (max-width: 480px) {
  .role-grid { grid-template-columns: 1fr; }
}
</style>
