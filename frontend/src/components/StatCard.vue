<template>
  <div class="stat-card" :class="`type-${type}`" @click="handleClick">
    <div class="stat-icon-wrapper">
      <div class="stat-icon">
        <slot name="icon">
          <el-icon :size="iconSize"><component :is="icon" /></el-icon>
        </slot>
      </div>
    </div>
    
    <div class="stat-content">
      <div class="stat-value-wrapper">
        <span class="stat-value">{{ displayValue }}</span>
        <span v-if="unit" class="stat-unit">{{ unit }}</span>
      </div>
      <div class="stat-label">{{ label }}</div>
      
      <div v-if="trend !== undefined" class="stat-trend" :class="trendClass">
        <el-icon v-if="trend > 0"><CaretTop /></el-icon>
        <el-icon v-else-if="trend < 0"><CaretBottom /></el-icon>
        <el-icon v-else><Minus /></el-icon>
        <span>{{ Math.abs(trend) }}%</span>
        <span class="trend-label">{{ trendLabel }}</span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { CaretTop, CaretBottom, Minus } from '@element-plus/icons-vue'

interface Props {
  label: string
  value: number | string
  unit?: string
  icon?: any
  iconSize?: number
  type?: 'primary' | 'success' | 'warning' | 'danger' | 'info'
  trend?: number
  trendLabel?: string
  clickable?: boolean
  formatter?: (value: number | string) => string
}

const props = withDefaults(defineProps<Props>(), {
  iconSize: 36,
  type: 'primary',
  trendLabel: '较上期',
  clickable: false
})

const emit = defineEmits<{
  click: []
}>()

const displayValue = computed(() => {
  if (props.formatter) {
    return props.formatter(props.value)
  }
  if (typeof props.value === 'number') {
    return props.value.toLocaleString()
  }
  return props.value
})

const trendClass = computed(() => {
  if (props.trend === undefined) return ''
  if (props.trend > 0) return 'trend-up'
  if (props.trend < 0) return 'trend-down'
  return 'trend-neutral'
})

const handleClick = () => {
  if (props.clickable) {
    emit('click')
  }
}
</script>

<style scoped>
.stat-card {
  background: #fff;
  border-radius: 12px;
  padding: 20px;
  display: flex;
  align-items: center;
  gap: 16px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
  transition: all 0.3s ease;
  border-left: 4px solid transparent;
  cursor: default;
}

.stat-card.clickable {
  cursor: pointer;
}

.stat-card:hover {
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.12);
  transform: translateY(-2px);
}

.stat-card.type-primary {
  border-left-color: #409eff;
  background: linear-gradient(135deg, #fff 0%, #e6f4ff 100%);
}

.stat-card.type-success {
  border-left-color: #67c23a;
  background: linear-gradient(135deg, #fff 0%, #f0f9e8 100%);
}

.stat-card.type-warning {
  border-left-color: #e6a23c;
  background: linear-gradient(135deg, #fff 0%, #fef7e6 100%);
}

.stat-card.type-danger {
  border-left-color: #f56c6c;
  background: linear-gradient(135deg, #fff 0%, #fef0f0 100%);
}

.stat-card.type-info {
  border-left-color: #909399;
  background: linear-gradient(135deg, #fff 0%, #f5f7fa 100%);
}

.stat-icon-wrapper {
  flex-shrink: 0;
}

.stat-icon {
  width: 60px;
  height: 60px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.type-primary .stat-icon {
  background: linear-gradient(135deg, #409eff 0%, #5a7bf5 100%);
}

.type-success .stat-icon {
  background: linear-gradient(135deg, #67c23a 0%, #85ce61 100%);
}

.type-warning .stat-icon {
  background: linear-gradient(135deg, #e6a23c 0%, #f0b452 100%);
}

.type-danger .stat-icon {
  background: linear-gradient(135deg, #f56c6c 0%, #f78989 100%);
}

.type-info .stat-icon {
  background: linear-gradient(135deg, #909399 0%, #b3b6bc 100%);
}

.stat-content {
  flex: 1;
  min-width: 0;
}

.stat-value-wrapper {
  display: flex;
  align-items: baseline;
  gap: 4px;
  margin-bottom: 4px;
}

.stat-value {
  font-size: 28px;
  font-weight: 700;
  color: #303133;
  line-height: 1;
}

.stat-unit {
  font-size: 14px;
  color: #909399;
  font-weight: 400;
}

.stat-label {
  font-size: 14px;
  color: #606266;
  margin-bottom: 6px;
}

.stat-trend {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 12px;
}

.stat-trend.trend-up {
  color: #67c23a;
}

.stat-trend.trend-down {
  color: #f56c6c;
}

.stat-trend.trend-neutral {
  color: #909399;
}

.trend-label {
  margin-left: 4px;
  color: #909399;
}
</style>
