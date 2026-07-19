<script setup lang="ts">
import { computed } from 'vue'
import { ChevronLeft, ChevronRight } from 'lucide-vue-next'

const props = defineProps<{
  page: number
  total: number
  pageSize?: number
}>()

const emit = defineEmits<{ 'update:page': [value: number] }>()

const totalPages = computed(() => Math.ceil(props.total / (props.pageSize || 10)))

const visiblePages = computed(() => {
  const pages: number[] = []
  const p = props.page
  const tp = totalPages.value
  const start = Math.max(1, p - 2)
  const end = Math.min(tp, p + 2)
  for (let i = start; i <= end; i++) pages.push(i)
  return pages
})

function goTo(p: number) {
  if (p >= 1 && p <= totalPages.value) emit('update:page', p)
}
</script>

<template>
  <div class="pagination" v-if="totalPages > 1">
    <span class="page-info">共 {{ total }} 条</span>
    <button class="page-btn" :disabled="page <= 1" @click="goTo(page - 1)"><ChevronLeft :size="16" /></button>
    <button v-if="visiblePages[0]! > 1" class="page-btn" @click="goTo(1)">1</button>
    <span v-if="visiblePages[0]! > 2" class="page-ellipsis">...</span>
    <button v-for="p in visiblePages" :key="p" class="page-btn" :class="{ active: p === page }" @click="goTo(p)">{{ p }}</button>
    <span v-if="visiblePages[visiblePages.length - 1]! < totalPages - 1" class="page-ellipsis">...</span>
    <button v-if="visiblePages[visiblePages.length - 1]! < totalPages" class="page-btn" @click="goTo(totalPages)">{{ totalPages }}</button>
    <button class="page-btn" :disabled="page >= totalPages" @click="goTo(page + 1)"><ChevronRight :size="16" /></button>
  </div>
</template>

<style scoped lang="scss">
.pagination {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  margin-top: 24px;
}

.page-info {
  font-size: 13px;
  color: #404944;
  margin-right: 12px;
}

.page-btn {
  min-width: 34px;
  height: 34px;
  border-radius: 6px;
  border: 1px solid #bfc9c3;
  background: #fff;
  color: #404944;
  font-size: 13px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;

  &:hover:not(:disabled) { border-color: #003527; color: #003527; }
  &.active { background: #003527; color: #fff; border-color: #003527; }
  &:disabled { opacity: 0.4; cursor: default; }
}

.page-ellipsis {
  font-size: 13px;
  color: #bfc9c3;
  padding: 0 4px;
}
</style>
