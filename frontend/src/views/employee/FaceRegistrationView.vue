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
  background: #f5f7fa;
}

.page-title {
  font-size: 18px;
  font-weight: 600;
  color: #303133;
}

.page-content {
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
}
</style>
