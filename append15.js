const fs = require('fs');
const p = "C:\\Users\\Administrator\\Desktop\\Zhihire-StarMap\\frontend\\src\\views\\common\\HomeView.vue";
let c = '';
c += '.section { padding: 64px 0; }\n';
c += '.section-inner { max-width: 1280px; margin: 0 auto; padding: 0 24px; }\n';
c += '.section-title { font-size: 28px; font-weight: 700; color: #1a3a5c; text-align: center; margin-bottom: 8px; }\n';
c += '.section-desc { font-size: 15px; color: #909399; text-align: center; margin-bottom: 40px; }\n';
c += '.section-header { display: flex; align-items: flex-end; justify-content: space-between; margin-bottom: 32px; .section-title, .section-desc { text-align: left; margin-bottom: 0; } .section-desc { margin-top: 4px; } }\n';
c += '.view-all { display: flex; align-items: center; gap: 4px; font-size: 14px; font-weight: 600; color: #0ea5e9; text-decoration: none; &:hover { text-decoration: underline; } }\n\n';

c += '.jobs-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 16px; }\n';
c += '.job-card { background: #fff; border-radius: 12px; padding: 24px; border: 1px solid #e5e7eb; cursor: pointer; transition: all 0.3s cubic-bezier(0.4,0,0.2,1); &:hover { transform: translateY(-6px); box-shadow: 0 16px 36px rgba(0,0,0,0.1); } }\n';
c += '.job-top { display: flex; align-items: flex-start; justify-content: space-between; margin-bottom: 8px; }\n';
c += '.job-title { font-size: 16px; font-weight: 600; color: #303133; }\n';
c += '.job-salary { font-size: 15px; font-weight: 700; color: #0ea5e9; white-space: nowrap; }\n';
c += '.job-company { font-size: 13px; color: #909399; margin-bottom: 12px; }\n';
c += '.job-tags { display: flex; gap: 6px; flex-wrap: wrap; }\n';
c += '.job-tag { font-size: 12px; padding: 3px 10px; border-radius: 999px; background: #f5f7fa; color: #606266; transition: all 0.2s; }\n';
c += '.job-card:hover .job-tag { background: rgba(14,165,233,0.08); color: #0ea5e9; }\n\n';

c += '.features-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 24px; }\n';
c += '.feature-block { text-align: center; padding: 40px 24px; background: #fff; border-radius: 12px; border: 1px solid #e5e7eb; transition: all 0.3s cubic-bezier(0.4,0,0.2,1); &:hover { transform: translateY(-6px); box-shadow: 0 12px 28px rgba(0,0,0,0.08); } }\n';
c += '.feat-icon { width: 64px; height: 64px; border-radius: 16px; background: linear-gradient(135deg, #1a3a5c 0%, #0ea5e9 100%); color: #fff; display: flex; align-items: center; justify-content: center; margin: 0 auto 20px; transition: transform 0.3s; }\n';
c += '.feature-block:hover .feat-icon { transform: scale(1.08) rotate(-3deg); }\n';
c += '.feature-block h3 { font-size: 18px; font-weight: 600; color: #303133; margin-bottom: 8px; }\n';
c += '.feature-block p { font-size: 14px; color: #909399; line-height: 1.6; }\n\n';

c += '.site-footer { background: #1a3a5c; padding: 48px 0 0; color: #fff; }\n';
c += '.footer-inner { max-width: 1440px; margin: 0 auto; padding: 0 40px; }\n';
c += '.footer-brand { margin-bottom: 32px; }\n';
c += '.footer-logo { font-size: 22px; font-weight: 700; margin-bottom: 8px; }\n';
c += '.footer-brand p { font-size: 13px; color: rgba(255,255,255,0.5); }\n';
c += '.footer-links { display: flex; gap: 80px; margin-bottom: 40px; }\n';
c += '.footer-col { display: flex; flex-direction: column; gap: 10px; h4 { font-size: 14px; font-weight: 600; margin-bottom: 4px; } a { font-size: 13px; color: rgba(255,255,255,0.5); text-decoration: none; transition: color 0.2s; &:hover { color: rgba(255,255,255,0.8); } } }\n';
c += '.footer-bottom { border-top: 1px solid rgba(255,255,255,0.1); padding: 20px 0; display: flex; justify-content: space-between; font-size: 12px; color: rgba(255,255,255,0.35); }\n\n';
fs.appendFileSync(p, c, 'utf-8');
console.log('CSS jobs/features/footer written: ' + c.length + ' chars');
