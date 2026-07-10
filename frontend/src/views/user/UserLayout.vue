<script setup lang="ts">
import AppHeader from '@/components/AppHeader.vue'
</script>

<template>
  <div class="user-layout">
    <AppHeader />
    <main class="user-main">
      <router-view />
    </main>
  </div>
</template>

<style scoped lang="scss">
.user-layout {
  min-height: 100vh;
  background: #f8f9fa;
}

.user-main {
  padding-top: 56px; // header height
  padding-bottom: 32px;
}
</style>
