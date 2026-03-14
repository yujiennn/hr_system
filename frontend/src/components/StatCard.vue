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
  border-radius: var(--hr-radius-lg);
  padding: 20px;
  display: flex;
  align-items: center;
  gap: 16px;
  box-shadow: var(--hr-shadow-card);
  transition: all var(--hr-transition-slow);
  border-left: 3px solid transparent;
  cursor: default;
  border: 1px solid var(--hr-gray-100);
}

.stat-card.clickable {
  cursor: pointer;
}

.stat-card:hover {
  box-shadow: var(--hr-shadow-card-hover);
  transform: translateY(-3px);
}

.stat-card.type-primary {
  border-left-color: var(--hr-primary);
}

.stat-card.type-success {
  border-left-color: var(--hr-success);
}

.stat-card.type-warning {
  border-left-color: var(--hr-warning);
}

.stat-card.type-danger {
  border-left-color: var(--hr-danger);
}

.stat-card.type-info {
  border-left-color: var(--hr-gray-400);
}

.stat-icon-wrapper {
  flex-shrink: 0;
}

.stat-icon {
  width: 52px;
  height: 52px;
  border-radius: var(--hr-radius-md);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
}

.type-primary .stat-icon {
  background: linear-gradient(135deg, #4f6ef7 0%, #6366f1 100%);
}

.type-success .stat-icon {
  background: linear-gradient(135deg, #22c55e 0%, #10b981 100%);
}

.type-warning .stat-icon {
  background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
}

.type-danger .stat-icon {
  background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
}

.type-info .stat-icon {
  background: linear-gradient(135deg, #6b7280 0%, #9ca3af 100%);
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
  font-size: 26px;
  font-weight: 800;
  color: var(--hr-gray-800);
  line-height: 1;
  letter-spacing: -0.5px;
}

.stat-unit {
  font-size: 13px;
  color: var(--hr-gray-400);
  font-weight: 400;
}

.stat-label {
  font-size: 13px;
  color: var(--hr-gray-500);
  margin-bottom: 6px;
}

.stat-trend {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 12px;
  font-weight: 500;
}

.stat-trend.trend-up {
  color: var(--hr-success);
}

.stat-trend.trend-down {
  color: var(--hr-danger);
}

.stat-trend.trend-neutral {
  color: var(--hr-gray-400);
}

.trend-label {
  margin-left: 4px;
  color: var(--hr-gray-400);
}
</style>
