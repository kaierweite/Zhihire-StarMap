import pathlib

p = pathlib.Path(r'C:\Users\Administrator\Desktop\Zhihire-StarMap\frontend\src\components\AppHeader.vue')
t = p.read_text(encoding='utf-8-sig')

# Change 个人中心 link to /user/profile
target = "<el-dropdown-item @click=\"\"router.push('/user')\"\"个人中心</el-dropdown-item>"
replacement = "<el-dropdown-item @click=\"\"router.push('/user/profile')\"\"个人中心</el-dropdown-item>"
t = t.replace(target, replacement)

# Remove 我的工作台 line
remove = "<el-dropdown-item @click=\"\"goDashboard\"\"我的工作台</el-dropdown-item>"
t = t.replace(remove + '\n', '')

p.write_text(t, encoding='utf-8')
print('Done')
