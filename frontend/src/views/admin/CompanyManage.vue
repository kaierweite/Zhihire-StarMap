<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Building2, Search, CheckCircle, XCircle, RefreshCw, Clock, Globe, MapPin } from 'lucide-vue-next'
import { listCompanyAudit, auditCompany } from '@/api/admin'
import type { CompanyAuditItem } from '@/types/admin'

const keyword = ref('')
const statusFilter = ref('')

const audits = ref<CompanyAuditItem[]>([])
const page = ref(1)
const size = ref(20)
const total = ref(0)
const loading = ref(false)

async function fetchData() {
  loading.value = true
  try {
    const res = await listCompanyAudit(page.value, size.value)
    const data = res.data.data
    audits.value = data.records
    total.value = data.total
  } catch {
    // handled by interceptor
  } finally {
    loading.value = false
  }
}

const filtered = computed(() => {
  let list = audits.value
  if (statusFilter.value) {
    list = list.filter(c => c.audit_status === statusFilter.value)
  }
  if (keyword.value.trim()) {
    const kw = keyword.value.trim().toLowerCase()
    list = list.filter(c =>
      c.company_name.toLowerCase().includes(kw) ||
      (c.contact_email || '').toLowerCase().includes(kw)
    )
  }
  return list
})

// --- Audit actions ---
const rejectDialogVisible = ref(false)
const rejectCompanyId = ref<number | null>(null)
const rejectReason = ref('')

function showRejectDialog(companyId: number) {
  rejectCompanyId.value = companyId
  rejectReason.value = ''
  rejectDialogVisible.value = true
}

async function confirmReject() {
  if (!rejectCompanyId.value) return
  try {
    await auditCompany(rejectCompanyId.value, 'reject', rejectReason.value || undefined)
    ElMessage.success('已拒绝该企业的认证审核')
    rejectDialogVisible.value = false
    await fetchData()
  } catch {
    // handled by interceptor
  }
}

async function approveCompanyAction(companyId: number) {
  try {
    await auditCompany(companyId, 'pass')
    ElMessage.success('已通过该企业的认证审核')
    await fetchData()
  } catch {
    // handled by interceptor
  }
}

function auditStatusLabel(s: string) {
  return s === 'PENDING' ? '待审核' : s === 'VERIFIED' ? '已通过' : '已拒绝'
}

function auditStatusClass(s: string) {
  return s === 'PENDING' ? 'pending' : s === 'VERIFIED' ? 'approved' : 'rejected'
}

function contactInfo(c: CompanyAuditItem): string {
  const parts: string[] = []
  if (c.contact_name) parts.push(c.contact_name)
  if (c.contact_phone) parts.push(c.contact_phone)
  if (c.contact_email) parts.push(c.contact_email)
  return parts.join(' | ') || '-'
}

onMounted(fetchData)
</script>

<template>
  <div class="page">
    <div class="page-header fade-up">
      <div>
        <h1>企业管理</h1>
        <p class="page-desc">管理平台企业信息，支持认证审核、搜索和筛选</p>
      </div>
      <button class="refresh-btn" :disabled="loading" @click="fetchData">
        <RefreshCw :size="14" :class="{ spinning: loading }" />
        {{ loading ? '刷新中...' : '刷新' }}
      </button>
    </div>

    <div class="filter-bar fade-up d1">
      <div class="search-box">
        <Search :size="16" />
        <input v-model="keyword" placeholder="搜索企业名称 / 邮箱..." @keyup.enter="fetchData" />
      </div>
      <select v-model="statusFilter" class="sel">
        <option value="">全部状态</option>
        <option value="PENDING">待审核</option>
        <option value="VERIFIED">已通过</option>
        <option value="REJECTED">已拒绝</option>
      </select>
      <span class="count">共 <strong>{{ filtered.length }}</strong> 家企业</span>
    </div>

    <div class="table fade-up d2">
      <div class="th">
        <span class="c-name">企业名称</span>
        <span class="c-info">行业 / 规模</span>
        <span class="c-contact">联系人</span>
        <span class="c-status">审核状态</span>
        <span class="c-date">提交时间</span>
        <span class="c-act">操作</span>
      </div>
      <div v-for="c in filtered" :key="c.id" class="tr" :class="{ rejected: c.audit_status === 'REJECTED' }">
        <span class="c-name">
          <strong>{{ c.company_name }}</strong>
        </span>
        <span class="c-info">
          <span class="info-text">{{ c.industry || '-' }} / {{ c.scale || '-' }}</span>
        </span>
        <span class="c-contact">
          <span class="contact-text">{{ contactInfo(c) }}</span>
        </span>
        <span class="c-status">
          <span class="status-tag" :class="auditStatusClass(c.audit_status)">{{ auditStatusLabel(c.audit_status) }}</span>
        </span>
        <span class="c-date">
          <Clock :size="12" />
          {{ c.created_at ? c.created_at.slice(0, 10) : '-' }}
        </span>
        <span class="c-act">
          <div v-if="c.audit_status === 'PENDING'" class="act-btns">
            <button class="approve-btn" @click="approveCompanyAction(c.id)">
              <CheckCircle :size="13" /> 通过
            </button>
            <button class="reject-btn" @click="showRejectDialog(c.id)">
              <XCircle :size="13" /> 拒绝
            </button>
          </div>
          <span v-else-if="c.audit_status === 'VERIFIED'" class="act-done">已操作</span>
          <span v-else class="act-done muted">已拒绝</span>
        </span>
      </div>
    </div>

    <div class="pagination-wrap fade-up d3">
      <el-pagination
        v-model:current-page="page"
        v-model:page-size="size"
        :total="total"
        :page-sizes="[10, 20, 50]"
        layout="total, sizes, prev, pager, next"
        background
        @current-change="fetchData"
        @size-change="fetchData"
      />
    </div>

    <!-- Reject Reason Dialog -->
    <el-dialog v-model="rejectDialogVisible" title="拒绝企业审核" width="420px">
      <p style="font-size:13px;color:#404944;margin-bottom:12px">请输入拒绝原因，企业端将收到此反馈：</p>
      <el-input
        v-model="rejectReason"
        type="textarea"
        :rows="4"
        placeholder="请输入拒绝原因（可选）"
      />
      <template #footer>
        <el-button @click="rejectDialogVisible = false">取消</el-button>
        <el-button type="danger" @click="confirmReject">确认拒绝</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<style scoped lang="scss">
.page { max-width: 1100px; margin: 0 auto; }

@keyframes fadeUp { from { opacity: 0; transform: translateY(20px); } to { opacity: 1; transform: translateY(0); } }
@keyframes spin { to { transform: rotate(360deg); } }
.fade-up { opacity: 0; animation: fadeUp 0.5s cubic-bezier(0.22,1,0.36,1) forwards; }
.d1 { animation-delay: 0.08s; } .d2 { animation-delay: 0.15s; } .d3 { animation-delay: 0.22s; }
.spinning { animation: spin 1s linear infinite; }

.page-header { display: flex; align-items: flex-start; justify-content: space-between; margin-bottom: 16px; }
h1 { font-size: 28px; font-weight: 700; color: #121c28; margin: 0 0 4px 0; }
.page-desc { font-size: 14px; color: #404944; margin: 0; }
.refresh-btn {
  display: flex; align-items: center; gap: 4px; padding: 8px 14px; border-radius: 8px;
  border: 1px solid #bfc9c3; background: #fff; color: #404944; font-size: 13px; font-weight: 500; cursor: pointer;
  &:hover:not(:disabled) { border-color: #003527; color: #003527; }
  &:disabled { opacity: 0.5; cursor: not-allowed; }
}

.filter-bar { display: flex; gap: 8px; align-items: center; flex-wrap: wrap; margin-bottom: 16px; }
.search-box { flex: 1; min-width: 200px; display: flex; align-items: center; gap: 8px; padding: 8px 12px; border: 1px solid #bfc9c3; border-radius: 8px; background: #fff; input { flex: 1; border: none; outline: none; font-size: 13px; } svg { color: #404944; } &:focus-within { border-color: #003527; } }
.sel { padding: 8px 10px; border: 1px solid #bfc9c3; border-radius: 8px; font-size: 12px; background: #fff; outline: none; }
.count { font-size: 13px; color: #404944; white-space: nowrap; }

.table { background: #fff; border-radius: 12px; border: 1px solid #bfc9c3; overflow: hidden; }
.th, .tr { display: flex; align-items: center; padding: 12px 16px; font-size: 13px; }
.th { background: #f8f9fa; font-weight: 600; color: #404944; border-bottom: 1px solid #bfc9c3; }
.tr { border-bottom: 1px solid #f0f0f0; color: #404944; transition: background 0.2s; &:hover { background: #f8f9fa; } &:last-child { border-bottom: none; } &.rejected { opacity: 0.55; } }
.c-name { flex: 2; strong { color: #121c28; } }
.c-info { flex: 1.5; }
.c-contact { flex: 1.8; }
.c-status { flex: 1; }
.c-date { flex: 1; display: flex; align-items: center; gap: 4px; font-size: 12px; color: #bfc9c3; }
.c-act { flex: 1.5; display: flex; justify-content: flex-end; }

.info-text, .contact-text { font-size: 12px; color: #404944; }
.contact-text { font-size: 12px; }

.status-tag { font-size: 11px; padding: 2px 10px; border-radius: 4px; font-weight: 600; white-space: nowrap; &.pending { background: #fff3cd; color: #856404; } &.approved { background: #d4edda; color: #155724; } &.rejected { background: #f8d7da; color: #721c24; } }

.act-btns { display: flex; gap: 6px; }
.approve-btn, .reject-btn { display: inline-flex; align-items: center; gap: 3px; padding: 4px 12px; border-radius: 6px; font-size: 12px; font-weight: 600; cursor: pointer; transition: all 0.2s; }
.approve-btn { background: #198754; color: #fff; border: none; &:hover { background: #157347; } }
.reject-btn { background: #fff; color: #dc3545; border: 1px solid #dc3545; &:hover { background: #dc3545; color: #fff; } }
.act-done { font-size: 12px; color: #bfc9c3; &.muted { opacity: 0.7; } }

.pagination-wrap { display: flex; justify-content: center; margin-top: 16px; }

@media (max-width: 768px) { .table { overflow-x: auto; } .th, .tr { min-width: 800px; } }
</style>
