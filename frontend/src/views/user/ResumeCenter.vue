
<script setup lang="ts">
import { ref, reactive, onMounted, onUnmounted } from "vue"
import { ElMessage, ElMessageBox } from "element-plus"
import { Upload, FileText, RefreshCw, Edit, Trash2, Plus, X,
        ArrowRight, Save, File, ChevronRight, Sparkles, UserCheck } from "lucide-vue-next"
import { uploadResume, listResumes, getResumeDetail,
        updateResume, deleteResume, getParseTaskStatus, syncToProfile } from "@/api/resume"
import type { ResumeListItem, ResumeDetail as ResumeDetailType } from "@/api/resume"
import AbilityMapSection from "./AbilityMapSection.vue"

type ViewMode = "list" | "upload" | "parsing" | "detail" | "error"
const view = ref<ViewMode>("list")
const selectedResumeId = ref<number | null>(null)
const resumeTitle = ref("")
const progress = ref(0)
const progressText = ref("")
const errorMsg = ref("")
let progressTimer: ReturnType<typeof setInterval> | null = null
let pollingTimer: ReturnType<typeof setInterval> | null = null

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
  if (progressTimer) clearInterval(progressTimer)
  if (pollingTimer) clearInterval(pollingTimer)
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
  syncing.value = true
  try {
    const resp = await syncToProfile(selectedResumeId.value)
    const result = resp.data.data
    if (result?.synced_to_profile) {
      const fields = result.synced_fields?.join("、") || ""
      ElMessage.success("已同步到个人中心：" + fields)
    } else if (result?.reason === "resume_not_found_or_empty") {
      ElMessage.warning("该简历暂无解析结果，请等待解析完成")
    } else {
      ElMessage.info("个人中心数据已是最新，无需同步")
    }
  } catch {
    ElMessage.error("同步失败，请稍后重试")
  } finally {
    syncing.value = false
  }
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
  view.value = "parsing"; progress.value = 0
  progressText.value = "正在上传简历..."
  let resumeId: number, taskId: number
  try {
    const resp = await uploadResume(file, file.name.replace(/\.[a-z]+$/i, ""))
    const d = resp.data.data; resumeId = d.resume_id
    taskId = d.task_id; resumeTitle.value = d.title
  } catch {
    view.value = "error"; errorMsg.value = "上传失败"; return
  }
  selectedResumeId.value = resumeId
  progressText.value = "正在解析简历..."
  progress.value = 15
  pollTask(taskId, resumeId)
}

function pollTask(taskId: number, rid: number) {
  let tries = 0; const MAX_TRIES = 120
  pollingTimer = setInterval(async () => {
    tries++; progress.value = Math.min(15 + Math.round((tries / MAX_TRIES) * 75), 90)
    try {
      const resp = await getParseTaskStatus(taskId)
      const st = resp.data.data
      if (st.status === "SUCCESS") {
        if (pollingTimer) { clearInterval(pollingTimer); pollingTimer = null }
        progress.value = 95; await loadDetail(rid); return
      }
      if (st.status === "FAILED") {
        if (pollingTimer) { clearInterval(pollingTimer); pollingTimer = null }
        view.value = "error"; errorMsg.value = "解析失败"; return
      }
    } catch { /* retry */ }
    if (tries >= MAX_TRIES) {
      if (pollingTimer) { clearInterval(pollingTimer); pollingTimer = null }
      view.value = "error"; errorMsg.value = "超时了"
    }
  }, 2000)
}

async function openDetail(id: number) {
  selectedResumeId.value = id
  view.value = "parsing"; progress.value = 50
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
  if (progressTimer) { clearInterval(progressTimer); progressTimer = null }
  if (pollingTimer) { clearInterval(pollingTimer); pollingTimer = null }
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
            <span class="card-status" :class="item.status.toLowerCase()">{{ item.status }}</span>
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

    <div v-if="view === 'parsing'" class="progress-card">
      <div class="progress-header"><RefreshCw :size="20" class="spinning" /><span class="progress-label">简历处理中</span></div>
      <div class="bar-track"><div class="bar-fill" :style="{ width: progress + '%' }" /></div>
      <p class="progress-text">{{ progressText }}</p>
    </div>

    <div v-if="view === 'error'" class="error-card">
      <p class="error-msg">{{ errorMsg || '出错了，请重试' }}</p>
      <div class="error-actions">
        <button class="retry-btn" @click="retryUpload"><RefreshCw :size="14" /> 重新上传</button>
        <button class="back-btn" @click="backToList">返回列表</button>
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
.page-title { font-size: 24px; font-weight: 700; color: #303133; margin: 0; }
.header-row { display: flex; align-items: center; justify-content: space-between; margin-bottom: 24px; }
.upload-new-btn { display: inline-flex; align-items: center; gap: 6px; padding: 8px 20px; border-radius: 999px; background: #1a3a5c; color: #fff; font-size: 13px; font-weight: 600; border: none; cursor: pointer; transition: all .2s; }
.upload-new-btn:hover { background: #24507a; }
.loading-hint { display: flex; align-items: center; justify-content: center; gap: 8px; padding: 60px 0; color: #909399; font-size: 14px; }
.empty-state { text-align: center; padding: 80px 24px; color: #909399; }
.empty-state .empty-icon { margin-bottom: 16px; color: #c0c4cc; }
.empty-state p { font-size: 14px; }
.resume-list { display: flex; flex-direction: column; gap: 10px; }
.resume-card { display: flex; align-items: center; justify-content: space-between; padding: 16px 20px; background: #fff; border-radius: 10px; border: 1px solid #e5e7eb; cursor: pointer; transition: all .2s; }
.resume-card:hover { border-color: #1a3a5c; box-shadow: 0 2px 12px rgba(26,58,92,0.06); }
.card-left { display: flex; align-items: center; gap: 14px; }
.card-icon { color: #1a3a5c; }
.card-meta { display: flex; flex-direction: column; gap: 2px; }
.card-title { font-size: 15px; font-weight: 600; color: #303133; }
.card-date { font-size: 12px; color: #909399; }
.card-right { display: flex; align-items: center; gap: 10px; }
.card-status { font-size: 11px; font-weight: 600; padding: 2px 10px; border-radius: 999px; }
.card-status.normal { background: #d4edda; color: #155724; }
.card-status.disabled { background: #f8f9fa; color: #6c757d; }
.card-status.banned { background: #f8d7da; color: #721c24; }
.card-delete { width: 30px; height: 30px; border-radius: 6px; border: 1px solid transparent; background: none; color: #c0c4cc; display: flex; align-items: center; justify-content: center; cursor: pointer; transition: all .2s; }
.card-delete:hover { border-color: #f56c6c; color: #f56c6c; }
.card-delete:disabled { opacity: 0.4; cursor: not-allowed; }

/* Upload Strip */
.upload-strip { width: 100%; max-width: 1200px; min-height: 180px; background: #fff; border-radius: 12px; border: 2px dashed #dcdfe6; margin: 0 auto 16px; display: flex; align-items: center; transition: all .2s; }
.upload-strip:hover { border-color: #1a3a5c; background: rgba(26,58,92,0.02); }
.strip-body { display: flex; align-items: center; justify-content: center; gap: 32px; padding: 14px 18px; }
.strip-left { display: flex; align-items: center; gap: 14px; flex: 1; min-width: 0; cursor: pointer; }
.strip-icon { color: #c0c4cc; flex-shrink: 0; }
.strip-text { display: flex; flex-direction: column; gap: 1px; min-width: 0; }
.strip-title { font-size: 14px; font-weight: 600; color: #303133; }
.strip-hint { font-size: 12px; color: #909399; }
.strip-right { flex-shrink: 0; margin-left: 16px; }
.strip-btn { display: inline-flex; align-items: center; gap: 6px; padding: 8px 20px; border-radius: 999px; background: #1a3a5c; color: #fff; font-size: 13px; font-weight: 600; border: none; cursor: pointer; transition: all .2s; }
.strip-btn:hover { background: #24507a; }

/* File Strip (has uploaded files) */
.file-strip { width: 100%; max-width: 1200px; background: #fff; border-radius: 12px; border: 1px solid #e5e7eb; margin: 0 auto 16px; padding: 12px 18px; transition: all .2s; }
.file-strip:hover { border-color: #1a3a5c; }
.file-strip-inner { display: flex; align-items: center; gap: 8px; }
.file-strip-items { display: flex; align-items: center; gap: 6px; flex: 1; min-width: 0; overflow-x: auto; padding: 2px 0; }
.file-strip-item { display: inline-flex; align-items: center; gap: 4px; padding: 4px 10px; border-radius: 6px; background: #f5f7fa; border: 1px solid #e5e7eb; cursor: pointer; white-space: nowrap; font-size: 12px; color: #303133; transition: all .15s; flex-shrink: 0; }
.file-strip-item:hover { border-color: #1a3a5c; background: #eef2f7; color: #1a3a5c; }
.file-strip-icon { color: #1a3a5c; flex-shrink: 0; }
.file-strip-name { max-width: 160px; overflow: hidden; text-overflow: ellipsis; }
.file-strip-add { flex-shrink: 0; width: 32px; height: 32px; border-radius: 8px; border: 1px dashed #dcdfe6; background: none; display: flex; align-items: center; justify-content: center; color: #909399; cursor: pointer; transition: all .15s; }
.file-strip-add:hover { border-color: #1a3a5c; color: #1a3a5c; background: rgba(26,58,92,0.02); }
.file-strip-footer { display: flex; align-items: center; gap: 12px; margin-top: 6px; padding-left: 2px; }
.file-strip-count { font-size: 11px; color: #909399; }
.file-strip-hint { font-size: 11px; color: #c0c4cc; }

.back-btn { margin-top: 16px; padding: 6px 16px; border-radius: 6px; border: 1px solid #dcdfe6; background: none; color: #606266; font-size: 13px; cursor: pointer; transition: all .2s; }
.back-btn:hover { border-color: #1a3a5c; color: #1a3a5c; }
.progress-card { background: #fff; border-radius: 12px; padding: 32px; border: 1px solid #e5e7eb; margin-top: 24px; }
.progress-header { display: flex; align-items: center; gap: 10px; margin-bottom: 16px; }
.progress-label { font-size: 16px; font-weight: 600; color: #303133; }
.bar-track { height: 8px; border-radius: 999px; background: #e9ecef; overflow: hidden; margin-bottom: 12px; }
.bar-fill { height: 100%; border-radius: 999px; background: linear-gradient(90deg, #1a3a5c, #0ea5e9); transition: width .4s ease; }
.progress-text { font-size: 13px; color: #909399; }
.error-card { background: #fff; border-radius: 12px; padding: 32px; border: 1px solid #f56c6c; text-align: center; }
.error-msg { color: #f56c6c; font-size: 14px; margin-bottom: 16px; }
.error-actions { display: flex; justify-content: center; align-items: center; margin-top: 8px; }
.retry-btn { display: inline-flex; align-items: center; gap: 6px; padding: 8px 20px; border-radius: 999px; border: 1px solid #1a3a5c; background: none; color: #1a3a5c; font-size: 13px; font-weight: 600; cursor: pointer; margin-right: 8px; transition: all .2s; }
.retry-btn:hover { background: #1a3a5c; color: #fff; }
.detail-nav { display: flex; align-items: center; gap: 6px; margin-bottom: 12px; font-size: 13px; color: #909399; }
.back-link { display: flex; align-items: center; gap: 2px; background: none; border: none; color: #909399; cursor: pointer; font-size: 13px; }
.back-link:hover { color: #1a3a5c; }
.rotate-180 { transform: rotate(180deg); }
.nav-sep { color: #dcdfe6; }
.nav-current { color: #303133; font-weight: 500; }
.result-actions { display: flex; align-items: center; justify-content: space-between; margin-bottom: 16px; }
.action-btn { display: inline-flex; align-items: center; gap: 6px; padding: 6px 16px; border-radius: 6px; border: 1px solid #dcdfe6; background: #fff; color: #606266; font-size: 13px; cursor: pointer; transition: all .2s; }
.action-btn:hover { border-color: #1a3a5c; color: #1a3a5c; }
.action-btn.danger:hover { border-color: #f56c6c; color: #f56c6c; }
.action-btn:disabled { opacity: 0.4; cursor: not-allowed; }
.save-btn { display: inline-flex; align-items: center; gap: 6px; padding: 8px 20px; border-radius: 999px; background: #1a3a5c; color: #fff; font-size: 13px; font-weight: 600; border: none; cursor: pointer; transition: all .2s; }
.save-btn:hover:not(:disabled) { background: #24507a; }
.save-btn:disabled { opacity: 0.6; cursor: not-allowed; }
.sync-btn { display: inline-flex; align-items: center; gap: 6px; padding: 8px 20px; border-radius: 999px; background: #059669; color: #fff; font-size: 13px; font-weight: 600; border: none; cursor: pointer; transition: all .2s; }
.sync-btn:hover:not(:disabled) { background: #047857; }
.sync-btn:disabled { opacity: 0.6; cursor: not-allowed; }
.action-left { display: flex; gap: 8px; }
.action-right { display: flex; gap: 8px; }
.result-section { background: #fff; border-radius: 12px; padding: 24px; margin-bottom: 16px; border: 1px solid #e5e7eb; }
.section-head { display: flex; align-items: center; justify-content: space-between; margin-bottom: 16px; }
.section-head h2 { font-size: 18px; font-weight: 700; color: #303133; }
.edit-toggle { width: 32px; height: 32px; border-radius: 8px; border: 1px solid #dcdfe6; background: #fff; color: #909399; display: flex; align-items: center; justify-content: center; cursor: pointer; transition: all .2s; }
.edit-toggle:hover { border-color: #1a3a5c; color: #1a3a5c; }
.info-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 12px 32px; }
.info-item { display: flex; align-items: center; font-size: 14px; }
.info-label { color: #909399; width: 70px; flex-shrink: 0; }
.info-value { color: #303133; }
.info-edit-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 12px 24px; }
.edit-field { display: flex; flex-direction: column; gap: 4px; }
.edit-field span { font-size: 12px; color: #909399; }
.edit-field input { padding: 6px 10px; border: 1px solid #dcdfe6; border-radius: 6px; font-size: 13px; color: #303133; outline: none; transition: border-color .2s; }
.edit-field input:focus { border-color: #1a3a5c; box-shadow: 0 0 0 2px rgba(26,58,92,0.08); }
.skills-list { display: flex; flex-wrap: wrap; gap: 8px; margin-bottom: 12px; }
.skill-chip { display: inline-flex; align-items: center; gap: 4px; padding: 4px 14px; border-radius: 4px; font-size: 12px; font-weight: 600; letter-spacing: 0.3px; }
.chip-primary { background: #dbeafe; color: #1e3a8a; }
.chip-success { background: #d4edda; color: #155724; }
.chip-neutral { background: #f3f4f5; color: #434656; }
.chip-warning { background: #fff3cd; color: #856404; }
.chip-purple { background: #e8d5f5; color: #6a1b9a; }
.chip-remove { width: 16px; height: 16px; border-radius: 50%; background: rgba(0,0,0,0.12); display: inline-flex; align-items: center; justify-content: center; cursor: pointer; transition: background .2s; border: none; color: inherit; padding: 0; }
.chip-remove:hover { background: rgba(220,53,69,0.25); }
.add-skill-row { display: flex; gap: 8px; margin-top: 8px; }
.skill-input { flex: 1; padding: 6px 10px; border: 1px solid #dcdfe6; border-radius: 6px; font-size: 13px; outline: none; }
.skill-input:focus { border-color: #1a3a5c; }
.add-skill-btn { padding: 6px 16px; border-radius: 6px; background: #1a3a5c; color: #fff; font-size: 12px; font-weight: 600; border: none; cursor: pointer; transition: background .2s; }
.add-skill-btn:hover { background: #24507a; }
.empty-hint { font-size: 13px; color: #c0c4cc; padding: 8px 0; }
.exp-list { position: relative; }
.exp-item { position: relative; padding-left: 24px; padding-bottom: 20px; border-left: 2px solid #e5e7eb; margin-left: 6px; }
.exp-item:last-child { border-left-color: transparent; padding-bottom: 0; }
.exp-dot { position: absolute; left: -5px; top: 6px; width: 8px; height: 8px; border-radius: 50%; background: #1a3a5c; }
.exp-content { padding-left: 8px; }
.exp-title-row { display: flex; align-items: baseline; justify-content: space-between; margin-bottom: 2px; }
.exp-title { font-size: 15px; font-weight: 600; color: #303133; }
.exp-period { font-size: 12px; color: #909399; }
.exp-company { font-size: 13px; color: #0ea5e9; font-weight: 500; margin-bottom: 4px; }
.exp-desc { font-size: 13px; color: #606266; line-height: 1.6; }
.exp-edit-btns { position: absolute; right: 0; top: 0; display: flex; gap: 4px; }
.icon-btn-sm { width: 28px; height: 28px; border-radius: 6px; border: 1px solid #dcdfe6; background: #fff; color: #909399; display: flex; align-items: center; justify-content: center; cursor: pointer; transition: all .2s; }
.icon-btn-sm:hover { border-color: #1a3a5c; color: #1a3a5c; }
.icon-btn-sm.danger:hover { border-color: #f56c6c; color: #f56c6c; }
.exp-edit-form { padding-left: 8px; display: flex; flex-direction: column; gap: 8px; }
.exp-edit-form .edit-row { display: flex; gap: 8px; }
.exp-edit-form input, .exp-edit-form textarea { width: 100%; padding: 6px 10px; border: 1px solid #dcdfe6; border-radius: 6px; font-size: 13px; color: #303133; outline: none; font-family: inherit; }
.exp-edit-form input:focus, .exp-edit-form textarea:focus { border-color: #1a3a5c; }
.exp-edit-form textarea { resize: vertical; }
.edit-form-actions { display: flex; gap: 8px; }
.confirm-btn { padding: 6px 16px; border-radius: 6px; background: #1a3a5c; color: #fff; font-size: 12px; font-weight: 600; border: none; cursor: pointer; }
.confirm-btn:hover { background: #24507a; }
.cancel-btn { padding: 6px 16px; border-radius: 6px; background: #fff; color: #606266; font-size: 12px; border: 1px solid #dcdfe6; cursor: pointer; }
.cancel-btn:hover { border-color: #1a3a5c; color: #1a3a5c; }
.add-exp-btn { display: flex; align-items: center; justify-content: center; gap: 6px; width: 100%; padding: 12px; border: 2px dashed #dcdfe6; border-radius: 8px; background: none; color: #909399; font-size: 13px; cursor: pointer; margin-top: 12px; transition: all .2s; }
.add-exp-btn:hover { border-color: #1a3a5c; color: #1a3a5c; }
.stats-section { padding: 16px 24px; }
.stats-row { display: flex; gap: 32px; justify-content: center; }
.stat-item { display: flex; flex-direction: column; align-items: center; gap: 2px; }
.stat-value { font-size: 24px; font-weight: 700; color: #1a3a5c; }
.stat-label { font-size: 12px; color: #909399; }
.pagination-wrap { display: flex; justify-content: center; margin-top: 16px; padding: 8px 0; }
.go-recommend { display: flex; gap: 12px; justify-content: center; flex-wrap: wrap; margin-top: 24px; }
.recommend-btn, .optimize-btn { display: inline-flex; align-items: center; gap: 8px; padding: 12px 28px; border-radius: 999px; font-size: 15px; font-weight: 600; text-decoration: none; transition: all .3s; }
.recommend-btn { background: #1a3a5c; color: #fff; }
.recommend-btn:hover { background: #24507a; transform: translateY(-2px); box-shadow: 0 8px 24px rgba(26,58,92,0.2); text-decoration: none; }
.optimize-btn { background: #0ea5e9; color: #fff; }
.optimize-btn:hover { background: #0c95d0; transform: translateY(-2px); box-shadow: 0 8px 24px rgba(14,165,233,0.2); text-decoration: none; }
@keyframes spin { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }
.spinning { color: #1a3a5c; animation: spin 1s linear infinite; }
.detail-view { animation: fadeUp 0.35s ease; }
@keyframes fadeUp { from { opacity: 0; transform: translateY(12px); } to { opacity: 1; transform: translateY(0); } }
@media (max-width: 640px) { .info-grid, .info-edit-grid { grid-template-columns: 1fr; } .exp-title-row { flex-direction: column; } }
</style>
