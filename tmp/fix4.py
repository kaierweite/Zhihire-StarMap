with open("C:\\Users\\Administrator\\Desktop\\Zhihire-StarMap\\frontend\\src\\views\\user\\ResumeCenter.vue", encoding="utf-8") as f:
    c = f.read()

# Find and replace the broken :title line
bad1_start = c.find(":title=\"item.title")
bad1_end = c.find("\n                >", bad1_start)

bad1_line = c[bad1_start:bad1_end]
print("Replacing: " + repr(bad1_line))

# Proper fix: use || (OR) operator, proper quote wrapping for empty string
good_line = ':title="item.title || item.file_name || \'\'"'
c = c.replace(bad1_line, good_line)

# Fix or -> || in the span
c = c.replace("{{ item.title or item.file_name or '未命名' }}", "{{ item.title || item.file_name || '未命名' }}")

with open("C:\\Users\\Administrator\\Desktop\\Zhihire-StarMap\\frontend\\src\\views\\user\\ResumeCenter.vue", "w", encoding="utf-8") as f:
    f.write(c)
print("Fixed")
