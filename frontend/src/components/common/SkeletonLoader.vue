<script setup lang="ts">
defineProps<{
  rows?: number
  avatar?: boolean
}>()
</script>

<template>
  <div class="skeleton">
    <div v-if="avatar" class="skeleton-header">
      <div class="skel skel-avatar" />
      <div class="skeleton-header-text">
        <div class="skel skel-title" />
        <div class="skel skel-subtitle" />
      </div>
    </div>
    <div v-for="i in (rows || 3)" :key="i" class="skeleton-row">
      <div class="skel skel-line" :style="{ width: (100 - i * 8) + '%' }" />
    </div>
  </div>
</template>

<style scoped lang="scss">
@keyframes shimmer {
  0% { background-position: -200px 0; }
  100% { background-position: 200px 0; }
}

.skeleton { display: flex; flex-direction: column; gap: 12px; }

.skel {
  background: linear-gradient(90deg, #f0f0f0 25%, #e8e8e8 50%, #f0f0f0 75%);
  background-size: 400px 100%;
  animation: shimmer 1.5s ease-in-out infinite;
  border-radius: 4px;
}

.skeleton-header { display: flex; align-items: center; gap: 12px; margin-bottom: 8px; }
.skel-avatar { width: 48px; height: 48px; border-radius: 50%; flex-shrink: 0; }
.skeleton-header-text { flex: 1; display: flex; flex-direction: column; gap: 8px; }
.skel-title { height: 16px; width: 40%; }
.skel-subtitle { height: 12px; width: 60%; }
.skel-line { height: 14px; }
</style>
