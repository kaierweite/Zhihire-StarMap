import pathlib

p = pathlib.Path(r'C:\Users\Administrator\Desktop\Zhihire-StarMap\frontend\src\components\AppHeader.vue')
t = p.read_text(encoding='utf-8-sig')

old_center = '<el-dropdown-item @click="router.push(\x27/user\x27)">\u4e2a\u4eba\u4e2d\u5fc3</el-dropdown-item>'
new_center = '<el-dropdown-item @click="router.push(\x27/user/profile\x27)">\u4e2a\u4eba\u4e2d\u5fc3</el-dropdown-item>'
t = t.replace(old_center, new_center)

old_workbench = '<el-dropdown-item @click="goDashboard">\u6211\u7684\u5de5\u4f5c\u53f0</el-dropdown-item>'
t = t.replace(old_workbench + '\n', '')

p.write_text(t, encoding='utf-8')
print('Done - changes applied')
print(f'  Personal center: {old_center in t}')
print(f'  Workbench found: {old_workbench in p.read_text(encoding="utf-8-sig")}')
