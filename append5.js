const fs = require('fs');
const p = "C:\\Users\\Administrator\\Desktop\\Zhihire-StarMap\\frontend\\src\\views\\common\\HomeView.vue";
let c = '';
c += "const currentSubmenu = computed(() => hoveredCategory.value ? submenuData[hoveredCategory.value] : null)\n";
c += 'function onCategoryEnter(key) { hoveredCategory.value = key }\n';
c += 'function onSidebarLeave() {\n';
c += '  setTimeout(() => {\n';
c += "    if (!document.querySelector('.submenu-panel:hover') && !document.querySelector('.category-sidebar:hover'))\n";
c += '      hoveredCategory.value = null\n';
c += '  }, 100)\n';
c += '}\n';
c += 'function onSubmenuLeave() { hoveredCategory.value = null }\n\n';

c += 'const featuredJobs = [\n';
c += '  { title: "高级前端工程师", company: "银河麒麟", city: "北京", salary: "25-40K", tags: ["Vue", "TypeScript", "Element Plus"] },\n';
c += '  { title: "AI 算法工程师", company: "DeepSeek", city: "杭州", salary: "35-60K", tags: ["Python", "NLP", "大模型"] },\n';
c += '  { title: "Java 后端开发", company: "人大金仓", city: "北京", salary: "20-35K", tags: ["Spring Boot", "MyBatis", "KingbaseES"] },\n';
c += '  { title: "数据分析师", company: "华为", city: "深圳", salary: "22-38K", tags: ["SQL", "Python", "ECharts"] },\n';
c += '  { title: "嵌入式开发工程师", company: "龙芯中科", city: "北京", salary: "20-35K", tags: ["C/C++", "LoongArch", "Linux"] },\n';
c += '  { title: "全栈工程师", company: "统信软件", city: "武汉", salary: "18-30K", tags: ["Vue", "Node.js", "PostgreSQL"] },\n';
c += ']\n\n';

c += 'const stats = [\n';
c += '  { value: 12000, suffix: "+", label: "活跃职位" },\n';
c += '  { value: 8500, suffix: "+", label: "注册企业" },\n';
c += '  { value: 45000, suffix: "+", label: "求职者" },\n';
c += '  { value: 98, suffix: "%", label: "匹配满意度" },\n';
c += ']\n';
c += 'const statsStarted = ref(false)\n';
c += 'let statsObserver = null\n\n';

c += 'function animateCounters() {\n';
c += '  if (statsStarted.value) return\n';
c += '  statsStarted.value = true\n';
c += '  document.querySelectorAll(".stat-num").forEach((el) => {\n';
c += "    const target = parseInt(el.dataset.target || '0', 10)\n";
c += "    const suffix = el.dataset.suffix || ''\n";
c += '    const duration = 1200\n';
c += '    const start = performance.now()\n';
c += '    function tick(now) {\n';
c += '      const progress = Math.min((now - start) / duration, 1)\n';
c += '      const eased = 1 - Math.pow(1 - progress, 3)\n';
c += '      el.textContent = Math.floor(eased * target).toLocaleString() + suffix\n';
c += '      if (progress < 1) requestAnimationFrame(tick)\n';
c += '    }\n';
c += '    requestAnimationFrame(tick)\n';
c += '  })\n';
c += '}\n\n';

c += 'onMounted(() => {\n';
c += '  slideTimer = setInterval(nextSlide, 5000)\n';
c += '  promoTimer = setInterval(nextPromo, 4000)\n';
c += "  const statsEl = document.querySelector('.stats-bar')\n";
c += '  if (statsEl) {\n';
c += '    statsObserver = new IntersectionObserver((entries) => {\n';
c += '      if (entries[0]?.isIntersecting) { animateCounters(); statsObserver?.disconnect() }\n';
c += "    }, { threshold: 0.3 })\n";
c += '    statsObserver.observe(statsEl)\n';
c += '  }\n';
c += '})\n\n';

c += 'onUnmounted(() => {\n';
c += '  if (slideTimer) clearInterval(slideTimer)\n';
c += '  if (promoTimer) clearInterval(promoTimer)\n';
c += '  statsObserver?.disconnect()\n';
c += '})\n\n';

c += 'function goDashboard() {\n';
c += '  const routes = { ADMIN: "/admin", USER: "/user", COMPANY: "/company" }\n';
c += "  router.push(routes[authStore.role] || '/login')\n";
c += '}\n';
c += '</script>\n\n';

fs.appendFileSync(p, c, 'utf-8');
console.log('Rest of script written: ' + c.length + ' chars');
