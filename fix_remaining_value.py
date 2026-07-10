import pathlib

filepath = pathlib.Path(r"C:\Users\Administrator\Desktop\Zhihire-StarMap\frontend\src\views\user\UserProfile.vue")
lines = filepath.read_text(encoding="utf-8-sig").splitlines(keepends=True)
changes = []

# Fix push() calls that lost .value
fixes = {
    # First pass: restore straightforward .value cases
}
search_replace = [
    (182, "...workForm)", "...workForm.value)"),   # profile.value.work.push({ ...workForm.value })
    (196, "...projectForm)", "...projectForm.value)"),  # profile.value.projects.push({ ...projectForm.value })
    (248, "...certificateForm)", "...certificateForm.value)"),  # profile.value.certificates.push({ ...certificateForm.value })
]
for lnum, old_pat, new_pat in search_replace:
    idx = lnum - 1
    if idx < len(lines) and old_pat in lines[idx]:
        lines[idx] = lines[idx].replace(old_pat, new_pat)
        changes.append(f"Restored {new_pat} at line {lnum}")

for c in changes:
    print(f"  {c}")

result = "".join(lines)
filepath.write_text(result, encoding="utf-8")
print(f"Done. {len(lines)} lines.")
