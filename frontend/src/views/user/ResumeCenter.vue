
<script setup lang="ts">
import { ref, reactive, onMounted, onUnmounted, h } from "vue"
import { ElMessage, ElMessageBox } from "element-plus"
import { Upload, FileText, RefreshCw, Edit, Trash2, Plus, X,
        ArrowRight, Save, File, ChevronRight, Sparkles, UserCheck } from "lucide-vue-next"
import { uploadResume, listResumes, getResumeDetail,
        updateResume, deleteResume, getParseTaskStatus, getParseTaskByResume, syncToProfile } from "@/api/resume"
import type { ResumeListItem, ResumeDetail as ResumeDetailType } from "@/api/resume"
import AbilityMapSection from "./AbilityMapSection.vue"

type ViewMode = "list" | "detail" | "error"
const view = ref<ViewMode>("list")
const selectedResumeId = ref<number | null>(null)
const resumeTitle = ref("")


// === Non-blocking parse task polling ===
// Maps resume_id -> TaskStatus (WAITING/PARSING/SUCCESS/FAILED)
const taskPollMap = reactive<Record<number, { status: string; taskId: number }>>({})
// Maps resume_id -> set to true once we've notified the user
const notifiedSet = reactive<Record<number, boolean>>({})
let backgroundPollTimer: ReturnType<typeof setInterval> | null = null
// Keep error state for inline display only
const errorMsg = ref("")

const listLoading = ref(false)
const detailLoading = ref(false)
const saving = ref(false)
const deleting = ref(false)
const syncing = ref(false)
const resumeList = ref<ResumeListItem[]>([])
const totalCount = ref(0)
const currentPage = ref(1)
const pageSize = ref(20)

interface ParsedData {
  name: string; education: string; years: string | number
  targetJob: string; city: string; skills: string[]
  experience: { title: string; company: string; period: string; description: string }[]
}
const parsedData = reactive<ParsedData>({
  name: "", education: "", years: "", targetJob: "", city: "",
  skills: [], experience: [],
})
const editInfo = ref(false); const editSkills = ref(false)
const editExp = ref(false); const newSkill = ref("")
const editingExpIdx = ref(-1); const hasChanges = ref(false)
const fileInputRef = ref<HTMLInputElement | null>(null)

onMounted(() => loadList())
onUnmounted(() => {
  if (backgroundPollTimer) { clearInterval(backgroundPollTimer); backgroundPollTimer = null }
})

async function loadList() {
  listLoading.value = true
  try {
    const resp = await listResumes(currentPage.value, pageSize.value)
    const r = resp.data.data
    resumeList.value = r.records; totalCount.value = r.total
  } catch {} finally { listLoading.value = false }
}

function onPageChange(page: number) {
  currentPage.value = page
  loadList()
}

function formatDate(d: string | null) { return d ? d.slice(0, 10) : "" }

async function handleSync() {
  if (!selectedResumeId.value) return
  await handleSyncWithId(selectedResumeId.value)
}

const ALLOWED_TYPES = [
  "application/pdf",
  "application/msword",
  "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
]
const MAX_SIZE = 10 * 1024 * 1024

function handleFileChange(e: Event) {
  const input = e.target as HTMLInputElement; const file = input.files?.[0]
  if (!file) return; const err = validateFile(file)
  if (err) { ElMessage.error(err); input.value = ""; return }
  doUpload(file); input.value = ""
}

function handleDrop(e: DragEvent) {
  e.preventDefault(); const file = e.dataTransfer?.files[0]
  if (!file) return; const err = validateFile(file)
  if (err) { ElMessage.error(err); return }
  doUpload(file)
}

function validateFile(f: File): string | null {
  if (!ALLOWED_TYPES.includes(f.type)) return "仅支持 PDF/DOC/DOCX 格式"
  if (f.size > MAX_SIZE) return "文件大小不能超过 10MB"
  return null
}

async function doUpload(file: File) {
  let resumeId: number, taskId: number
  try {
    const resp = await uploadResume(file, file.name.replace(/\.[a-z]+$/i, ""))
    const d = resp.data.data; resumeId = d.resume_id
    taskId = d.task_id; resumeTitle.value = d.title
  } catch {
    ElMessage.error("上传失败，请重试")
    return
  }
  selectedResumeId.value = resumeId

  // Mark task for background polling
  taskPollMap[resumeId] = { status: "WAITING", taskId }
  notifiedSet[resumeId] = false
  startBackgroundPolling()

  // Immediately return to list view
  ElMessage.success("简历上传成功，正在后台解析...")
  view.value = "list"
  await loadList()
}

function startBackgroundPolling() {
  if (backgroundPollTimer) return
  backgroundPollTimer = setInterval(async () => {
    for (const [resumeIdStr, taskInfo] of Object.entries(taskPollMap)) {
      const rid = Number(resumeIdStr)
      if (taskInfo.status === "SUCCESS" || taskInfo.status === "FAILED") continue

      try {
        const resp = await getParseTaskByResume(rid)
        const st = resp.data.data
        taskPollMap[rid] = { status: st.status, taskId: st.task_id }

        if (st.status === "SUCCESS") {
          if (notifiedSet[rid]) continue
          notifiedSet[rid] = true
          showParseCompleteToast(rid)
        } else if (st.status === "FAILED") {
          if (notifiedSet[rid]) continue
          notifiedSet[rid] = true
          ElMessage.error("简历解析失败，请重新上传")
        }
      } catch { /* retry */ }
    }
    // Clean up completed tasks from map after a delay
    for (const [ridStr, taskInfo] of Object.entries(taskPollMap)) {
      if (taskInfo.status === "SUCCESS" || taskInfo.status === "FAILED") {
        // Keep in map for status badges, but we can stop polling after all are done
      }
    }
  }, 3000)
}


function showParseCompleteToast(resumeId: number) {
  const taskInfo = taskPollMap[resumeId]
  if (!taskInfo) return
  ElMessage({
    message: h("div", { style: "display: flex; flex-direction: column; gap: 8px;" }, [
      h("div", { style: "font-weight: 600; font-size: 14px;" }, "简历解析完成！"),
      h("div", { style: "display: flex; gap: 12px; margin-top: 4px;" }, [
        h("span", { style: "cursor:pointer;padding:4px 12px;background:#003527;color:#fff;border-radius:6px;font-size:12px;", onClick: () => openDetail(resumeId) }, "查看详情"),
        h("span", { style: "cursor:pointer;padding:4px 12px;background:#059669;color:#fff;border-radius:6px;font-size:12px;", onClick: () => { handleSyncWithId(resumeId); } }, "同步"),
        h("span", { style: "cursor:pointer;padding:4px 12px;background:#064e3b;color:#fff;border-radius:6px;font-size:12px;", onClick: () => { window.open("/user/resume/optimize?resume_id=" + resumeId, "_self"); } }, "AI 优化"),
      ]),
    ]),
    duration: 10000,
    showClose: true,
  })
}

async function handleSyncWithId(resumeId: number) {
  try {
    const resp = await syncToProfile(resumeId)
    const result = resp.data.data
    if (result?.synced_to_profile) {
      ElMessage.success("已同步到个人中心：" + (result.synced_fields?.join("、") || ""))
    } else {
      ElMessage.info("个人中心数据已是最新，无需同步")
    }
  } catch {
    ElMessage.error("同步失败，请稍后重试")
  }
}
async function openDetail(id: number) {
  selectedResumeId.value = id
  view.value = "detail"
  await loadDetail(id)
}

async function loadDetail(id: number) {
  try {
    const resp = await getResumeDetail(id)
    renderDetail(resp.data.data); view.value = "detail"
  } catch {
    view.value = "error"; errorMsg.value = "加载失败"
  }
}

function extractParsed(content_text: string | null): Record<string, any> | null {
  if (!content_text) return null
  try {
    const obj = JSON.parse(content_text)
    let raw: Record<string, any> = obj
    if (obj.raw_response && typeof obj.raw_response === "string") {
      const m = obj.raw_response.match(/\`\`\`(?:json)?\s*([\s\S]*?)\`\`\`/)
      if (m) raw = JSON.parse(m[1].trim())
      else return null
    }
    const norm: Record<string, any> = { ...raw }
    if (norm.workYears && !norm.years) norm.years = norm.workYears
    if (norm.work_years && !norm.years) norm.years = norm.work_years
    if (norm.education && typeof norm.education === "object") {
      norm.education = norm.education.degree || norm.education.school || JSON.stringify(norm.education)
    }
    if (norm.experience && Array.isArray(norm.experience)) {
      norm.experience = norm.experience.map((e: any) => ({
        title: e.title || e.position || "",
        company: e.company || "",
        period: e.period || e.date || e.duration || "",
        description: Array.isArray(e.description)
          ? e.description.join("\n")
          : (e.description || e.desc || e.summary || ""),
      }))
    }
    return norm
  } catch {}
  return null
}

function renderDetail(d: ResumeDetailType) {
  resumeTitle.value = d.title ?? ""
  const p = d.parsed || extractParsed(d.content_text); if (!p) return
  parsedData.name = p.name ?? ""
  parsedData.education = p.education ?? ""
  parsedData.years = p.years ?? (p.years === 0 ? 0 : "")
  parsedData.targetJob = p.targetJob ?? ""
  parsedData.city = p.city ?? ""
  parsedData.skills = Array.isArray(p.skills)
    ? p.skills.map((s: any) => typeof s === "string" ? s : (s.name ?? "")).filter(Boolean)
    : []
  parsedData.experience = Array.isArray(p.experience)
    ? p.experience.map((e: any) => ({
        title: e.title ?? "", company: e.company ?? "",
        period: e.period ?? "", description: e.description ?? "",
      }))
    : []
  hasChanges.value = false; editInfo.value = false; editSkills.value = false
  editExp.value = false; editingExpIdx.value = -1
}

async function saveAll() {
  if (!selectedResumeId.value) return; saving.value = true
  try {
    await updateResume(selectedResumeId.value, {
      content_text: JSON.stringify({
        name: parsedData.name, education: parsedData.education,
        years: parsedData.years, targetJob: parsedData.targetJob,
        city: parsedData.city, skills: parsedData.skills.map(n => ({ name: n })),
        experience: parsedData.experience.map(e => ({
          company: e.company, title: e.title,
          period: e.period, description: e.description,
        })),
      }),
    })
    hasChanges.value = false; editInfo.value = false; editSkills.value = false
    editExp.value = false; editingExpIdx.value = -1
    ElMessage.success("保存成功")
  } catch {} finally { saving.value = false }
}

async function handleDelete(id: number) {
  try {
    await ElMessageBox.confirm("确定要删除这份简历吗？", "确认", {
      confirmButtonText: "删除", cancelButtonText: "取消", type: "warning",
    })
  } catch { return }
  deleting.value = true
  try {
    await deleteResume(id); ElMessage.success("删除成功")
    if (selectedResumeId.value === id) backToList()
    await loadList()
  } catch {} finally { deleting.value = false }
}

function showUpload() { triggerFileInput() }
function backToList() {
  view.value = "list"; selectedResumeId.value = null; errorMsg.value = ""
  hasChanges.value = false; editInfo.value = false; editSkills.value = false; editExp.value = false
  loadList()
}
function retryUpload() { showUpload() }
function triggerFileInput() { fileInputRef.value?.click() }

function removeSkill(i: number) { parsedData.skills.splice(i, 1); hasChanges.value = true }
function addSkill() {
  const v = newSkill.value.trim()
  if (v && !parsedData.skills.includes(v)) { parsedData.skills.push(v); hasChanges.value = true }
  newSkill.value = ""
}
function deleteExp(i: number) {
  parsedData.experience.splice(i, 1); hasChanges.value = true
  if (editingExpIdx.value === i) editingExpIdx.value = -1
}
function addExp() {
  parsedData.experience.push({ title: "New", company: "公司", period: "-", description: "" })
  editingExpIdx.value = parsedData.experience.length - 1; editExp.value = true; hasChanges.value = true
}

function getTaskStatusClass(status: string): string {
  switch (status) {
    case "WAITING": return "waiting"
    case "PARSING": return "parsing"
    case "SUCCESS": return "success"
    case "FAILED": return "failed"
    default: return "normal"
  }
}

function getTaskStatusText(status: string): string {
  switch (status) {
    case "WAITING": return "等待解析"
    case "PARSING": return "解析中"
    case "SUCCESS": return "已解析"
    case "FAILED": return "解析失败"
    default: return status
  }
}

const CHIPS = ["chip-primary","chip-success","chip-neutral","chip-warning","chip-purple"]
function displayYears(y: string | number): string {
  if (y === "" || y == null) return "未填写"
  const n = Number(y); return Number.isNaN(n) ? String(y) : n + " 年"
}
</script>
<template>
  <div class="resume-page"><div class="resume-container">
    <template v-if="view === 'list'">
      <div class="header-row">
          <h1 class="page-title">简历中心</h1>
        </div>

        <!-- Upload Strip / File Strip -->
        <div v-if="!resumeList.length" class="upload-strip" @dragover.prevent @drop="handleDrop">
          <div class="strip-body">
            <div class="strip-left">
              <Upload :size="22" class="strip-icon" />
              <div class="strip-text">
                <span class="strip-title">拖拽简历文件到此处</span>
                <span class="strip-hint">支持 PDF / DOC / DOCX · 最大 10MB</span>
              </div>
            </div>
            <div class="strip-right">
              <button class="strip-btn" type="button" @click="triggerFileInput">
                <Upload :size="15" /> 选择文件
              </button>
            </div>
          </div>
          <input ref="fileInputRef" type="file" accept=".pdf,.doc,.docx" @change="handleFileChange" hidden />
        </div>

        <div v-else class="file-strip" @dragover.prevent @drop="handleDrop">
          <div class="file-strip-inner">
            <div class="file-strip-items">
              <div
                v-for="item in resumeList"
                :key="item.id"
                class="file-strip-item"
                @click="openDetail(item.id)"
                :title="item.title || item.file_name || ''"
              >
                <FileText :size="16" class="file-strip-icon" />
                <span class="file-strip-name">{{ item.title || item.file_name || '未命名' }}</span>
              </div>
            </div>
            <button class="file-strip-add" type="button" @click="triggerFileInput" title="继续上传">
              <Plus :size="18" />
            </button>
          </div>
          <div class="file-strip-footer">
            <span class="file-strip-count">共 {{ totalCount }} 份简历</span>
            <span class="file-strip-hint">点击简历查看详情</span>
          </div>
          <input ref="fileInputRef" type="file" accept=".pdf,.doc,.docx" @change="handleFileChange" hidden />
        </div>

        <AbilityMapSection />
      <div v-if="listLoading && !resumeList.length" class="loading-hint"><RefreshCw :size="18" class="spinning" /> 加载中...</div>
      <div v-else-if="!resumeList.length" class="empty-state"><File :size="48" class="empty-icon" /><p>暂无简历，上传你的第一份简历开始吧</p></div>
      <div v-else class="resume-list">
        <div v-for="item in resumeList" :key="item.id" class="resume-card" @click="openDetail(item.id)">
          <div class="card-left"><FileText :size="28" class="card-icon" />
            <div class="card-meta"><span class="card-title">{{ item.title || item.file_name || '未命名' }}</span><span class="card-date">{{ formatDate(item.updated_at || item.created_at) }}</span></div>
          </div>
          <div class="card-right">
            <span v-if="taskPollMap[item.id]" class="card-status" :class="getTaskStatusClass(taskPollMap[item.id]?.status ?? item.status)">{{ getTaskStatusText(taskPollMap[item.id]?.status ?? item.status) }}</span>
            <span v-else class="card-status" :class="item.status.toLowerCase()">{{ item.status }}</span>
            <button class="card-delete" :disabled="deleting" @click.stop="handleDelete(item.id)"><Trash2 :size="14" /></button>
          </div>
        </div>
    </div>

      <div v-if="totalCount > pageSize" class="pagination-wrap">
        <el-pagination
          v-model:current-page="currentPage"
          :page-size="pageSize"
          :total="totalCount"
          layout="prev, pager, next"
          @current-change="onPageChange"
          small
        />
      </div>
    </template>



    <div v-if="errorMsg" class="error-card">
      <p class="error-msg">{{ errorMsg }}</p>
      <div class="error-actions">
        <button class="retry-btn" @click="retryUpload"><RefreshCw :size="14" /> 重新上传</button>
        <button class="back-btn" @click="errorMsg = ''">取消</button>
      </div>
    </div>

    <div v-if="view === 'detail'" class="detail-view">
      <div class="detail-nav">
        <button class="back-link" @click="backToList"><ChevronRight :size="14" class="rotate-180" /> 简历列表</button>
        <span class="nav-sep">/</span><span class="nav-current">{{ resumeTitle || '简历详情' }}</span>
      </div>
      <div class="result-actions">
        <div class="action-left">
          <button class="action-btn" @click="showUpload"><Upload :size="14" /> 上传简历</button>
          <button class="action-btn danger" :disabled="deleting" @click="handleDelete(selectedResumeId!)"><Trash2 :size="14" /> 删除</button>
        </div>
        <div class="action-right">
          <button class="sync-btn" :disabled="syncing" @click="handleSync"><UserCheck :size="14" /> {{ syncing ? '同步中...' : '同步到个人中心' }}</button>
          <button v-if="hasChanges" class="save-btn" :disabled="saving" @click="saveAll"><Save :size="14" /> {{ saving ? '保存中...' : '保存修改' }}</button>
        </div>
      </div>

      <section class="result-section">
        <div class="section-head"><h2>基本信息</h2><button class="edit-toggle" @click="editInfo = !editInfo"><component :is="editInfo ? X : Edit" :size="14" /></button></div>
        <div v-if="!editInfo" class="info-grid">
          <div class="info-item"><span class="info-label">姓名</span><span class="info-value">{{ parsedData.name || '未填写' }}</span></div>
          <div class="info-item"><span class="info-label">学历</span><span class="info-value">{{ parsedData.education || '未填写' }}</span></div>
          <div class="info-item"><span class="info-label">工作年限</span><span class="info-value">{{ displayYears(parsedData.years) }}</span></div>
          <div class="info-item"><span class="info-label">目标职位</span><span class="info-value">{{ parsedData.targetJob || '未填写' }}</span></div>
          <div class="info-item"><span class="info-label">城市</span><span class="info-value">{{ parsedData.city || '未填写' }}</span></div>
        </div>
        <div v-else class="info-edit-grid">
          <label class="edit-field"><span>姓名</span><input v-model="parsedData.name" @input="hasChanges = true" /></label>
          <label class="edit-field"><span>学历</span><input v-model="parsedData.education" @input="hasChanges = true" /></label>
          <label class="edit-field"><span>工作年限</span><input v-model="parsedData.years" @input="hasChanges = true" /></label>
          <label class="edit-field"><span>目标职位</span><input v-model="parsedData.targetJob" @input="hasChanges = true" /></label>
          <label class="edit-field"><span>城市</span><input v-model="parsedData.city" @input="hasChanges = true" /></label>
        </div>
      </section>

      <section class="result-section">
        <div class="section-head"><h2>技能</h2><button class="edit-toggle" @click="editSkills = !editSkills"><component :is="editSkills ? X : Edit" :size="14" /></button></div>
        <div v-if="parsedData.skills.length" class="skills-list">
          <span v-for="(skill, i) in parsedData.skills" :key="skill" class="skill-chip" :class="CHIPS[i % CHIPS.length]">{{ skill }}<button v-if="editSkills" class="chip-remove" @click="removeSkill(i)"><X :size="10" /></button></span>
        </div>
        <p v-else class="empty-hint">暂无技能</p>
        <div v-if="editSkills" class="add-skill-row">
          <input v-model="newSkill" placeholder="输入技能名称后按回车" @keydown.enter="addSkill" class="skill-input" />
          <button class="add-skill-btn" @click="addSkill">添加</button>
        </div>
      </section>

      <section class="result-section">
        <div class="section-head"><h2>工作经历</h2><button class="edit-toggle" @click="editExp = !editExp; editingExpIdx = -1"><component :is="editExp ? X : Edit" :size="14" /></button></div>
        <div v-if="parsedData.experience.length" class="exp-list">
          <div v-for="(exp, i) in parsedData.experience" :key="i" class="exp-item">
            <template v-if="!editExp || editingExpIdx !== i">
              <div class="exp-dot" /><div class="exp-content">
                <div class="exp-title-row"><span class="exp-title">{{ exp.title }}</span><span class="exp-period">{{ exp.period }}</span></div>
                <div class="exp-company">{{ exp.company }}</div><p class="exp-desc">{{ exp.description }}</p>
              </div>
              <div v-if="editExp" class="exp-edit-btns">
                <button class="icon-btn-sm" @click="editingExpIdx = i"><Edit :size="13" /></button>
                <button class="icon-btn-sm danger" @click="deleteExp(i)"><Trash2 :size="13" /></button>
              </div>
            </template>
            <template v-else>
              <div class="exp-edit-form">
                <div class="edit-row"><input v-model="exp.title" placeholder="职位" @input="hasChanges = true" /><input v-model="exp.company" placeholder="公司" @input="hasChanges = true" /></div>
                <input v-model="exp.period" placeholder="时间段" @input="hasChanges = true" />
                <textarea v-model="exp.description" placeholder="工作描述" rows="2" @input="hasChanges = true" />
                <div class="edit-form-actions"><button class="confirm-btn" @click="editingExpIdx = -1">确认</button><button class="cancel-btn" @click="editingExpIdx = -1">取消</button></div>
              </div>
            </template>
          </div>
        </div>
        <p v-else class="empty-hint">暂无工作经历</p>
        <button v-if="editExp" class="add-exp-btn" @click="addExp"><Plus :size="16" /> 添加工作经历</button>
      </section>

      <section class="result-section stats-section">
        <div class="stats-row">
          <div class="stat-item"><span class="stat-value">{{ parsedData.skills.length }}</span><span class="stat-label">技能</span></div>
          <div class="stat-item"><span class="stat-value">{{ parsedData.experience.length }}</span><span class="stat-label">经历数</span></div>
        </div>
      </section>

      <div class="go-recommend">
        <router-link to="/user/jobs" class="recommend-btn">查看推荐职位 <ArrowRight :size="16" /></router-link>
        <router-link :to="'/user/resume/optimize?resume_id=' + selectedResumeId" class="optimize-btn"><Sparkles :size="16" /> AI 优化</router-link>
      </div>
    </div>
  </div></div>
</template>

<style scoped lang="scss">
.resume-page { padding: 24px 16px; }
.resume-container { max-width: 800px; margin: 0 auto; }
.page-title { font-size: 24px; font-weight: 700; color: #121c28; margin: 0; }
.header-row { display: flex; align-items: center; justify-content: space-between; margin-bottom: 24px; }
.upload-new-btn { display: inline-flex; align-items: center; gap: 6px; padding: 8px 20px; border-radius: 999px; background: #003527; color: #fff; font-size: 13px; font-weight: 600; border: none; cursor: pointer; transition: all .2s; }
.upload-new-btn:hover { background: #064e3b; }
.loading-hint { display: flex; align-items: center; justify-content: center; gap: 8px; padding: 60px 0; color: #404944; font-size: 14px; }
.empty-state { text-align: center; padding: 80px 24px; color: #404944; }
.empty-state .empty-icon { margin-bottom: 16px; color: #bfc9c3; }
.empty-state p { font-size: 14px; }
.resume-list { display: flex; flex-direction: column; gap: 10px; }
.resume-card { display: flex; align-items: center; justify-content: space-between; padding: 16px 20px; background: #fff; border-radius: 10px; border: 1px solid #bfc9c3; cursor: pointer; transition: all .2s; }
.resume-card:hover { border-color: #003527; box-shadow: 0 2px 12px rgba(26,58,92,0.06); }
.card-left { display: flex; align-items: center; gap: 14px; }
.card-icon { color: #003527; }
.card-meta { display: flex; flex-direction: column; gap: 2px; }
.card-title { font-size: 15px; font-weight: 600; color: #121c28; }
.card-date { font-size: 12px; color: #404944; }
.card-right { display: flex; align-items: center; gap: 10px; }
.card-status { font-size: 11px; font-weight: 600; padding: 2px 10px; border-radius: 999px; }
.card-status.normal { background: #d4edda; color: #155724; }
.card-status.disabled { background: #f8f9fa; color: #6c757d; }
.card-status.banned { background: #f8d7da; color: #721c24; }
.card-status.waiting { background: #fff3cd; color: #856404; animation: pulse 1.5s ease-in-out infinite; }
.card-status.parsing { background: #cce5ff; color: #004085; animation: pulse 1.5s ease-in-out infinite; }
.card-status.success { background: #d4edda; color: #155724; }
.card-status.failed { background: #f8d7da; color: #721c24; }
@keyframes pulse { 0%, 100% { opacity: 0.7; } 50% { opacity: 1; } }
.card-delete { width: 30px; height: 30px; border-radius: 6px; border: 1px solid transparent; background: none; color: #bfc9c3; display: flex; align-items: center; justify-content: center; cursor: pointer; transition: all .2s; }
.card-delete:hover { border-color: #f56c6c; color: #f56c6c; }
.card-delete:disabled { opacity: 0.4; cursor: not-allowed; }

/* Upload Strip */
.upload-strip { width: 100%; max-width: 1200px; min-height: 180px; background: #fff; border-radius: 12px; border: 2px dashed #bfc9c3; margin: 0 auto 16px; display: flex; align-items: center; transition: all .2s; }
.upload-strip:hover { border-color: #003527; background: rgba(26,58,92,0.02); }
.strip-body { display: flex; align-items: center; justify-content: center; gap: 32px; padding: 14px 18px; }
.strip-left { display: flex; align-items: center; gap: 14px; flex: 1; min-width: 0; cursor: pointer; }
.strip-icon { color: #bfc9c3; flex-shrink: 0; }
.strip-text { display: flex; flex-direction: column; gap: 1px; min-width: 0; }
.strip-title { font-size: 14px; font-weight: 600; color: #121c28; }
.strip-hint { font-size: 12px; color: #404944; }
.strip-right { flex-shrink: 0; margin-left: 16px; }
.strip-btn { display: inline-flex; align-items: center; gap: 6px; padding: 8px 20px; border-radius: 999px; background: #003527; color: #fff; font-size: 13px; font-weight: 600; border: none; cursor: pointer; transition: all .2s; }
.strip-btn:hover { background: #064e3b; }

/* File Strip (has uploaded files) */
.file-strip { width: 100%; max-width: 1200px; background: #fff; border-radius: 12px; border: 1px solid #bfc9c3; margin: 0 auto 16px; padding: 12px 18px; transition: all .2s; }
.file-strip:hover { border-color: #003527; }
.file-strip-inner { display: flex; align-items: center; gap: 8px; }
.file-strip-items { display: flex; align-items: center; gap: 6px; flex: 1; min-width: 0; overflow-x: auto; padding: 2px 0; }
.file-strip-item { display: inline-flex; align-items: center; gap: 4px; padding: 4px 10px; border-radius: 6px; background: #f8f9ff; border: 1px solid #bfc9c3; cursor: pointer; white-space: nowrap; font-size: 12px; color: #121c28; transition: all .15s; flex-shrink: 0; }
.file-strip-item:hover { border-color: #003527; background: #eef2f7; color: #003527; }
.file-strip-icon { color: #003527; flex-shrink: 0; }
.file-strip-name { max-width: 160px; overflow: hidden; text-overflow: ellipsis; }
.file-strip-add { flex-shrink: 0; width: 32px; height: 32px; border-radius: 8px; border: 1px dashed #bfc9c3; background: none; display: flex; align-items: center; justify-content: center; color: #404944; cursor: pointer; transition: all .15s; }
.file-strip-add:hover { border-color: #003527; color: #003527; background: rgba(26,58,92,0.02); }
.file-strip-footer { display: flex; align-items: center; gap: 12px; margin-top: 6px; padding-left: 2px; }
.file-strip-count { font-size: 11px; color: #404944; }
.file-strip-hint { font-size: 11px; color: #bfc9c3; }

.back-btn { margin-top: 16px; padding: 6px 16px; border-radius: 6px; border: 1px solid #bfc9c3; background: none; color: #404944; font-size: 13px; cursor: pointer; transition: all .2s; }
.back-btn:hover { border-color: #003527; color: #003527; }
.progress-card { background: #fff; border-radius: 12px; padding: 32px; border: 1px solid #bfc9c3; margin-top: 24px; }
.progress-header { display: flex; align-items: center; gap: 10px; margin-bottom: 16px; }
.progress-label { font-size: 16px; font-weight: 600; color: #121c28; }
.bar-track { height: 8px; border-radius: 999px; background: #e9ecef; overflow: hidden; margin-bottom: 12px; }
.bar-fill { height: 100%; border-radius: 999px; background: linear-gradient(90deg, #003527, #064e3b); transition: width .4s ease; }
.progress-text { font-size: 13px; color: #404944; }
.error-card { background: #fff; border-radius: 12px; padding: 32px; border: 1px solid #f56c6c; text-align: center; }
.error-msg { color: #f56c6c; font-size: 14px; margin-bottom: 16px; }
.error-actions { display: flex; justify-content: center; align-items: center; margin-top: 8px; }
.retry-btn { display: inline-flex; align-items: center; gap: 6px; padding: 8px 20px; border-radius: 999px; border: 1px solid #003527; background: none; color: #003527; font-size: 13px; font-weight: 600; cursor: pointer; margin-right: 8px; transition: all .2s; }
.retry-btn:hover { background: #003527; color: #fff; }
.detail-nav { display: flex; align-items: center; gap: 6px; margin-bottom: 12px; font-size: 13px; color: #404944; }
.back-link { display: flex; align-items: center; gap: 2px; background: none; border: none; color: #404944; cursor: pointer; font-size: 13px; }
.back-link:hover { color: #003527; }
.rotate-180 { transform: rotate(180deg); }
.nav-sep { color: #bfc9c3; }
.nav-current { color: #121c28; font-weight: 500; }
.result-actions { display: flex; align-items: center; justify-content: space-between; margin-bottom: 16px; }
.action-btn { display: inline-flex; align-items: center; gap: 6px; padding: 6px 16px; border-radius: 6px; border: 1px solid #bfc9c3; background: #fff; color: #404944; font-size: 13px; cursor: pointer; transition: all .2s; }
.action-btn:hover { border-color: #003527; color: #003527; }
.action-btn.danger:hover { border-color: #f56c6c; color: #f56c6c; }
.action-btn:disabled { opacity: 0.4; cursor: not-allowed; }
.save-btn { display: inline-flex; align-items: center; gap: 6px; padding: 8px 20px; border-radius: 999px; background: #003527; color: #fff; font-size: 13px; font-weight: 600; border: none; cursor: pointer; transition: all .2s; }
.save-btn:hover:not(:disabled) { background: #064e3b; }
.save-btn:disabled { opacity: 0.6; cursor: not-allowed; }
.sync-btn { display: inline-flex; align-items: center; gap: 6px; padding: 8px 20px; border-radius: 999px; background: #059669; color: #fff; font-size: 13px; font-weight: 600; border: none; cursor: pointer; transition: all .2s; }
.sync-btn:hover:not(:disabled) { background: #047857; }
.sync-btn:disabled { opacity: 0.6; cursor: not-allowed; }
.action-left { display: flex; gap: 8px; }
.action-right { display: flex; gap: 8px; }
.result-section { background: #fff; border-radius: 12px; padding: 24px; margin-bottom: 16px; border: 1px solid #bfc9c3; }
.section-head { display: flex; align-items: center; justify-content: space-between; margin-bottom: 16px; }
.section-head h2 { font-size: 18px; font-weight: 700; color: #121c28; }
.edit-toggle { width: 32px; height: 32px; border-radius: 8px; border: 1px solid #bfc9c3; background: #fff; color: #404944; display: flex; align-items: center; justify-content: center; cursor: pointer; transition: all .2s; }
.edit-toggle:hover { border-color: #003527; color: #003527; }
.info-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 12px 32px; }
.info-item { display: flex; align-items: center; font-size: 14px; }
.info-label { color: #404944; width: 70px; flex-shrink: 0; }
.info-value { color: #121c28; }
.info-edit-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 12px 24px; }
.edit-field { display: flex; flex-direction: column; gap: 4px; }
.edit-field span { font-size: 12px; color: #404944; }
.edit-field input { padding: 6px 10px; border: 1px solid #bfc9c3; border-radius: 6px; font-size: 13px; color: #121c28; outline: none; transition: border-color .2s; }
.edit-field input:focus { border-color: #003527; box-shadow: 0 0 0 2px rgba(26,58,92,0.08); }
.skills-list { display: flex; flex-wrap: wrap; gap: 8px; margin-bottom: 12px; }
.skill-chip { display: inline-flex; align-items: center; gap: 4px; padding: 4px 14px; border-radius: 4px; font-size: 12px; font-weight: 600; letter-spacing: 0.3px; }
.chip-primary { background: #003527; color: #fff; }
.chip-success { background: #d4edda; color: #155724; }
.chip-neutral { background: #f3f4f5; color: #434656; }
.chip-warning { background: #fff3cd; color: #856404; }
.chip-purple { background: #e8d5f5; color: #6a1b9a; }
.chip-remove { width: 16px; height: 16px; border-radius: 50%; background: rgba(0,0,0,0.12); display: inline-flex; align-items: center; justify-content: center; cursor: pointer; transition: background .2s; border: none; color: inherit; padding: 0; }
.chip-remove:hover { background: rgba(220,53,69,0.25); }
.add-skill-row { display: flex; gap: 8px; margin-top: 8px; }
.skill-input { flex: 1; padding: 6px 10px; border: 1px solid #bfc9c3; border-radius: 6px; font-size: 13px; outline: none; }
.skill-input:focus { border-color: #003527; }
.add-skill-btn { padding: 6px 16px; border-radius: 6px; background: #003527; color: #fff; font-size: 12px; font-weight: 600; border: none; cursor: pointer; transition: background .2s; }
.add-skill-btn:hover { background: #064e3b; }
.empty-hint { font-size: 13px; color: #bfc9c3; padding: 8px 0; }
.exp-list { position: relative; }
.exp-item { position: relative; padding-left: 24px; padding-bottom: 20px; border-left: 2px solid #bfc9c3; margin-left: 6px; }
.exp-item:last-child { border-left-color: transparent; padding-bottom: 0; }
.exp-dot { position: absolute; left: -5px; top: 6px; width: 8px; height: 8px; border-radius: 50%; background: #003527; }
.exp-content { padding-left: 8px; }
.exp-title-row { display: flex; align-items: baseline; justify-content: space-between; margin-bottom: 2px; }
.exp-title { font-size: 15px; font-weight: 600; color: #121c28; }
.exp-period { font-size: 12px; color: #404944; }
.exp-company { font-size: 13px; color: #064e3b; font-weight: 500; margin-bottom: 4px; }
.exp-desc { font-size: 13px; color: #404944; line-height: 1.6; }
.exp-edit-btns { position: absolute; right: 0; top: 0; display: flex; gap: 4px; }
.icon-btn-sm { width: 28px; height: 28px; border-radius: 6px; border: 1px solid #bfc9c3; background: #fff; color: #404944; display: flex; align-items: center; justify-content: center; cursor: pointer; transition: all .2s; }
.icon-btn-sm:hover { border-color: #003527; color: #003527; }
.icon-btn-sm.danger:hover { border-color: #f56c6c; color: #f56c6c; }
.exp-edit-form { padding-left: 8px; display: flex; flex-direction: column; gap: 8px; }
.exp-edit-form .edit-row { display: flex; gap: 8px; }
.exp-edit-form input, .exp-edit-form textarea { width: 100%; padding: 6px 10px; border: 1px solid #bfc9c3; border-radius: 6px; font-size: 13px; color: #121c28; outline: none; font-family: inherit; }
.exp-edit-form input:focus, .exp-edit-form textarea:focus { border-color: #003527; }
.exp-edit-form textarea { resize: vertical; }
.edit-form-actions { display: flex; gap: 8px; }
.confirm-btn { padding: 6px 16px; border-radius: 6px; background: #003527; color: #fff; font-size: 12px; font-weight: 600; border: none; cursor: pointer; }
.confirm-btn:hover { background: #064e3b; }
.cancel-btn { padding: 6px 16px; border-radius: 6px; background: #fff; color: #404944; font-size: 12px; border: 1px solid #bfc9c3; cursor: pointer; }
.cancel-btn:hover { border-color: #003527; color: #003527; }
.add-exp-btn { display: flex; align-items: center; justify-content: center; gap: 6px; width: 100%; padding: 12px; border: 2px dashed #bfc9c3; border-radius: 8px; background: none; color: #404944; font-size: 13px; cursor: pointer; margin-top: 12px; transition: all .2s; }
.add-exp-btn:hover { border-color: #003527; color: #003527; }
.stats-section { padding: 16px 24px; }
.stats-row { display: flex; gap: 32px; justify-content: center; }
.stat-item { display: flex; flex-direction: column; align-items: center; gap: 2px; }
.stat-value { font-size: 24px; font-weight: 700; color: #003527; }
.stat-label { font-size: 12px; color: #404944; }
.pagination-wrap { display: flex; justify-content: center; margin-top: 16px; padding: 8px 0; }
.go-recommend { display: flex; gap: 12px; justify-content: center; flex-wrap: wrap; margin-top: 24px; }
.recommend-btn, .optimize-btn { display: inline-flex; align-items: center; gap: 8px; padding: 12px 28px; border-radius: 999px; font-size: 15px; font-weight: 600; text-decoration: none; transition: all .3s; }
.recommend-btn { background: #003527; color: #fff; }
.recommend-btn:hover { background: #064e3b; transform: translateY(-2px); box-shadow: 0 8px 24px rgba(26,58,92,0.2); text-decoration: none; }
.optimize-btn { background: #064e3b; color: #fff; }
.optimize-btn:hover { background: #0c95d0; transform: translateY(-2px); box-shadow: 0 8px 24px rgba(14,165,233,0.2); text-decoration: none; }
@keyframes spin { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }
.spinning { color: #003527; animation: spin 1s linear infinite; }
.detail-view { animation: fadeUp 0.35s ease; }
@keyframes fadeUp { from { opacity: 0; transform: translateY(12px); } to { opacity: 1; transform: translateY(0); } }
@media (max-width: 640px) { .info-grid, .info-edit-grid { grid-template-columns: 1fr; } .exp-title-row { flex-direction: column; } }
</style>
