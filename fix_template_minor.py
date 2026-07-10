import pathlib

filepath = pathlib.Path(r"C:\Users\Administrator\Desktop\Zhihire-StarMap\frontend\src\views\user\UserProfile.vue")
lines = filepath.read_text(encoding="utf-8-sig").splitlines(keepends=True)
changes = []

for i, line in enumerate(lines):
    s = line.rstrip()

    # Fix certificate item to have a remove button with proper structure
    if 'v-for="(c, i) in profile.certificates" :key="i" class="cert-item"' in s and "removeCertificate" not in s:
        lines[i] = s.replace(
            '{{ c.name }}</div>',
            '{{ c.name }}<span class="remove-link" @click="removeCertificate(i)">删除</span></div>'
        ) + "\n"
        changes.append(f"Fixed certificate remove button at line {i+1}")

    # Fix language remove button: it's outside the lang-item div, move it inside
    # Current: lines[i] = remove-link line, lines[i-1] = closing span tag
    if 'class="remove-link" @click="removeLanguage(i)"' in s:
        # This is the remove button - check if it should be inside
        prev = lines[i-2].rstrip() if i >= 2 else ""
        current_indent = len(s) - len(s.lstrip())
        prev_indent = len(prev) - len(prev.lstrip()) if prev else 0
        if current_indent < prev_indent:
            # The remove link is at a lower indent than the lang-level span - it's outside
            # Move it to be inside the lang-item div
            actual_indent = "          "  # 10 spaces, same as the spans
            lines[i] = actual_indent + '<span class="remove-link" @click="removeLanguage(i)">删除</span>\n'
            changes.append(f"Fixed language remove indent at line {i+1}")

for c in changes:
    print(f"  {c}")

result = "".join(lines)
filepath.write_text(result, encoding="utf-8")
print(f"Done. {len(lines)} lines.")
