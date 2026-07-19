<script setup lang="ts">
import { ref, watch, onMounted } from "vue"
import { useRoute, useRouter } from "vue-router"
import { ElMessage } from "element-plus"
import {
  Search, Sparkles, Send, FileText, X,
} from "lucide-vue-next"
import type { JobItem, JobSearchParams, JobType } from "@/api/job"
import { listJobs, applyJob } from "@/api/job"
import { getRecommendedJobs } from "@/api/match"
import type { MatchDetail } from "@/api/match"

const route = useRoute()
const router = useRouter()
const keyword = ref((route.query.q as string) || "")
const filterCity = ref((route.query.city as string) || "")
const filterEdu = ref("")
const filterType = ref("")
const filterMajor = ref("")
const filterJobCategory = ref("")

const activeFilterTab = ref<'major' | 'category'>('major')

const showMajorModal = ref(false)
const showCityModal = ref(false)
const showCategoryModal = ref(false)

const selectedMajorFirst = ref("")
const selectedMajorSecond = ref("")
const selectedMajorThird = ref("")

const selectedCategoryFirst = ref("")
const selectedCategorySecond = ref("")
const selectedCategoryThird = ref("")

const selectedCity = ref("")

const majorCategories = ref([
  { name: "会计学", children: [
    { name: "基础会计", children: ["会计核算", "财务报表"] },
    { name: "成本会计", children: ["成本核算", "成本分析"] },
  ]},
  { name: "电子商务", children: [
    { name: "电商运营", children: ["店铺运营", "活动策划"] },
    { name: "电商客服", children: ["售前客服", "售后客服"] },
  ]},
  { name: "计算机科学与技术", children: [
    { name: "软件开发", children: ["前端开发", "后端开发", "移动端开发"] },
    { name: "测试", children: ["功能测试", "自动化测试"] },
  ]},
  { name: "软件工程", children: [
    { name: "软件设计", children: ["架构设计", "需求分析"] },
    { name: "项目管理", children: ["进度管理", "团队协调"] },
  ]},
  { name: "工商管理", children: [
    { name: "企业管理", children: ["战略管理", "运营管理"] },
    { name: "市场营销", children: ["市场调研", "品牌推广"] },
  ]},
  { name: "土木工程", children: [
    { name: "建筑工程", children: ["施工管理", "工程造价"] },
    { name: "结构工程", children: ["结构设计", "力学分析"] },
  ]},
  { name: "财务管理", children: [
    { name: "财务分析", children: ["财务报表分析", "预算管理"] },
    { name: "税务筹划", children: ["税务申报", "税收筹划"] },
  ]},
  { name: "学前教育", children: [
    { name: "幼儿教育", children: ["幼儿园教学", "早教指导"] },
    { name: "儿童心理学", children: ["儿童心理发展", "行为矫正"] },
  ]},
  { name: "市场营销", children: [
    { name: "品牌营销", children: ["品牌策划", "广告投放"] },
    { name: "新媒体运营", children: ["社交媒体运营", "内容创作"] },
  ]},
])

const jobCategories = ref([
  { name: "技术开发", children: [
    { name: "软件开发", children: ["Java开发", "Python开发", "Go开发"] },
    { name: "前端开发", children: ["Vue开发", "React开发", "小程序开发"] },
    { name: "后端开发", children: ["微服务", "数据库开发", "API开发"] },
  ]},
  { name: "产品设计", children: [
    { name: "产品经理", children: ["需求分析", "产品规划", "原型设计"] },
    { name: "UI设计", children: ["界面设计", "交互设计", "视觉设计"] },
  ]},
  { name: "运营推广", children: [
    { name: "产品运营", children: ["用户运营", "活动运营", "内容运营"] },
    { name: "市场推广", children: ["品牌推广", "广告投放", "渠道拓展"] },
  ]},
  { name: "职能岗位", children: [
    { name: "人力资源", children: ["招聘", "培训", "薪酬绩效"] },
    { name: "财务会计", children: ["会计核算", "财务管理", "审计"] },
    { name: "行政管理", children: ["办公室管理", "行政助理", "后勤保障"] },
  ]},
])

const cities = ref([
  { name: "热门城市", children: ["北京", "上海", "广州", "深圳", "杭州", "成都", "武汉", "南京"] },
  { name: "一线城市", children: ["北京", "上海", "广州", "深圳"] },
  { name: "新一线城市", children: ["杭州", "成都", "武汉", "南京", "重庆", "天津", "苏州", "西安"] },
  { name: "二线城市", children: ["宁波", "青岛", "郑州", "长沙", "沈阳", "济南", "合肥", "大连"] },
])

function selectMajorFirst(item: string) {
  selectedMajorFirst.value = item
  const firstLevel = majorCategories.value.find(cat => cat.name === item)
  if (firstLevel && firstLevel.children.length > 0) {
    selectedMajorSecond.value = firstLevel.children[0].name
    if (firstLevel.children[0].children.length > 0) {
      selectedMajorThird.value = firstLevel.children[0].children[0]
    } else {
      selectedMajorThird.value = ""
    }
  } else {
    selectedMajorSecond.value = ""
    selectedMajorThird.value = ""
  }
}

function selectMajorSecond(item: string) {
  selectedMajorSecond.value = item
  const firstLevel = majorCategories.value.find(cat => cat.name === selectedMajorFirst.value)
  if (firstLevel) {
    const secondLevel = firstLevel.children.find(cat => cat.name === item)
    if (secondLevel && secondLevel.children.length > 0) {
      selectedMajorThird.value = secondLevel.children[0]
    } else {
      selectedMajorThird.value = ""
    }
  }
}

function selectCategoryFirst(item: string) {
  selectedCategoryFirst.value = item
  const firstLevel = jobCategories.value.find(cat => cat.name === item)
  if (firstLevel && firstLevel.children.length > 0) {
    selectedCategorySecond.value = firstLevel.children[0].name
    if (firstLevel.children[0].children.length > 0) {
      selectedCategoryThird.value = firstLevel.children[0].children[0]
    } else {
      selectedCategoryThird.value = ""
    }
  } else {
    selectedCategorySecond.value = ""
    selectedCategoryThird.value = ""
  }
}

function selectCategorySecond(item: string) {
  selectedCategorySecond.value = item
  const firstLevel = jobCategories.value.find(cat => cat.name === selectedCategoryFirst.value)
  if (firstLevel) {
    const secondLevel = firstLevel.children.find(cat => cat.name === item)
    if (secondLevel && secondLevel.children.length > 0) {
      selectedCategoryThird.value = secondLevel.children[0]
    } else {
      selectedCategoryThird.value = ""
    }
  }
}

function confirmMajorSelect() {
  if (selectedMajorThird.value) {
    filterMajor.value = selectedMajorThird.value
  } else if (selectedMajorSecond.value) {
    filterMajor.value = selectedMajorSecond.value
  } else if (selectedMajorFirst.value) {
    filterMajor.value = selectedMajorFirst.value
  }
  showMajorModal.value = false
}

function confirmCategorySelect() {
  if (selectedCategoryThird.value) {
    filterJobCategory.value = selectedCategoryThird.value
  } else if (selectedCategorySecond.value) {
    filterJobCategory.value = selectedCategorySecond.value
  } else if (selectedCategoryFirst.value) {
    filterJobCategory.value = selectedCategoryFirst.value
  }
  showCategoryModal.value = false
}

function confirmCitySelect() {
  filterCity.value = selectedCity.value
  showCityModal.value = false
}

function clearMajorFilter() {
  filterMajor.value = ""
  selectedMajorFirst.value = ""
  selectedMajorSecond.value = ""
  selectedMajorThird.value = ""
}

function clearCategoryFilter() {
  filterJobCategory.value = ""
  selectedCategoryFirst.value = ""
  selectedCategorySecond.value = ""
  selectedCategoryThird.value = ""
}

const jobs = ref<JobItem[]>([])
const total = ref(0)
const page = ref(1)
const size = ref(10)
const loading = ref(false)
const appliedJobIds = ref<Set<number>>(new Set())

const typeDisplay: Record<string, string> = {
  FULL_TIME: "全职",
  PART_TIME: "兼职",
  INTERN: "实习",
}

const logoColors = [
  "#dbeafe", "#d4edda", "#e8d5f5", "#fff3cd", "#f8d7da",
]

function logoInfo(name: string | null) {
  const first = (name || "?").charAt(0)
  const idx = (name || "").length % logoColors.length
  return { char: first, color: logoColors[idx] }
}

const matchMap = ref<Map<number, MatchDetail>>(new Map())
const matchLoaded = ref(false)

async function fetchMatchData() {
  matchLoaded.value = false
  try {
    const res = await getRecommendedJobs()
    const jobs = res.data.data.jobs
    const map = new Map<number, MatchDetail>()
    for (const job of jobs) {
      map.set(job.job_id, job.match_detail)
    }
    matchMap.value = map
  } catch { }
  matchLoaded.value = true
}

function getMatchDetail(jobId: number): MatchDetail | undefined {
  return matchMap.value.get(jobId)
}

function matchClass(score: number) {
  if (score >= 80) return "match-high"
  if (score >= 60) return "match-mid"
  return "match-low"
}

function salaryDisplay(min: number | null, max: number | null): string {
  const minK = min && min > 0 ? Math.round(min / 1000) : null
  const maxK = max && max > 0 ? Math.round(max / 1000) : null
  
  if (minK != null && maxK != null) {
    if (minK === maxK) return `${minK}K`
    return `${minK}-${maxK}K`
  }
  if (minK != null) return `${minK}K起`
  if (maxK != null) return `最高${maxK}K`
  return "面议"
}

function expDisplay(min: number | null): string {
  if (min == null) return "经验不限"
  if (min === 0) return "在校/应届"
  return `${min}年以上`
}

function educationDisplay(edu: string | null): string {
  return edu || "学历不限"
}

function typeLabel(t: string): string {
  return typeDisplay[t] || t
}

async function fetchJobs() {
  loading.value = true
  try {
    const params: JobSearchParams = { page: page.value, size: size.value }
    if (keyword.value) params.keyword = keyword.value
    if (filterCity.value) params.city = filterCity.value
    if (filterEdu.value) params.education_requirement = filterEdu.value
    if (filterType.value) {
      const map: Record<string, JobType> = { "全职": "FULL_TIME", "实习": "INTERN", "兼职": "PART_TIME" }
      params.job_type = map[filterType.value]
    }
    if (filterMajor.value) params.major = filterMajor.value
    if (filterJobCategory.value) params.job_category = filterJobCategory.value
    const res = await listJobs(params)
    jobs.value = res.data.data.records
    total.value = res.data.data.total
  } catch { } finally { loading.value = false }
}

function goDetail(jobId: number) {
  router.push(`/user/jobs/${jobId}`)
}

async function handleApply(jobId: number) {
  if (appliedJobIds.value.has(jobId)) return
  try {
    await applyJob(jobId)
    appliedJobIds.value = new Set([...appliedJobIds.value, jobId])
    ElMessage.success("投递成功")
  } catch (err: any) {
    if (err?.response?.data?.code === 409) {
      appliedJobIds.value = new Set([...appliedJobIds.value, jobId])
      ElMessage.info("已投递过该岗位")
    }
  }
}

function goPage(p: number) { page.value = p; fetchJobs() }
const totalPages = () => Math.ceil(total.value / size.value)

watch([keyword, filterCity, filterEdu, filterType, filterMajor, filterJobCategory], () => { page.value = 1; fetchJobs() })
onMounted(async () => { await fetchJobs(); await fetchMatchData() })

function clearFilters() {
  keyword.value = ""; filterCity.value = ""; filterEdu.value = ""; filterType.value = ""
  filterMajor.value = ""; filterJobCategory.value = ""
  selectedCity.value = ""
}
</script>

<template>
  <div class="search-page">
    <div class="search-container">
      <div class="search-hero">
        <div class="search-box">
          <Sparkles :size="20" class="sparkle-icon" />
          <input v-model="keyword" type="text" placeholder="搜索岗位名称、公司、城市..." />
          <button class="search-btn" @click="fetchJobs"><Search :size="16" /> 搜索</button>
        </div>
      </div>

      <div class="filter-container">
        <div class="filter-tabs">
          <button 
            class="tab-btn" 
            :class="{ active: activeFilterTab === 'major' }"
            @click="activeFilterTab = 'major'"
          >
            <Sparkles :size="14" /> 按专业筛选
          </button>
          <button 
            class="tab-btn" 
            :class="{ active: activeFilterTab === 'category' }"
            @click="activeFilterTab = 'category'"
          >
            <Search :size="14" /> 按职类筛选
          </button>
        </div>

        <div v-if="activeFilterTab === 'major'" class="filter-content">
          <div class="filter-section">
            <span class="section-title">专业分类</span>
            <div class="filter-options">
              <button 
                v-for="cat in majorCategories" 
                :key="cat.name"
                class="filter-tag"
                :class="{ active: filterMajor === cat.name }"
                @click="filterMajor === cat.name ? clearMajorFilter() : (filterMajor = cat.name)"
              >
                {{ cat.name }}
              </button>
              <button class="filter-more" @click="showMajorModal = true">
                更多专业 <X :size="12" />
              </button>
            </div>
          </div>
        </div>

        <div v-if="activeFilterTab === 'category'" class="filter-content">
          <div class="filter-section">
            <span class="section-title">职位分类</span>
            <div class="filter-options">
              <button 
                v-for="cat in jobCategories" 
                :key="cat.name"
                class="filter-tag"
                :class="{ active: filterJobCategory === cat.name }"
                @click="filterJobCategory === cat.name ? clearCategoryFilter() : (filterJobCategory = cat.name)"
              >
                {{ cat.name }}
              </button>
              <button class="filter-more" @click="showCategoryModal = true">
                更多职类 <X :size="12" />
              </button>
            </div>
          </div>
        </div>

        <div class="filter-section">
          <span class="section-title">工作地点</span>
          <div class="filter-options">
            <button 
              v-for="city in ['全国', '北京', '上海', '广州', '深圳', '杭州', '成都', '武汉', '南京', '西安']" 
              :key="city"
              class="filter-tag"
              :class="{ active: filterCity === city }"
              @click="filterCity === city ? filterCity = '' : filterCity = city"
            >
              {{ city }}
            </button>
            <button class="filter-more" @click="showCityModal = true">
              更多城市 <X :size="12" />
            </button>
          </div>
        </div>

        <div class="other-filters">
          <select v-model="filterEdu" class="filter-select">
            <option value="">学历</option>
            <option value="大专">大专</option>
            <option value="本科">本科</option>
            <option value="硕士">硕士</option>
            <option value="不限">不限</option>
          </select>
          <select v-model="filterType" class="filter-select">
            <option value="">工作性质</option>
            <option value="全职">全职</option>
            <option value="实习">实习</option>
            <option value="兼职">兼职</option>
          </select>
        </div>
      </div>

      <div class="job-list">
        <div v-if="loading" class="empty-state">加载中...</div>
        <template v-else-if="jobs.length > 0">
          <div v-for="job in jobs" :key="job.id" class="job-card" @click="goDetail(job.id)">
            <div class="card-inner">
              <div class="card-left">
                <div class="card-title-row">
                  <span class="card-title">{{ job.title }}</span>
                  <span v-if="job.city" class="tag-city">「{{ job.city }}」</span>
                  <span v-if="job.is_campus" class="tag-campus">校招网申</span>
                  <span v-if="job.company_type" class="tag-company-type">{{ job.company_type }}</span>
                </div>
                <div class="card-tags">
                  <span class="chip">{{ expDisplay(job.experience_min) }}</span>
                  <span class="chip">{{ educationDisplay(job.education_requirement) }}</span>
                  <span class="chip">{{ typeLabel(job.job_type) }}</span>
                </div>
                <div class="card-company">
                  <div class="company-logo" :style="{ background: logoInfo(job.company_name).color }">{{ logoInfo(job.company_name).char }}</div>
                  <div class="company-info">
                    <span class="company-name">{{ job.company_name || "未知企业" }}</span>
                    <span v-if="job.industry || job.scale || job.company_type" class="company-meta">
                      <template v-if="job.industry">{{ job.industry }}</template>
                      <template v-if="job.industry && job.scale"> | </template>
                      <template v-if="job.scale">{{ job.scale }}</template>
                      <template v-if="(job.industry || job.scale) && job.company_type"> | </template>
                      <template v-if="job.company_type">{{ job.company_type }}</template>
                    </span>
                  </div>
                </div>
              </div>

              <div class="card-center">
                <div class="match-dashboard">
                  <div class="circle-scores">
                    <div class="circle-score-item">
                      <svg class="score-circle" viewBox="0 0 52 52">
                        <circle cx="26" cy="26" r="22" class="circle-bg" />
                        <circle cx="26" cy="26" r="22" class="circle-fill skill" :style="{ strokeDasharray: (getMatchDetail(job.id)?.breakdown.skill.score ? Math.round((getMatchDetail(job.id)!.breakdown.skill.score / 10) * 100) : 0) * 1.38 + ' 138' }" transform="rotate(-90, 26, 26)" />
                        <text x="26" y="28" text-anchor="middle" class="circle-text">{{ getMatchDetail(job.id)?.breakdown.skill.score ? Math.round((getMatchDetail(job.id)!.breakdown.skill.score / 10) * 100) : 0 }}%</text>
                      </svg>
                      <span class="circle-label">技能</span>
                    </div>
                    <div class="circle-score-item">
                      <svg class="score-circle" viewBox="0 0 52 52">
                        <circle cx="26" cy="26" r="22" class="circle-bg" />
                        <circle cx="26" cy="26" r="22" class="circle-fill exp" :style="{ strokeDasharray: (getMatchDetail(job.id)?.breakdown.exp.score ? Math.round((getMatchDetail(job.id)!.breakdown.exp.score / 10) * 100) : 0) * 1.38 + ' 138' }" transform="rotate(-90, 26, 26)" />
                        <text x="26" y="28" text-anchor="middle" class="circle-text">{{ getMatchDetail(job.id)?.breakdown.exp.score ? Math.round((getMatchDetail(job.id)!.breakdown.exp.score / 10) * 100) : 0 }}%</text>
                      </svg>
                      <span class="circle-label">经验</span>
                    </div>
                    <div class="circle-score-item">
                      <svg class="score-circle" viewBox="0 0 52 52">
                        <circle cx="26" cy="26" r="22" class="circle-bg" />
                        <circle cx="26" cy="26" r="22" class="circle-fill city" :style="{ strokeDasharray: (getMatchDetail(job.id)?.breakdown.city.score ? Math.round((getMatchDetail(job.id)!.breakdown.city.score / 10) * 100) : 0) * 1.38 + ' 138' }" transform="rotate(-90, 26, 26)" />
                        <text x="26" y="28" text-anchor="middle" class="circle-text">{{ getMatchDetail(job.id)?.breakdown.city.score ? Math.round((getMatchDetail(job.id)!.breakdown.city.score / 10) * 100) : 0 }}%</text>
                      </svg>
                      <span class="circle-label">位置</span>
                    </div>
                    <div class="circle-score-item">
                      <svg class="score-circle" viewBox="0 0 52 52">
                        <circle cx="26" cy="26" r="22" class="circle-bg" />
                        <circle cx="26" cy="26" r="22" class="circle-fill edu" :style="{ strokeDasharray: (getMatchDetail(job.id)?.breakdown.edu.score ? Math.round((getMatchDetail(job.id)!.breakdown.edu.score / 12) * 100) : 0) * 1.38 + ' 138' }" transform="rotate(-90, 26, 26)" />
                        <text x="26" y="28" text-anchor="middle" class="circle-text">{{ getMatchDetail(job.id)?.breakdown.edu.score ? Math.round((getMatchDetail(job.id)!.breakdown.edu.score / 12) * 100) : 0 }}%</text>
                      </svg>
                      <span class="circle-label">文化</span>
                    </div>
                    <div class="circle-score-item main-score">
                      <svg class="score-circle" viewBox="0 0 52 52">
                        <circle cx="26" cy="26" r="22" class="circle-bg" />
                        <circle cx="26" cy="26" r="22" class="circle-fill main" :class="matchClass(getMatchDetail(job.id)?.score || 0)" :style="{ strokeDasharray: (getMatchDetail(job.id)?.score || 0) * 1.38 + ' 138' }" transform="rotate(-90, 26, 26)" />
                        <text x="26" y="28" text-anchor="middle" class="circle-text">{{ getMatchDetail(job.id)?.score ? Math.round(getMatchDetail(job.id)!.score) : 0 }}%</text>
                      </svg>
                      <span class="circle-label">总体匹配</span>
                    </div>
                  </div>
                </div>
              </div>

              <div class="card-right">
                <span class="card-salary">{{ salaryDisplay(job.salary_min, job.salary_max) }}</span>
                <button class="apply-btn" :class="{ applied: appliedJobIds.has(job.id) }" :disabled="appliedJobIds.has(job.id)" @click.stop="handleApply(job.id)">
                  <Send :size="14" /> {{ appliedJobIds.has(job.id) ? "已投递" : "立即投递" }}
                </button>
              </div>
            </div>
          </div>
        </template>
        <div v-else class="empty-state">暂无匹配职位</div>

        <div v-if="totalPages() > 1" class="pagination-bar">
          <button class="page-btn" :disabled="page <= 1" @click="goPage(page - 1)">上一页</button>
          <span class="page-info">{{ page }} / {{ totalPages() }}</span>
          <button class="page-btn" :disabled="page >= totalPages()" @click="goPage(page + 1)">下一页</button>
        </div>
      </div>

      <!-- 专业选择弹窗 -->
      <ElDialog v-model="showMajorModal" title="请选择专业" width="700px" :close-on-click-modal="false" :show-footer="false">
        <div class="modal-content">
          <div class="modal-column">
            <div class="column-title">一级分类</div>
            <div class="column-items">
              <button 
                v-for="cat in majorCategories" 
                :key="cat.name"
                class="modal-item"
                :class="{ active: selectedMajorFirst === cat.name }"
                @click="selectMajorFirst(cat.name)"
              >
                {{ cat.name }}
              </button>
            </div>
          </div>
          <div class="modal-column">
            <div class="column-title">二级分类</div>
            <div class="column-items">
              <button 
                v-for="cat in (majorCategories.find(c => c.name === selectedMajorFirst)?.children || [])" 
                :key="cat.name"
                class="modal-item"
                :class="{ active: selectedMajorSecond === cat.name }"
                @click="selectMajorSecond(cat.name)"
              >
                {{ cat.name }}
              </button>
            </div>
          </div>
          <div class="modal-column">
            <div class="column-title">三级分类</div>
            <div class="column-items">
              <button 
                v-for="item in ((majorCategories.find(c => c.name === selectedMajorFirst)?.children.find(c => c.name === selectedMajorSecond)?.children) || [])" 
                :key="item"
                class="modal-item"
                :class="{ active: selectedMajorThird === item }"
                @click="selectedMajorThird = item"
              >
                {{ item }}
              </button>
            </div>
          </div>
        </div>
        <div class="modal-footer">
          <button class="modal-btn cancel" @click="showMajorModal = false">取消</button>
          <button class="modal-btn confirm" @click="confirmMajorSelect">确认</button>
        </div>
      </ElDialog>

      <!-- 城市选择弹窗 -->
      <ElDialog v-model="showCityModal" title="请选择城市" width="500px" :close-on-click-modal="false" :show-footer="false">
        <div class="city-modal-content">
          <div v-for="group in cities" :key="group.name" class="city-group">
            <div class="city-group-title">{{ group.name }}</div>
            <div class="city-items">
              <button 
                v-for="city in group.children" 
                :key="city"
                class="city-item"
                :class="{ active: selectedCity === city }"
                @click="selectedCity = city"
              >
                {{ city }}
              </button>
            </div>
          </div>
        </div>
        <div class="modal-footer">
          <button class="modal-btn cancel" @click="showCityModal = false">取消</button>
          <button class="modal-btn confirm" @click="confirmCitySelect">确认</button>
        </div>
      </ElDialog>

      <!-- 职位分类选择弹窗 -->
      <ElDialog v-model="showCategoryModal" title="请选择职位分类" width="700px" :close-on-click-modal="false" :show-footer="false">
        <div class="modal-content">
          <div class="modal-column">
            <div class="column-title">一级分类</div>
            <div class="column-items">
              <button 
                v-for="cat in jobCategories" 
                :key="cat.name"
                class="modal-item"
                :class="{ active: selectedCategoryFirst === cat.name }"
                @click="selectCategoryFirst(cat.name)"
              >
                {{ cat.name }}
              </button>
            </div>
          </div>
          <div class="modal-column">
            <div class="column-title">二级分类</div>
            <div class="column-items">
              <button 
                v-for="cat in (jobCategories.find(c => c.name === selectedCategoryFirst)?.children || [])" 
                :key="cat.name"
                class="modal-item"
                :class="{ active: selectedCategorySecond === cat.name }"
                @click="selectCategorySecond(cat.name)"
              >
                {{ cat.name }}
              </button>
            </div>
          </div>
          <div class="modal-column">
            <div class="column-title">三级分类</div>
            <div class="column-items">
              <button 
                v-for="item in ((jobCategories.find(c => c.name === selectedCategoryFirst)?.children.find(c => c.name === selectedCategorySecond)?.children) || [])" 
                :key="item"
                class="modal-item"
                :class="{ active: selectedCategoryThird === item }"
                @click="selectedCategoryThird = item"
              >
                {{ item }}
              </button>
            </div>
          </div>
        </div>
        <div class="modal-footer">
          <button class="modal-btn cancel" @click="showCategoryModal = false">取消</button>
          <button class="modal-btn confirm" @click="confirmCategorySelect">确认</button>
        </div>
      </ElDialog>
    </div>
  </div>
</template>

<style scoped lang="scss">
.search-page { padding: 0; min-height: 100vh; background: rgb(245, 247, 252); }
.search-container { max-width: 1200px; margin: 0 auto; }
.search-hero { height: 80px; display: flex; align-items: center; background: #fff; border-radius: 12px; margin: 0 auto; width: 1200px; box-shadow: 0 2px 8px rgba(0,0,0,0.06); }
.search-box { display: flex; align-items: center; width: 800px; margin: 0 auto; border: 2px solid #bfc9c3; border-radius: 16px; padding: 4px 6px 4px 16px; transition: all 0.3s; background: #fff; &:focus-within { border-color: #003527; box-shadow: 0 0 0 3px rgba(0,53,39,0.06); } input { flex: 1; border: none; outline: none; font-size: 15px; padding: 10px 12px; color: #121c28; &::placeholder { color: #bfc9c3; } } }
.sparkle-icon { color: #003527; flex-shrink: 0; }
.search-btn { display: flex; align-items: center; gap: 6px; padding: 10px 24px; border: none; border-radius: 12px; background: #003527; color: #fff; font-size: 14px; font-weight: 600; cursor: pointer; transition: all 0.2s; &:hover { background: #064e3b; } }

/* 筛选容器 */
.filter-container { 
  background: #fff; 
  width: 1200px; 
  height: 240px; 
  margin: 16px auto; 
  border-radius: 12px; 
  padding: 12px; 
  box-shadow: 0 2px 8px rgba(0,0,0,0.06);
}

/* 标签切换 */
.filter-tabs { 
  display: flex; 
  gap: 8px; 
  margin-bottom: 8px; 
  padding-bottom: 8px; 
  border-bottom: 1px solid #f0f0f0;
}
.tab-btn { 
  display: flex; 
  align-items: center; 
  gap: 4px; 
  padding: 6px 14px; 
  border: 2px solid transparent; 
  border-radius: 16px; 
  background: #f8f9ff; 
  color: #404944; 
  font-size: 13px; 
  font-weight: 500; 
  cursor: pointer; 
  transition: all 0.2s; 
  &:hover { background: #eef2f7; } 
  &.active { border-color: #003527; background: rgba(0,53,39,0.06); color: #003527; }
}

/* 筛选内容 */
.filter-content { margin-bottom: 8px; }
.filter-section { margin-bottom: 8px; }
.section-title { 
  display: inline-block; 
  padding: 2px 0; 
  margin-bottom: 6px; 
  font-size: 12px; 
  font-weight: 600; 
  color: #121c28; 
}
.filter-options { 
  display: flex; 
  flex-wrap: wrap; 
  gap: 6px; 
}
.filter-tag { 
  padding: 4px 12px; 
  border-radius: 14px; 
  border: 1px solid #e4e7ed; 
  background: #fff; 
  color: #404944; 
  font-size: 12px; 
  cursor: pointer; 
  transition: all 0.2s; 
  &:hover { border-color: #bfc9c3; background: #fafafa; } 
  &.active { border-color: #003527; background: rgba(0,53,39,0.08); color: #003527; }
}
.filter-more { 
  display: flex; 
  align-items: center; 
  gap: 3px; 
  padding: 4px 10px; 
  border-radius: 14px; 
  border: 1px solid #e4e7ed; 
  background: #fff; 
  color: #404944; 
  font-size: 12px; 
  cursor: pointer; 
  transition: all 0.2s; 
  &:hover { border-color: #003527; color: #003527; }
}

/* 其他筛选 */
.other-filters { 
  display: flex; 
  gap: 8px; 
  padding-top: 8px; 
  border-top: 1px solid #f0f0f0;
}
.filter-select { 
  appearance: none; 
  padding: 4px 20px 4px 8px; 
  border: 1px solid #bfc9c3; 
  border-radius: 6px; 
  font-size: 11px; 
  color: #404944; 
  background: #fff; 
  cursor: pointer; 
  outline: none; 
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='12' height='12' viewBox='0 0 24 24' fill='none' stroke='%23909399' stroke-width='2'%3E%3Cpolyline points='6 9 12 15 18 9'/%3E%3C/svg%3E"); 
  background-repeat: no-repeat; 
  background-position: right 4px center; 
  &:focus { border-color: #003527; } 
}

/* 模态框样式 */
.modal-content { 
  display: flex; 
  gap: 0; 
  height: 320px; 
  border: 1px solid #e4e7ed; 
  border-radius: 8px; 
  overflow: hidden;
}
.modal-column { 
  flex: 1; 
  display: flex; 
  flex-direction: column; 
  border-right: 1px solid #e4e7ed; 
  &:last-child { border-right: none; }
}
.column-title { 
  padding: 12px 16px; 
  font-size: 12px; 
  font-weight: 600; 
  color: #404944; 
  background: #fafafa; 
}
.column-items { 
  flex: 1; 
  overflow-y: auto; 
  padding: 8px;
}
.modal-item { 
  display: block; 
  width: 100%; 
  padding: 10px 12px; 
  text-align: left; 
  border: none; 
  background: none; 
  color: #404944; 
  font-size: 13px; 
  cursor: pointer; 
  border-radius: 6px; 
  transition: all 0.2s; 
  &:hover { background: #f8f9ff; } 
  &.active { background: rgba(0,53,39,0.08); color: #003527; font-weight: 500; }
}
.modal-footer { 
  display: flex; 
  justify-content: flex-end; 
  gap: 12px; 
  margin-top: 20px; 
  padding-top: 16px; 
  border-top: 1px solid #f0f0f0;
}
.modal-btn { 
  padding: 8px 24px; 
  border-radius: 8px; 
  font-size: 14px; 
  font-weight: 500; 
  cursor: pointer; 
  transition: all 0.2s; 
  &.cancel { 
    border: 1px solid #bfc9c3; 
    background: #fff; 
    color: #404944; 
    &:hover { background: #f5f5f5; } 
  } 
  &.confirm { 
    border: none; 
    background: #003527; 
    color: #fff; 
    &:hover { background: #064e3b; } 
  }
}

/* 城市选择弹窗 */
.city-modal-content { 
  max-height: 300px; 
  overflow-y: auto;
}
.city-group { margin-bottom: 16px; }
.city-group-title { 
  font-size: 12px; 
  font-weight: 600; 
  color: #404944; 
  margin-bottom: 8px; 
  padding-left: 4px;
}
.city-items { 
  display: flex; 
  flex-wrap: wrap; 
  gap: 8px;
}
.city-item { 
  padding: 6px 16px; 
  border-radius: 20px; 
  border: 1px solid #e4e7ed; 
  background: #fff; 
  color: #404944; 
  font-size: 13px; 
  cursor: pointer; 
  transition: all 0.2s; 
  &:hover { border-color: #bfc9c3; } 
  &.active { border-color: #003527; background: rgba(0,53,39,0.08); color: #003527; }
}

.job-list { padding: 0; display: flex; flex-direction: column; gap: 16px; max-width: 1200px; margin: 0 auto; }
.job-card { width: 1200px; padding: 20px 24px; background: #fff; border-radius: 16px; border: 1px solid #e8ecf1; cursor: pointer; transition: all 0.25s cubic-bezier(0.22, 1, 0.36, 1); box-shadow: 0 1px 3px rgba(0,0,0,0.04); }
.job-card:hover { box-shadow: 0 8px 25px rgba(0,0,0,0.10); transform: translateY(-2px); border-color: #d0d5dd; }
.job-card:hover .card-title { color: #003527; }
.job-card:hover .apply-btn:not(.applied):not(:disabled) { background: #003527; color: #fff; border-color: #003527; }
.card-inner { display: flex; gap: 24px; align-items: stretch; }
.card-left { flex: 1; min-width: 0; display: flex; flex-direction: column; }
.card-title-row { display: flex; align-items: center; gap: 8px; flex-wrap: wrap; margin-bottom: 8px; }
.card-title { font-size: 18px; font-weight: 700; color: #121c28; transition: color 0.2s; }
.tag-city { font-size: 13px; color: #404944; font-weight: 500; }
.tag-campus { font-size: 11px; padding: 2px 10px; border-radius: 4px; background: #fff3cd; color: #856404; font-weight: 600; }
.tag-company-type { font-size: 11px; padding: 2px 10px; border-radius: 4px; background: #003527; color: #fff; font-weight: 600; }
.card-tags { display: flex; gap: 8px; flex-wrap: wrap; margin-bottom: 10px; }
.chip { font-size: 12px; padding: 3px 12px; border-radius: 4px; background: #f3f4f5; color: #404944; }
.card-company { display: flex; align-items: center; gap: 10px; }
.company-logo { width: 36px; height: 36px; border-radius: 8px; display: flex; align-items: center; justify-content: center; font-size: 16px; font-weight: 700; flex-shrink: 0; }
.company-info { display: flex; flex-direction: column; gap: 2px; }
.company-name { font-size: 14px; font-weight: 600; color: #121c28; }
.company-meta { font-size: 12px; color: #404944; }

.card-center { flex: 1.2; min-width: 0; display: flex; flex-direction: column; }
.match-dashboard { background: #ffffff; border-radius: 12px; padding: 14px; flex: 1; display: flex; flex-direction: column; }
.circle-scores { display: grid; grid-template-columns: repeat(5, 1fr); gap: 8px; flex: 1; }
.circle-score-item { display: flex; flex-direction: column; align-items: center; gap: 4px; }
.score-circle { width: 52px; height: 52px; }
.circle-bg { fill: none; stroke: #bfc9c3; stroke-width: 4; }
.circle-fill { fill: none; stroke-width: 4; stroke-linecap: round; transition: stroke-dasharray 0.6s ease; &.skill { stroke: #003527; } &.exp { stroke: #064e3b; } &.city { stroke: #f59e0b; } &.edu { stroke: #8b5cf6; } &.main.match-high { stroke: #198754; } &.main.match-mid { stroke: #b8860b; } &.main.match-low { stroke: #dc3545; } }
.circle-text { font-size: 10px; font-weight: 700; fill: #121c28; }
.circle-label { font-size: 10px; color: #404944; }

.card-right { display: flex; flex-direction: column; align-items: flex-end; gap: 14px; flex-shrink: 0; padding-left: 24px; min-width: 160px; }
.card-salary { font-size: 22px; font-weight: 700; color: #c0392b; white-space: nowrap; }
.apply-btn { display: flex; align-items: center; justify-content: center; gap: 6px; padding: 8px 24px; border-radius: 999px; border: 1px solid #bfc9c3; background: #fff; color: #404944; font-size: 13px; font-weight: 600; cursor: pointer; transition: all 0.25s; width: 100%; }
.apply-btn:hover:not(.applied):not(:disabled) { border-color: #003527; color: #003527; }
.apply-btn.applied, .apply-btn:disabled { background: #d4edda; color: #155724; border-color: #d4edda; cursor: default; }
.empty-state { text-align: center; padding: 80px 24px; color: #404944; font-size: 15px; }
.pagination-bar { display: flex; align-items: center; justify-content: center; gap: 12px; padding: 24px 0; }
.page-btn { padding: 6px 16px; border-radius: 6px; border: 1px solid #bfc9c3; background: #fff; color: #404944; font-size: 13px; cursor: pointer; transition: all 0.2s; }
.page-btn:hover:not(:disabled) { border-color: #003527; color: #003527; }
.page-btn:disabled { opacity: 0.4; cursor: default; }
.page-info { font-size: 13px; color: #404944; }
</style>