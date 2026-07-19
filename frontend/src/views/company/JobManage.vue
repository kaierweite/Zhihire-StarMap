<script setup lang="ts">
import { ref, computed, onMounted } from "vue"
import { useRouter } from "vue-router"
import { ElMessage, ElMessageBox } from "element-plus"
import { Plus, Edit, Delete, Search, Clock, MapPin, Network, MoreHorizontal, FileText } from "lucide-vue-next"
import { listJobs, deleteJob, updateJob, getJobDetail, type JobItem, type JobStatus, type UpdateJobForm } from "@/api/job"
import { getCompanyProfile } from "@/api/company"

const router = useRouter()

// 数据
const jobs = ref<JobItem[]>([])
const loading = ref(false)
const companyId = ref<number | null>(null)

// ====== 统计 ======
const stats = ref({ total: 0, open: 0, closed: 0, draft: 0 })
const searchKw = ref('')
const filteredJobs = computed(() => {
  if (!searchKw.value.trim()) return jobs.value
  const kw = searchKw.value.trim().toLowerCase()
  return jobs.value.filter(j => j.title.toLowerCase().includes(kw))
})

// ====== 编辑弹窗 ======
const editDialog = ref(false)
const editingJob = ref<JobItem | null>(null)
const editForm = ref<UpdateJobForm>({})
const editSaving = ref(false)

// ====== 初始化 ======
async function loadData() {
  loading.value = true
  try {
    const profileRes = await getCompanyProfile()
    if (profileRes.data.code !== 200 || !profileRes.data.data) {
      ElMessage.error("获取企业信息失败")
      return
    }
    companyId.value = profileRes.data.data.id

    const jobsRes = await listJobs({ company_id: companyId.value, status: "ALL", size: 100 })
    if (jobsRes.data.code === 200 && jobsRes.data.data) {
      const records = jobsRes.data.data.records || []
      jobs.value = records
      stats.value = {
        total: records.length,
        open: records.filter((j: JobItem) => j.status === "OPEN").length,
        closed: records.filter((j: JobItem) => j.status === "CLOSED").length,
        draft: records.filter((j: JobItem) => j.status === "DRAFT").length,
      }
    }
  } catch {
    ElMessage.error("加载岗位列表失败")
  } finally {
    loading.value = false
  }
}

// ====== 操作菜单 ======
function handleAction(cmd: string, job: JobItem) {
  switch (cmd) {
    case "detail":
      router.push('/company/jobs/detail/' + job.id)
      break
    case "graph":
      router.push('/company/jobs/ability-map/' + job.id)
      break
    case "edit":
      openEdit(job)
      break
    case "delete":
      handleDelete(job)
      break
  }
}

// ====== 删除 ======
async function handleDelete(job: JobItem) {
  try {
    await ElMessageBox.confirm(
      `确定要删除岗位「${job.title}」吗？删除后不可恢复。`,
      "确认删除",
      { confirmButtonText: "删除", cancelButtonText: "取消", type: "warning" }
    )
    const res = await deleteJob(job.id)
    if (res.data.code === 200) {
      ElMessage.success("已删除")
      await loadData()
    } else {
      ElMessage.error(res.data.message || "删除失败")
    }
  } catch {
    // 取消或失败
  }
}

// ====== 编辑 ======
async function openEdit(job: JobItem) {
  editingJob.value = job
  editForm.value = {
    title: job.title,
    city: job.city,
    status: job.status,
    salary_min: job.salary_min ? Math.round(job.salary_min / 1000) : null,
    salary_max: job.salary_max ? Math.round(job.salary_max / 1000) : null,
    job_type: job.job_type,
  }
  editDialog.value = true
}

async function handleEditSave() {
  if (!editingJob.value) return
  editSaving.value = true
  try {
    const payload = {
      ...editForm.value,
      salary_min: editForm.value.salary_min ? editForm.value.salary_min * 1000 : null,
      salary_max: editForm.value.salary_max ? editForm.value.salary_max * 1000 : null,
    }
    const res = await updateJob(editingJob.value.id, payload)
    if (res.data.code === 200) {
      ElMessage.success("更新成功")
      editDialog.value = false
      await loadData()
    } else {
      ElMessage.error(res.data.message || "更新失败")
    }
  } catch {
    ElMessage.error("网络异常")
  } finally {
    editSaving.value = false
  }
}

// ====== 快速切换状态 ======
async function toggleStatus(job: JobItem) {
  const newStatus: JobStatus = job.status === "OPEN" ? "CLOSED" : "OPEN"
  try {
    const res = await updateJob(job.id, { status: newStatus })
    if (res.data.code === 200) {
      ElMessage.success(newStatus === "OPEN" ? "已开启" : "已关闭")
      await loadData()
    }
  } catch {
    ElMessage.error("操作失败")
  }
}

// ====== 工具 ======
function formatSalary(min: number | null, max: number | null): string {
  const minK = min && min > 0 ? Math.round(min / 1000) : null
  const maxK = max && max > 0 ? Math.round(max / 1000) : null
  
  if (minK != null && maxK != null) {
    if (minK === maxK) return `${minK}K`
    return `${minK}K-${maxK}K`
  }
  if (minK != null) return `${minK}K起`
  if (maxK != null) return `至${maxK}K`
  return "面议"
}

const statusLabels: Record<string, string> = {
  OPEN: "招聘中",
  CLOSED: "已关闭",
  DRAFT: "草稿",
}
const statusType: Record<string, string> = {
  OPEN: "success",
  CLOSED: "info",
  DRAFT: "warning",
}
const jobTypeLabels: Record<string, string> = {
  FULL_TIME: "全职",
  PART_TIME: "兼职",
  INTERN: "实习",
}

onMounted(loadData)
</script>

<template>
  <div class="page">
    <!-- 头部 -->
    <div class="page-header fade-up">
      <div class="header-left">
        <h1>岗位管理</h1>
        <span class="total-badge">{{ stats.total }} 个岗位</span>
      </div>
      <el-button type="primary" size="large" @click="router.push('/company/jobs/publish')">
        <Plus :size="16" style="margin-right:4px" /> 发布岗位
      </el-button>
    </div>

    <!-- 统计卡片 -->
    <div class="stats-row fade-up d1">
      <div class="mini-stat"><span class="ms-num">{{ stats.total }}</span><span class="ms-lbl">全部</span></div>
      <div class="mini-stat open"><span class="ms-num">{{ stats.open }}</span><span class="ms-lbl">招聘中</span></div>
      <div class="mini-stat closed"><span class="ms-num">{{ stats.closed }}</span><span class="ms-lbl">已关闭</span></div>
      <div class="mini-stat draft"><span class="ms-num">{{ stats.draft }}</span><span class="ms-lbl">草稿</span></div>
    </div>

    <!-- 搜索栏 -->
    <div class="toolbar fade-up d2">
      <Search :size="16" />
      <input v-model="searchKw" placeholder="搜索岗位名称..." class="toolbar-search" />
    </div>

    <!-- 表格 -->
    <div class="table-wrap fade-up d3">
      <div v-if="loading" class="loading-hint">加载中...</div>

      <el-table v-else :data="filteredJobs" stripe style="width: 100%" empty-text="暂无岗位数据">
        <el-table-column label="岗位名称" min-width="180">
          <template #default="{ row }: { row: JobItem }">
            <span class="job-title">{{ row.title }}</span>
          </template>
        </el-table-column>
        <el-table-column label="城市" width="80">
          <template #default="{ row }: { row: JobItem }">
            <span v-if="row.city"><MapPin :size="13" /> {{ row.city }}</span>
            <span v-else class="muted">不限</span>
          </template>
        </el-table-column>
        <el-table-column label="类型" width="80">
          <template #default="{ row }: { row: JobItem }">
            {{ jobTypeLabels[row.job_type] || row.job_type }}
          </template>
        </el-table-column>
        <el-table-column label="薪资" width="120">
          <template #default="{ row }: { row: JobItem }">
            {{ formatSalary(row.salary_min, row.salary_max) }}
          </template>
        </el-table-column>
        <el-table-column label="状态" width="100">
          <template #default="{ row }: { row: JobItem }">
            <el-tag :type="statusType[row.status] || 'info'" size="small" style="cursor:pointer" @click="toggleStatus(row)">
              {{ statusLabels[row.status] || row.status }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="views" label="浏览" width="70" />
        <el-table-column label="创建时间" width="110">
          <template #default="{ row }: { row: JobItem }">
            <span class="time-cell">{{ (row.created_at || "").slice(0, 10) }}</span>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="140">
          <template #default="{ row }: { row: JobItem }">
            <el-dropdown trigger="click" @command="(cmd: string) => handleAction(cmd, row)">
              <el-button type="primary" size="small" plain>
                <MoreHorizontal :size="14" style="margin-right:4px" /> 操作
              </el-button>
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item command="detail"><FileText :size="14" style="margin-right:6px" /> 详情</el-dropdown-item>
                  <el-dropdown-item command="graph"><Network :size="14" style="margin-right:6px" /> 能力图谱</el-dropdown-item>
                  <el-dropdown-item command="edit"><Edit :size="14" style="margin-right:6px" /> 编辑</el-dropdown-item>
                  <el-dropdown-item command="delete" divided><Delete :size="14" style="margin-right:6px" /> 删除</el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <!-- 编辑弹窗 -->
    <el-dialog v-model="editDialog" title="编辑岗位" width="500px" :close-on-click-modal="false">
      <el-form v-if="editingJob" :model="editForm" label-width="100px">
        <el-form-item label="岗位名称">
          <el-input v-model="editForm.title" />
        </el-form-item>
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="城市">
              <el-input v-model="editForm.city" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="工作类型">
              <el-select v-model="editForm.job_type" style="width:100%">
                <el-option label="全职" value="FULL_TIME" />
                <el-option label="兼职" value="PART_TIME" />
                <el-option label="实习" value="INTERN" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="最低薪资">
              <el-input-number v-model="editForm.salary_min" :min="0" :max="200" style="width:100%" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="最高薪资">
              <el-input-number v-model="editForm.salary_max" :min="0" :max="200" style="width:100%" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="状态">
          <el-select v-model="editForm.status" style="width:100%">
            <el-option label="招聘中" value="OPEN" />
            <el-option label="已关闭" value="CLOSED" />
            <el-option label="草稿" value="DRAFT" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="editDialog = false">取消</el-button>
        <el-button type="primary" :loading="editSaving" @click="handleEditSave">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<style scoped lang="scss">
.page { max-width: 1100px; margin: 0 auto; }

@keyframes fadeUp {
  from { opacity: 0; transform: translateY(16px); }
  to { opacity: 1; transform: translateY(0); }
}
.fade-up { opacity: 0; animation: fadeUp 0.4s cubic-bezier(0.22,1,0.36,1) forwards; }
.d1 { animation-delay: 0.06s; } .d2 { animation-delay: 0.12s; } .d3 { animation-delay: 0.18s; }

.page-header {
  display: flex; align-items: center; justify-content: space-between; margin-bottom: 20px;
}
.header-left { display: flex; align-items: center; gap: 12px; }
h1 { font-size: 28px; font-weight: 700; color: #121c28; margin: 0; }
.total-badge {
  font-size: 13px; color: #404944; background: #f3f4f5; padding: 4px 12px; border-radius: 999px;
}

.stats-row {
  display: flex; gap: 12px; margin-bottom: 18px;
}
.mini-stat {
  flex: 1; background: #fff; border-radius: 10px; padding: 14px 16px;
  border: 1px solid #bfc9c3; display: flex; flex-direction: column; gap: 2px;
  &.open { border-left: 3px solid #27ae60; }
  &.closed { border-left: 3px solid #404944; }
  &.draft { border-left: 3px solid #e6a23c; }
}
.ms-num { font-size: 22px; font-weight: 700; color: #121c28; }
.ms-lbl { font-size: 12px; color: #404944; }

.toolbar {
  display: flex; align-items: center; gap: 8px;
  padding: 8px 14px; background: #fff; border-radius: 10px;
  border: 1px solid #bfc9c3; margin-bottom: 16px;
  svg { color: #404944; }
}
.toolbar-search {
  flex: 1; border: none; outline: none; font-size: 13px; background: none;
}

.table-wrap { background: #fff; border-radius: 12px; border: 1px solid #bfc9c3; overflow: auto; }
.loading-hint { text-align: center; padding: 60px; color: #404944; font-size: 14px; }

.job-title { font-weight: 500; color: #121c28; }
.muted { color: #bfc9c3; font-style: italic; }

.time-cell { font-family: "SF Mono", "Fira Code", Consolas, monospace; font-size: 12px; color: #404944; }
.actions { display: flex; gap: 4px; }
</style>
