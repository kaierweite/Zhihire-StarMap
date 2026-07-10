import pathlib

path = pathlib.Path(r"C:\Users\Administrator\Desktop\Zhihire-StarMap\frontend\src\views\user\UserProfile.vue")
lines = path.read_text(encoding="utf-8-sig").splitlines(keepends=True)
changes = []

# 1) Add edit button after the section title h2 for 求职意向
for i, line in enumerate(lines):
    s = line.strip()
    if "<h2 class=\"section-title\">" in s and "求职意向" in s:
        indent = "          "
        lines[i] = indent + "<h2 class=\"section-title\">求职意向</h2>\n"
        lines.insert(i+1, indent + "<button class=\"edit-btn\" @click=\"openIntentionDialog\"><Edit :size=\"14\" /> 编辑</button>\n")
        changes.append(f"Added edit button at line {i+1}")
        break

# 2) Add @click to intention-grid
for i, line in enumerate(lines):
    s = line.strip()
    if '<div class="intention-grid">' in s:
        lines[i] = s.replace('class="intention-grid"', 'class="intention-grid" @click="openIntentionDialog" style="cursor: pointer;"') + "\n"
        changes.append(f"Added @click to intention-grid at line {i+1}")
        break

# 3) Add dialogState.intention
for i, line in enumerate(lines):
    s = line.strip()
    if "const dialogState = reactive({" in s:
        for j in range(i, min(i+15, len(lines))):
            if "})" in lines[j].strip():
                lines[j] = lines[j].replace("})", "  intention: false,\n})")
                changes.append(f"Added dialogState.intention at line {j+1}")
                break
        break

# 4) Add intentionForm
for i, line in enumerate(lines):
    s = line.strip()
    if "const certificateForm = ref({" in s:
        indent = "  "
        lines.insert(i+1, indent + 'const intentionForm = ref({ positions: "", salary_min: null, salary_max: null, city: "", worktype: "", industry: "" })\n')
        changes.append(f"Added intentionForm at line {i+2}")
        break

# 5) Add openIntentionDialog and saveIntention functions after the remove functions block
for i, line in enumerate(lines):
    s = line.strip()
    if "function removeCertificate" in s:
        # Find the closing brace of removeCertificate (it's on the same line)
        indent = "  "
        funcs = "\n" + indent + """// ====== 求职意向 ======
function openIntentionDialog() {
  const v = profile.value.intention
  intentionForm.value = {
    positions: v.positions || "",
    salary_min: null,
    salary_max: null,
    city: v.cities || "",
    worktype: v.worktype || "",
    industry: v.industry || "",
  }
  dialogState.intention = true
}
function saveIntention() {
  const form = intentionForm.value
  const p = profile.value.intention
  p.positions = form.positions || ""
  p.salary = form.salary_min || form.salary_max
    ? (form.salary_min ? form.salary_min + "K" : "") + "-" + (form.salary_max ? form.salary_max + "K" : "")
    : ""
  p.cities = form.city || ""
  p.worktype = form.worktype || ""
  p.industry = form.industry || ""
  dialogState.intention = false
  updateProfile({
    expected_city: form.city || null,
    expected_salary_min: form.salary_min,
    expected_salary_max: form.salary_max,
  }).then(() => {
    ElMessage.success("求职意向已更新")
  }).catch(() => {})
}
"""
        lines.insert(i+1, funcs)
        changes.append(f"Added intention functions after line {i+1}")
        break

# 6) Add intention dialog component after certificate dialog
in_dialog_block = False
dialog_count = 0
for i, line in enumerate(lines):
    s = line.strip()
    if s.startswith("<el-dialog"):
        in_dialog_block = True
    if s.startswith("</el-dialog>") and in_dialog_block:
        dialog_count += 1
        in_dialog_block = False
        # After 7th dialog (certificate), insert intention dialog
        if dialog_count == 7:
            indent = "        "
            dialog = "\n" + indent + """<!-- ========== 求职意向对话框 ========== -->
        <el-dialog v-model="dialogState.intention" title="编辑求职意向" width="500px" :close-on-click-modal="false">
          <el-form label-position="top">
            <el-form-item label="期望职位">
              <el-input v-model="intentionForm.position" placeholder="请输入期望职位" />
            </el-form-item>
            <el-form-item label="期望薪资（最低 K/月）">
              <el-input-number v-model="intentionForm.salary_min" :min="0" :step="1" style="width: 100%" />
            </el-form-item>
            <el-form-item label="期望薪资（最高 K/月）">
              <el-input-number v-model="intentionForm.salary_max" :min="0" :step="1" style="width: 100%" />
            </el-form-item>
            <el-form-item label="期望城市">
              <el-input v-model="intentionForm.city" placeholder="请输入期望城市" />
            </el-form-item>
            <el-form-item label="工作类型">
              <el-select v-model="intentionForm.worktype" placeholder="请选择工作类型" style="width: 100%">
                <el-option label="全职" value="全职" />
                <el-option label="兼职" value="兼职" />
                <el-option label="实习" value="实习" />
              </el-select>
            </el-form-item>
            <el-form-item label="期望行业">
              <el-input v-model="intentionForm.industry" placeholder="请输入期望行业" />
            </el-form-item>
          </el-form>
          <template #footer>
            <el-button @click="dialogState.intention = false">取消</el-button>
            <el-button type="primary" @click="saveIntention">保存</el-button>
          </template>
        </el-dialog>
"""
            lines.insert(i+1, dialog)
            changes.append(f"Added intention dialog after dialog {dialog_count} at line {i+1}")
            break

result = "".join(lines)
path.write_text(result, encoding="utf-8")
print(f"Done. {len(lines)} lines.")
for c in changes:
    print(f"  {c}")
