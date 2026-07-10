import pathlib

filepath = pathlib.Path(r"C:\Users\Administrator\Desktop\Zhihire-StarMap\frontend\src\views\user\UserProfile.vue")
lines = filepath.read_text(encoding="utf-8-sig").splitlines(keepends=True)
changes = []

for i, line in enumerate(lines):
    s = line.rstrip()

    # Fix line 165-167: last possibly undefined after push
    if "const last = profile.value.education[profile.value.education.length - 1]" in s:
        lines[i] = s.replace(
            "const last = profile.value.education[profile.value.education.length - 1]",
            "const last = profile.value.education.at(-1)"
        ) + "\n"
        changes.append(f"Fixed last possibly undefined at line {i+1}")

    # Fix template form refs: remove .value from v-model expressions
    # educationForm.value.field -> educationForm.field
    if ".value" in s and ("educationForm" in s or "workForm" in s or "projectForm" in s or "languageForm" in s or "certificateForm" in s):
        new_line = s.replace(".value", "")
        if new_line != s:
            lines[i] = new_line + "\n"
            changes.append(f"Removed .value at line {i+1}: {s.strip()[:60]}")

for c in changes:
    print(f"  {c}")

result = "".join(lines)
filepath.write_text(result, encoding="utf-8")
print(f"Done. {len(lines)} lines.")
