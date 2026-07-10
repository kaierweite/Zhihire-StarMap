with open("C:\\Users\\Administrator\\Desktop\\Zhihire-StarMap\\frontend\\src\\views\\user\\ResumeCenter.vue", encoding="utf-8") as f:
    c = f.read()

# Find the bad string around :title
idx1 = c.find(":title=\"item.title")
end1 = c.find('"', idx1 + 20)
bad1 = c[idx1:end1+1]
print("bad1 = " + repr(bad1))

idx2 = c.find("{{ item.title")
end2 = c.find("}}", idx2) + 2
bad2 = c[idx2:end2]
print("bad2 = " + repr(bad2))
