<template>
  <el-dialog
    v-model="visible"
    :title="`位置打卡 - ${clockTypeText}`"
    width="90%"
    max-width="500px"
    :close-on-click-modal="false"
    :close-on-press-escape="false"
  >
    <div class="location-clock-content">
      <!-- 位置状态显示 -->
      <div class="location-status">
        <div v-if="!locationLoading && !currentLocation" class="status-item warning">
          <el-icon><LocationInformation /></el-icon>
          <span>点击下方按钮获取位置信息</span>
        </div>
        
        <div v-else-if="locationLoading" class="status-item loading">
          <el-icon class="rotating"><Loading /></el-icon>
          <span>正在获取位置信息...</span>
        </div>
        
        <div v-else-if="currentLocation && !nearestLocation" class="status-item loading">
          <el-icon class="rotating"><Loading /></el-icon>
          <span>正在验证打卡位置...</span>
        </div>
        
        <div v-else-if="nearestLocation && nearestLocation.in_range" class="status-item success">
          <el-icon><SuccessFilled /></el-icon>
          <span>位置验证成功，可以打卡</span>
        </div>
        
        <div v-else-if="nearestLocation && !nearestLocation.in_range" class="status-item error">
          <el-icon><WarningFilled /></el-icon>
          <span>不在打卡范围内</span>
        </div>
      </div>

      <!-- 位置信息详情 -->
      <div v-if="nearestLocation" class="location-details">
        <el-descriptions :column="1" border>
          <el-descriptions-item label="最近位置">
            {{ nearestLocation.name }}
          </el-descriptions-item>
          <el-descriptions-item label="位置地址">
            {{ nearestLocation.address }}
          </el-descriptions-item>
          <el-descriptions-item label="当前距离">
            <el-tag 
              :type="nearestLocation.in_range ? 'success' : 'danger'"
              effect="light"
            >
              {{ nearestLocation.distance }}米
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="允许范围">
            {{ nearestLocation.radius }}米
          </el-descriptions-item>
          <el-descriptions-item label="位置精度" v-if="currentLocation?.accuracy">
            {{ Math.round(currentLocation.accuracy) }}米
          </el-descriptions-item>
        </el-descriptions>
      </div>

      <!-- 备注输入 -->
      <div class="note-section">
        <el-input
          v-model="note"
          type="textarea"
          :rows="2"
          placeholder="打卡备注（可选）"
          maxlength="200"
          show-word-limit
        />
      </div>

      <!-- 操作按钮 -->
      <div class="action-buttons">
        <el-button
          v-if="!currentLocation"
          type="primary"
          size="large"
          @click="getCurrentLocation"
          :loading="locationLoading"
        >
          <el-icon><LocationInformation /></el-icon>
          获取当前位置
        </el-button>
        
        <template v-else>
          <el-button
            v-if="nearestLocation?.in_range"
            type="success"
            size="large"
            @click="submitClock"
            :loading="submitting"
          >
            <el-icon><Check /></el-icon>
            确认{{ clockTypeText }}
          </el-button>
          
          <el-button
            v-else
            type="warning"
            size="large"
            @click="forceSubmitClock"
            :loading="submitting"
          >
            <el-icon><Warning /></el-icon>
            强制{{ clockTypeText }}
          </el-button>
          
          <el-button
            type="info"
            size="large"
            @click="refreshLocation"
            :loading="locationLoading"
          >
            <el-icon><Refresh /></el-icon>
            刷新位置
          </el-button>
        </template>
      </div>

      <!-- 提示信息 -->
      <div class="tips">
        <el-alert
          v-if="nearestLocation && !nearestLocation.in_range"
          title="温馨提示"
          type="warning"
          :closable="false"
          show-icon
        >
          您当前位置距离打卡点较远，如需强制打卡请点击"强制打卡"按钮。强制打卡可能需要说明原因。
        </el-alert>
        
        <el-alert
          v-else-if="currentLocation && currentLocation.accuracy && currentLocation.accuracy > 100"
          title="位置精度提示"
          type="info"
          :closable="false"
          show-icon
        >
          当前位置精度较低（{{ Math.round(currentLocation.accuracy) }}米），建议在空旷地带重新获取位置。
        </el-alert>
      </div>
    </div>
  </el-dialog>
</template>

<script setup lang="ts">
import { ref, computed, watch, onUnmounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { 
  LocationInformation, Loading, SuccessFilled, WarningFilled, 
  Check, Warning, Refresh
} from '@element-plus/icons-vue'
import locationService, { type UserLocation, type CompanyLocation } from '@/services/location'
import attendanceService, { type LocationClockData } from '@/services/attendance'

// Props
interface Props {
  visible: boolean
  clockType: 'in' | 'out'
}

const props = withDefaults(defineProps<Props>(), {
  visible: false,
  clockType: 'in'
})

// Emits
const emit = defineEmits<{
  'update:visible': [value: boolean]
  'success': [result: any]
}>()

// 响应式变量
const currentLocation = ref<UserLocation | null>(null)
const nearestLocation = ref<(CompanyLocation & { distance: number; in_range: boolean }) | null>(null)
const locationLoading = ref(false)
const submitting = ref(false)
const note = ref('')
const watchId = ref<number | null>(null)

// 计算属性
const visible = computed({
  get: () => props.visible,
  set: (value) => emit('update:visible', value)
})

const clockTypeText = computed(() => {
  return props.clockType === 'in' ? '上班打卡' : '下班打卡'
})

// 监听对话框关闭
watch(visible, (newVal) => {
  if (!newVal) {
    resetState()
  }
})

// 重置状态
const resetState = () => {
  currentLocation.value = null
  nearestLocation.value = null
  locationLoading.value = false
  submitting.value = false
  note.value = ''
  
  // 停止位置监听
  if (watchId.value !== null) {
    locationService.clearWatch(watchId.value)
    watchId.value = null
  }
}

// 获取当前位置
const getCurrentLocation = async () => {
  try {
    locationLoading.value = true
    
    // 获取当前位置
    const location = await locationService.getCurrentPosition({
      enableHighAccuracy: true,
      timeout: 15000,
      maximumAge: 30000
    })
    
    currentLocation.value = location
    
    // 获取最近的公司位置
    await getNearestLocation()
    
  } catch (error: any) {
    console.error('获取位置失败:', error)
    ElMessage.error(error.message || '获取位置失败，请检查位置权限')
  } finally {
    locationLoading.value = false
  }
}

// 获取最近的公司位置
const getNearestLocation = async () => {
  if (!currentLocation.value) return
  
  try {
    const response = await locationService.getNearestLocation(
      currentLocation.value.latitude,
      currentLocation.value.longitude
    )
    
    if (response.success) {
      nearestLocation.value = response.data
    } else {
      ElMessage.warning('未找到可用的打卡位置')
    }
  } catch (error: any) {
    console.error('获取最近位置失败:', error)
    ElMessage.error('获取打卡位置失败')
  }
}

// 刷新位置
const refreshLocation = async () => {
  await getCurrentLocation()
}

// 提交打卡
const submitClock = async () => {
  if (!currentLocation.value || !nearestLocation.value) {
    ElMessage.error('位置信息不完整')
    return
  }

  try {
    submitting.value = true
    
    const clockData: LocationClockData = {
      latitude: currentLocation.value.latitude,
      longitude: currentLocation.value.longitude,
      location_id: nearestLocation.value.id,
      location: nearestLocation.value.name,
      note: note.value,
      force_clock: false
    }

    let response
    if (props.clockType === 'in') {
      response = await attendanceService.locationClockIn(clockData)
    } else {
      response = await attendanceService.locationClockOut(clockData)
    }

    ElMessage.success(response.message || `${clockTypeText.value}成功`)
    emit('success', response)
    visible.value = false
    
  } catch (error: any) {
    console.error('打卡失败:', error)
    ElMessage.error(error.response?.data?.error || '打卡失败')
  } finally {
    submitting.value = false
  }
}

// 强制打卡
const forceSubmitClock = async () => {
  if (!currentLocation.value || !nearestLocation.value) {
    ElMessage.error('位置信息不完整')
    return
  }

  try {
    await ElMessageBox.confirm(
      `您当前距离打卡点${nearestLocation.value.distance}米，超出允许范围${nearestLocation.value.radius}米。确定要强制打卡吗？`,
      '确认强制打卡',
      {
        confirmButtonText: '确认强制打卡',
        cancelButtonText: '取消',
        type: 'warning',
      }
    )

    submitting.value = true
    
    const clockData: LocationClockData = {
      latitude: currentLocation.value.latitude,
      longitude: currentLocation.value.longitude,
      location_id: nearestLocation.value.id,
      location: nearestLocation.value.name,
      note: note.value || `强制打卡：距离${nearestLocation.value.distance}米`,
      force_clock: true
    }

    let response
    if (props.clockType === 'in') {
      response = await attendanceService.locationClockIn(clockData)
    } else {
      response = await attendanceService.locationClockOut(clockData)
    }

    ElMessage.success(response.message || `${clockTypeText.value}成功`)
    emit('success', response)
    visible.value = false
    
  } catch (error: any) {
    if (error !== 'cancel') {
      console.error('强制打卡失败:', error)
      ElMessage.error(error.response?.data?.error || '强制打卡失败')
    }
  } finally {
    submitting.value = false
  }
}

// 组件卸载时清理
onUnmounted(() => {
  resetState()
})
</script>

<style scoped>
.location-clock-content {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.location-status {
  text-align: center;
  padding: 16px;
  border-radius: 8px;
  background: #f8f9fa;
}

.status-item {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  font-size: 16px;
  font-weight: 500;
}

.status-item.success {
  color: #67c23a;
}

.status-item.warning {
  color: #e6a23c;
}

.status-item.error {
  color: #f56c6c;
}

.status-item.loading {
  color: #409eff;
}

.rotating {
  animation: rotate 1s linear infinite;
}

@keyframes rotate {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.location-details {
  margin: 16px 0;
}

.note-section {
  margin: 16px 0;
}

.action-buttons {
  display: flex;
  gap: 12px;
  justify-content: center;
  flex-wrap: wrap;
}

.action-buttons .el-button {
  min-width: 120px;
}

.tips {
  margin-top: 16px;
}

@media (max-width: 768px) {
  .action-buttons {
    flex-direction: column;
  }
  
  .action-buttons .el-button {
    width: 100%;
  }
}
</style>
