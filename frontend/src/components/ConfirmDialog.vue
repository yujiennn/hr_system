<template>
  <el-dialog
    v-model="visible"
    :title="title"
    width="450px"
    :show-close="false"
    :close-on-click-modal="false"
    class="confirm-dialog"
  >
    <div class="confirm-content">
      <div class="confirm-icon" :class="`type-${type}`">
        <el-icon v-if="type === 'warning'" :size="50"><WarningFilled /></el-icon>
        <el-icon v-else-if="type === 'danger'" :size="50"><CircleCloseFilled /></el-icon>
        <el-icon v-else-if="type === 'info'" :size="50"><InfoFilled /></el-icon>
        <el-icon v-else :size="50"><QuestionFilled /></el-icon>
      </div>
      
      <div class="confirm-message">
        <div class="message-title">{{ message }}</div>
        <div v-if="description" class="message-description">{{ description }}</div>
        
        <!-- 需要输入确认文本的情况 -->
        <div v-if="requireConfirmText" class="confirm-input">
          <p class="confirm-hint">请输入 <strong>{{ confirmText }}</strong> 以确认操作</p>
          <el-input
            v-model="inputValue"
            :placeholder="`请输入 ${confirmText}`"
            @keyup.enter="handleConfirm"
          />
        </div>
      </div>
    </div>

    <template #footer>
      <div class="dialog-footer">
        <el-button @click="handleCancel" size="large">
          {{ cancelText }}
        </el-button>
        <el-button
          :type="type === 'danger' ? 'danger' : 'primary'"
          @click="handleConfirm"
          :disabled="requireConfirmText && inputValue !== confirmText"
          :loading="confirming"
          size="large"
        >
          {{ confirmButtonText }}
        </el-button>
      </div>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'
import { WarningFilled, CircleCloseFilled, InfoFilled, QuestionFilled } from '@element-plus/icons-vue'

interface Props {
  title?: string
  message: string
  description?: string
  type?: 'warning' | 'danger' | 'info' | 'question'
  confirmButtonText?: string
  cancelText?: string
  requireConfirmText?: boolean
  confirmText?: string
}

const props = withDefaults(defineProps<Props>(), {
  title: '确认操作',
  type: 'warning',
  confirmButtonText: '确定',
  cancelText: '取消',
  requireConfirmText: false,
  confirmText: '确认'
})

const emit = defineEmits<{
  confirm: []
  cancel: []
}>()

const visible = ref(false)
const confirming = ref(false)
const inputValue = ref('')

const show = () => {
  visible.value = true
  inputValue.value = ''
}

const hide = () => {
  visible.value = false
  confirming.value = false
  inputValue.value = ''
}

const handleConfirm = () => {
  if (props.requireConfirmText && inputValue.value !== props.confirmText) {
    return
  }
  
  confirming.value = true
  emit('confirm')
}

const handleCancel = () => {
  emit('cancel')
  hide()
}

watch(visible, (val) => {
  if (!val) {
    inputValue.value = ''
    confirming.value = false
  }
})

defineExpose({
  show,
  hide
})
</script>

<style scoped>
.confirm-dialog :deep(.el-dialog__header) {
  padding: 20px 24px;
  border-bottom: 1px solid #f0f0f0;
}

.confirm-dialog :deep(.el-dialog__body) {
  padding: 30px 24px;
}

.confirm-dialog :deep(.el-dialog__footer) {
  padding: 16px 24px;
  border-top: 1px solid #f0f0f0;
}

.confirm-content {
  display: flex;
  gap: 20px;
}

.confirm-icon {
  flex-shrink: 0;
  width: 60px;
  height: 60px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.confirm-icon.type-warning {
  background: #fef7e6;
  color: #e6a23c;
}

.confirm-icon.type-danger {
  background: #fef0f0;
  color: #f56c6c;
}

.confirm-icon.type-info {
  background: #f0f9ff;
  color: #409eff;
}

.confirm-icon.type-question {
  background: #f5f7fa;
  color: #909399;
}

.confirm-message {
  flex: 1;
}

.message-title {
  font-size: 16px;
  font-weight: 600;
  color: #303133;
  margin-bottom: 8px;
  line-height: 1.5;
}

.message-description {
  font-size: 14px;
  color: #606266;
  line-height: 1.6;
  margin-bottom: 16px;
}

.confirm-input {
  margin-top: 20px;
}

.confirm-hint {
  font-size: 13px;
  color: #606266;
  margin-bottom: 12px;
}

.confirm-hint strong {
  color: #f56c6c;
  font-weight: 600;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}
</style>
