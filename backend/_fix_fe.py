import io
p = r"C:\Users\Administrator\Desktop\Zhihire-StarMap\frontend\src\views\user\UserProfile.vue"
with io.open(p, encoding="utf-8") as f:
    t = f.read()

# ===== 1. mapProfile 补全子表 + 意向字段 =====
old_map = (
    "  profile.value.intention.salary = formatSalary(data.expected_salary_min, data.expected_salary_max)\n"
    "  profile.value.intention.cities = data.expected_city || \"\"\n"
)
new_map = (
    "  profile.value.intention.salary = formatSalary(data.expected_salary_min, data.expected_salary_max)\n"
    "  profile.value.intention.cities = data.expected_city || \"\"\n"
    "  profile.value.intention.positions = data.expected_position || \"\"\n"
    "  profile.value.intention.worktype = data.expected_worktype || \"\"\n"
    "  profile.value.intention.industry = data.expected_industry || \"\"\n"
    "  profile.value.work = (data.work_experiences || []).map(w => ({ title: w.title, company: w.company, period: w.period || \"\", desc: w.description || \"\" }))\n"
    "  profile.value.projects = (data.project_experiences || []).map(p => ({ name: p.name, desc: p.description || \"\" }))\n"
    "  profile.value.languages = (data.languages || []).map(l => ({ name: l.name, level: l.level || \"\" }))\n"
    "  profile.value.certificates = (data.certificates || []).map(c => ({ name: c.name }))\n"
)
assert old_map in t, "old map block not found"
t = t.replace(old_map, new_map)

# ===== 2. openIntentionDialog 回填薪资起止值 =====
old_intent_dlg = (
    "function openIntentionDialog() {\n"
    "    const v = profile.value.intention\n"
    "    intentionForm.value = {\n"
    "      positions: v.positions || \"\",\n"
    "      salary_min: null,\n"
    "      salary_max: null,\n"
    "      city: v.cities || \"\",\n"
    '      worktype: v.worktype || "",\n'
    '      industry: v.industry || "",\n'
    "    }\n"
    "    dialogState.intention = true\n"
    "  }"
)
new_intent_dlg = (
    "function openIntentionDialog() {\n"
    "    const v = profile.value.intention\n"
    "    intentionForm.value = {\n"
    "      positions: v.positions || \"\",\n"
    "      salary_min: null,\n"
    "      salary_max: null,\n"
    "      city: v.cities || \"\",\n"
    '      worktype: v.worktype || "",\n'
    '      industry: v.industry || "",\n'
    "    }\n"
    "    dialogState.intention = true\n"
    "    // 页面加载后先 GET 一次，用解析到的值回填\n"
    "    getProfile().then(res => {\n"
    "      if (res.data.code === 200 && res.data.data) {\n"
    "        const d = res.data.data\n"
    "        if (d.expected_salary_min != null) intentionForm.value.salary_min = Math.round(d.expected_salary_min / 1000)\n"
    "        if (d.expected_salary_max != null) intentionForm.value.salary_max = Math.round(d.expected_salary_max / 1000)\n"
    "      }\n"
    "    }).catch(() => {})\n"
    "  }"
)
assert old_intent_dlg in t, "old openIntentionDialog not found"
t = t.replace(old_intent_dlg, new_intent_dlg)

# ===== 3. saveIntention 补传 expected_position/worktype/industry =====
old_save_intent = (
    "    dialogState.intention = false\n"
    "  updateProfile({\n"
    "      expected_city: form.city,\n"
    "      expected_salary_min: form.salary_min,\n"
    "      expected_salary_max: form.salary_max,\n"
    "    }).then(() => {\n"
    "      ElMessage.success(\"求职意向已更新\")\n"
    "    }).catch(() => {})\n"
    "  }"
)
new_save_intent = (
    "    dialogState.intention = false\n"
    "  updateProfile({\n"
    "      expected_city: form.city,\n"
    "      expected_position: form.positions,\n"
    "      expected_worktype: form.worktype,\n"
    "      expected_industry: form.industry,\n"
    "      expected_salary_min: form.salary_min,\n"
    "      expected_salary_max: form.salary_max,\n"
    "    }).then(() => {\n"
    "      ElMessage.success(\"求职意向已更新\")\n"
    "    }).catch(() => {})\n"
    "  }"
)
assert old_save_intent in t, "old saveIntention not found"
t = t.replace(old_save_intent, new_save_intent)

# ===== 4. saveWork 改为调用 updateProfile =====
old_save_work = (
    '  profile.value.work.push({ ...workForm.value })\n'
    '  dialogState.work = false\n'
    '  ElMessage.success("工作经历已添加（本地保存，后端同步即将支持）")'
)
new_save_work = (
    '  profile.value.work.push({ ...workForm.value })\n'
    '  dialogState.work = false\n'
    '  const arr = profile.value.work.map(w => ({ title: w.title, company: w.company, period: w.period || null, description: w.desc || null }))\n'
    '  updateProfile({ work_experiences: arr }).then(() => {\n'
    '    ElMessage.success("工作经历已添加")\n'
    '  }).catch(() => {})'
)
assert old_save_work in t, "old saveWork not found"
t = t.replace(old_save_work, new_save_work)

# ===== 5. saveProject 改为调用 updateProfile =====
old_save_proj = (
    '  profile.value.projects.push({ ...projectForm.value })\n'
    '  dialogState.project = false\n'
    '  ElMessage.success("项目经历已添加（本地保存，后端同步即将支持）")'
)
new_save_proj = (
    '  profile.value.projects.push({ ...projectForm.value })\n'
    '  dialogState.project = false\n'
    '  const arr = profile.value.projects.map(p => ({ name: p.name, description: p.desc || null }))\n'
    '  updateProfile({ project_experiences: arr }).then(() => {\n'
    '    ElMessage.success("项目经历已添加")\n'
    '  }).catch(() => {})'
)
assert old_save_proj in t, "old saveProject not found"
t = t.replace(old_save_proj, new_save_proj)

# ===== 6. saveLanguage 改为调用 updateProfile =====
old_save_lang = (
    '  profile.value.languages.push({ ...languageForm.value })\n'
    '  dialogState.language = false\n'
    '  ElMessage.success("语言能力已添加（本地保存，后端同步即将支持）")'
)
new_save_lang = (
    '  profile.value.languages.push({ ...languageForm.value })\n'
    '  dialogState.language = false\n'
    '  const arr = profile.value.languages.map(l => ({ name: l.name, level: l.level || null }))\n'
    '  updateProfile({ languages: arr }).then(() => {\n'
    '    ElMessage.success("语言能力已添加")\n'
    '  }).catch(() => {})'
)
assert old_save_lang in t, "old saveLanguage not found"
t = t.replace(old_save_lang, new_save_lang)

# ===== 7. saveCertificate 改为调用 updateProfile =====
old_save_cert = (
    '  profile.value.certificates.push({ ...certificateForm.value })\n'
    '  dialogState.certificate = false\n'
    '  ElMessage.success("证书已添加（本地保存，后端同步即将支持）")'
)
new_save_cert = (
    '  profile.value.certificates.push({ ...certificateForm.value })\n'
    '  dialogState.certificate = false\n'
    '  const arr = profile.value.certificates.map(c => ({ name: c.name }))\n'
    '  updateProfile({ certificates: arr }).then(() => {\n'
    '    ElMessage.success("证书已添加")\n'
    '  }).catch(() => {})'
)
assert old_save_cert in t, "old saveCertificate not found"
t = t.replace(old_save_cert, new_save_cert)

# ===== 8. removeWork/Project/Language/Certificate 调用 updateProfile =====
# removeWork
old_rw = "function removeWork(idx: number) { profile.value.work.splice(idx, 1) }"
new_rw = (
    "function removeWork(idx: number) {\n"
    "  profile.value.work.splice(idx, 1)\n"
    "  const arr = profile.value.work.map(w => ({ title: w.title, company: w.company, period: w.period || null, description: w.desc || null }))\n"
    "  updateProfile({ work_experiences: arr }).catch(() => {})\n"
    "}"
)
assert old_rw in t, "old removeWork not found"
t = t.replace(old_rw, new_rw)

# removeProject
old_rp = "function removeProject(idx: number) { profile.value.projects.splice(idx, 1) }"
new_rp = (
    "function removeProject(idx: number) {\n"
    "  profile.value.projects.splice(idx, 1)\n"
    "  const arr = profile.value.projects.map(p => ({ name: p.name, description: p.desc || null }))\n"
    "  updateProfile({ project_experiences: arr }).catch(() => {})\n"
    "}"
)
assert old_rp in t, "old removeProject not found"
t = t.replace(old_rp, new_rp)

# removeLanguage
old_rl = "function removeLanguage(idx: number) { profile.value.languages.splice(idx, 1) }"
new_rl = (
    "function removeLanguage(idx: number) {\n"
    "  profile.value.languages.splice(idx, 1)\n"
    "  const arr = profile.value.languages.map(l => ({ name: l.name, level: l.level || null }))\n"
    "  updateProfile({ languages: arr }).catch(() => {})\n"
    "}"
)
assert old_rl in t, "old removeLanguage not found"
t = t.replace(old_rl, new_rl)

# removeCertificate
old_rc = "function removeCertificate(idx: number) { profile.value.certificates.splice(idx, 1) }"
new_rc = (
    "function removeCertificate(idx: number) {\n"
    "  profile.value.certificates.splice(idx, 1)\n"
    "  const arr = profile.value.certificates.map(c => ({ name: c.name }))\n"
    "  updateProfile({ certificates: arr }).catch(() => {})\n"
    "}"
)
assert old_rc in t, "old removeCertificate not found"
t = t.replace(old_rc, new_rc)

with io.open(p, "w", encoding="utf-8") as f:
    f.write(t)
print("ok")
