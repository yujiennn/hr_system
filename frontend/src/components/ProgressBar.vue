<template>
  <div v-if="isLoading" class="progress-bar-container">
    <div class="progress-bar" :style="{ width: progress + '%' }"></div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'

const isLoading = ref(false)
const progress = ref(0)
let timer: number | null = null

// 开始加载
const start = () => {
  isLoading.value = true
  progress.value = 0
  
  if (timer) {
    clearInterval(timer)
  }
  
  timer = window.setInterval(() => {
    if (progress.value < 90) {
      progress.value += Math.random() * 10
    }
  }, 200)
}

// 完成加载
const finish = () => {
  progress.value = 100
  
  setTimeout(() => {
    isLoading.value = false
    progress.value = 0
    if (timer) {
      clearInterval(timer)
      timer = null
    }
  }, 300)
}

// 失败
const fail = () => {
  progress.value = 100
  
  setTimeout(() => {
    isLoading.value = false
    progress.value = 0
    if (timer) {
      clearInterval(timer)
      timer = null
    }
  }, 300)
}

// 暴露方法
defineExpose({
  start,
  finish,
  fail
})
</script>

<style scoped>
.progress-bar-container {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  height: 3px;
  z-index: 9999;
  background: transparent;
}

.progress-bar {
  height: 100%;
  background: linear-gradient(90deg, #667eea 0%, #764ba2 50%, #f093fb 100%);
  transition: width 0.2s ease;
  box-shadow: 0 0 10px rgba(102, 126, 234, 0.5);
}
</style>
