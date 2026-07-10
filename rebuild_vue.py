import pathlib

filepath = pathlib.Path(r"C:\Users\Administrator\Desktop\Zhihire-StarMap\frontend\src\views\user\UserProfile.vue")
old_lines = filepath.read_text(encoding="utf-8-sig").splitlines(keepends=True)

# Find template start in existing (corrupted) file
template_idx = None
for i, line in enumerate(old_lines):
    if "<template>" in line:
        template_idx = i
        break
assert template_idx is not None, "Could not find <template>"

# The corrupted file has no </script>. Everything from <template> onwards is the intact template+style.
template_content = "".join(old_lines[template_idx:])

new_script = '''<script setup lang="ts">
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
const genderMap: Record<string, string> = { MALE: "\u7537", FEMALE: "\u5973", OTHER: "\u5176\u4ed6" }

function formatSalary(min: number | null, max: number | null): string {
  if (min === null && max === null) return ""
  const fmt = (v: number) => (v >= 1000 ? Math.round(v / 1000) + "K" : String(v))
  if (min !== null && max !== null) return `${fmt(min)}-${fmt(max)}`
  if (min !== null) return `${fmt(min)}\u4ee5\u4e0a`
  return `${fmt(max!)}\u4ee5\u5185`
}

function calcAge(birthDate: string | null): string {
  if (!birthDate) return ""
  const year = new Date(birthDate).getFullYear()
  if (isNaN(year)) return ""
  return String(new Date().getFullYear() - year)
}

// ====== 响应式档案数据（结构匹配模板引用） ======
const profile = ref({
  name: "\u672a\u586b\u5199",
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
  profile.value.name = data.real_name || authStore.username || "\u672a\u586b\u5199"
  profile.value.gender = data.gender ? (genderMap[data.gender] || data.gender) : ""
  profile.value.age = calcAge(data.birth_date)
  profile.value.city = data.current_city || ""
  profile.value.phone = data.phone || ""
  profile.value.strengths = data.bio || ""
  profile.value.skills = data.skills.map((s) => s.name)

  profile.value.intention.salary = formatSalary(data.expected_salary_min, data.expected_salary_max)
  profile.value.intention.cities = data.expected_city || ""

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
  { label: "\u57fa\u672c\u4fe1\u606f", done: !!profile.value.name || !!profile.value.phone },
  { label: "\u6c42\u804c\u610f\u5411", done: !!profile.value.intention.salary || !!profile.value.intention.cities },
  { label: "\u6559\u80b2\u7ecf\u5386", done: profile.value.education.length > 0 },
  { label: "\u4e13\u4e1a\u6280\u80fd", done: profile.value.skills.length > 0 },
  { label: "\u5de5\u4f5c\u7ecf\u5386", done: profile.value.work.length > 0 },
  { label: "\u9879\u76ee\u7ecf\u5386", done: profile.value.projects.length > 0 },
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
})

// ====== 表单临时数据 ======
const strengthsForm = ref("")
const educationForm = ref({ school: "", degree: "", major: "", period: "" })
const workForm = ref({ title: "", company: "", period: "", desc: "" })
const projectForm = ref({ name: "", desc: "" })
const skillInput = ref("")
const languageForm = ref({ name: "", level: "" })
const certificateForm = ref({ name: "" })

// ====== 打开/保存 对话框函数 ======
function openStrengthsDialog() {
  strengthsForm.value = profile.value.strengths
  dialogState.strengths = true
}
function saveStrengths() {
  profile.value.strengths = strengthsForm.value
  dialogState.strengths = false
  updateProfile({ bio: strengthsForm.value || null }).then(() => {
    ElMessage.success("\u4e2a\u4eba\u4f18\u52bf\u5df2\u66f4\u65b0")
  }).catch(() => {})
}

function openEducationDialog() {
  educationForm.value = { school: "", degree: "", major: "", period: "" }
  dialogState.education = true
}
function saveEducation() {
  const form = educationForm.value
  if (!form.school && !form.degree) {
    ElMessage.warning("\u8bf7\u81f3\u5c11\u586b\u5199\u5b66\u6821\u540d\u79f0\u6216\u5b66\u5386")
    return
  }
  profile.value.education.push({ ...form })
  dialogState.education = false
  const last = profile.value.education[profile.value.education.length - 1]
  updateProfile({
    school: last.school || null,
    education: last.degree || null,
    major: last.major || null,
  }).then(() => {
    ElMessage.success("\u6559\u80b2\u7ecf\u5386\u5df2\u6dfb\u52a0")
  }).catch(() => {})
}

function openWorkDialog() {
  workForm.value = { title: "", company: "", period: "", desc: "" }
  dialogState.work = true
}
function saveWork() {
  if (!workForm.value.title || !workForm.value.company) {
    ElMessage.warning("\u8bf7\u81f3\u5c11\u586b\u5199\u804c\u4f4d\u548c\u516c\u53f8\u540d\u79f0")
    return
  }
  profile.value.work.push({ ...workForm.value })
  dialogState.work = false
  ElMessage.success("\u5de5\u4f5c\u7ecf\u5386\u5df2\u6dfb\u52a0\uff08\u672c\u5730\u4fdd\u5b58\uff0c\u540e\u7aef\u540c\u6b65\u5373\u5c06\u652f\u6301\uff09")
}

function openProjectDialog() {
  projectForm.value = { name: "", desc: "" }
  dialogState.project = true
}
function saveProject() {
  if (!projectForm.value.name) {
    ElMessage.warning("\u8bf7\u586b\u5199\u9879\u76ee\u540d\u79f0")
    return
  }
  profile.value.projects.push({ ...projectForm.value })
  dialogState.project = false
  ElMessage.success("\u9879\u76ee\u7ecf\u5386\u5df2\u6dfb\u52a0\uff08\u672c\u5730\u4fdd\u5b58\uff0c\u540e\u7aef\u540c\u6b65\u5373\u5c06\u652f\u6301\uff09")
}

function openSkillDialog() {
  skillInput.value = ""
  dialogState.skill = true
}
function addSkill() {
  const val = skillInput.value.trim()
  if (!val) return
  if (profile.value.skills.includes(val)) {
    ElMessage.warning("\u8be5\u6280\u80fd\u5df2\u5b58\u5728")
    return
  }
  profile.value.skills.push(val)
  skillInput.value = ""
  updateProfile({ skills: [...profile.value.skills] }).then(() => {
    ElMessage.success("\u4e13\u4e1a\u6280\u80fd\u5df2\u6dfb\u52a0")
  }).catch(() => {})
}
function removeSkill(idx: number) {
  profile.value.skills.splice(idx, 1)
  updateProfile({ skills: [...profile.value.skills] }).then(() => {
    ElMessage.success("\u6280\u80fd\u5df2\u79fb\u9664")
  }).catch(() => {})
}

function openLanguageDialog() {
  languageForm.value = { name: "", level: "" }
  dialogState.language = true
}
function saveLanguage() {
  if (!languageForm.value.name) {
    ElMessage.warning("\u8bf7\u586b\u5199\u8bed\u8a00\u540d\u79f0")
    return
  }
  profile.value.languages.push({ ...languageForm.value })
  dialogState.language = false
  ElMessage.success("\u8bed\u8a00\u80fd\u529b\u5df2\u6dfb\u52a0\uff08\u672c\u5730\u4fdd\u5b58\uff0c\u540e\u7aef\u540c\u6b65\u5373\u5c06\u652f\u6301\uff09")
}

function openCertificateDialog() {
  certificateForm.value = { name: "" }
  dialogState.certificate = true
}
function saveCertificate() {
  if (!certificateForm.value.name) {
    ElMessage.warning("\u8bf7\u586b\u5199\u8bc1\u4e66\u540d\u79f0")
    return
  }
  profile.value.certificates.push({ ...certificateForm.value })
  dialogState.certificate = false
  ElMessage.success("\u8bc1\u4e66\u5df2\u6dfb\u52a0\uff08\u672c\u5730\u4fdd\u5b58\uff0c\u540e\u7aef\u540c\u6b65\u5373\u5c06\u652f\u6301\uff09")
}

// ====== 删除函数 ======
function removeWork(idx: number) { profile.value.work.splice(idx, 1) }
function removeProject(idx: number) { profile.value.projects.splice(idx, 1) }
function removeEducation(idx: number) { profile.value.education.splice(idx, 1) }
function removeLanguage(idx: number) { profile.value.languages.splice(idx, 1) }
function removeCertificate(idx: number) { profile.value.certificates.splice(idx, 1) }
</script>
'''

new_content = new_script + "\n" + template_content
filepath.write_text(new_content, encoding="utf-8")
print(f"Written {len(new_content)} chars ({len(filepath.read_text(encoding='utf-8').splitlines())} lines)")
