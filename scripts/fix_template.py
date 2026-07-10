import re
with open("C:\\Users\\Administrator\\Desktop\\Zhihire-StarMap\\frontend\\src\\views\\user\\AbilityMapSection.vue", "r", encoding="utf-8") as f:
    content = f.read()

# fix v-show -> v-else-if 
content = content.replace('v-show="graphData.nodes.length"', 'v-else-if="graphData.nodes.length"')

# fix orphan v-else-if -> v-else
old = '<div v-else-if="!loading '
old += '&&'
old += ' !graphData.nodes.length '
old += '&&'
old += ' !error" class="empty-chart">'
new = '<div v-else class="empty-chart">'
content = content.replace(old, new)

with open("C:\\Users\\Administrator\\Desktop\\Zhihire-StarMap\\frontend\\src\\views\\user\\AbilityMapSection.vue", "w", encoding="utf-8") as f:
    f.write(content)

print("done")
