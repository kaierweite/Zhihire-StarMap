import pathlib

filepath = pathlib.Path(r"C:\Users\Administrator\Desktop\Zhihire-StarMap\frontend\src\views\user\UserProfile.vue")
lines = filepath.read_text(encoding="utf-8-sig").splitlines(keepends=True)
changes = []

for i, line in enumerate(lines):
    s = line.rstrip()

    # Fix work: add (w, i) and removeWork(i)
    if '<div v-for="w in profile.work" :key="w.title + w.company" class="exp-item">' in s:
        lines[i] = line.replace('v-for="w in profile.work"', 'v-for="(w, i) in profile.work"')
        changes.append(f"Fixed work loop to use index at line {i+1}")

    if 'removeWork(idx)' in s:
        lines[i] = line.replace('removeWork(idx)', 'removeWork(i)')
        changes.append(f"Fixed removeWork call at line {i+1}")

    # Fix projects: add (p, i) and removeProject(i)
    if '<div v-for="p in profile.projects" :key="p.name + p.desc" class="exp-item">' in s:
        lines[i] = line.replace('v-for="p in profile.projects"', 'v-for="(p, i) in profile.projects"')
        changes.append(f"Fixed project loop to use index at line {i+1}")
    elif '<div v-for="p in profile.projects"' in s and ':(p, i)' not in s and ':(p,i)' not in s:
        # Might have been the original version
        lines[i] = line.replace('v-for="p in profile.projects"', 'v-for="(p, i) in profile.projects"')
        changes.append(f"Fixed project loop (alt) at line {i+1}")

    if 'removeProject(idx)' in s:
        lines[i] = line.replace('removeProject(idx)', 'removeProject(i)')
        changes.append(f"Fixed removeProject call at line {i+1}")

    # Fix education: add (edu, i) and removeEducation(i)
    if '<div v-for="edu in profile.education" :key="edu.school + edu.degree" class="edu-item">' in s:
        lines[i] = line.replace('v-for="edu in profile.education"', 'v-for="(edu, i) in profile.education"')
        changes.append(f"Fixed education loop to use index at line {i+1}")

    if "removeEducation('edu')" in s:
        lines[i] = line.replace("removeEducation('edu')", "removeEducation(i)")
        changes.append(f"Fixed removeEducation call at line {i+1}")

    # Fix languages: add (l, i) and removeLanguage(i)
    if '<div v-for="l in profile.languages" :key="l.name" class="lang-item">' in s:
        lines[i] = line.replace('v-for="l in profile.languages"', 'v-for="(l, i) in profile.languages"')
        changes.append(f"Fixed language loop to use index at line {i+1}")

    if 'removeLanguage(idx)' in s:
        lines[i] = line.replace('removeLanguage(idx)', 'removeLanguage(i)')
        changes.append(f"Fixed removeLanguage call at line {i+1}")

    # Fix certificates v-for (already has (c, i) from my earlier fix? Let's check)
    if '<div v-for="(c, i) in profile.certificates"' in s:
        pass  # Already correct
    elif '<div v-for="c in profile.certificates"' in s:
        lines[i] = line.replace('v-for="c in profile.certificates"', 'v-for="(c, i) in profile.certificates"')
        changes.append(f"Fixed certificate loop to use index at line {i+1}")

    # Fix skill dialog @click
    if 'class="add-placeholder small"' in s and "@click" not in s:
        lines[i] = s.replace('class="add-placeholder small"', 'class="add-placeholder small" @click="openSkillDialog"') + "\n"
        changes.append(f"Added @click=openSkillDialog at line {i+1}")

# Also fix certificate section - look for the second add-placeholder without @click
# For certificates, we need to also handle the <div v-else class="add-placeholder"> without @click
for i, line in enumerate(lines):
    s = line.rstrip()
    if 'class="add-placeholder"' in s and '@click' not in s and 'small' not in s:
        # Check context: is this in the certificate section? (after "证书" and before "</template>")
        context_before = "".join(lines[max(0,i-3):i])
        context_after = "".join(lines[i:min(len(lines),i+3)])
        if "证书" in context_before + context_after and "@click" not in s:
            lines[i] = s.replace('class="add-placeholder"', 'class="add-placeholder" @click="openCertificateDialog"') + "\n"
            changes.append(f"Fixed certificate add-placeholder @click at line {i+1}")

# Also fix the v-else for both skill and certificate sections
for i, line in enumerate(lines):
    s = line.rstrip()
    if 'v-else class="add-placeholder"' in s and '@click' not in s:
        context = "".join(lines[max(0,i-10):i+5])
        # Check if it's in skills or certificate section
        if "技能" in context:
            lines[i] = s.replace('v-else class="add-placeholder"', 'v-else class="add-placeholder" @click="openSkillDialog"') + "\n"
            changes.append(f"Fixed v-else skill add-placeholder @click at line {i+1}")
        elif "证" in context:
            lines[i] = s.replace('v-else class="add-placeholder"', 'v-else class="add-placeholder" @click="openCertificateDialog"') + "\n"
            changes.append(f"Fixed v-else cert add-placeholder @click at line {i+1}")

result = "".join(lines)
filepath.write_text(result, encoding="utf-8")
print(f"Total lines: {len(lines)}")
for c in changes:
    print(f"  {c}")
