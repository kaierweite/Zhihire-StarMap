<script setup lang="ts">
defineProps<{
  text?: string
  size?: 'small' | 'default' | 'large'
}>()
</script>

<template>
  <div class="loading-spinner" :class="size || 'default'">
    <div class="spinner" />
    <span v-if="text" class="loading-text">{{ text }}</span>
  </div>
</template>

<style scoped lang="scss">
.loading-spinner {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 12px;
  padding: 40px 20px;
}

.spinner {
  border: 3px solid #e5e7eb;
  border-top-color: #1a3a5c;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;

  .small & { width: 20px; height: 20px; border-width: 2px; }
  .default & { width: 32px; height: 32px; }
  .large & { width: 48px; height: 48px; border-width: 4px; }
}

@keyframes spin { to { transform: rotate(360deg); } }

.loading-text {
  font-size: 13px;
  color: #909399;
}
</style>
