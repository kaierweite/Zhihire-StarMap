# -*- coding: utf-8 -*-
import sys
sys.stdout.reconfigure(encoding='utf-8')
path = r'C:\Users\Administrator\Desktop\Zhihire-StarMap\frontend\src\views\user\AbilityMap.vue'
content = open(path, encoding='utf-8').read()

# Comprehensive context-based fixes for all corrupted Chinese text
fixes = [
    ('@click="fetchGraph">技能缺口</button>', '@click="fetchGraph">\u91cd\u65b0\u52a0\u8f7d</button>'),
    ('<p>缺口图谱视图缺口图谱视图缺口图谱视图可选</p>', '<p>\u6682\u65e0\u56fe\u8c31\u6570\u636e\u3002\u8bf7\u5148\u5728\u4e2a\u4eba\u6863\u6848\u4e2d\u6dfb\u52a0\u6280\u80fd\u3002</p>'),
    ('<span class="legend-label">已匹配</span>\n                <span class="legend-item"><span class="line-solid line-primary" />', '<span class="legend-label">\u5173\u7cfb\uff1a</span>\n                <span class="legend-item"><span class="line-solid line-primary" />'),
    ('<span class="line-solid line-primary" /> 可选</span>', '<span class="line-solid line-primary" /> \u524d\u7f6e</span>'),
    ('<span class="line-dashed line-green" /> 可选</span>', '<span class="line-dashed line-green" /> \u5305\u542b</span>'),
    ('<span class="line-dotted line-yellow" /> 可选</span>', '<span class="line-dotted line-yellow" /> \u76f8\u4f3c</span>'),
    ('<span class="line-thick line-purple" /> 可选</span>', '<span class="line-thick line-purple" /> \u4e92\u8865</span>'),
    ('<span class="legend-label">已匹配</span>\n                <span v-for="(color, name) in categoryColors"', '<span class="legend-label">\u5206\u7c7b\uff1a</span>\n                <span v-for="(color, name) in categoryColors"'),
    ('<div class="card-header"><BarChart3 :size="18" /><h3>技能缺口</h3></div>', '<div class="card-header"><BarChart3 :size="18" /><h3>\u6280\u80fd\u6982\u89c8</h3></div>'),
    ('<span class="stat-unit">已匹配</span>', '<span class="stat-unit">\u9879\u6280\u80fd</span>'),
    ('<div class="card-header"><TrendingUp :size="18" /><h3>技能缺口</h3></div>', '<div class="card-header"><TrendingUp :size="18" /><h3>\u6280\u80fd\u5206\u5e03</h3></div>'),
    ('<div class="card-header"><Lightbulb :size="18" /><h3>技能缺口</h3></div>', '<div class="card-header"><Lightbulb :size="18" /><h3>\u5b66\u4e60\u5efa\u8bae</h3></div>'),
    ('<p class="gap-desc">缺口图谱视图缺口图谱视图缺口图谱视图缺口图谱视图技能缺口</p>', '<p class="gap-desc">\u9009\u62e9\u76ee\u6807\u5c97\u4f4d\u89d2\u8272\uff0c\u5bf9\u6bd4\u5f53\u524d\u6280\u80fd\u4e0e\u5c97\u4f4d\u8981\u6c42\uff0c\u8bc6\u522b\u5dee\u8ddd\u4e0e\u91cd\u53e0</p>'),
    ('<span class="role-label">技能缺口?</span>', '<span class="role-label">\u76ee\u6807\u89d2\u8272\uff1a</span>'),
    ('placeholder="缺口图谱视图已匹配"', 'placeholder="\u8bf7\u9009\u62e9\u76ee\u6807\u5c97\u4f4d\u89d2\u8272"'),
    ('<p>缺口图谱视图缺口图谱视图<br/>缺口图谱视图技能缺口?</p>', '<p>\u8bf7\u5148\u9009\u62e9\u4e00\u4e2a\u76ee\u6807\u5c97\u4f4d\u89d2\u8272<br/>\u7cfb\u7edf\u5c06\u81ea\u52a8\u6bd4\u5bf9\u6280\u80fd\u5dee\u8ddd</p>'),
    ('<p>缺口图谱视图可选...</p>', '<p>\u6b63\u5728\u5206\u6790\u6280\u80fd\u5dee\u8ddd...</p>'),
    ('<span>技能缺口?</span>\n              <span class="target-tag">{{ roles.find((r) => r.id === selectedRoleId)?.name || \'技能缺口\' }}', '<span>\u76ee\u6807\u5c97\u4f4d\uff1a</span>\n              <span class="target-tag">{{ roles.find((r) => r.id === selectedRoleId)?.name || \'\u672a\u77e5\u5c97\u4f4d\' }}'),
    ('<span class="target-match">已匹配 {{ coveragePercent }}%</span>', '<span class="target-match">\u5339\u914d\u5ea6 {{ coveragePercent }}%</span>'),
    ('<span class="req-badge req-must">可选</span> 缺口图谱视图?', '<span class="req-badge req-must">\u5fc5\u5907</span> \u5fc5\u987b\u638c\u63e1\u7684\u6280\u80fd'),
    ('<span class="req-badge req-better">可选</span> 缺口图谱视图?', '<span class="req-badge req-better">\u52a0\u5206</span> \u5efa\u8bae\u638c\u63e1\u7684\u6280\u80fd'),
    ('<span class="req-badge req-optional">可选</span> 缺口图谱视图?', '<span class="req-badge req-optional">\u53ef\u9009</span> \u53ef\u9009\u7684\u62d3\u5c55\u6280\u80fd'),
    ('<strong>AI 可选</strong>技能缺口?', '<strong>AI \u5efa\u8bae</strong>\u91cd\u70b9\u8865\u9f50'),
    ('<span class="gap-legend-hint">缺口图谱视图已匹配</span>', '<span class="gap-legend-hint">\u7ea2\u8272\u8282\u70b9\u4e3a\u7f3a\u53e3\u6280\u80fd</span>'),
    # Fix the join separator
    (".map((s) => s.skill_name).join('\u003f')", ".map((s) => s.skill_name).join('\u3001')"),
]

for old, new in fixes:
    if old in content:
        content = content.replace(old, new)
        print(f'Fixed: {old[:50]}...')
    else:
        print(f'NOT FOUND: {old[:50]}...')

with open(path, 'w', encoding='utf-8') as f:
    f.write(content)
print('\nAll fixes applied')
