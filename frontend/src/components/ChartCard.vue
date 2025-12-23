<template>
  <div class="chart-card">
    <div class="chart-header">
      <h3 class="chart-title">{{ title }}</h3>
      <div class="chart-actions">
        <el-tooltip content="刷新数据">
          <el-button :icon="Refresh" circle size="small" @click="handleRefresh" />
        </el-tooltip>
        <el-tooltip content="查看详情">
          <el-button :icon="MoreFilled" circle size="small" @click="handleMore" />
        </el-tooltip>
      </div>
    </div>
    <div class="chart-body" v-loading="loading">
      <slot></slot>
    </div>
    <div v-if="footer" class="chart-footer">
      <slot name="footer">{{ footer }}</slot>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { Refresh, MoreFilled } from '@element-plus/icons-vue'

interface Props {
  title: string
  footer?: string
  loading?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  loading: false
})

const emit = defineEmits<{
  refresh: []
  more: []
}>()

const handleRefresh = () => {
  emit('refresh')
}

const handleMore = () => {
  emit('more')
}
</script>

<style scoped>
.chart-card {
  background: #fff;
  border-radius: 12px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
  overflow: hidden;
  transition: all 0.3s ease;
}

.chart-card:hover {
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.12);
  transform: translateY(-2px);
}

.chart-header {
  padding: 16px 20px;
  border-bottom: 1px solid #f0f0f0;
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: linear-gradient(to right, #fafbfc, #fff);
}

.chart-title {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
  color: #303133;
}

.chart-actions {
  display: flex;
  gap: 8px;
}

.chart-body {
  padding: 20px;
  min-height: 200px;
}

.chart-footer {
  padding: 12px 20px;
  border-top: 1px solid #f0f0f0;
  background: #fafafa;
  font-size: 13px;
  color: #909399;
  text-align: center;
}
</style>
