import re
path = "C:\\Users\\Administrator\\Desktop\\Zhihire-StarMap\\frontend\\src\\views\\user\\ResumeCenter.vue"
with open(path, encoding="utf-8") as f:
    c = f.read()

# Fix by precise substring replacement
# :title="item.title '' item.file_name ''''"  -> :title="item.title || item.file_name || ''"
bad1 = ':title="item.title \'\' item.file_name \'\'\'\'"'
pipe = "||"
good1 = ':title="item.title ' + pipe + ' item.file_name ' + pipe + " ''\""
c = c.replace(bad1, good1)

# {{ item.title '' item.file_name '' \u672a\u547d\u540d'' }}  -> {{ item.title || item.file_name || '\u672a\u547d\u540d' }}
bad2 = "{{ item.title '' item.file_name '' \u672a\u547d\u540d'' }}"
good2 = "{{ item.title " + pipe + " item.file_name " + pipe + " '\u672a\u547d\u540d' }}"
c = c.replace(bad2, good2)

# Fix dot back to middle dot
c = c.replace("PDF / DOC / DOCX . \u6700\u5927", "PDF / DOC / DOCX \u00b7 \u6700\u5927")

with open(path, "w", encoding="utf-8") as f:
    f.write(c)
print("Fixed")
