<script setup lang="ts">
import { onMounted } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()
onMounted(() => { router.replace('/user/profile') })
</script>

<template>
  <div></div>
</template>

