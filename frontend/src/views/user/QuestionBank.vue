<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { Search, Brain, ChevronDown, ChevronUp } from 'lucide-vue-next'
import { ElMessage } from 'element-plus'
import { queryQuestionBank } from '@/api/interview'
import type { QuestionBankItem } from '@/types/interview'

const keyword = ref('')
const filterType = ref<string>('')
const currentPage = ref(1)
const pageSize = ref(20)
const records = ref<QuestionBankItem[]>([])
const total = ref(0)
const loading = ref(false)
const expandedId = ref<number | null>(null)

const QUESTION_TYPES = [
  { label: '全部', value: '' },
  { label: '技术题', value: 'TECHNICAL' },
  { label: '行为题', value: 'BEHAVIORAL' },
  { label: '情景题', value: 'SITUATIONAL' },
  { label: '简历延伸题', value: 'RESUME_BASED' },
]

const typeLabels: Record<string, string> = {
  TECHNICAL: '技术题',
  BEHAVIORAL: '行为题',
  SITUATIONAL: '情景题',
  RESUME_BASED: '简历延伸题',
}

const typeColors: Record<string, string> = {
  TECHNICAL: 'tech',
  BEHAVIORAL: 'behavior',
  SITUATIONAL: 'scenario',
  RESUME_BASED: 'resume',
}

const filtered = computed(() => {
  if (!keyword.value.trim()) return records.value
  const kw = keyword.value.toLowerCase()
  return records.value.filter((q) => q.content.toLowerCase().includes(kw))
})

async function fetchData() {
  loading.value = true
  try {
    const params: { question_type?: string; page: number; size: number } = {
      page: currentPage.value,
      size: pageSize.value,
    }
    if (filterType.value) params.question_type = filterType.value
    const res = await queryQuestionBank(params)
    records.value = res.data.data.records
    total.value = res.data.data.total
    expandedId.value = null
  } catch {
    ElMessage.error('加载题库失败')
  } finally {
    loading.value = false
  }
}

onMounted(fetchData)

watch([filterType, currentPage], fetchData)

function onPageChange(page: number) {
  currentPage.value = page
}

const totalPages = computed(() => Math.max(1, Math.ceil(total.value / pageSize.value)))
</script>

<template>
  <div class="bank-page">
    <div class="bank-container">
      <h1 class="page-title fade-up">面试题库</h1>
      <p class="page-desc fade-up d1">AI 据岗位 JD 与职业技能图谱生成，所有题目均不爬取外部来源</p>

      <div class="filter-bar fade-up d2">
        <div class="search-box">
          <Search :size="16" />
          <input v-model="keyword" placeholder="搜索题目关键词..." />
        </div>
      </div>

      <div class="type-tabs fade-up d2">
        <button
          v-for="t in QUESTION_TYPES"
          :key="t.value"
          class="type-tab"
          :class="{ active: filterType === t.value }"
          @click="filterType = t.value; currentPage = 1"
        >
          {{ t.label }}
        </button>
      </div>

      <div v-if="loading" class="loading-state">
        <div class="loading-spinner" />
        <p>加载中...</p>
      </div>

      <div v-else class="question-list">
        <div v-if="filtered.length === 0" class="empty-hint">暂无匹配的面试题</div>
        <div
          v-for="q in filtered"
          :key="q.id"
          class="question-card fade-up"
          @click="expandedId = expandedId === q.id ? null : q.id"
        >
          <div class="q-header">
            <div class="q-left">
              <span class="q-type" :class="typeColors[q.question_type] || 'tech'">
                {{ typeLabels[q.question_type] || q.question_type }}
              </span>
            </div>
            <span class="q-no">#{{ q.order_no }}</span>
          </div>
          <p class="q-content">{{ q.content }}</p>
          <div class="q-footer">
            <span class="q-id">ID: {{ q.id }}</span>
            <button class="expand-btn">
              {{ expandedId === q.id ? '收起' : '查看详情' }}
              <component :is="expandedId === q.id ? ChevronUp : ChevronDown" :size="14" />
            </button>
          </div>
          <div v-if="expandedId === q.id" class="q-answer">
            <div class="answer-label"><Brain :size="14" /> 题目编号 #{{ q.order_no }}</div>
            <p>{{ q.content }}</p>
          </div>
        </div>
      </div>

      <div v-if="total > pageSize" class="pagination-bar fade-up d4">
        <button class="page-btn" :disabled="currentPage <= 1" @click="onPageChange(currentPage - 1)">上一页</button>
        <span class="page-info">{{ currentPage }} / {{ totalPages }}（共 {{ total }} 题）</span>
        <button class="page-btn" :disabled="currentPage >= totalPages" @click="onPageChange(currentPage + 1)">下一页</button>
      </div>
    </div>
  </div>
</template>

<style scoped lang="scss">
.bank-page { padding: 24px 16px; }
.bank-container { max-width: 800px; margin: 0 auto; }

@keyframes fadeUp { from { opacity: 0; transform: translateY(20px); } to { opacity: 1; transform: translateY(0); } }
.fade-up { opacity: 0; animation: fadeUp 0.5s cubic-bezier(0.22,1,0.36,1) forwards; }
.d1 { animation-delay: 0.08s; } .d2 { animation-delay: 0.15s; } .d3 { animation-delay: 0.22s; } .d4 { animation-delay: 0.3s; }

.page-title { font-size: 32px; font-weight: 700; color: #121c28; margin-bottom: 6px; }
.page-desc { font-size: 15px; color: #404944; margin-bottom: 24px; }

.filter-bar { display: flex; gap: 10px; margin-bottom: 16px; flex-wrap: wrap; }
.search-box { flex: 1; min-width: 240px; display: flex; align-items: center; gap: 8px; padding: 8px 14px; border: 1px solid #bfc9c3; border-radius: 8px; background: #fff; input { flex: 1; border: none; outline: none; font-size: 14px; } svg { color: #404944; } &:focus-within { border-color: #003527; } }

.type-tabs { display: flex; gap: 6px; margin-bottom: 20px; flex-wrap: wrap; }
.type-tab { padding: 6px 16px; border-radius: 999px; font-size: 13px; font-weight: 500; border: 1px solid #bfc9c3; background: #fff; color: #404944; cursor: pointer; transition: all 0.2s; &:hover { border-color: #003527; } &.active { background: #003527; color: #fff; border-color: #003527; } }

.loading-state { display: flex; flex-direction: column; align-items: center; gap: 12px; padding: 60px 0; color: #404944; }
.loading-spinner { width: 36px; height: 36px; border: 3px solid #bfc9c3; border-top-color: #003527; border-radius: 50%; animation: spin 0.8s linear infinite; }
@keyframes spin { to { transform: rotate(360deg); } }

.question-list { display: flex; flex-direction: column; gap: 12px; }
.empty-hint { text-align: center; color: #bfc9c3; padding: 40px 0; font-size: 14px; }
.question-card { background: #fff; border-radius: 12px; padding: 20px; border: 1px solid #bfc9c3; cursor: pointer; transition: all 0.25s; &:hover { box-shadow: 0 6px 20px rgba(0,0,0,0.05); } }
.q-header { display: flex; align-items: center; justify-content: space-between; margin-bottom: 10px; }
.q-left { display: flex; gap: 8px; }
.q-type { font-size: 11px; padding: 2px 10px; border-radius: 4px; font-weight: 600; &.tech { background: #003527; color: #fff; } &.behavior { background: #d4edda; color: #155724; } &.scenario { background: #fff3cd; color: #856404; } &.resume { background: #e8d5f5; color: #6a1b9a; } }
.q-no { font-size: 12px; color: #bfc9c3; }
.q-content { font-size: 14px; color: #121c28; line-height: 1.7; margin-bottom: 10px; }
.q-footer { display: flex; align-items: center; justify-content: space-between; }
.q-id { font-size: 12px; color: #bfc9c3; }
.expand-btn { display: flex; align-items: center; gap: 4px; font-size: 13px; color: #064e3b; background: none; border: none; cursor: pointer; font-weight: 600; &:hover { text-decoration: underline; } }
.q-answer { margin-top: 14px; padding: 14px; border-radius: 8px; background: #f8f9fa; border-left: 3px solid #003527; }
.answer-label { display: flex; align-items: center; gap: 6px; font-size: 12px; font-weight: 600; color: #003527; margin-bottom: 8px; }
.q-answer p { font-size: 13px; color: #404944; line-height: 1.7; }

.pagination-bar { display: flex; align-items: center; justify-content: center; gap: 16px; margin-top: 24px; padding: 16px 0; }
.page-btn { padding: 8px 16px; border-radius: 8px; border: 1px solid #bfc9c3; background: #fff; color: #404944; font-size: 13px; cursor: pointer; transition: all 0.2s; &:hover:not(:disabled) { border-color: #003527; color: #003527; } &:disabled { opacity: 0.4; cursor: default; } }
.page-info { font-size: 13px; color: #404944; }
</style>
