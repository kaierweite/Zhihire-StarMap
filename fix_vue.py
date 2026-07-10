# -*- coding: utf-8 -*-
import sys
sys.stdout.reconfigure(encoding='utf-8')
path = r'C:\Users\Administrator\Desktop\Zhihire-StarMap\frontend\src\views\user\AbilityMap.vue'
content = open(path, encoding='utf-8').read()

# Fix 1: Level distribution keys
content = content.replace("return { '通用': expert, '通用': proficient, '通用': basic }", "return { '精通': expert, '熟练': proficient, '了解': basic }")

# Fix 2: Page title
content = content.replace('<h1 class="page-title fade-up">\u7f3a\u53e3\u56fe\u8c31\u89c6\u56fe</h1>', '<h1 class="page-title fade-up">\u4e2a\u4eba\u80fd\u529b\u56fe\u8c31</h1>')

# Fix 3: Page description
content = content.replace('<p class="page-desc fade-up d1">\u53ef\u9009 AI \u7f3a\u53e3\u56fe\u8c31\u89c6\u56fe\u7f3a\u53e3\u56fe\u8c31\u89c6\u56fe?</p>', '<p class="page-desc fade-up d1">\u57fa\u4e8e AI \u8bed\u4e49\u7406\u89e3\u6784\u5efa\u7684\u6280\u80fd\u77e5\u8bc6\u56fe\u8c31</p>')

with open(path, 'w', encoding='utf-8') as f:
    f.write(content)
print('All fixes applied')
