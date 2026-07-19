<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { ShieldCheck, CheckCircle, XCircle, BookOpen, RefreshCw } from 'lucide-vue-next'
import { listSkillAudit, auditSkill } from '@/api/admin'
import type { SkillAuditItem } from '@/types/admin'

const skillAudits = ref<SkillAuditItem[]>([])
const skillPage = ref(1)
const skillSize = ref(20)
const skillTotal = ref(0)
const skillLoading = ref(false)

async function fetchSkillAudits() {
  skillLoading.value = true
  try {
    const res = await listSkillAudit(skillPage.value, skillSize.value)
    const data = res.data.data
    skillAudits.value = data.records
    skillTotal.value = data.total
  } catch {
    // handled by interceptor
  } finally {
    skillLoading.value = false
  }
}

async function approveSkillAction(skillId: number) {
  try {
    await auditSkill(skillId, 'approve')
    ElMessage.success('已批准技能合并')
    await fetchSkillAudits()
  } catch {
    // handled by interceptor
  }
}

async function rejectSkillAction(skillId: number) {
  try {
    await auditSkill(skillId, 'reject')
    ElMessage.info('已拒绝技能合并')
    await fetchSkillAudits()
  } catch {
    // handled by interceptor
  }
}

const pendingSkills = computed(() => skillAudits.value.filter(s => s.status === 'CANDIDATE').length)

function skillStatusLabel(s: string) {
  return s === 'CANDIDATE' ? '待审核' : s === 'ACTIVE' ? '已通过' : '已合并'
}

function skillStatusClass(s: string) {
  return s === 'CANDIDATE' ? 'pending' : s === 'ACTIVE' ? 'approved' : 'rejected'
}

onMounted(fetchSkillAudits)
</script>

<template>
  <div class="page">
    <h1 class="page-title fade-up">审核管理</h1>
    <p class="page-desc fade-up d1">管理技能字典同义合并</p>

    <div class="toolbar fade-up d1">
      <span class="count">待审核 <strong>{{ pendingSkills }}</strong> 项</span>
      <button class="refresh-btn" :disabled="skillLoading" @click="fetchSkillAudits">
        <RefreshCw :size="14" :class="{ spinning: skillLoading }" />
        {{ skillLoading ? '刷新中...' : '刷新' }}
      </button>
    </div>

    <div class="audit-list fade-up d2">
      <div v-for="s in skillAudits" :key="s.id" class="audit-card">
        <div class="audit-info">
          <h3>{{ s.name }}</h3>
          <p>分类: {{ s.category || '未分类' }} · 提交于{{ s.created_at }}</p>
        </div>
        <span class="status-tag" :class="skillStatusClass(s.status)">{{ skillStatusLabel(s.status) }}</span>
        <div v-if="s.status === 'CANDIDATE'" class="audit-actions">
          <button class="approve-btn" @click="approveSkillAction(s.id)"><CheckCircle :size="14" /> 通过</button>
          <button class="reject-btn" @click="rejectSkillAction(s.id)"><XCircle :size="14" /> 拒绝</button>
        </div>
      </div>
      <div class="pagination-wrap">
        <el-pagination
          v-model:current-page="skillPage"
          v-model:page-size="skillSize"
          :total="skillTotal"
          :page-sizes="[10, 20, 50]"
          layout="total, sizes, prev, pager, next"
          background
          @current-change="fetchSkillAudits"
          @size-change="fetchSkillAudits"
        />
      </div>
    </div>
  </div>
</template>

<style scoped lang="scss">
.page { max-width: 800px; margin: 0 auto; }
@keyframes fadeUp { from { opacity: 0; transform: translateY(20px); } to { opacity: 1; transform: translateY(0); } }
@keyframes spin { to { transform: rotate(360deg); } }
.fade-up { opacity: 0; animation: fadeUp 0.5s cubic-bezier(0.22,1,0.36,1) forwards; }
.d1 { animation-delay: 0.08s; } .d2 { animation-delay: 0.15s; }
.spinning { animation: spin 1s linear infinite; }

.page-title { font-size: 28px; font-weight: 700; color: #121c28; margin-bottom: 4px; }
.page-desc { font-size: 14px; color: #404944; margin-bottom: 20px; }

.toolbar { display: flex; align-items: center; justify-content: space-between; margin-bottom: 16px; }
.count { font-size: 13px; color: #404944; strong { color: #f56c6c; } }
.refresh-btn {
  display: flex; align-items: center; gap: 4px; padding: 6px 14px; border-radius: 6px;
  border: 1px solid #bfc9c3; background: #fff; color: #404944; font-size: 12px; font-weight: 500; cursor: pointer;
  &:hover:not(:disabled) { border-color: #003527; color: #003527; }
  &:disabled { opacity: 0.5; cursor: not-allowed; }
}

.audit-list { display: flex; flex-direction: column; gap: 12px; }
.audit-card { display: flex; align-items: center; gap: 16px; padding: 16px 20px; background: #fff; border-radius: 12px; border: 1px solid #bfc9c3; transition: all 0.25s; &:hover { box-shadow: 0 4px 16px rgba(0,0,0,0.04); } }
.audit-info { flex: 1; h3 { font-size: 15px; font-weight: 600; color: #121c28; margin-bottom: 2px; } p { font-size: 13px; color: #404944; } }
.status-tag { font-size: 11px; padding: 3px 12px; border-radius: 999px; font-weight: 600; &.pending { background: #fff3cd; color: #856404; } &.approved { background: #d4edda; color: #155724; } &.rejected { background: #f8d7da; color: #721c24; } }
.audit-actions { display: flex; gap: 8px; }
.approve-btn { display: flex; align-items: center; gap: 4px; padding: 6px 14px; border-radius: 999px; background: #198754; color: #fff; font-size: 12px; font-weight: 600; border: none; cursor: pointer; &:hover { background: #157347; } }
.reject-btn { display: flex; align-items: center; gap: 4px; padding: 6px 14px; border-radius: 999px; background: #fff; color: #dc3545; font-size: 12px; font-weight: 600; border: 1px solid #dc3545; cursor: pointer; &:hover { background: #dc3545; color: #fff; } }
.pagination-wrap { display: flex; justify-content: center; margin-top: 16px; }
</style>
