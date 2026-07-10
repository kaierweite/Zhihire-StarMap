const fs = require('fs');
const p = "C:\\Users\\Administrator\\Desktop\\Zhihire-StarMap\\frontend\\src\\views\\common\\HomeView.vue";
let c = '';

// Featured jobs
c += '    <!-- 精选职位 -->\n';
c += '    <section class="section">\n';
c += '      <div class="section-inner">\n';
c += '        <div class="section-header reveal">\n';
c += '          <div><h2 class="section-title">精选职位</h2><p class="section-desc">AI 推荐的高匹配度岗位</p></div>\n';
c += '          <router-link to="/user/jobs" class="view-all">查看全部 <ArrowRight :size="16" /></router-link>\n';
c += '        </div>\n';
c += '        <div class="jobs-grid">\n';
c += '          <div v-for="job in featuredJobs" :key="job.title" class="job-card reveal">\n';
c += '            <div class="job-top"><h3 class="job-title">{{ job.title }}</h3><span class="job-salary">{{ job.salary }}</span></div>\n';
c += '            <div class="job-company">{{ job.company }} · {{ job.city }}</div>\n';
c += '            <div class="job-tags"><span v-for="tag in job.tags" :key="tag" class="job-tag">{{ tag }}</span></div>\n';
c += '          </div>\n';
c += '        </div>\n';
c += '      </div>\n';
c += '    </section>\n\n';

// Features
c += '    <!-- 平台特色 -->\n';
c += '    <section class="section features-section">\n';
c += '      <div class="section-inner">\n';
c += '        <h2 class="section-title reveal">平台特色</h2>\n';
c += '        <p class="section-desc reveal">基于银河麒麟操作系统，融合 AI 技术的全新招聘体验</p>\n';
c += '        <div class="features-grid">\n';
c += '          <div class="feature-block reveal">\n';
c += '            <div class="feat-icon"><Network :size="28" /></div>\n';
c += '            <h3>能力图谱</h3>\n';
c += '            <p>AI 语义驱动的技能知识网络，可视化展示你的能力全景</p>\n';
c += '          </div>\n';
c += '          <div class="feature-block reveal">\n';
c += '            <div class="feat-icon"><Sparkles :size="28" /></div>\n';
c += '            <h3>AI 智能匹配</h3>\n';
c += '            <p>基于 DeepSeek 大模型，精准对接岗位需求与人才画像</p>\n';
c += '          </div>\n';
c += '          <div class="feature-block reveal">\n';
c += '            <div class="feat-icon"><Route :size="28" /></div>\n';
c += '            <h3>AI 职业规划</h3>\n';
c += '            <p>个性化职业发展路径推荐，数据驱动的成长建议</p>\n';
c += '          </div>\n';
c += '        </div>\n';
c += '      </div>\n';
c += '    </section>\n\n';

// Footer
c += '    <!-- Footer -->\n';
c += '    <footer class="site-footer">\n';
c += '      <div class="footer-inner">\n';
c += '        <div class="footer-brand"><div class="footer-logo">智聘星图</div><p>基于银河麒麟操作系统的 AI 智能匹配与能力图谱平台</p></div>\n';
c += '        <div class="footer-links">\n';
c += '          <div class="footer-col"><h4>产品</h4><a href="#">职位推荐</a><a href="#">能力图谱</a><a href="#">模拟面试</a></div>\n';
c += '          <div class="footer-col"><h4>支持</h4><a href="#">帮助中心</a><a href="#">服务条款</a><a href="#">隐私政策</a></div>\n';
c += '          <div class="footer-col"><h4>技术栈</h4><a href="#">银河麒麟 V11</a><a href="#">人大金仓</a><a href="#">DeepSeek</a></div>\n';
c += '        </div>\n';
c += '        <div class="footer-bottom"><span>第十五届中国软件杯 B2 赛题作品</span><span>Powered by 银河麒麟 · 人大金仓 · DeepSeek</span></div>\n';
c += '      </div>\n';
c += '    </footer>\n';
c += '  </div>\n';
c += '</template>\n\n';
fs.appendFileSync(p, c, 'utf-8');
console.log('Jobs/features/footer written: ' + c.length + ' chars');
