path = "C:\\Users\\Administrator\\Desktop\\Zhihire-StarMap\\frontend\\src\\views\\user\\ResumeCenter.vue"
with open(path, encoding="utf-8") as f:
    c = f.read()

# Fix :title binding
old1 = ':title="item.title \'\' item.file_name \'\'\'\'"'
new1 = ':title="item.title or item.file_name or \'\'"'
c = c.replace(old1, new1)

# Fix name display
old2 = "{{ item.title '' item.file_name '' 未命名'' }}"
new2 = "{{ item.title or item.file_name or '未命名' }}"
c = c.replace(old2, new2)

# Fix the · character (was replaced with .)
c = c.replace("PDF / DOC / DOCX . 最大", "PDF / DOC / DOCX · 最大")

with open(path, "w", encoding="utf-8") as f:
    f.write(c)
print("Fixed")
