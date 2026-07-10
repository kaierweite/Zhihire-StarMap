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
      const fields = result.synced_fields?.join("\u3001") || ""
      ElMessage.success(`\u5df2\u540c\u6b65\u5230\u4e2a\u4eba\u4e2d\u5fc3\uff1a${fields}`)
    } else if (result?.reason === "resume_not_found_or_empty") {
      ElMessage.warning("\u8be5\u7b80\u5386\u6682\u65e0\u89e3\u6790\u7ed3\u679c\uff0c\u8bf7\u7b49\u5f85\u89e3\u6790\u5b8c\u6210")
    } else {
      ElMessage.info("\u4e2a\u4eba\u4e2d\u5fc3\u6570\u636e\u5df2\u662f\u6700\u65b0\uff0c\u65e0\u9700\u540c\u6b65")
    }
  } catch {
    ElMessage.error("\u540c\u6b65\u5931\u8d25\uff0c\u8bf7\u7a0d\u540e\u91cd\u8bd5")
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
  if (!ALLOWED_TYPES.includes(f.type)) return "\u4ec5\u652f\u6301 PDF/DOC/DOCX \u683c\u5f0f"
  if (f.size > MAX_SIZE) return "\u6587\u4ef6\u5927\u5c0f\u4e0d\u80fd\u8d85\u8fc7 10MB"
  return null
}

async function doUpload(file: File) {
  view.value = "parsing"; progress.value = 0
  progressText.value = "\u6b63\u5728\u4e0a\u4f20\u7b80\u5386..."
  let resumeId: number, taskId: number
  try {
    const resp = await uploadResume(file, file.name.replace(/\.[a-z]+$/i, ""))
    const d = resp.data.data; resumeId = d.resume_id
    taskId = d.task_id; resumeTitle.value = d.title
  } catch {
    view.value = "error"; errorMsg.value = "\u4e0a\u4f20\u5931\u8d25"; return
  }
  selectedResumeId.value = resumeId
  progressText.value = "\u6b63\u5728\u89e3\u6790\u7b80\u5386..."
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
        view.value = "error"; errorMsg.value = "\u89e3\u6790\u5931\u8d25"; return
      }
    } catch { /* retry */ }
    if (tries >= MAX_TRIES) {
      if (pollingTimer) { clearInterval(pollingTimer); pollingTimer = null }
      view.value = "error"; errorMsg.value = "\u8d85\u65f6\u4e86"
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
    view.value = "error"; errorMsg.value = "\u52a0\u8f7d\u5931\u8d25"
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
  parsedData.name = p.name ?? ""; parsedData.education = p.education ?? ""
  parsedData.years = p.years ?? (p.years === 0 ? 0 : "")
  parsedData.targetJob = p.targetJob ?? ""; parsedData.city = p.city ?? ""
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
    ElMessage.success("\u4fdd\u5b58\u6210\u529f")
  } catch {} finally { saving.value = false }
}

async function handleDelete(id: number) {
  try {
    await ElMessageBox.confirm("\u786e\u5b9a\u8981\u5220\u9664\u8fd9\u4efd\u7b80\u5386\u5417\uff1f", "\u786e\u8ba4", {
      confirmButtonText: "\u5220\u9664", cancelButtonText: "\u53d6\u6d88", type: "warning",
    })
  } catch { return }
  deleting.value = true
  try {
    await deleteResume(id); ElMessage.success("\u5220\u9664\u6210\u529f")
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
