<template>
  <el-dialog
    v-model="dialogVisible"
    :title="dialogTitle"
    width="600px"
    :close-on-click-modal="false"
    :close-on-press-escape="false"
    destroy-on-close
  >
    <div class="face-recognition-dialog">
      <!-- 摄像头预览区域 -->
      <div class="camera-section">
        <div class="video-container">
          <video
            ref="videoRef"
            class="video-preview"
            autoplay
            muted
            playsinline
          ></video>
          <canvas
            ref="canvasRef"
            class="capture-canvas"
            style="display: none"
          ></canvas>
          
          <!-- 人脸框指示 -->
          <div class="face-guide">
            <div class="face-oval"></div>
            <div class="guide-text">请将面部对准框内</div>
          </div>
        </div>
        
        <div class="camera-status">
          <div v-if="!cameraStarted && !startingCamera" class="status-text">
            <el-icon><Camera /></el-icon>
            点击下方按钮启动摄像头进行{{ clockTypeText }}
          </div>
          <div v-else-if="startingCamera" class="status-text">
            <el-icon class="rotating"><Loading /></el-icon>
            正在启动摄像头...
          </div>
          <div v-else-if="cameraStarted && !recognizing" class="status-text success">
            <el-icon><SuccessFilled /></el-icon>
            摄像头已就绪，点击拍照进行{{ clockTypeText }}
          </div>
          <div v-else-if="recognizing" class="status-text processing">
            <el-icon class="rotating"><Loading /></el-icon>
            正在识别人脸，请稍候...
          </div>
        </div>
      </div>

      <!-- 拍摄的照片预览 -->
      <div v-if="capturedImage" class="captured-section">
        <h4>拍摄的照片：</h4>
        <div class="captured-image">
          <img :src="capturedImage" alt="拍摄的照片" />
        </div>
      </div>

      <!-- 识别结果 -->
      <div v-if="recognitionResult" class="result-section">
        <el-result
          :icon="recognitionResult.success ? 'success' : 'error'"
          :title="recognitionResult.success ? '识别成功' : '识别失败'"
          :sub-title="recognitionResult.message"
        >
          <template #extra v-if="recognitionResult.success">
            <div class="recognition-info">
              <p><strong>用户：</strong>{{ recognitionResult.user_name }}</p>
              <p><strong>相似度：</strong>{{ recognitionResult.similarity }}</p>
            </div>
          </template>
        </el-result>
      </div>
    </div>

    <template #footer>
      <div class="dialog-footer">
        <el-button @click="handleCancel">取消</el-button>
        
        <el-button
          v-if="!cameraStarted"
          type="primary"
          @click="startCamera"
          :loading="startingCamera"
        >
          <el-icon><VideoPlay /></el-icon>
          启动摄像头
        </el-button>
        
        <template v-else-if="!capturedImage">
          <el-button
            type="success"
            size="large"
            @click="capturePhotoAndRecognize"
            :disabled="!cameraStarted || recognizing"
            :loading="recognizing"
          >
            <el-icon><Camera /></el-icon>
            {{ recognizing ? '正在识别...' : `拍照${clockTypeText}` }}
          </el-button>
          <el-button
            type="info"
            @click="stopCamera"
            :disabled="recognizing"
          >
            <el-icon><VideoPause /></el-icon>
            关闭摄像头
          </el-button>
        </template>
        
        <template v-else-if="!recognitionResult">
          <el-button
            type="primary"
            @click="submitRecognition"
            :loading="recognizing"
          >
            <el-icon><Check /></el-icon>
            确认{{ clockTypeText }}
          </el-button>
          <el-button
            type="default"
            @click="retakePhoto"
          >
            <el-icon><RefreshLeft /></el-icon>
            重新拍照
          </el-button>
        </template>
        
        <template v-else-if="recognitionResult.success">
          <el-button
            type="primary"
            @click="handleSuccess"
          >
            <el-icon><Check /></el-icon>
            完成
          </el-button>
        </template>
        
        <template v-else>
          <el-button
            type="primary"
            @click="retakePhoto"
          >
            <el-icon><RefreshLeft /></el-icon>
            重新识别
          </el-button>
        </template>
      </div>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { ref, computed, watch, onUnmounted } from 'vue'
import { ElMessage } from 'element-plus'
import { 
  Camera, VideoPlay, VideoPause, Check, RefreshLeft, 
  Loading, SuccessFilled 
} from '@element-plus/icons-vue'
import attendanceService from '@/services/attendance'

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
  'confirm': [result: any]
}>()

// 响应式变量
const videoRef = ref<HTMLVideoElement>()
const canvasRef = ref<HTMLCanvasElement>()
const cameraStarted = ref(false)
const startingCamera = ref(false)
const capturedImage = ref('')
const recognizing = ref(false)
const mediaStream = ref<MediaStream | null>(null)

// 识别结果
const recognitionResult = ref<{
  success: boolean
  message: string
  user_name?: string
  similarity?: string
  data?: any
} | null>(null)

// 计算属性
const dialogVisible = computed({
  get: () => props.visible,
  set: (value) => emit('update:visible', value)
})

const clockTypeText = computed(() => {
  return props.clockType === 'in' ? '上班打卡' : '下班打卡'
})

const dialogTitle = computed(() => {
  return `人脸识别${clockTypeText.value}`
})

// 监听对话框关闭
watch(dialogVisible, (newVal) => {
  if (!newVal) {
    resetState()
  }
})

// 重置状态
const resetState = () => {
  stopCamera()
  capturedImage.value = ''
  recognitionResult.value = null
  recognizing.value = false
}

// 启动摄像头
const startCamera = async () => {
  try {
    startingCamera.value = true
    
    const stream = await navigator.mediaDevices.getUserMedia({
      video: {
        width: { ideal: 640 },
        height: { ideal: 480 },
        facingMode: 'user'
      }
    })
    
    mediaStream.value = stream
    
    // 等待video元素准备好
    await new Promise((resolve) => {
      const checkVideo = () => {
        if (videoRef.value) {
          videoRef.value.srcObject = stream
          videoRef.value.onloadedmetadata = () => {
            videoRef.value?.play()
            resolve(true)
          }
        } else {
          setTimeout(checkVideo, 100)
        }
      }
      checkVideo()
    })
    
    cameraStarted.value = true
    ElMessage.success('摄像头启动成功')
    
  } catch (error) {
    console.error('启动摄像头失败:', error)
    ElMessage.error('启动摄像头失败，请检查摄像头权限')
  } finally {
    startingCamera.value = false
  }
}

// 停止摄像头
const stopCamera = () => {
  if (mediaStream.value) {
    mediaStream.value.getTracks().forEach(track => {
      track.stop()
    })
    mediaStream.value = null
  }
  
  if (videoRef.value) {
    videoRef.value.srcObject = null
  }
  
  cameraStarted.value = false
}

// 拍照并立即进行识别
const capturePhotoAndRecognize = async () => {
  if (!videoRef.value || !canvasRef.value) {
    ElMessage.error('摄像头未就绪')
    return
  }

  try {
    recognizing.value = true
    
    const video = videoRef.value
    const canvas = canvasRef.value
    const ctx = canvas.getContext('2d')

    if (!ctx) {
      ElMessage.error('无法获取画布上下文')
      return
    }

    // 设置画布尺寸
    canvas.width = video.videoWidth
    canvas.height = video.videoHeight

    // 绘制当前帧到画布
    ctx.drawImage(video, 0, 0, canvas.width, canvas.height)

    // 转换为base64
    capturedImage.value = canvas.toDataURL('image/jpeg', 0.8)
    
    // 停止摄像头
    stopCamera()
    
    // 立即进行人脸识别打卡
    const data = {
      face_image: capturedImage.value,
      location: '', // 可以添加位置信息
      note: `人脸识别${clockTypeText.value}`
    }

    let response
    if (props.clockType === 'in') {
      response = await attendanceService.faceClockIn(data)
    } else {
      response = await attendanceService.faceClockOut(data)
    }

    // 设置识别结果
    recognitionResult.value = {
      success: true,
      message: response.message || `${clockTypeText.value}成功`,
      user_name: response.recognition_info?.user_name,
      similarity: response.recognition_info?.similarity,
      data: response.record
    }
    
    ElMessage.success(recognitionResult.value.message)
    
    // 自动关闭对话框并通知父组件
    setTimeout(() => {
      emit('confirm', recognitionResult.value)
      dialogVisible.value = false
    }, 1500)
    
  } catch (error: any) {
    console.error('拍照识别失败:', error)
    
    // 设置错误结果
    recognitionResult.value = {
      success: false,
      message: error.response?.data?.error || error.message || '人脸识别失败，请重试'
    }
    
    ElMessage.error(recognitionResult.value.message)
    
    // 识别失败后重新启动摄像头
    setTimeout(() => {
      retakePhoto()
    }, 1000)
    
  } finally {
    recognizing.value = false
  }
}

// 拍照（保留原有功能）
const capturePhoto = () => {
  if (!videoRef.value || !canvasRef.value) {
    ElMessage.error('摄像头未就绪')
    return
  }

  const video = videoRef.value
  const canvas = canvasRef.value
  const ctx = canvas.getContext('2d')

  if (!ctx) {
    ElMessage.error('无法获取画布上下文')
    return
  }

  // 设置画布尺寸
  canvas.width = video.videoWidth
  canvas.height = video.videoHeight

  // 绘制当前帧到画布
  ctx.drawImage(video, 0, 0, canvas.width, canvas.height)

  // 转换为base64
  capturedImage.value = canvas.toDataURL('image/jpeg', 0.8)
  
  ElMessage.success('照片拍摄成功')
  stopCamera()
}

// 重新拍照
const retakePhoto = () => {
  capturedImage.value = ''
  recognitionResult.value = null
  if (!cameraStarted.value) {
    startCamera()
  }
}

// 提交识别
const submitRecognition = async () => {
  if (!capturedImage.value) {
    ElMessage.error('请先拍照')
    return
  }

  try {
    recognizing.value = true
    
    const data = {
      face_image: capturedImage.value,
      location: '', // 可以添加位置信息
      note: `人脸识别${clockTypeText.value}`
    }

    let response
    if (props.clockType === 'in') {
      response = await attendanceService.faceClockIn(data)
    } else {
      response = await attendanceService.faceClockOut(data)
    }

    recognitionResult.value = {
      success: true,
      message: response.message || `${clockTypeText.value}成功`,
      user_name: response.recognition_info?.user_name,
      similarity: response.recognition_info?.similarity,
      data: response.record
    }
    
    ElMessage.success(recognitionResult.value.message)
    
  } catch (error: any) {
    console.error('人脸识别失败:', error)
    
    recognitionResult.value = {
      success: false,
      message: error.response?.data?.error || `${clockTypeText.value}失败`
    }
    
    ElMessage.error(recognitionResult.value.message)
  } finally {
    recognizing.value = false
  }
}

// 处理成功
const handleSuccess = () => {
  emit('confirm', recognitionResult.value)
  dialogVisible.value = false
}

// 取消
const handleCancel = () => {
  dialogVisible.value = false
}

// 生命周期
onUnmounted(() => {
  stopCamera()
})
</script>

<style scoped>
.face-recognition-dialog {
  text-align: center;
}

.camera-section {
  margin-bottom: 20px;
}

.video-container {
  position: relative;
  display: inline-block;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  margin-bottom: 16px;
}

.video-preview {
  width: 100%;
  max-width: 480px;
  height: auto;
  display: block;
}

.face-guide {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  pointer-events: none;
}

.face-oval {
  width: 200px;
  height: 240px;
  border: 3px solid #409EFF;
  border-radius: 50%;
  opacity: 0.8;
  animation: pulse 2s infinite;
}

.guide-text {
  margin-top: 10px;
  color: #409EFF;
  font-weight: bold;
  text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.5);
}

@keyframes pulse {
  0% {
    transform: scale(1);
    opacity: 0.8;
  }
  50% {
    transform: scale(1.05);
    opacity: 1;
  }
  100% {
    transform: scale(1);
    opacity: 0.8;
  }
}

.camera-status {
  padding: 12px;
  border-radius: 8px;
  background: #f5f7fa;
}

.status-text {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  color: #606266;
  font-size: 14px;
}

.status-text.success {
  color: #67c23a;
}

.rotating {
  animation: rotate 1s linear infinite;
}

@keyframes rotate {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}

.captured-section {
  margin: 20px 0;
}

.captured-section h4 {
  margin-bottom: 12px;
  color: #303133;
}

.captured-image {
  display: inline-block;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.captured-image img {
  max-width: 300px;
  width: 100%;
  height: auto;
  display: block;
}

.result-section {
  margin: 20px 0;
}

.recognition-info {
  text-align: left;
  color: #606266;
}

.recognition-info p {
  margin: 4px 0;
}

.dialog-footer {
  display: flex;
  justify-content: center;
  gap: 12px;
  flex-wrap: wrap;
}

@media (max-width: 768px) {
  .face-oval {
    width: 150px;
    height: 180px;
  }
  
  .video-preview {
    max-width: 100%;
  }
  
  .dialog-footer {
    flex-direction: column;
    align-items: center;
  }
}
</style>
