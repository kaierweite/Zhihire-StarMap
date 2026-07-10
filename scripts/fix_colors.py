import sys
c = open(sys.argv[1], "r", encoding="utf-8").read()

# 1) Give root node a proper color so white text is readable
old_root = 'name: "能力图谱"'
new_root = 'name: "能力图谱",\n    itemStyle: { color: "#1a3a5c" }'
if old_root in c:
    c = c.replace(old_root, new_root)
else:
    # try with single quotes
    old_root_sq = "name: '能力图谱'"
    new_root_sq = "name: '能力图谱',\n    itemStyle: { color: '#1a3a5c' }"
    c = c.replace(old_root_sq, new_root_sq)

# 2) Fix level 1 labels - white with shadow
old_l1 = "label: { rotate: 'tangential', fontSize: 14, fontWeight: 700, color: '#303133' }"
new_l1 = "label: { rotate: 'tangential', fontSize: 14, fontWeight: 700, color: '#fff', textShadowBlur: 3, textShadowColor: 'rgba(0,0,0,0.5)' }"
c = c.replace(old_l1, new_l1)

# 3) Fix level 2 labels - white with shadow  
old_l2 = "label: { rotate: 'tangential', fontSize: 12, color: '#606266' }"
new_l2 = "label: { rotate: 'tangential', fontSize: 12, color: '#fff', textShadowBlur: 3, textShadowColor: 'rgba(0,0,0,0.5)' }"
c = c.replace(old_l2, new_l2)

open(sys.argv[1], "w", encoding="utf-8").write(c)
print("done")
