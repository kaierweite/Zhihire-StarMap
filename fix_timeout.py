# -*- coding: utf-8 -*-
import sys
sys.stdout.reconfigure(encoding='utf-8')
path = r'C:\Users\Administrator\Desktop\Zhihire-StarMap\frontend\src\views\user\AbilityMap.vue'
content = open(path, encoding='utf-8').read()

# Fix 1: Replace fetchGraph with a version that has a 6-second timeout
old_fetch = (
    "async function fetchGraph() {"
    "\n  loading.value = true"
    "\n  error.value = ''"
    "\n  try {"
    "\n    const res = await getUserGraph()"
    "\n    graphData.value = res.data.data || { nodes: [], edges: [], gap_skills: [], state: \"empty\", categories: [] }"
    "\n    await nextTick()"
    "\n    chartGraph = initChart(graphData.value, [], chartRefGraph.value, chartGraph)"
    "\n  } catch (e: any) {"
    "\n    error.value = e.message || '\u52a0\u8f7d\u56fe\u8c31\u5931\u8d25'"
    "\n  } finally {"
    "\n    loading.value = false"
    "\n  }"
    "\n}"
)

new_fetch = (
    "async function fetchGraph() {"
    "\n  loading.value = true"
    "\n  error.value = ''"
    "\n  // Timeout guard: stop spinning after 6s if backend/database is down"
    "\n  const timeoutId = setTimeout(() => {"
    "\n    if (loading.value) {"
    "\n      loading.value = false"
    "\n      error.value = '\u540e\u7aef\u670d\u52a1\u8fde\u63a5\u8d85\u65f6\uff0c\u8bf7\u68c0\u67e5\u6570\u636e\u5e93\u662f\u5426\u5df2\u542f\u52a8'"
    "\n    }"
    "\n  }, 6000)"
    "\n  try {"
    "\n    const res = await getUserGraph()"
    "\n    clearTimeout(timeoutId)"
    "\n    graphData.value = res.data.data || { nodes: [], edges: [], gap_skills: [], state: \"empty\", categories: [] }"
    "\n    if (graphData.value.nodes.length === 0) {"
    "\n      graphData.value.state = \"empty\""
    "\n    }"
    "\n    await nextTick()"
    "\n    chartGraph = initChart(graphData.value, [], chartRefGraph.value, chartGraph)"
    "\n  } catch (e: any) {"
    "\n    clearTimeout(timeoutId)"
    "\n    error.value = e.message || '\u52a0\u8f7d\u56fe\u8c31\u5931\u8d25'"
    "\n  } finally {"
    "\n    clearTimeout(timeoutId)"
    "\n    loading.value = false"
    "\n  }"
    "\n}"
)

if old_fetch in content:
    content = content.replace(old_fetch, new_fetch)
    print('fetchGraph replaced')
else:
    print('fetchGraph NOT FOUND in file')
    # Debug: show first 80 chars of area around "fetchGraph"
    idx = content.find('async function fetchGraph')
    if idx >= 0:
        print('Found at position', idx)
        print(repr(content[idx:idx+500]))

# Fix 2: Change empty-graph v-if to not rely on backend state field
content = content.replace(
    "\u6240\u4ee5\u4f60\u53ef\u4ee5\u5b89\u5168\u7684\u4f7f\u7528"  # dummy, won't match
)

# The empty-graph v-if uses graphData.state === 'empty'
# Change it to also work when nodes is empty and not loading
old_empty_vif = "graphData.state === 'empty'"
new_empty_vif = "!loading && graphData.nodes.length === 0"
content = content.replace(old_empty_vif, new_empty_vif)
print('empty v-if replaced')

# Fix 3: Change echarts container v-show to not rely on backend state
content = content.replace(
    "v-show=\"graphData.state === 'ready'\" ref=\"chartRefGraph\"",
    "v-show=\"graphData.nodes.length > 0\" ref=\"chartRefGraph\""
)
print('ready v-show replaced')

with open(path, 'w', encoding='utf-8') as f:
    f.write(content)
print('All fixes applied')
