import pathlib

filepath = pathlib.Path(r"C:\Users\Administrator\Desktop\Zhihire-StarMap\frontend\src\views\user\UserProfile.vue")
lines = filepath.read_text(encoding="utf-8-sig").splitlines(keepends=True)
changes = []

for i, line in enumerate(lines):
    s = line.rstrip()

    # Only check template sections (lines after <template> line marker)
    # Find the template section
    pass

# First, find where the template starts and ends
template_start = None
template_end = None
for i, line in enumerate(lines):
    if "<template>" in line:
        template_start = i
    if "</template>" in line and template_start is not None and template_end is None:
        template_end = i
        break

print(f"Template: lines {template_start+1} to {template_end+1}")

# Restore .value in script section for all the form refs
# List of form vars that are refs and need .value in script
script_line_fixes = {
    # line numbers are 1-based, convert to 0-based
    # These are the lines (1-based) that we need to restore .value in
    152: 'educationForm.value = { school: "", degree: "", major: "", period: "" }',
    156: '  const form = educationForm.value',
    174: '  workForm.value = { title: "", company: "", period: "", desc: "" }',
    178: '  if (!workForm.value.title || !workForm.value.company) {',
    182: '  profile.value.work.push({ ...workForm.value })',
    188: '  projectForm.value = { name: "", desc: "" }',
    192: '  if (!projectForm.value.name) {',
    196: '  profile.value.projects.push({ ...projectForm.value })',
    226: '  languageForm.value = { name: "", level: "" }',
    230: '  if (!languageForm.value.name) {',
    234: '  profile.value.languages.push({ ...languageForm.value })',
    240: '  certificateForm.value = { name: "" }',
    244: '  if (!certificateForm.value.name) {',
    248: '  profile.value.certificates.push({ ...certificateForm.value })',
}

for lnum, expected_content in script_line_fixes.items():
    idx = lnum - 1
    # Check if .value was removed from this line
    if idx < len(lines) and ".value" not in lines[idx]:
        # Check if this is the right line
        if "educationForm" in lines[idx] or "workForm" in lines[idx] or "projectForm" in lines[idx] or "languageForm" in lines[idx] or "certificateForm" in lines[idx]:
            # Restore .value by finding the form var and adding .value before = or .
            for var_name in ["educationForm", "workForm", "projectForm", "languageForm", "certificateForm"]:
                if var_name in lines[idx] and (" = " in lines[idx] or "." in lines[idx].split(var_name, 1)[1][:5]):
                    # The line has formVar = or formVar. - add back .value
                    lines[idx] = lines[idx].replace(var_name + " = ", var_name + ".value = ")
                    lines[idx] = lines[idx].replace(var_name + ".", var_name + ".value.", 1)
                    changes.append(f"Restored .value at line {lnum}")

for c in changes:
    print(f"  {c}")

result = "".join(lines)
filepath.write_text(result, encoding="utf-8")
print(f"Done. {len(lines)} lines.")
