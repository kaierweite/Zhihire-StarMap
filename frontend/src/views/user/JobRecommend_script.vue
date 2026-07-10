<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  MapPin, GraduationCap, Briefcase, Building2, Send, Brain, FileText,
  ChevronDown, X, SlidersHorizontal, ArrowUpDown, Loader2,
} from 'lucide-vue-next'
import { getRecommendedJobs, applyMatchJob } from '@/api/match'
import { getJobDetail } from '@/api/job'
import type { JobDetail as JobDetailType } from '@/api/job'

// ====== 筛选状态 ======
const filterCity = ref('')
const filterEdu = ref('')
const filterType = ref('')
const filterCompanyType = ref('')
const filterSalary = ref('')
const sortBy = ref<'match' | 'salary'>('match')
const currentPage = ref(1)
const pageSize = 5
const loading = ref(true)
const error = ref('')

const jobTypeMap: Record<string, string> = {
  FULL_TIME: '全职',
  PART_TIME: '兼职',
  INTERN: '实习',
}

// ====== 数据类型 ======
interface Job {
  id: number
  resume_id: number
  title: string
  company: string
  logo: string
  logoColor: string
  city: string
  exp: string
  edu: string
  salary: string
  salaryNum: number
  type: string
  companyType: string
  industry: string
  companySize: string
  score: number
  tags: string[]
  skillScore: number
  eduScore: number
  expScore: number
  cityScore: number
  rationale: string
  graphHints: string[]
  applied: boolean
}

function scaleScore(value: number, max: number): number {
  return Math.min(Math.round((value / max) * 100), 100)
}

// ====== 获取推荐数据 ======
const allJobs = ref<Job[]>([])

async function fetchRecommendations() {
  loading.value = true
  error.value = ''
  try {
    const res = await getRecommendedJobs()
    const jobs = res.data.data.jobs

    // 并行获取岗位详情以补充 city / salary 等信息
    const details = await Promise.all(
      jobs.map((job) =>
        getJobDetail(job.job_id)
          .then((r) => r.data.data)
          .catch((): null => null),
      ),
    )

    allJobs.value = jobs.map((job, idx) => {
      const detail: JobDetailType | null = details[idx]
      const md = job.match_detail
      return {
        id: job.job_id,
        resume_id: job.resume_id,
        title: job.title,
        company: job.company_name,
        score: Math.round(job.score),
        skillScore: scaleScore(md.breakdown.skill.score, 10),
        eduScore: scaleScore(md.breakdown.edu.score, 12),
        expScore: scaleScore(md.breakdown.exp.score, 10),
        cityScore: scaleScore(md.breakdown.city.score, 10),
        rationale: md.rationale,
        graphHints: md.graph_hints,
        // 以下字段从岗位详情补充，缺失时用空值
        city: detail?.city || '',
        exp: detail?.experience_min ? `${detail.experience_min}年` : '',
        edu: detail?.education_requirement || '',
        type: detail?.job_type ? (jobTypeMap[detail.job_type] || detail.job_type) : '',
        salary:
          detail?.salary_min != null
            ? `${detail.salary_min}-${detail.salary_max ?? '?'}K`
            : '',
        salaryNum: detail?.salary_min ?? 0,
        companyType: '',
        industry: '',
        companySize: '',
        tags: ['AI推荐'],
        logo: job.company_name.charAt(0),
        logoColor: '#dbeafe',
        applied: false,
      }
    })
  } catch (e: any) {
    error.value = e?.message || '加载推荐失败'
    allJobs.value = []
  } finally {
    loading.value = false
  }
}

onMounted(fetchRecommendations)

// ====== 筛选逻辑 ======
const filteredJobs = computed(() => {
  let result = allJobs.value.filter((j) => {
    if (filterCity.value && j.city !== filterCity.value) return false
    if (filterEdu.value && j.edu !== filterEdu.value) return false
    if (filterType.value && j.type !== filterType.value) return false
    if (filterCompanyType.value && j.companyType !== filterCompanyType.value) return false
    if (filterSalary.value) {
      const parts = filterSalary.value.split('-')
      const min = Number(parts[0]) || 0
      const max = Number(parts[1]) || 999
      if (j.salaryNum < min || j.salaryNum > max) return false
    }
    return true
  })
  result.sort((a, b) =>
    sortBy.value === 'match' ? b.score - a.score : b.salaryNum - a.salaryNum,
  )
  return result
})

const pagedJobs = computed(() => {
  const start = (currentPage.value - 1) * pageSize
  return filteredJobs.value.slice(start, start + pageSize)
})

const totalPages = computed(() => Math.ceil(filteredJobs.value.length / pageSize))

function clearFilters() {
  filterCity.value = ''
  filterEdu.value = ''
  filterType.value = ''
  filterCompanyType.value = ''
  filterSalary.value = ''
  currentPage.value = 1
}

function matchClass(score: number) {
  if (score >= 80) return 'match-high'
  if (score >= 60) return 'match-mid'
  return 'match-low'
}

async function handleApply(job: Job) {
  try {
    await ElMessageBox.confirm(
      `确认投递「${job.title} · ${job.company}」？`,
      '投递确认',
      {
        confirmButtonText: '确认投递',
        cancelButtonText: '取消',
        type: 'info',
      },
    )
    await applyMatchJob({ job_id: job.id, resume_id: job.resume_id })
    job.applied = true
    ElMessage.success(`已投递「${job.title}」，企业端已收到你的简历`)
  } catch {
    /* cancelled by user */
  }
}
</script>
