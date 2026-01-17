<template>
  <div id="app">
    <RouterView />
  </div>
</template>

<script setup lang="ts">
import { RouterView } from 'vue-router'
import { onMounted } from 'vue'
import { useAuthStore } from '@/stores/counter'

const userStore = useAuthStore()

onMounted(async () => {
  // 初始化用户认证状态
  await userStore.initAuth()
})
</script>

<style>
#app {
  width: 100vw;
  min-height: 100vh;
  margin: 0;
  padding: 0;
  overflow-x: hidden;
  overflow-y: auto;
}

html, body {
  margin: 0;
  padding: 0;
  min-height: 100%;
  overflow-x: hidden;
}
</style>
