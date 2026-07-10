import pathlib, json

filepath = pathlib.Path(r"C:\Users\Administrator\Desktop\Zhihire-StarMap\frontend\src\views\user\UserProfile.vue")
old = filepath.read_text(encoding="utf-8-sig")
lines = old.splitlines(keepends=True)
changes = []

# 1) Add @click to add-placeholder divs
add_click_map = {
    "openStrengthsDialog": 330,
    "openEducationDialog": 372,
    "openWorkDialog": 390,
    "openProjectDialog": 407,
    "openSkillDialog": 429,
    "openLanguageDialog": 447,
    "openCertificateDialog": 461,
}
for fn_name, lnum in add_click_map.items():
    idx = lnum - 1  # 0-based
    line = lines[idx]
    if "@click" not in line:
        new_line = line.replace('class="add-placeholder"', f'class="add-placeholder" @click="{fn_name}"')
        if new_line != line:
            lines[idx] = new_line
            changes.append(f"Added @click={fn_name} at line {lnum}")

# 2) Insert dialog components before </template>
template_close_idx = 468  # 0-based (469 - 1)
# Skip past current template close and empty lines
for t_idx in range(469, len(lines)):
    if lines[t_idx].strip() == "</template>":
        template_close_idx = t_idx
        break

dialogs = '''        <!-- 个人优势对话框 -->
        <el-dialog v-model="dialogState.strengths" title="编辑个人优势" width="500px" :close-on-click-modal="false">
          <el-input v-model="strengthsForm" type="textarea" :rows="5" placeholder="请描述您的个人优势，如：沟通能力强、团队协作、学习能力..." maxlength="500" show-word-limit />
          <template #footer>
            <el-button @click="dialogState.strengths = false">取消</el-button>
            <el-button type="primary" @click="saveStrengths">保存</el-button>
          </template>
        </el-dialog>

        <!-- 教育经历对话框 -->
        <el-dialog v-model="dialogState.education" title="添加教育经历" width="500px" :close-on-click-modal="false">
          <el-form label-position="top">
            <el-form-item label="学校名称" required>
              <el-input v-model="educationForm.value.school" placeholder="请输入学校名称" />
            </el-form-item>
            <el-form-item label="学历" required>
              <el-select v-model="educationForm.value.degree" placeholder="请选择学历" style="width: 100%">
                <el-option label="博士" value="博士" />
                <el-option label="硕士" value="硕士" />
                <el-option label="本科" value="本科" />
                <el-option label="大专" value="大专" />
                <el-option label="高中/中专" value="高中/中专" />
                <el-option label="其他" value="其他" />
              </el-select>
            </el-form-item>
            <el-form-item label="专业">
              <el-input v-model="educationForm.value.major" placeholder="请输入专业名称" />
            </el-form-item>
            <el-form-item label="就读时间">
              <el-input v-model="educationForm.value.period" placeholder="如：2020.09 - 2024.06" />
            </el-form-item>
          </el-form>
          <template #footer>
            <el-button @click="dialogState.education = false">取消</el-button>
            <el-button type="primary" @click="saveEducation">添加</el-button>
          </template>
        </el-dialog>

        <!-- 工作/实习经历对话框 -->
        <el-dialog v-model="dialogState.work" title="添加工作/实习经历" width="550px" :close-on-click-modal="false">
          <el-form label-position="top">
            <el-form-item label="职位" required>
              <el-input v-model="workForm.value.title" placeholder="请输入职位名称" />
            </el-form-item>
            <el-form-item label="公司名称" required>
              <el-input v-model="workForm.value.company" placeholder="请输入公司名称" />
            </el-form-item>
            <el-form-item label="工作时间">
              <el-input v-model="workForm.value.period" placeholder="如：2024.01 - 至今" />
            </el-form-item>
            <el-form-item label="工作描述">
              <el-input v-model="workForm.value.desc" type="textarea" :rows="3" placeholder="请描述您的主要工作内容" />
            </el-form-item>
          </el-form>
          <template #footer>
            <el-button @click="dialogState.work = false">取消</el-button>
            <el-button type="primary" @click="saveWork">添加</el-button>
          </template>
        </el-dialog>

        <!-- 项目经历对话框 -->
        <el-dialog v-model="dialogState.project" title="添加项目经历" width="550px" :close-on-click-modal="false">
          <el-form label-position="top">
            <el-form-item label="项目名称" required>
              <el-input v-model="projectForm.value.name" placeholder="请输入项目名称" />
            </el-form-item>
            <el-form-item label="项目描述">
              <el-input v-model="projectForm.value.desc" type="textarea" :rows="4" placeholder="请描述您在项目中的角色与主要贡献" />
            </el-form-item>
          </el-form>
          <template #footer>
            <el-button @click="dialogState.project = false">取消</el-button>
            <el-button type="primary" @click="saveProject">添加</el-button>
          </template>
        </el-dialog>

        <!-- 专业技能对话框 -->
        <el-dialog v-model="dialogState.skill" title="添加专业技能" width="450px" :close-on-click-modal="false">
          <div class="skill-add-row">
            <el-input v-model="skillInput" placeholder="输入技能名称后点击添加" @keydown.enter="addSkill" style="flex:1" />
            <el-button type="primary" @click="addSkill">添加</el-button>
          </div>
          <div v-if="profile.skills.length" class="skills-list" style="margin-top: 16px">
            <span v-for="(skill, i) in profile.skills" :key="skill" class="skill-chip" :class="chipColors[i % chipColors.length]">
              {{ skill }}
              <span class="chip-remove" @click="removeSkill(i)"><X :size="10" /></span>
            </span>
          </div>
          <div v-else style="margin-top: 16px; color: #909399; font-size: 13px; text-align: center;">暂无技能，请在上方输入添加</div>
          <template #footer>
            <el-button @click="dialogState.skill = false">完成</el-button>
          </template>
        </el-dialog>

        <!-- 语言能力对话框 -->
        <el-dialog v-model="dialogState.language" title="添加语言能力" width="450px" :close-on-click-modal="false">
          <el-form label-position="top">
            <el-form-item label="语言" required>
              <el-select v-model="languageForm.value.name" placeholder="请选择语言" style="width: 100%">
                <el-option label="中文（普通话）" value="中文（普通话）" />
                <el-option label="英语" value="英语" />
                <el-option label="日语" value="日语" />
                <el-option label="韩语" value="韩语" />
                <el-option label="法语" value="法语" />
                <el-option label="德语" value="德语" />
                <el-option label="西班牙语" value="西班牙语" />
                <el-option label="俄语" value="俄语" />
                <el-option label="其他" value="其他" />
              </el-select>
            </el-form-item>
            <el-form-item label="熟练程度" required>
              <el-select v-model="languageForm.value.level" placeholder="请选择熟练程度" style="width: 100%">
                <el-option label="母语" value="母语" />
                <el-option label="精通" value="精通" />
                <el-option label="熟练" value="熟练" />
                <el-option label="良好" value="良好" />
                <el-option label="一般" value="一般" />
                <el-option label="基础" value="基础" />
              </el-select>
            </el-form-item>
          </el-form>
          <template #footer>
            <el-button @click="dialogState.language = false">取消</el-button>
            <el-button type="primary" @click="saveLanguage">添加</el-button>
          </template>
        </el-dialog>

        <!-- 证书对话框 -->
        <el-dialog v-model="dialogState.certificate" title="添加证书" width="450px" :close-on-click-modal="false">
          <el-form label-position="top">
            <el-form-item label="证书名称" required>
              <el-input v-model="certificateForm.value.name" placeholder="请输入证书名称" />
            </el-form-item>
          </el-form>
          <template #footer>
            <el-button @click="dialogState.certificate = false">取消</el-button>
            <el-button type="primary" @click="saveCertificate">添加</el-button>
          </template>
        </el-dialog>
'''

# Insert dialogs before </template>
dialogs_lines = [l + "\n" for l in dialogs.split("\n")]
# Remove the last newline if present
if dialogs_lines and dialogs_lines[-1] == "\n":
    dialogs_lines = dialogs_lines[:-1]

lines_before = lines[:template_close_idx]
lines_after = lines[template_close_idx:]
new_lines = lines_before + dialogs_lines + lines_after
changes.append(f"Inserted dialog components before </template> (line {template_close_idx+1})")
lines = new_lines

# 3) Update education section to add remove button - find the key line
# Line 378: the edu-item div
for i, line in enumerate(lines):
    stripped = line.strip()
    if '<div v-for="edu in profile.education" :key="edu.school + edu.degree" class="edu-item">' in stripped:
        # Add remove button after the detail div
        for j in range(i, min(i+10, len(lines))):
            if '</div>' in lines[j] and lines[j].strip() == '</div>' and j > i:
                # This is the closing </div> of the edu-item
                indent = ' '*10
                lines[j] = indent + '<span class="remove-link" @click="removeEducation(\'edu\')">删除</span>\n' + lines[j]
                changes.append(f"Added remove button to education at line {j}")
                break
        break

# 4) Update work section to use index-based key and add remove
for i, line in enumerate(lines):
    stripped = line.strip()
    if '<div v-for="w in profile.work" :key="w.title" class="exp-item">' in stripped:
        lines[i] = line.replace(':key="w.title"', ':key="w.title + w.company"')
        # Add remove after desc
        for j in range(i, min(i+10, len(lines))):
            if 'exp-desc' in lines[j] or 'exp-meta' in lines[j]:
                continue
            if '</div>' in lines[j] and lines[j].strip() == '</div>' and j > i:
                indent = ' '*10
                lines[j] = indent + '<span class="remove-link" @click="removeWork(idx)">删除</span>\n' + lines[j]
                changes.append(f"Added remove button to work at line {j}")
                break
        break

# 5) Update projects section
for i, line in enumerate(lines):
    stripped = line.strip()
    if '<div v-for="p in profile.projects" :key="p.name" class="exp-item">' in stripped:
        lines[i] = line.replace(':key="p.name"', ':key="p.name + p.desc"')
        for j in range(i, min(i+10, len(lines))):
            if 'exp-desc' in lines[j] or 'exp-title' in lines[j]:
                continue
            if '</div>' in lines[j] and lines[j].strip() == '</div>' and j > i:
                indent = ' '*10
                lines[j] = indent + '<span class="remove-link" @click="removeProject(idx)">删除</span>\n' + lines[j]
                changes.append(f"Added remove button to project at line {j}")
                break
        break

# 6) Update languages section
for i, line in enumerate(lines):
    stripped = line.strip()
    if '<div v-for="l in profile.languages" :key="l.name" class="lang-item">' in stripped:
        for j in range(i, min(i+10, len(lines))):
            if '</div>' in lines[j] and 'lang-item' not in lines[j]:
                indent = ' '*12
                lines[j] = indent + '<span class="remove-link" @click="removeLanguage(idx)">删除</span>\n' + lines[j]
                changes.append(f"Added remove button to language at line {j}")
                break
        break

# 7) Update certificates section
for i, line in enumerate(lines):
    stripped = line.strip()
    if '<div v-for="c in profile.certificates" :key="c.name" class="cert-item">' in stripped:
        lines[i] = line.replace('<div v-for="c in profile.certificates" :key="c.name" class="cert-item">',
                                '<div v-for="(c, i) in profile.certificates" :key="i" class="cert-item" style="display: flex; justify-content: space-between;">')
        indent = ' '*10
        # Replace the line after c.name
        for j in range(i+1, min(i+5, len(lines))):
            if '{{ c.name }}' in lines[j]:
                lines[j] = indent + '{{ c.name }}\n'
                lines.insert(j+1, indent + '<span class="remove-link" @click="removeCertificate(i)">删除</span>\n')
                changes.append(f"Added remove button to certificate around line {j}")
                break
        break

# 8) Add new CSS before </style>
style_close_idx = None
for i in range(len(lines)-1, -1, -1):
    if "</style>" in lines[i] and lines[i].strip().startswith('</style>'):
        style_close_idx = i
        break

if style_close_idx:
    new_css = """/* ====== 删除链接 ====== */
.remove-link {
  font-size: 12px;
  color: #f56c6c;
  cursor: pointer;
  margin-left: 8px;
  &:hover { text-decoration: underline; }
}
/* 工具类 */
.skill-add-row { display: flex; gap: 8px; align-items: center; }
.mt-16 { margin-top: 16px; }
.chip-remove { margin-left: 4px; cursor: pointer; }
"""
    css_lines = new_css.splitlines(keepends=True)
    lines_before = lines[:style_close_idx]
    lines_after = lines[style_close_idx:]
    lines = lines_before + css_lines + lines_after
    changes.append(f"Added CSS before </style> at line {style_close_idx+1}")

# Write back
result = "".join(lines)
filepath.write_text(result, encoding="utf-8")
print(json.dumps({"changes": changes, "line_count": len(lines)}))
