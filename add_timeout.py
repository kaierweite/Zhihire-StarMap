import sys
sys.stdout.reconfigure(encoding='utf-8')
path = r'C:\Users\Administrator\Desktop\Zhihire-StarMap\frontend\src\views\user\AbilityMap.vue'
content = open(path, encoding='utf-8').read()

old_func = '''async function fetchGraph() {
  loading.value = true
  error.value = ''
  try {
    const res = await getUserGraph()
    graphData.value = res.data.data || { nodes: [], edges: [], gap_skills: [], state: "empty", categories: [] }
    await nextTick()
    chartGraph = initChart(graphData.value, [], chartRefGraph.value, chartGraph)
  } catch (e: any) {
    error.value = e.message || '\u52a0\u8f7d\u56fe\u8c31\u5931\u8d25'
  } finally {
    loading.value = false
  }
}'''

new_func = '''async function fetchGraph() {
  loading.value = true
  error.value = ''
  // Timeout guard: stop spinning after 6s if backend/database is down
  const timeoutId = setTimeout(() => {
    if (loading.value) {
      loading.value = false
      graphData.value.state = 'empty'
    }
  }, 6000)
  try {
    const res = await getUserGraph()
    clearTimeout(timeoutId)
    graphData.value = res.data.data || { nodes: [], edges: [], gap_skills: [], state: "empty", categories: [] }
    if (graphData.value.nodes.length === 0) {
      graphData.value.state = "empty"
    }
    await nextTick()
    chartGraph = initChart(graphData.value, [], chartRefGraph.value, chartGraph)
  } catch (e: any) {
    clearTimeout(timeoutId)
    error.value = e.message || '\u52a0\u8f7d\u56fe\u8c31\u5931\u8d25'
  } finally {
    clearTimeout(timeoutId)
    loading.value = false
  }
}'''

count = content.count(old_func)
if count == 0:
    print('ERROR: old function not found')
    idx = content.find('async function fetchGraph')
    if idx >= 0:
        print('Found at', idx)
        print(repr(content[idx:idx+210]))
else:
    content = content.replace(old_func, new_func)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    print('fetchGraph replaced successfully')
