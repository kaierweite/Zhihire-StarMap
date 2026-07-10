<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Search, Ban } from 'lucide-vue-next'
import { listUsers, updateUserStatus } from '@/api/admin'
import type { UserAdminItem } from '@/types/admin'

const keyword = ref('')
const filterRole = ref('')
const users = ref<UserAdminItem[]>([])
const page = ref(1)
const size = ref(20)
const total = ref(0)
const loading = ref(false)

async function fetchUsers() {
  loading.value = true
  try {
    const res = await listUsers(keyword.value || undefined, filterRole.value || undefined, page.value, size.value)
    const data = res.data.data
    users.value = data.records
    total.value = data.total
  } catch {
    // Error handled by request interceptor
  } finally {
    loading.value = false
  }
}

function onSearch() {
  page.value = 1
  fetchUsers()
}

async function toggleBan(u: UserAdminItem) {
  if (u.role === 'ADMIN') { ElMessage.warning('不能封禁管理员'); return }
  const targetStatus = u.status === 'NORMAL' ? 'BANNED' : 'NORMAL'
  const action = targetStatus === 'BANNED' ? '封禁' : '解封'
  try {
    await ElMessageBox.confirm(`确认${action}用户「${u.username}」？`, `${action}确认`, { type: 'warning' })
    await updateUserStatus(u.id, targetStatus)
    ElMessage.success(`已${action}「${u.username}」`)
    await fetchUsers()
  } catch { /* cancelled */ }
}

function roleLabel(r: string) {
  return r === 'USER' ? '求职者' : r === 'COMPANY' ? '企业' : '管理员'
}

onMounted(() => { onSearch() })
</script>

<template>
  <div class="page">
    <h1 class="page-title fade-up">用户管理</h1>
    <p class="page-desc fade-up d1">管理平台用户，支持搜索、筛选和封禁操作</p>

    <div class="filter-bar fade-up d2">
      <div class="search-box"><Search :size="16" /><input v-model="keyword" placeholder="搜索用户名 / 邮箱..." @keyup.enter="onSearch" /></div>
      <select v-model="filterRole" class="sel" @change="onSearch"><option value="">全部角色</option><option value="USER">求职者</option><option value="COMPANY">企业</option><option value="ADMIN">管理员</option></select>
      <span class="count">共<strong>{{ total }}</strong> 个用户</span>
    </div>

    <div class="table fade-up d3">
      <div class="th"><span class="c-name">用户名</span><span class="c-role">角色</span><span class="c-email">邮箱</span><span class="c-status">状态</span><span class="c-date">注册日期</span><span class="c-act">操作</span></div>
      <div v-for="u in users" :key="u.id" class="tr" :class="{ banned: u.status === 'BANNED' }">
        <span class="c-name"><strong>{{ u.username }}</strong></span>
        <span class="c-role"><span class="role-badge" :class="u.role.toLowerCase()">{{ roleLabel(u.role) }}</span></span>
        <span class="c-email">{{ u.email }}</span>
        <span class="c-status"><span class="status-dot" :class="u.status.toLowerCase()" />{{ u.status === 'NORMAL' ? '正常' : '已封禁' }}</span>
        <span class="c-date">{{ u.created_at }}</span>
        <span class="c-act"><button v-if="u.role !== 'ADMIN'" class="ban-btn" :class="u.status === 'BANNED' ? 'unban' : ''" @click="toggleBan(u)"><Ban :size="13" /> {{ u.status === 'NORMAL' ? '封禁' : '解封' }}</button></span>
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
        @current-change="fetchUsers"
        @size-change="fetchUsers"
      />
    </div>
  </div>
</template>

<style scoped lang="scss">
.page { max-width: 1000px; margin: 0 auto; }
@keyframes fadeUp { from { opacity: 0; transform: translateY(20px); } to { opacity: 1; transform: translateY(0); } }
.fade-up { opacity: 0; animation: fadeUp 0.5s cubic-bezier(0.22,1,0.36,1) forwards; }
.d1 { animation-delay: 0.08s; } .d2 { animation-delay: 0.15s; } .d3 { animation-delay: 0.22s; }
.page-title { font-size: 28px; font-weight: 700; color: #303133; margin-bottom: 4px; }
.page-desc { font-size: 14px; color: #909399; margin-bottom: 20px; }

.filter-bar { display: flex; gap: 8px; align-items: center; flex-wrap: wrap; margin-bottom: 16px; }
.search-box { flex: 1; min-width: 200px; display: flex; align-items: center; gap: 8px; padding: 8px 12px; border: 1px solid #dcdfe6; border-radius: 8px; background: #fff; input { flex: 1; border: none; outline: none; font-size: 13px; } svg { color: #909399; } &:focus-within { border-color: #1a3a5c; } }
.sel { padding: 8px 10px; border: 1px solid #dcdfe6; border-radius: 8px; font-size: 12px; background: #fff; outline: none; }
.count { font-size: 13px; color: #909399; margin-left: auto; }

.table { background: #fff; border-radius: 12px; border: 1px solid #e5e7eb; overflow: hidden; }
.th, .tr { display: flex; align-items: center; padding: 12px 16px; font-size: 13px; }
.th { background: #f8f9fa; font-weight: 600; color: #909399; border-bottom: 1px solid #e5e7eb; }
.tr { border-bottom: 1px solid #f0f0f0; color: #606266; transition: background 0.2s; &:hover { background: #f8f9fa; } &:last-child { border-bottom: none; } &.banned { opacity: 0.6; } }
.c-name { flex: 1.2; strong { color: #303133; } }
.c-role { flex: 1; }
.c-email { flex: 1.5; }
.c-status { flex: 1; display: flex; align-items: center; gap: 6px; }
.c-date { flex: 1; color: #c0c4cc; font-size: 12px; }
.c-act { flex: 1; }

.role-badge { font-size: 11px; padding: 2px 10px; border-radius: 4px; font-weight: 600; &.user { background: #dbeafe; color: #1e3a8a; } &.company { background: #e8d5f5; color: #6a1b9a; } &.admin { background: #fff3cd; color: #856404; } }
.status-dot { width: 8px; height: 8px; border-radius: 50%; &.normal { background: #198754; } &.banned { background: #dc3545; } }
.ban-btn { display: inline-flex; align-items: center; gap: 3px; padding: 4px 12px; border-radius: 6px; font-size: 12px; font-weight: 600; cursor: pointer; transition: all 0.2s; background: #fff; border: 1px solid #dc3545; color: #dc3545; &:hover { background: #dc3545; color: #fff; } &.unban { border-color: #198754; color: #198754; &:hover { background: #198754; color: #fff; } } }

.pagination-wrap { display: flex; justify-content: center; margin-top: 16px; }

@media (max-width: 768px) { .table { overflow-x: auto; } .th, .tr { min-width: 700px; } }
</style>
