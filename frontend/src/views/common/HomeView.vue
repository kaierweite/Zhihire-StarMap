<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, nextTick } from "vue"
import { useRouter } from "vue-router"
import { useAuthStore } from "@/store/auth"
import AppHeader from "@/components/AppHeader.vue"
import { useScrollReveal } from "@/composables/useScrollReveal"
import {
  Search, MapPin, ChevronLeft, ChevronRight, Briefcase, Bell, ArrowRight,
  Network, Sparkles, Route, ChevronRightIcon, ChevronDown,
} from 'lucide-vue-next'

const router = useRouter()
const authStore = useAuthStore()
const page = ref()
useScrollReveal(page)

// ====== 英雄轮播 ======
const heroSlides = [
  'https://images.unsplash.com/photo-1521737604893-d14cc237f11d?w=1920&q=80&auto=format',
  'https://images.unsplash.com/photo-1522202176988-66273c2fd55f?w=1920&q=80&auto=format',
  'https://images.unsplash.com/photo-1542744173-8e7e53415bb0?w=1920&q=80&auto=format',
  'https://images.unsplash.com/photo-1559136555-9303baea8ebd?w=1920&q=80&auto=format',
]
const currentSlide = ref(0)
let slideTimer = null
function nextSlide() { currentSlide.value = (currentSlide.value + 1) % heroSlides.length }
function prevSlide() { currentSlide.value = (currentSlide.value - 1 + heroSlides.length) % heroSlides.length }
function goToSlide(i) { currentSlide.value = i }
// ====== 推广横幅轮播 ======
const promoSlides = [
  'https://images.unsplash.com/photo-1552664730-d307ca884978?w=1200&q=80&auto=format',
  'https://images.unsplash.com/photo-1553877522-43269d4ea984?w=1200&q=80&auto=format',
  'https://images.unsplash.com/photo-1600880292203-757bb62b4baf?w=1200&q=80&auto=format',
]
const currentPromo = ref(0)
let promoTimer = null
function nextPromo() { currentPromo.value = (currentPromo.value + 1) % promoSlides.length }
function prevPromo() { currentPromo.value = (currentPromo.value - 1 + promoSlides.length) % promoSlides.length }

// ====== 搜索 ======
const searchKeyword = ref("")
const searchCity = ref("")
function handleSearch() {
  router.push({ path: "/user/jobs/search", query: { q: searchKeyword.value, city: searchCity.value } })
}

// ====== 分类侧边栏 ======
const activeCategoryTab = ref('profession')
const hoveredCategory = ref(null)

const professionCategories = [
  { key: "engineering", icon: "📡", label: "工学", preview: "安全科学与工程类" },
  { key: "science", icon: "📩", label: "理学", preview: "大气科学类" },
  { key: "medical", icon: "🃖", label: "医学", preview: "动物医学类" },
  { key: "agriculture", icon: "🌶", label: "农学", preview: "草学类" },
  { key: "management", icon: "📳", label: "管理学", preview: "工商管理类" },
  { key: "literature", icon: "📉", label: "文学", preview: "历史学类" },
  { key: "law", icon: "⚖️", label: "法学", preview: "法学类" },
]
const jobtypeCategories = [
  { key: "sales", icon: "📈", label: "销售/商务拓展", preview: "销售顾问" },
  { key: "hr", icon: "🧑", label: "人事/行政/财务/法务", preview: "人事" },
  { key: "tech", icon: "📇", label: "互联网/通信及硬件", preview: "软件研发" },
  { key: "ops", icon: "🛡", label: "运维/测试", preview: "运维支持" },
  { key: "design", icon: "🎨", label: "视觉/交互/设计", preview: "视觉/交互" },
  { key: "cs", icon: "📓", label: "运营/客服", preview: "电商运营" },
  { key: "pm", icon: "📵", label: "产品/项目/高级管理", preview: "产品" },
]
const activeCategories = computed(() =>
  activeCategoryTab.value === 'profession' ? professionCategories : jobtypeCategories,
)

const submenuData: Record<string, { title: string; sections: { name: string; items: string[] }[] }> = {
  // 专业分类子菜单
  engineering: {
    title: "工学类",
    sections: [
      { name: "计算机类", items: ["计算机科学与技术", "软件工程", "网络工程", "信息安全", "物联网工程"] },
      { name: "电子信息类", items: ["电子信息工程", "通信工程", "微电子科学与工程", "光电信息科学与工程"] },
      { name: "自动化类", items: ["自动化", "测控技术与仪器", "电气工程及其自动化"] },
      { name: "机械类", items: ["机械工程", "机械设计制造及其自动化", "智能制造工程"] },
    ]
  },
  science: {
    title: "理学类",
    sections: [
      { name: "数学类", items: ["数学与应用数学", "信息与计算科学", "统计学"] },
      { name: "物理类", items: ["物理学", "应用物理学", "声学"] },
      { name: "化学类", items: ["化学", "应用化学", "材料化学"] },
      { name: "生物类", items: ["生物科学", "生物技术", "生态学"] },
    ]
  },
  medical: {
    title: "医学类",
    sections: [
      { name: "临床医学", items: ["临床医学", "麻醉学", "医学影像学", "眼视光医学"] },
      { name: "口腔医学", items: ["口腔医学"] },
      { name: "护理学", items: ["护理学"] },
      { name: "药学", items: ["药学", "中药学", "药物制剂"] },
    ]
  },
  agriculture: {
    title: "农学类",
    sections: [
      { name: "植物生产类", items: ["农学", "园艺", "植物保护", "茶学"] },
      { name: "动物生产类", items: ["动物科学", "动物医学", "水产养殖学"] },
      { name: "林学类", items: ["林学", "园林", "森林保护"] },
    ]
  },
  management: {
    title: "管理学类",
    sections: [
      { name: "工商管理类", items: ["工商管理", "市场营销", "会计学", "财务管理", "人力资源管理"] },
      { name: "公共管理类", items: ["行政管理", "公共事业管理", "劳动与社会保障"] },
      { name: "物流管理", items: ["物流管理", "供应链管理"] },
    ]
  },
  literature: {
    title: "文学类",
    sections: [
      { name: "中国语言文学", items: ["汉语言文学", "汉语言", "汉语国际教育"] },
      { name: "外国语言文学", items: ["英语", "日语", "法语", "德语", "西班牙语"] },
      { name: "新闻传播类", items: ["新闻学", "广播电视学", "广告学", "网络与新媒体"] },
    ]
  },
  law: {
    title: "法学类",
    sections: [
      { name: "法学", items: ["法学", "知识产权", "监狱学"] },
      { name: "政治学类", items: ["政治学与行政学", "国际政治", "外交学"] },
    ]
  },
  // 职类分类子菜单
  sales: {
    title: "销售/商务拓展",
    sections: [
      { name: "销售", items: ["销售顾问", "大客户销售", "渠道销售", "区域销售经理"] },
      { name: "商务拓展", items: ["商务专员", "BD经理", "战略合作"] },
      { name: "客户管理", items: ["客户代表", "客户成功经理"] },
    ]
  },
  hr: {
    title: "人事/行政/财务/法务",
    sections: [
      { name: "人力资源", items: ["HR专员", "招聘专员", "薪酬绩效", "员工关系"] },
      { name: "行政", items: ["行政专员", "前台接待", "办公室主任"] },
      { name: "财务", items: ["会计", "出纳", "财务分析"] },
      { name: "法务", items: ["法务专员", "合规专员"] },
    ]
  },
  tech: {
    title: "互联网/通信及硬件",
    sections: [
      { name: "软件开发", items: ["前端开发", "后端开发", "全栈开发", "移动端开发"] },
      { name: "算法", items: ["算法工程师", "AI工程师", "数据挖掘"] },
      { name: "硬件", items: ["硬件工程师", "嵌入式开发", "芯片设计"] },
    ]
  },
  ops: {
    title: "运维/测试",
    sections: [
      { name: "运维", items: ["运维工程师", "DevOps", "SRE", "云计算运维"] },
      { name: "测试", items: ["测试工程师", "自动化测试", "性能测试"] },
      { name: "网络", items: ["网络工程师", "信息安全"] },
    ]
  },
  design: {
    title: "视觉/交互/设计",
    sections: [
      { name: "UI设计", items: ["UI设计师", "网页设计", "APP设计"] },
      { name: "UX设计", items: ["UX设计师", "交互设计", "用户研究"] },
      { name: "视觉设计", items: ["平面设计", "品牌设计", "插画设计"] },
    ]
  },
  cs: {
    title: "运营/客服",
    sections: [
      { name: "产品运营", items: ["运营专员", "内容运营", "活动运营"] },
      { name: "电商运营", items: ["淘宝运营", "京东运营", "跨境电商"] },
      { name: "客服", items: ["客服专员", "售后客服", "技术支持"] },
    ]
  },
  pm: {
    title: "产品/项目/高级管理",
    sections: [
      { name: "产品", items: ["产品经理", "产品助理", "产品运营"] },
      { name: "项目管理", items: ["项目经理", "项目协调", "Scrum Master"] },
      { name: "高级管理", items: ["部门经理", "总监", "副总裁"] },
    ]
  },
}

const currentSubmenu = computed(() => hoveredCategory.value ? submenuData[hoveredCategory.value] : null)
function onCategoryEnter(key) { hoveredCategory.value = key }
function onSidebarLeave() {
  setTimeout(() => {
    if (!document.querySelector('.submenu-panel:hover') && !document.querySelector('.category-sidebar:hover'))
      hoveredCategory.value = null
  }, 100)
}
function onSubmenuLeave() { hoveredCategory.value = null }

const featuredJobs = [
  { title: "高级前端工程师", company: "银河麒麟", city: "北京", salary: "25-40K", tags: ["Vue", "TypeScript", "Element Plus"] },
  { title: "AI 算法工程师", company: "DeepSeek", city: "杭州", salary: "35-60K", tags: ["Python", "NLP", "大模型"] },
  { title: "Java 后端开发", company: "人大金仓", city: "北京", salary: "20-35K", tags: ["Spring Boot", "MyBatis", "KingbaseES"] },
  { title: "数据分析师", company: "华为", city: "深圳", salary: "22-38K", tags: ["SQL", "Python", "ECharts"] },
  { title: "嵌入式开发工程师", company: "龙芯中科", city: "北京", salary: "20-35K", tags: ["C/C++", "LoongArch", "Linux"] },
  { title: "全栈工程师", company: "统信软件", city: "武汉", salary: "18-30K", tags: ["Vue", "Node.js", "PostgreSQL"] },
]

const stats = [
  { value: 12000, suffix: "+", label: "活跃职位" },
  { value: 8500, suffix: "+", label: "注册企业" },
  { value: 45000, suffix: "+", label: "求职者" },
  { value: 98, suffix: "%", label: "匹配满意度" },
]
const statsStarted = ref(false)
let statsObserver = null

function animateCounters() {
  if (statsStarted.value) return
  statsStarted.value = true
  document.querySelectorAll(".stat-num").forEach((el) => {
    const target = parseInt(el.dataset.target || '0', 10)
    const suffix = el.dataset.suffix || ''
    const duration = 1200
    const start = performance.now()
    function tick(now) {
      const progress = Math.min((now - start) / duration, 1)
      const eased = 1 - Math.pow(1 - progress, 3)
      el.textContent = Math.floor(eased * target).toLocaleString() + suffix
      if (progress < 1) requestAnimationFrame(tick)
    }
    requestAnimationFrame(tick)
  })
}

onMounted(() => {
  slideTimer = setInterval(nextSlide, 5000)
  promoTimer = setInterval(nextPromo, 4000)
  const statsEl = document.querySelector('.stats-bar')
  if (statsEl) {
    statsObserver = new IntersectionObserver((entries) => {
      if (entries[0]?.isIntersecting) { animateCounters(); statsObserver?.disconnect() }
    }, { threshold: 0.3 })
    statsObserver.observe(statsEl)
  }
})

onUnmounted(() => {
  if (slideTimer) clearInterval(slideTimer)
  if (promoTimer) clearInterval(promoTimer)
  statsObserver?.disconnect()
})

function goDashboard() {
  const routes = { ADMIN: "/admin", USER: "/user", COMPANY: "/company" }
  router.push(routes[authStore.role] || '/login')
}
</script>

<template>
  <div ref="page" class="home-page">
    <AppHeader />

    <!-- 英雄区 -->
    <section class="hero-section">
      <div class="carousel">
        <div v-for="(img, i) in heroSlides" :key="i" class="slide" :class="{ active: i === currentSlide }" :style="{ backgroundImage: `url(${img})` }" />
        <div class="carousel-overlay" />
      </div>
      <button class="carousel-btn left" @click="prevSlide"><ChevronLeft :size="22" /></button>
      <button class="carousel-btn right" @click="nextSlide"><ChevronRight :size="22" /></button>
      <div class="carousel-dots">
        <button v-for="(_, i) in heroSlides" :key="i" class="dot" :class="{ active: i === currentSlide }" @click="goToSlide(i)" />
      </div>
      <div class="hero-content">
        <h1 class="hero-title hero-anim">成就你的非凡未来</h1>
        <p class="hero-subtitle hero-anim">触达最具影响力的科技职位、AI 精准匹配，让每位人才找到理想舞台。</p>
        <div class="search-bar hero-anim">
          <div class="search-field"><Briefcase :size="18" class="search-icon" /><input v-model="searchKeyword" type="text" placeholder="搜索职位、公司或关键词" @keydown.enter="handleSearch" /></div>
          <div class="search-divider" />
          <div class="search-field"><MapPin :size="18" class="search-icon" /><input v-model="searchCity" type="text" placeholder="城市" @keydown.enter="handleSearch" /></div>
          <button class="search-btn" @click="handleSearch"><Search :size="18" /> 搜索</button>
        </div>
        <div class="hot-tags hero-anim">
          <span class="tag-label">热门：</span>
          <button class="hot-tag" @click="searchKeyword = '前端开发'; handleSearch()">前端开发</button>
          <button class="hot-tag" @click="searchKeyword = 'AI 算法'; handleSearch()">AI 算法</button>
          <button class="hot-tag" @click="searchKeyword = 'Java'; handleSearch()">Java</button>
          <button class="hot-tag" @click="searchKeyword = '数据分析'; handleSearch()">数据分析</button>
        </div>
      </div>
    </section>

    <!-- 统计栏 -->
    <section class="stats-bar">
      <div class="stats-inner">
        <div v-for="stat in stats" :key="stat.label" class="stat-item">
          <div class="stat-num" :data-target="stat.value" :data-suffix="stat.suffix">0</div>
          <div class="stat-label">{{ stat.label }}</div>
        </div>
      </div>
    </section>

    <!-- 职位分类 -->
    <section class="category-section">
      <div class="category-inner">
        <div class="category-grid">
          <aside class="category-sidebar" @mouseleave="onSidebarLeave">
            <div class="cat-tabs">
              <button class="cat-tab" :class="{ active: activeCategoryTab === 'profession' }" @click="activeCategoryTab = 'profession'; hoveredCategory = null">按专业筛选</button>
              <button class="cat-tab" :class="{ active: activeCategoryTab === 'jobtype' }" @click="activeCategoryTab = 'jobtype'; hoveredCategory = null">按职类筛选</button>
            </div>
            <div class="cat-list">
              <div v-for="cat in activeCategories" :key="cat.key" class="cat-item" :class="{ hovered: hoveredCategory === cat.key }" @mouseenter="onCategoryEnter(cat.key)">
                <div class="cat-item-left"><span class="cat-emoji">{{ cat.icon }}</span><span class="cat-name">{{ cat.label }}</span></div>
                <div class="cat-item-right"><span class="cat-preview">{{ cat.preview }}</span><ChevronRightIcon :size="14" /></div>
              </div>
            </div>
            <div class="cat-footer"><router-link to="/user/jobs" class="cat-all-link">全部专业 <ArrowRight :size="14" /></router-link></div>
          </aside>
          <div class="category-right" @mouseleave="onSubmenuLeave">
            <transition name="submenu-fade">
              <div v-if="currentSubmenu" class="submenu-panel">
                <h3 class="submenu-title">{{ currentSubmenu.title }}</h3>
                <div class="submenu-sections">
                  <div v-for="sec in currentSubmenu.sections" :key="sec.name" class="submenu-section">
                    <h4 class="submenu-section-name">{{ sec.name }}</h4>
                    <div class="submenu-tags">
                      <router-link v-for="item in sec.items" :key="item" :to="{ path: '/user/jobs/search', query: { q: item } }" class="submenu-tag">{{ item }}</router-link>
                    </div>
                  </div>
                </div>
              </div>
            </transition>
            <div v-show="!currentSubmenu" class="promo-banner">
              <div v-for="(img, i) in promoSlides" :key="i" class="promo-slide" :class="{ active: i === currentPromo }" :style="{ backgroundImage: 'url(' + img + ')' }" />
              <div class="promo-overlay" />
              <div class="promo-content">
                <h3 class="promo-title">发现更多可能</h3>
                <p class="promo-desc">AI 驱动的精准推荐，让好工作主动找到你</p>
                <router-link to="/user/jobs" class="promo-btn">立即探索 <ArrowRight :size="16" /></router-link>
              </div>
              <button class="promo-nav left" @click="prevPromo"><ChevronLeft :size="16" /></button>
              <button class="promo-nav right" @click="nextPromo"><ChevronRight :size="16" /></button>
              <div class="promo-dots">
                <button v-for="(_, i) in promoSlides" :key="i" class="promo-dot" :class="{ active: i === currentPromo }" @click="currentPromo = i" />
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- 精选职位 -->
    <section class="section">
      <div class="section-inner">
        <div class="section-header reveal">
          <div><h2 class="section-title">精选职位</h2><p class="section-desc">AI 推荐的高匹配度岗位</p></div>
          <router-link to="/user/jobs" class="view-all">查看全部 <ArrowRight :size="16" /></router-link>
        </div>
        <div class="jobs-grid">
          <div v-for="job in featuredJobs" :key="job.title" class="job-card reveal">
            <div class="job-top"><h3 class="job-title">{{ job.title }}</h3><span class="job-salary">{{ job.salary }}</span></div>
            <div class="job-company">{{ job.company }} · {{ job.city }}</div>
            <div class="job-tags"><span v-for="tag in job.tags" :key="tag" class="job-tag">{{ tag }}</span></div>
          </div>
        </div>
      </div>
    </section>

    <!-- 平台特色 -->
    <section class="section features-section">
      <div class="section-inner">
        <h2 class="section-title reveal">平台特色</h2>
        <p class="section-desc reveal">基于银河麒麟操作系统，融合 AI 技术的全新招聘体验</p>
        <div class="features-grid">
          <div class="feature-block reveal">
            <div class="feat-icon"><Network :size="28" /></div>
            <h3>能力图谱</h3>
            <p>AI 语义驱动的技能知识网络，可视化展示你的能力全景</p>
          </div>
          <div class="feature-block reveal">
            <div class="feat-icon"><Sparkles :size="28" /></div>
            <h3>AI 智能匹配</h3>
            <p>基于 DeepSeek 大模型，精准对接岗位需求与人才画像</p>
          </div>
          <div class="feature-block reveal">
            <div class="feat-icon"><Route :size="28" /></div>
            <h3>AI 职业规划</h3>
            <p>个性化职业发展路径推荐，数据驱动的成长建议</p>
          </div>
        </div>
      </div>
    </section>

    <!-- Footer -->
    <footer class="site-footer">
      <div class="footer-inner">
        <div class="footer-brand"><div class="footer-logo">智聘星图</div><p>基于银河麒麟操作系统的 AI 智能匹配与能力图谱平台</p></div>
        <div class="footer-links">
          <div class="footer-col"><h4>产品</h4><a href="#">职位推荐</a><a href="#">能力图谱</a><a href="#">模拟面试</a></div>
          <div class="footer-col"><h4>支持</h4><a href="#">帮助中心</a><a href="#">服务条款</a><a href="#">隐私政策</a></div>
          <div class="footer-col"><h4>技术栈</h4><a href="#">银河麒麟 V11</a><a href="#">人大金仓</a><a href="#">DeepSeek</a></div>
        </div>
        <div class="footer-bottom"><span>第十五届中国软件杯 B2 赛题作品</span><span>Powered by 银河麒麟 · 人大金仓 · DeepSeek</span></div>
      </div>
    </footer>
  </div>
</template>

<style scoped lang="scss">
.home-page { min-height: 100vh; background: #f8f9ff; }

.reveal { opacity: 0; transform: translateY(30px); transition: opacity 0.6s cubic-bezier(0.22,1,0.36,1), transform 0.6s cubic-bezier(0.22,1,0.36,1); }
.reveal.revealed { opacity: 1; transform: translateY(0); }

@keyframes heroUp { from { opacity: 0; transform: translateY(30px); } to { opacity: 1; transform: translateY(0); } }
.hero-anim { opacity: 0; animation: heroUp 0.6s cubic-bezier(0.22,1,0.36,1) forwards; }
.hero-anim:nth-child(1) { animation-delay: 0.2s; }
.hero-anim:nth-child(2) { animation-delay: 0.35s; }
.hero-anim:nth-child(3) { animation-delay: 0.5s; }
.hero-anim:nth-child(4) { animation-delay: 0.6s; }

.hero-section { position: relative; height: calc(85vh + 56px); min-height: calc(520px + 56px); max-height: calc(720px + 56px); display: flex; align-items: center; overflow: hidden; margin-top: -56px; padding-top: 56px; }
.carousel { position: absolute; inset: 0; }
.slide { position: absolute; inset: 0; background-size: cover; background-position: center; opacity: 0; transition: opacity 1s ease-in-out; &.active { opacity: 1; } }
.carousel-overlay { position: absolute; inset: 0; background: linear-gradient(135deg, rgba(0,53,39,0.45) 0%, rgba(6,78,59,0.3) 100%); }
.carousel-btn { position: absolute; top: 50%; transform: translateY(-50%); z-index: 10; width: 44px; height: 44px; border-radius: 50%; border: 1px solid rgba(255,255,255,0.25); background: rgba(255,255,255,0.15); backdrop-filter: blur(8px); color: #fff; cursor: pointer; display: flex; align-items: center; justify-content: center; transition: all 0.25s; &:hover { background: rgba(255,255,255,0.3); } &.left { left: 24px; } &.right { right: 24px; } }
.carousel-dots { position: absolute; bottom: 24px; left: 50%; transform: translateX(-50%); z-index: 10; display: flex; gap: 8px; }
.dot { width: 8px; height: 8px; border-radius: 999px; border: none; background: rgba(255,255,255,0.4); cursor: pointer; transition: all 0.3s; &.active { background: #fff; width: 22px; } }
.hero-content { position: relative; z-index: 10; max-width: 1280px; margin: 0 auto; padding: 0 40px; width: 100%; }
.hero-title { font-size: 48px; font-weight: 700; color: #fff; margin-bottom: 16px; letter-spacing: -1px; }
.hero-subtitle { font-size: 18px; color: rgba(255,255,255,0.85); margin-bottom: 36px; line-height: 1.6; white-space: nowrap; }
.search-bar { display: flex; align-items: center; max-width: 640px; background: rgba(0,53,39,0.85); backdrop-filter: blur(12px); border: 1px solid rgba(255,255,255,0.12); border-radius: 12px; padding: 6px; transition: box-shadow 0.3s; &:focus-within { box-shadow: 0 0 0 3px rgba(128,190,166,0.3); } }
.search-field { flex: 1; display: flex; align-items: center; gap: 10px; padding: 10px 14px; input { background: none; border: none; outline: none; color: #fff; font-size: 14px; width: 100%; &::placeholder { color: rgba(255,255,255,0.5); } } }
.search-icon { color: rgba(255,255,255,0.5); flex-shrink: 0; }
.search-divider { width: 1px; height: 24px; background: rgba(255,255,255,0.15); }
.search-btn { display: flex; align-items: center; gap: 6px; padding: 10px 24px; border: none; border-radius: 8px; background: #064e3b; color: #fff; font-size: 14px; font-weight: 600; cursor: pointer; white-space: nowrap; transition: all 0.25s; &:hover { background: #003527; } }
.hot-tags { display: flex; align-items: center; gap: 8px; margin-top: 16px; flex-wrap: wrap; }
.tag-label { font-size: 13px; color: rgba(255,255,255,0.5); }
.hot-tag { font-size: 12px; color: rgba(255,255,255,0.75); padding: 4px 12px; border-radius: 999px; border: 1px solid rgba(255,255,255,0.2); background: rgba(255,255,255,0.08); cursor: pointer; transition: all 0.25s; &:hover { background: rgba(255,255,255,0.18); color: #fff; } }

.stats-bar { background: #003527; padding: 32px 0; }
.stats-inner { max-width: 1440px; margin: 0 auto; padding: 0 40px; display: flex; justify-content: space-around; }
.stat-item { text-align: center; }
.stat-num { font-size: 28px; font-weight: 700; color: #fff; font-variant-numeric: tabular-nums; }
.stat-label { font-size: 13px; color: rgba(255,255,255,0.6); margin-top: 4px; }

.category-section { padding: 48px 0; }
.category-inner { max-width: 1280px; margin: 0 auto; padding: 0 24px; }
.category-grid { display: grid; grid-template-columns: 300px 1fr; gap: 24px; margin-top: 10px; }
.category-sidebar { background: #fff; border-radius: 12px; border: 1px solid #bfc9c3; box-shadow: 0 1px 4px rgba(0,0,0,0.04); overflow: hidden; }
.cat-tabs { display: flex; border-bottom: 1px solid #bfc9c3; }
.cat-tab { flex: 1; padding: 12px 0; font-size: 12px; font-weight: 700; letter-spacing: 0.5px; text-align: center; cursor: pointer; border: none; background: none; color: #404944; transition: all 0.2s; &:first-child { border-right: 1px solid #bfc9c3; } &.active { color: #003527; border-bottom: 2px solid #064e3b; background: rgba(6,78,59,0.05); } &:hover:not(.active) { color: #121c28; } }
.cat-list { padding: 8px 0; }
.cat-item { display: flex; align-items: center; justify-content: space-between; padding: 10px 16px; cursor: pointer; transition: all 0.2s; &:hover, &.hovered { background: #f8f9ff; } }
.cat-item-left { display: flex; align-items: center; gap: 10px; }
.cat-emoji { font-size: 16px; }
.cat-name { font-size: 14px; font-weight: 500; color: #121c28; }
.cat-item-right { display: flex; align-items: center; gap: 4px; }
.cat-preview { font-size: 12px; color: #404944; }
.cat-footer { padding: 12px; border-top: 1px solid #bfc9c3; text-align: center; }
.cat-all-link { font-size: 14px; font-weight: 600; color: #003527; text-decoration: none; display: inline-flex; align-items: center; gap: 4px; &:hover { color: #064e3b; text-decoration: none; } }

.category-right { position: relative; min-height: 400px; border-radius: 12px; overflow: hidden; }
.submenu-panel { position: absolute; inset: 0; z-index: 20; background: #fff; border-radius: 12px; border: 1px solid #bfc9c3; box-shadow: 0 8px 32px rgba(0,0,0,0.08); padding: 28px; overflow-y: auto; }
.submenu-fade-enter-active { transition: opacity 0.25s ease; }
.submenu-fade-leave-active { transition: opacity 0.15s ease; }
.submenu-fade-enter-from, .submenu-fade-leave-to { opacity: 0; }
.submenu-title { font-size: 18px; font-weight: 700; color: #121c28; margin-bottom: 24px; }
.submenu-sections { display: flex; flex-direction: column; gap: 20px; }
.submenu-section-name { font-size: 13px; font-weight: 700; color: #003527; margin-bottom: 10px; letter-spacing: 0.3px; }
.submenu-tags { display: flex; flex-wrap: wrap; gap: 8px; }
.submenu-tag { padding: 6px 14px; border-radius: 6px; background: #f8f9ff; font-size: 13px; color: #404944; text-decoration: none; transition: all 0.2s; &:hover { background: #064e3b; color: #fff; } }

.promo-banner { position: relative; height: 100%; min-height: 400px; border-radius: 12px; overflow: hidden; }
.promo-slide { position: absolute; inset: 0; background-size: cover; background-position: center; opacity: 0; transition: opacity 0.8s ease-in-out; &.active { opacity: 1; } }
.promo-overlay { position: absolute; inset: 0; z-index: 1; background: linear-gradient(135deg, rgba(0,53,39,0.35) 0%, rgba(6,78,59,0.2) 100%); }
.promo-content { position: absolute; inset: 0; z-index: 2; display: flex; flex-direction: column; justify-content: center; padding: 48px 48px 48px 100px; }
.promo-title { font-size: 32px; font-weight: 700; color: #fff; margin-bottom: 12px; }
.promo-desc { font-size: 16px; color: rgba(255,255,255,0.8); margin-bottom: 24px; max-width: 360px; line-height: 1.6; }
.promo-btn { display: inline-flex; align-items: center; gap: 8px; padding: 12px 32px; border-radius: 999px; background: #064e3b; color: #fff; font-size: 15px; font-weight: 600; text-decoration: none; box-shadow: 0 4px 16px rgba(0,0,0,0.12); transition: all 0.25s; width: fit-content; &:hover { transform: translateY(-2px); box-shadow: 0 8px 24px rgba(0,0,0,0.16); background: #003527; text-decoration: none; } }
.promo-nav { position: absolute; top: 50%; transform: translateY(-50%); z-index: 10; width: 36px; height: 36px; border-radius: 50%; border: 1px solid rgba(255,255,255,0.25); background: rgba(255,255,255,0.15); backdrop-filter: blur(8px); color: #fff; cursor: pointer; display: flex; align-items: center; justify-content: center; transition: all 0.25s; &:hover { background: rgba(255,255,255,0.3); } &.left { left: 16px; } &.right { right: 16px; } }
.promo-dots { position: absolute; bottom: 16px; left: 50%; transform: translateX(-50%); z-index: 10; display: flex; gap: 6px; }
.promo-dot { width: 6px; height: 6px; border-radius: 999px; border: none; background: rgba(255,255,255,0.4); cursor: pointer; transition: all 0.3s; &.active { background: #fff; width: 18px; } }

.section { padding: 64px 0; }
.section-inner { max-width: 1280px; margin: 0 auto; padding: 0 24px; }
.section-title { font-size: 28px; font-weight: 700; color: #003527; text-align: center; margin-bottom: 8px; }
.section-desc { font-size: 15px; color: #404944; text-align: center; margin-bottom: 40px; }
.section-header { display: flex; align-items: flex-end; justify-content: space-between; margin-bottom: 32px; .section-title, .section-desc { text-align: left; margin-bottom: 0; } .section-desc { margin-top: 4px; } }
.view-all { display: flex; align-items: center; gap: 4px; font-size: 14px; font-weight: 600; color: #064e3b; text-decoration: none; &:hover { text-decoration: underline; } }

.jobs-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 16px; }
.job-card { background: #fff; border-radius: 12px; padding: 24px; border: 1px solid #bfc9c3; cursor: pointer; transition: all 0.3s cubic-bezier(0.4,0,0.2,1); &:hover { transform: translateY(-6px); box-shadow: 0 16px 36px rgba(0,0,0,0.1); } }
.job-top { display: flex; align-items: flex-start; justify-content: space-between; margin-bottom: 8px; }
.job-title { font-size: 16px; font-weight: 600; color: #121c28; }
.job-salary { font-size: 15px; font-weight: 700; color: #064e3b; white-space: nowrap; }
.job-company { font-size: 13px; color: #404944; margin-bottom: 12px; }
.job-tags { display: flex; gap: 6px; flex-wrap: wrap; }
.job-tag { font-size: 12px; padding: 3px 10px; border-radius: 999px; background: #f8f9ff; color: #404944; transition: all 0.2s; }
.job-card:hover .job-tag { background: rgba(6,78,59,0.08); color: #064e3b; }

.features-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 24px; }
.feature-block { text-align: center; padding: 40px 24px; background: #fff; border-radius: 12px; border: 1px solid #bfc9c3; transition: all 0.3s cubic-bezier(0.4,0,0.2,1); &:hover { transform: translateY(-6px); box-shadow: 0 12px 28px rgba(0,0,0,0.08); } }
.feat-icon { width: 64px; height: 64px; border-radius: 16px; background: linear-gradient(135deg, #003527 0%, #064e3b 100%); color: #fff; display: flex; align-items: center; justify-content: center; margin: 0 auto 20px; transition: transform 0.3s; }
.feature-block:hover .feat-icon { transform: scale(1.08) rotate(-3deg); }
.feature-block h3 { font-size: 18px; font-weight: 600; color: #121c28; margin-bottom: 8px; }
.feature-block p { font-size: 14px; color: #404944; line-height: 1.6; }

.site-footer { background: #003527; padding: 48px 0 0; color: #fff; }
.footer-inner { max-width: 1440px; margin: 0 auto; padding: 0 40px; }
.footer-brand { margin-bottom: 32px; }
.footer-logo { font-size: 22px; font-weight: 700; margin-bottom: 8px; }
.footer-brand p { font-size: 13px; color: rgba(255,255,255,0.5); }
.footer-links { display: flex; gap: 80px; margin-bottom: 40px; }
.footer-col { display: flex; flex-direction: column; gap: 10px; h4 { font-size: 14px; font-weight: 600; margin-bottom: 4px; } a { font-size: 13px; color: rgba(255,255,255,0.5); text-decoration: none; transition: color 0.2s; &:hover { color: rgba(255,255,255,0.8); } } }
.footer-bottom { border-top: 1px solid rgba(255,255,255,0.1); padding: 20px 0; display: flex; justify-content: space-between; font-size: 12px; color: rgba(255,255,255,0.35); }

@media (max-width: 1024px) {
  .nav-links { gap: 8px; flex-wrap: wrap; justify-content: flex-start; overflow: visible; }
  .nav-inner { padding: 0 16px; } .hero-title { font-size: 32px; }
  .category-grid { grid-template-columns: 1fr; } .category-sidebar { max-height: 320px; overflow-y: auto; }
  .jobs-grid { grid-template-columns: 1fr 1fr; } .features-grid { grid-template-columns: 1fr; } .footer-links { gap: 40px; }
}
@media (max-width: 640px) {
  .hero-section { height: 70vh; } .hero-title { font-size: 26px; } .hero-subtitle { font-size: 15px; }
  .nav-links { gap: 4px; } .nav-link, .interview-trigger { font-size: 11px; }
  .search-bar { flex-direction: column; } .search-divider { display: none; }
  .jobs-grid { grid-template-columns: 1fr; }
  .footer-links { flex-direction: column; gap: 24px; } .footer-bottom { flex-direction: column; gap: 8px; }
  .stats-inner { flex-wrap: wrap; gap: 16px; } .stat-item { width: 45%; }
}
</style>