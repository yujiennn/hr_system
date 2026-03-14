<template>
  <div class="face-registration-page">
    <el-page-header @back="$router.back()" title="返回">
      <template #content>
        <span class="page-title">人脸录入管理</span>
      </template>
    </el-page-header>

    <div class="page-content">
      <FaceRegistration />
    </div>
  </div>
</template>

<script setup lang="ts">
import FaceRegistration from '@/components/FaceRegistration.vue'
</script>

<style scoped>
.face-registration-page {
  height: 100vh;
  background: var(--color-background-page);
}

.page-title {
  font-size: 17px;
  font-weight: 600;
  color: var(--color-text-primary);
}

.page-content {
  padding: var(--hr-space-lg);
  max-width: 1200px;
  margin: 0 auto;
}
</style>
