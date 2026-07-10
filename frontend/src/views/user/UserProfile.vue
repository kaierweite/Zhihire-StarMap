<script setup lang="ts">
import { ref, reactive, computed, onMounted } from "vue"
import { useAuthStore } from "@/store/auth"
import { ElMessage } from "element-plus"
import { Edit, Plus, Phone, MapPin, GraduationCap, Briefcase, Award, Loader2, X } from "lucide-vue-next"
import { getProfile, updateProfile } from "@/api/user"
import type { UserProfileData } from "@/api/user"

const authStore = useAuthStore()
const avatarLetter = computed(() => authStore.username?.charAt(0).toUpperCase() || "U")

// ====== 加载状态 ======
const loading = ref(true)
const loadError = ref(false)

// ====== 后端数据 -> 模板展示的映射 ======
const genderMap: Record<string, string> = { MALE: "男", FEMALE: "女", OTHER: "其他" }

function formatSalary(min: number | null, max: number | null): string {
  if (min === null && max === null) return ""
  const fmt = (v: number) => (v >= 1000 ? Math.round(v / 1000) + "K" : String(v))
  if (min !== null && max !== null) return `${fmt(min)}-${fmt(max)}`
  if (min !== null) return `${fmt(min)}以上`
  return `${fmt(max!)}以内`
}

function calcAge(birthDate: string | null): string {
  if (!birthDate) return ""
  const year = new Date(birthDate).getFullYear()
  if (isNaN(year)) return ""
  return String(new Date().getFullYear() - year)
}

// ====== 响应式档案数据（结构匹配模板引用） ======
const profile = ref({
  name: "未填写",
  gender: "",
  age: "",
  city: "",
  phone: "",
  graduationYear: "",
  tag: "",
  jobStatus: "",
  intention: {
    positions: "",
    salary: "",
    cities: "",
    worktype: "",
    industry: "",
  },
  strengths: "",
  education: [] as { school: string; degree: string; major: string; period: string }[],
  work: [] as { title: string; company: string; period: string; desc: string }[],
  projects: [] as { name: string; desc: string }[],
  training: [] as { name: string; period: string }[],
  languages: [] as { name: string; level: string }[],
  skills: [] as string[],
  certificates: [] as { name: string }[],
  portfolio: [] as { name: string }[],
  studentLeader: [] as { role: string; org: string; period: string }[],
})

// ====== 完成度（从后端回传的数值驱动） ======
const profileCompleteness = ref(0)

// ====== 从后端 DTO 映射到模板结构 ======
function mapProfile(data: UserProfileData) {
  profile.value.name = data.real_name || authStore.username || "未填写"
  profile.value.gender = data.gender ? (genderMap[data.gender] || data.gender) : ""
  profile.value.age = calcAge(data.birth_date)
  profile.value.city = data.current_city || ""
  profile.value.phone = data.phone || ""
  profile.value.strengths = data.bio || ""
  profile.value.skills = data.skills.map((s) => s.name)

  profile.value.intention.salary = formatSalary(data.expected_salary_min, data.expected_salary_max)
  profile.value.intention.cities = data.expected_city || ""
  profile.value.intention.positions = data.expected_position || ""
  profile.value.intention.worktype = data.expected_worktype || ""
  profile.value.intention.industry = data.expected_industry || ""
  profile.value.work = (data.work_experiences || []).map(w => ({ title: w.title, company: w.company, period: w.period || "", desc: w.description || "" }))
  profile.value.projects = (data.project_experiences || []).map(p => ({ name: p.name, desc: p.description || "" }))
  profile.value.languages = (data.languages || []).map(l => ({ name: l.name, level: l.level || "" }))
  profile.value.certificates = (data.certificates || []).map(c => ({ name: c.name }))

  if (data.education) {
    profile.value.education = [
      { school: data.school || "", degree: data.education, major: data.major || "", period: "" },
    ]
  } else {
    profile.value.education = []
  }

  profileCompleteness.value = data.profile_completeness
}

// ====== 互补的完成度清单（前端根据实际数据动态展示） ======
const completionItems = computed(() => [
  { label: "基本信息", done: !!profile.value.name || !!profile.value.phone },
  { label: "求职意向", done: !!profile.value.intention.salary || !!profile.value.intention.cities },
  { label: "教育经历", done: profile.value.education.length > 0 },
  { label: "专业技能", done: profile.value.skills.length > 0 },
  { label: "工作经历", done: profile.value.work.length > 0 },
  { label: "项目经历", done: profile.value.projects.length > 0 },
])

const chipColors = ["chip-primary", "chip-success", "chip-neutral", "chip-warning", "chip-purple"]

// ====== 加载档案 ======
onMounted(async () => {
  try {
    loading.value = true
    loadError.value = false
    const res = await getProfile()
    if (res.data.code === 200 && res.data.data) {
      mapProfile(res.data.data)
    }
  } catch {
    loadError.value = true
  } finally {
    loading.value = false
  }
})

// ====== 对话框状态 ======
const dialogState = reactive({
  strengths: false,
  education: false,
  work: false,
  project: false,
  skill: false,
  language: false,
  certificate: false,
  intention: false,
})

// ====== 表单临时数据 ======
const strengthsForm = ref("")
const educationForm = ref({ school: "", degree: "", major: "", period: "" })
const workForm = ref({ title: "", company: "", period: "", desc: "" })
const projectForm = ref({ name: "", desc: "" })
const skillInput = ref("")
const languageForm = ref({ name: "", level: "" })
const certificateForm = ref({ name: "" })
  const intentionForm = ref({ positions: "", salary_min: null, salary_max: null, city: "", worktype: "", industry: "" })

// ====== 打开/保存 对话框函数 ======
function openStrengthsDialog() {
  strengthsForm.value = profile.value.strengths
  dialogState.strengths = true
}
function saveStrengths() {
  profile.value.strengths = strengthsForm.value
  dialogState.strengths = false
  updateProfile({ bio: strengthsForm.value || null }).then(() => {
    ElMessage.success("个人优势已更新")
  }).catch(() => {})
}

function openEducationDialog() {
  educationForm.value = { school: "", degree: "", major: "", period: "" }
  dialogState.education = true
}
function saveEducation() {
  const form = educationForm.value
  if (!form.school && !form.degree) {
    ElMessage.warning("请至少填写学校名称或学历")
    return
  }
  profile.value.education.push({ ...form })
  dialogState.education = false
  const last = profile.value.education[profile.value.education.length - 1]
  updateProfile({
    school: last!.school || null,
    education: last!.degree || null,
    major: last!.major || null,
  }).then(() => {
    ElMessage.success("教育经历已添加")
  }).catch(() => {})
}

function openWorkDialog() {
  workForm.value = { title: "", company: "", period: "", desc: "" }
  dialogState.work = true
}
function saveWork() {
  if (!workForm.value.title || !workForm.value.company) {
    ElMessage.warning("请至少填写职位和公司名称")
    return
  }
  profile.value.work.push({ ...workForm.value })
  dialogState.work = false
  const wrk = profile.value.work.map(w => ({ title: w.title, company: w.company, period: w.period || null, description: w.desc || null }))
  updateProfile({ work_experiences: wrk }).then(() => ElMessage.success("工作经历已添加")).catch(() => {})
}

function openProjectDialog() {
  projectForm.value = { name: "", desc: "" }
  dialogState.project = true
}
function saveProject() {
  if (!projectForm.value.name) {
    ElMessage.warning("请填写项目名称")
    return
  }
  profile.value.projects.push({ ...projectForm.value })
  dialogState.project = false
  const prj = profile.value.projects.map(p => ({ name: p.name, description: p.desc || null }))
  updateProfile({ project_experiences: prj }).then(() => ElMessage.success("项目经历已添加")).catch(() => {})
}

function openSkillDialog() {
  skillInput.value = ""
  dialogState.skill = true
}
function addSkill() {
  const val = skillInput.value.trim()
  if (!val) return
  if (profile.value.skills.includes(val)) {
    ElMessage.warning("该技能已存在")
    return
  }
  profile.value.skills.push(val)
  skillInput.value = ""
  updateProfile({ skills: [...profile.value.skills] }).then(() => {
    ElMessage.success("专业技能已添加")
  }).catch(() => {})
}
function removeSkill(idx: number) {
  profile.value.skills.splice(idx, 1)
  updateProfile({ skills: [...profile.value.skills] }).then(() => {
    ElMessage.success("技能已移除")
  }).catch(() => {})
}

function openLanguageDialog() {
  languageForm.value = { name: "", level: "" }
  dialogState.language = true
}
function saveLanguage() {
  if (!languageForm.value.name) {
    ElMessage.warning("请填写语言名称")
    return
  }
  profile.value.languages.push({ ...languageForm.value })
  dialogState.language = false
  const lang = profile.value.languages.map(l => ({ name: l.name, level: l.level || null }))
  updateProfile({ languages: lang }).then(() => ElMessage.success("语言能力已添加")).catch(() => {})
}

function openCertificateDialog() {
  certificateForm.value = { name: "" }
  dialogState.certificate = true
}
function saveCertificate() {
  if (!certificateForm.value.name) {
    ElMessage.warning("请填写证书名称")
    return
  }
  profile.value.certificates.push({ ...certificateForm.value })
  dialogState.certificate = false
  const cert = profile.value.certificates.map(c => ({ name: c.name }))
  updateProfile({ certificates: cert }).then(() => ElMessage.success("证书已添加")).catch(() => {})
}

// ====== 删除函数 ======
function removeWork(idx: number) {
  profile.value.work.splice(idx, 1)
  const a = profile.value.work.map(w => ({ title: w.title, company: w.company, period: w.period || null, description: w.desc || null }))
  updateProfile({ work_experiences: a }).catch(() => {})
}
function removeProject(idx: number) {
  profile.value.projects.splice(idx, 1)
  const a = profile.value.projects.map(p => ({ name: p.name, description: p.desc || null }))
  updateProfile({ project_experiences: a }).catch(() => {})
}
function removeEducation(idx: number) { profile.value.education.splice(idx, 1) }
function removeLanguage(idx: number) {
  profile.value.languages.splice(idx, 1)
  const a = profile.value.languages.map(l => ({ name: l.name, level: l.level || null }))
  updateProfile({ languages: a }).catch(() => {})
}
function removeCertificate(idx: number) {
  profile.value.certificates.splice(idx, 1)
  const a = profile.value.certificates.map(c => ({ name: c.name }))
  updateProfile({ certificates: a }).catch(() => {})
}

  // ====== 求职意向 ======
function openIntentionDialog() {
  const v = profile.value.intention
  intentionForm.value = {
    positions: v.positions || "",
    salary_min: null,
    salary_max: null,
    city: v.cities || "",
    worktype: v.worktype || "",
    industry: v.industry || "",
  }
  dialogState.intention = true
  getProfile().then(res => {
    if (res.data.code === 200 && res.data.data) {
      const d = res.data.data
      if (d.expected_salary_min != null) intentionForm.value.salary_min = Math.round(d.expected_salary_min / 1000)
      if (d.expected_salary_max != null) intentionForm.value.salary_max = Math.round(d.expected_salary_max / 1000)
    }
  }).catch(() => {})
}
function saveIntention() {
  const form = intentionForm.value
  const p = profile.value.intention
  p.positions = form.positions || ""
  p.salary = form.salary_min || form.salary_max
    ? (form.salary_min ? form.salary_min + "K" : "") + "-" + (form.salary_max ? form.salary_max + "K" : "")
    : ""
  p.cities = form.city || ""
  p.worktype = form.worktype || ""
  p.industry = form.industry || ""
  dialogState.intention = false
  updateProfile({
    expected_city: form.city || null,
    expected_position: form.positions || null,
    expected_worktype: form.worktype || null,
    expected_industry: form.industry || null,
    expected_salary_min: form.salary_min,
    expected_salary_max: form.salary_max,
  }).then(() => {
    ElMessage.success("求职意向已更新")
  }).catch(() => {})
}
</script>

<template>
  <div class="profile-page">
    <div class="profile-container">
      <!-- ========== 加载中 ========== -->
      <div v-if="loading" class="loading-box">
        <Loader2 :size="32" class="spinner" />
        <span>加载中...</span>
      </div>

      <!-- ========== 加载失败 ========== -->
      <div v-else-if="loadError" class="loading-box">
        <span>加载失败，请刷新重试</span>
      </div>

      <template v-else>
        <!-- ========== 资料完成度 ========== -->
        <section class="completion-card">
          <div class="completion-header">
            <span class="completion-label">资料完成度</span>
            <span class="completion-percent">{{ profileCompleteness }}%</span>
          </div>
          <div class="bar-track">
            <div class="bar-fill" :style="{ width: profileCompleteness + '%' }" />
          </div>
          <div class="completion-items">
            <span
              v-for="item in completionItems"
              :key="item.label"
              class="completion-chip"
              :class="item.done ? 'done' : 'todo'"
            >
              {{ item.label }}
            </span>
          </div>
        </section>

        <!-- ========== 头像 + 基本信息 ========== -->
        <section class="profile-section">
          <div class="section-header">
            <div class="profile-basic">
              <div class="profile-avatar">{{ avatarLetter }}</div>
              <div class="profile-info">
                <div class="profile-name-row">
                  <h1 class="profile-name">{{ profile.name }}</h1>
                </div>
                <div class="profile-meta">
                  <span v-if="profile.gender">{{ profile.gender }}</span>
                  <span v-if="profile.gender && profile.age" class="sep">|</span>
                  <span v-if="profile.age">{{ profile.age }}岁</span>
                  <span v-if="(profile.gender || profile.age) && profile.city" class="sep">|</span>
                  <span v-if="profile.city">{{ profile.city }}</span>
                </div>
                <div v-if="profile.phone" class="profile-phone">
                  <Phone :size="14" />
                  <span>{{ profile.phone }}</span>
                </div>
              </div>
            </div>
          </div>
        </section>

        <!-- ========== 个人优势 ========== -->
        <section class="profile-section">
          <div class="section-header">
            <h2 class="section-title">个人优势</h2>
          </div>
          <div v-if="profile.strengths" class="section-body">
            <p>{{ profile.strengths }}</p>
          </div>
          <div v-else class="add-placeholder" @click="openStrengthsDialog">
            <Plus :size="28" class="placeholder-icon" />
            <span>添加个人优势</span>
          </div>
        </section>


        <section class="profile-section">
          <div class="section-header">
            <h2 class="section-title">求职意向</h2>
            <button class="edit-btn" @click="openIntentionDialog"><Edit :size="14" /> 编辑</button>
            <span class="required-badge">必填</span>
            </div>
          <div class="section-body">
            <div class="intention-grid" @click="openIntentionDialog" style="cursor: pointer;">
              <div class="intention-item">
                <span class="intention-label">薪资要求:</span>
                <span class="intention-value">{{ profile.intention.salary || "未填写" }}</span>
              </div>
              <div class="intention-item">
                <span class="intention-label">期望城市:</span>
                <span class="intention-value">{{ profile.intention.cities || "未填写" }}</span>
              </div>
            </div>
          </div>
        </section>

        <!-- ========== 教育经历 ========== -->
        <section class="profile-section">
          <div class="section-header">
            <h2 class="section-title">教育经历</h2>
            <span class="required-badge">必填</span>
          </div>
          <div v-if="profile.education.length" class="section-body">
            <div v-for="(edu, i) in profile.education" :key="edu.school + edu.degree" class="edu-item">
              <div class="edu-school">{{ edu.school || "未填写" }}</div>
              <div class="edu-detail">
                <span>{{ edu.degree }}</span>
                <span v-if="edu.major" class="sep">&#xFF5C;</span>
                <span v-if="edu.major">{{ edu.major }}</span>
          <span class="remove-link" @click="removeEducation(i)">删除</span>
              </div>
            </div>
          </div>
          <div v-else class="add-placeholder" @click="openEducationDialog">
            <Plus :size="28" class="placeholder-icon" />
            <span>添加教育经历</span>
          </div>
        </section>

        <!-- ========== 工作/实习经历 ========== -->
        <section class="profile-section">
          <div class="section-header">
            <h2 class="section-title">工作/实习经历</h2>
          </div>
          <div v-if="profile.work.length" class="section-body">
            <div v-for="(w, i) in profile.work" :key="w.title + w.company" class="exp-item">
              <div class="exp-title">{{ w.title }}</div>
              <div class="exp-meta">{{ w.company }} · {{ w.period }}</div>
              <p v-if="w.desc" class="exp-desc">{{ w.desc }}</p>
          <span class="remove-link" @click="removeWork(i)">删除</span>
            </div>
          </div>
          <div v-else class="add-placeholder" @click="openWorkDialog">
            <Plus :size="28" class="placeholder-icon" />
            <span>添加工作/实习经历</span>
          </div>
        </section>

        <!-- ========== 项目经历 ========== -->
        <section class="profile-section">
          <div class="section-header">
            <h2 class="section-title">项目经历</h2>
          </div>
          <div v-if="profile.projects.length" class="section-body">
            <div v-for="(p, i) in profile.projects" :key="p.name + p.desc" class="exp-item">
              <div class="exp-title">{{ p.name }}</div>
              <p class="exp-desc">{{ p.desc }}</p>
          <span class="remove-link" @click="removeProject(i)">删除</span>
            </div>
          </div>
          <div v-else class="add-placeholder" @click="openProjectDialog">
            <Plus :size="28" class="placeholder-icon" />
            <span>添加项目经历</span>
          </div>
        </section>

        <!-- ========== 专业技能 ========== -->
        <section class="profile-section">
          <div class="section-header">
            <h2 class="section-title">专业技能</h2>
          </div>
          <div class="section-body">
            <div v-if="profile.skills.length" class="skills-list">
              <span
                v-for="(skill, i) in profile.skills"
                :key="skill"
                class="skill-chip"
                :class="chipColors[i % chipColors.length]"
              >
                {{ skill }}
              </span>
            </div>
            <div class="add-placeholder small" @click="openSkillDialog">
              <Plus :size="20" class="placeholder-icon" />
              <span>添加专业技能</span>
            </div>
          </div>
        </section>

        <!-- ========== 语言能力 ========== -->
        <section class="profile-section">
          <div class="section-header">
            <h2 class="section-title">语言能力</h2>
          </div>
          <div v-if="profile.languages.length" class="section-body">
            <div v-for="(l, i) in profile.languages" :key="l.name" class="lang-item">
              <span class="lang-name">{{ l.name }}</span>
              <span class="lang-level">{{ l.level }}</span>
          <span class="remove-link" @click="removeLanguage(i)">删除</span>
            </div>
          </div>
          <div v-else class="add-placeholder" @click="openLanguageDialog">
            <Plus :size="28" class="placeholder-icon" />
            <span>添加语言能力</span>
          </div>
        </section>

        <!-- ========== 证书 ========== -->
        <section class="profile-section">
          <div class="section-header">
            <h2 class="section-title">证书</h2>
          </div>
          <div v-if="profile.certificates.length" class="section-body">
            <div v-for="(c, i) in profile.certificates" :key="i" class="cert-item" style="display: flex; justify-content: space-between;">{{ c.name }}<span class="remove-link" @click="removeCertificate(i)">删除</span></div>
          </div>
          <div v-else class="add-placeholder" @click="openCertificateDialog">
            <Plus :size="28" class="placeholder-icon" />
            <span>添加证书</span>
          </div>
        </section>
      </template>
    </div>
  </div>
        <!-- 个人优势对话框 -->
        <el-dialog v-model="dialogState.strengths" title="编辑个人优势" width="500px" :close-on-click-modal="false">
          <el-input v-model="strengthsForm" type="textarea" :rows="5" placeholder="请描述您的个人优势，如：沟通能力强、团队协作、学习能力..." maxlength="500" show-word-limit />
          <template #footer>
            <el-button @click="dialogState.strengths = false">取消</el-button>
            <el-button type="primary" @click="saveStrengths">保存</el-button>
          </template>
        </el-dialog>

        <!-- 教育经历对话框 -->
        <el-dialog v-model="dialogState.education" title="添加教育经历" width="500px" :close-on-click-modal="false">
          <el-form label-position="top">
            <el-form-item label="学校名称" required>
              <el-input v-model="educationForm.school" placeholder="请输入学校名称" />
            </el-form-item>
            <el-form-item label="学历" required>
              <el-select v-model="educationForm.degree" placeholder="请选择学历" style="width: 100%">
                <el-option label="博士" value="博士" />
                <el-option label="硕士" value="硕士" />
                <el-option label="本科" value="本科" />
                <el-option label="大专" value="大专" />
                <el-option label="高中/中专" value="高中/中专" />
                <el-option label="其他" value="其他" />
              </el-select>
            </el-form-item>
            <el-form-item label="专业">
              <el-input v-model="educationForm.major" placeholder="请输入专业名称" />
            </el-form-item>
            <el-form-item label="就读时间">
              <el-input v-model="educationForm.period" placeholder="如：2020.09 - 2024.06" />
            </el-form-item>
          </el-form>
          <template #footer>
            <el-button @click="dialogState.education = false">取消</el-button>
            <el-button type="primary" @click="saveEducation">添加</el-button>
          </template>
        </el-dialog>

        <!-- 工作/实习经历对话框 -->
        <el-dialog v-model="dialogState.work" title="添加工作/实习经历" width="550px" :close-on-click-modal="false">
          <el-form label-position="top">
            <el-form-item label="职位" required>
              <el-input v-model="workForm.title" placeholder="请输入职位名称" />
            </el-form-item>
            <el-form-item label="公司名称" required>
              <el-input v-model="workForm.company" placeholder="请输入公司名称" />
            </el-form-item>
            <el-form-item label="工作时间">
              <el-input v-model="workForm.period" placeholder="如：2024.01 - 至今" />
            </el-form-item>
            <el-form-item label="工作描述">
              <el-input v-model="workForm.desc" type="textarea" :rows="3" placeholder="请描述您的主要工作内容" />
            </el-form-item>
          </el-form>
          <template #footer>
            <el-button @click="dialogState.work = false">取消</el-button>
            <el-button type="primary" @click="saveWork">添加</el-button>
          </template>
        </el-dialog>

        <!-- 项目经历对话框 -->
        <el-dialog v-model="dialogState.project" title="添加项目经历" width="550px" :close-on-click-modal="false">
          <el-form label-position="top">
            <el-form-item label="项目名称" required>
              <el-input v-model="projectForm.name" placeholder="请输入项目名称" />
            </el-form-item>
            <el-form-item label="项目描述">
              <el-input v-model="projectForm.desc" type="textarea" :rows="4" placeholder="请描述您在项目中的角色与主要贡献" />
            </el-form-item>
          </el-form>
          <template #footer>
            <el-button @click="dialogState.project = false">取消</el-button>
            <el-button type="primary" @click="saveProject">添加</el-button>
          </template>
        </el-dialog>

        <!-- 专业技能对话框 -->
        <el-dialog v-model="dialogState.skill" title="添加专业技能" width="450px" :close-on-click-modal="false">
          <div class="skill-add-row">
            <el-input v-model="skillInput" placeholder="输入技能名称后点击添加" @keydown.enter="addSkill" style="flex:1" />
            <el-button type="primary" @click="addSkill">添加</el-button>
          </div>
          <div v-if="profile.skills.length" class="skills-list" style="margin-top: 16px">
            <span v-for="(skill, i) in profile.skills" :key="skill" class="skill-chip" :class="chipColors[i % chipColors.length]">
              {{ skill }}
              <span class="chip-remove" @click="removeSkill(i)"><X :size="10" /></span>
            </span>
          </div>
          <div v-else style="margin-top: 16px; color: #909399; font-size: 13px; text-align: center;">暂无技能，请在上方输入添加</div>
          <template #footer>
            <el-button @click="dialogState.skill = false">完成</el-button>
          </template>
        </el-dialog>

        <!-- 语言能力对话框 -->
        <el-dialog v-model="dialogState.language" title="添加语言能力" width="450px" :close-on-click-modal="false">
          <el-form label-position="top">
            <el-form-item label="语言" required>
              <el-select v-model="languageForm.name" placeholder="请选择语言" style="width: 100%">
                <el-option label="中文（普通话）" value="中文（普通话）" />
                <el-option label="英语" value="英语" />
                <el-option label="日语" value="日语" />
                <el-option label="韩语" value="韩语" />
                <el-option label="法语" value="法语" />
                <el-option label="德语" value="德语" />
                <el-option label="西班牙语" value="西班牙语" />
                <el-option label="俄语" value="俄语" />
                <el-option label="其他" value="其他" />
              </el-select>
            </el-form-item>
            <el-form-item label="熟练程度" required>
              <el-select v-model="languageForm.level" placeholder="请选择熟练程度" style="width: 100%">
                <el-option label="母语" value="母语" />
                <el-option label="精通" value="精通" />
                <el-option label="熟练" value="熟练" />
                <el-option label="良好" value="良好" />
                <el-option label="一般" value="一般" />
                <el-option label="基础" value="基础" />
              </el-select>
            </el-form-item>
          </el-form>
          <template #footer>
            <el-button @click="dialogState.language = false">取消</el-button>
            <el-button type="primary" @click="saveLanguage">添加</el-button>
          </template>
        </el-dialog>

        <!-- 证书对话框 -->
        <el-dialog v-model="dialogState.certificate" title="添加证书" width="450px" :close-on-click-modal="false">
          <el-form label-position="top">
            <el-form-item label="证书名称" required>
              <el-input v-model="certificateForm.name" placeholder="请输入证书名称" />
            </el-form-item>
          </el-form>
          <template #footer>
            <el-button @click="dialogState.certificate = false">取消</el-button>
            <el-button type="primary" @click="saveCertificate">添加</el-button>
          </template>
        </el-dialog>

        <!-- ========== 求职意向对话框 ========== -->
        <el-dialog v-model="dialogState.intention" title="编辑求职意向" width="500px" :close-on-click-modal="false">
          <el-form label-position="top">
            <el-form-item label="期望职位">
              <el-input v-model="intentionForm.positions" placeholder="请输入期望职位" />
            </el-form-item>
            <el-form-item label="期望薪资（最低 K/月）">
              <el-input-number v-model="intentionForm.salary_min" :min="0" :step="1" style="width: 100%" />
            </el-form-item>
            <el-form-item label="期望薪资（最高 K/月）">
              <el-input-number v-model="intentionForm.salary_max" :min="0" :step="1" style="width: 100%" />
            </el-form-item>
            <el-form-item label="期望城市">
              <el-input v-model="intentionForm.city" placeholder="请输入期望城市" />
            </el-form-item>
            <el-form-item label="工作类型">
              <el-select v-model="intentionForm.worktype" placeholder="请选择工作类型" style="width: 100%">
                <el-option label="全职" value="全职" />
                <el-option label="兼职" value="兼职" />
                <el-option label="实习" value="实习" />
              </el-select>
            </el-form-item>
            <el-form-item label="期望行业">
              <el-input v-model="intentionForm.industry" placeholder="请输入期望行业" />
            </el-form-item>
          </el-form>
          <template #footer>
            <el-button @click="dialogState.intention = false">取消</el-button>
            <el-button type="primary" @click="saveIntention">保存</el-button>
          </template>
        </el-dialog>
</template>
<style scoped lang="scss">
.profile-page {
  padding: 24px 16px;
}

.profile-container {
  max-width: 960px;
  margin: 0 auto;
}

/* ====== 加载状态 ====== */
.loading-box {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 12px;
  padding: 80px 0;
  color: #909399;
  font-size: 14px;
}

.spinner {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

/* ====== 资料完成度 ====== */
.completion-card {
  background: #fff;
  border-radius: 12px;
  padding: 20px 24px;
  margin-bottom: 20px;
  border: 1px solid #e5e7eb;
}

.completion-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 10px;
}

.completion-label {
  font-size: 14px;
  font-weight: 600;
  color: #303133;
}

.completion-percent {
  font-size: 14px;
  font-weight: 700;
  color: #1a3a5c;
}

.bar-track {
  height: 8px;
  border-radius: 999px;
  background: #e9ecef;
  overflow: hidden;
  margin-bottom: 14px;
}

.bar-fill {
  height: 100%;
  border-radius: 999px;
  background: linear-gradient(90deg, #1a3a5c, #0ea5e9);
  transition: width 0.8s ease;
}

.completion-items {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.completion-chip {
  font-size: 12px;
  font-weight: 600;
  padding: 4px 12px;
  border-radius: 4px;
  letter-spacing: 0.3px;

  &.done {
    background: #d4edda;
    color: #155724;
  }
  &.todo {
    background: #f3f4f5;
    color: #909399;
  }
}

/* ====== 通用 Section ====== */
.profile-section {
  background: #fff;
  border-radius: 12px;
  padding: 24px;
  margin-bottom: 16px;
  border: 1px solid #e5e7eb;
  border-bottom: 1px solid #e5e7eb;
}

.section-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 16px;
}

.section-title {
  font-size: 20px;
  font-weight: 700;
  color: #303133;
}

.required-badge {
  font-size: 10px;
  font-weight: 700;
  padding: 2px 8px;
  border-radius: 4px;
  background: #f8d7da;
  color: #721c24;
}

.edit-btn {
  margin-left: auto;
  display: inline-flex;
  align-items: center;
  gap: 4px;
  font-size: 13px;
  color: #909399;
  background: none;
  border: none;
  cursor: pointer;
  transition: color 0.2s;
  &:hover { color: #1a3a5c; }
}

.section-body {
  color: #303133;
  font-size: 14px;
  line-height: 1.7;
}

/* ====== 头像 + 基本信息 ====== */
.profile-basic {
  display: flex;
  align-items: flex-start;
  gap: 20px;
}

.profile-avatar {
  width: 80px;
  height: 80px;
  border-radius: 12px;
  background: #f5f7fa;
  border: 1px solid #e5e7eb;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 32px;
  font-weight: 700;
  color: #909399;
  flex-shrink: 0;
}

.profile-info {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.profile-name-row {
  display: flex;
  align-items: center;
  gap: 10px;
}

.profile-name {
  font-size: 24px;
  font-weight: 700;
  color: #303133;
}

.profile-tag {
  font-size: 12px;
  font-weight: 500;
  padding: 2px 10px;
  border-radius: 4px;
  background: #dbeafe;
  color: #1e3a8a;
}

.profile-meta {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 14px;
  color: #606266;
}

.sep {
  color: #dcdfe6;
  margin: 0 4px;
}

.profile-phone {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 14px;
  color: #606266;
}

/* ====== 求职意向 ====== */
.intention-positions {
  font-size: 15px;
  font-weight: 500;
  color: #303133;
  margin-bottom: 12px;
}

.intention-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 8px 48px;
}

.intention-item {
  display: flex;
  align-items: center;
  font-size: 14px;
}

.intention-label {
  color: #909399;
  width: 70px;
  flex-shrink: 0;
}

.intention-value {
  color: #303133;
}

/* ====== 教育经历 ====== */
.edu-item {
  padding-bottom: 12px;
  &:not(:last-child) { margin-bottom: 12px; border-bottom: 1px solid #f0f0f0; }
}

.edu-school {
  font-size: 15px;
  font-weight: 600;
  color: #303133;
  margin-bottom: 4px;
}

.edu-detail {
  font-size: 14px;
  color: #606266;
  display: flex;
  align-items: center;
  gap: 4px;
}

.edu-period {
  margin-left: auto;
  color: #909399;
}

/* ====== 经历 ====== */
.exp-item {
  padding-bottom: 12px;
  margin-bottom: 12px;
  border-bottom: 1px solid #f0f0f0;
  &:last-child { border-bottom: none; margin-bottom: 0; }
}

.exp-title {
  font-size: 15px;
  font-weight: 600;
  color: #303133;
  margin-bottom: 4px;
}

.exp-meta {
  font-size: 13px;
  color: #909399;
  margin-bottom: 4px;
}

.exp-desc {
  font-size: 14px;
  color: #606266;
  line-height: 1.6;
}

/* ====== 技能标签 ====== */
.skills-list {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-bottom: 12px;
}

.skill-chip {
  display: inline-flex;
  align-items: center;
  padding: 4px 14px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 600;
  letter-spacing: 0.3px;
}

.chip-primary { background: #dbeafe; color: #1e3a8a; }
.chip-success { background: #d4edda; color: #155724; }
.chip-neutral { background: #f3f4f5; color: #434656; }
.chip-warning { background: #fff3cd; color: #856404; }
.chip-purple { background: #e8d5f5; color: #6a1b9a; }

/* ====== 语言 ====== */
.lang-item {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 8px;
}

.lang-name {
  font-size: 14px;
  font-weight: 500;
  color: #303133;
}

.lang-level {
  font-size: 13px;
  color: #909399;
}

/* ====== 添加占位 ====== */
.add-placeholder {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 32px;
  border: 2px dashed #dcdfe6;
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.2s;
  color: #c0c4cc;

  span {
    font-size: 13px;
    margin-top: 4px;
  }

  &:hover {
    border-color: #1a3a5c;
    color: #1a3a5c;
    background: rgba(26, 58, 92, 0.02);
  }

  &.small {
    padding: 16px;
    flex-direction: row;
    gap: 8px;
    span { margin-top: 0; }
  }
}

.placeholder-icon {
  opacity: 0.4;
}

/* ====== 证书 ====== */
.cert-item {
  font-size: 14px;
  color: #606266;
  margin-bottom: 4px;
}

@media (max-width: 640px) {
  .profile-container { padding: 0 8px; }
  .profile-basic { flex-direction: column; align-items: center; text-align: center; }
  .profile-info { align-items: center; }
  .profile-meta { flex-wrap: wrap; justify-content: center; }
  .intention-grid { grid-template-columns: 1fr; }
  .edu-detail { flex-wrap: wrap; }
  .edu-period { margin-left: 0; }
}
/* ====== 删除链接 ====== */
.remove-link {
  font-size: 12px;
  color: #f56c6c;
  cursor: pointer;
  margin-left: 8px;
  &:hover { text-decoration: underline; }
}
/* 工具类 */
.skill-add-row { display: flex; gap: 8px; align-items: center; }
.mt-16 { margin-top: 16px; }
.chip-remove { margin-left: 4px; cursor: pointer; }
</style>


