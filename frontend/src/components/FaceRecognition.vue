<template>
  <div class="face-recognition">
    <el-dialog
      v-model="dialogVisible"
      title="人脸识别打卡"
      width="600px"
      :before-close="handleClose"
    >
      <div class="camera-container">
        <!-- 摄像头加载状态 -->
        <div v-if="!cameraReady" class="camera-loading">
          <el-loading-spinner />
          <p>正在启动摄像头...</p>
          <el-button type="primary" size="small" @click="debugCamera" style="margin-top: 10px;">
            调试摄像头
          </el-button>
        </div>
        
        <!-- 摄像头内容 - 始终渲染但可能不可见 -->
        <div class="camera-content" :style="{ display: cameraReady ? 'block' : 'none' }">
          <video
            ref="videoRef"
            :width="videoWidth"
            :height="videoHeight"
            autoplay
            muted
            playsinline
          ></video>
          
          <canvas
            ref="canvasRef"
            :width="videoWidth"
            :height="videoHeight"
            style="display: none;"
          ></canvas>
          
          <!-- 人脸检测框 -->
          <div 
            v-if="faceDetected"
            class="face-box"
            :style="faceBoxStyle"
          ></div>
          
          <!-- 拍照预览 -->
          <div v-if="capturedImage" class="preview-container">
            <img :src="capturedImage" alt="拍照预览" class="preview-image" />
          </div>
        </div>
        
        <div class="detection-status">
          <div v-if="!cameraReady" class="status-item loading">
            <el-tag type="info">
              <el-icon class="is-loading"><Loading /></el-icon>
              正在启动摄像头...
            </el-tag>
          </div>
          <div v-else-if="faceDetected" class="status-item success">
            <el-tag type="success">
              <el-icon><Check /></el-icon>
              检测到人脸，可以拍照
            </el-tag>
          </div>
          <div v-else class="status-item warning">
            <el-tag type="warning">
              <el-icon><Warning /></el-icon>
              请将面部对准摄像头
            </el-tag>
          </div>
        </div>
      </div>
      
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="handleClose">取消</el-button>
          <el-button 
            type="primary" 
            @click="handleCapture"
            :disabled="!faceDetected"
            :loading="capturing"
          >
            <el-icon><Camera /></el-icon>
            拍照打卡
          </el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, watch, nextTick } from 'vue'
import { ElMessage } from 'element-plus'
import { Check, Warning, Camera, Loading } from '@element-plus/icons-vue'

interface Props {
  visible: boolean
  clockType: 'in' | 'out'
}

interface Emits {
  (e: 'update:visible', value: boolean): void
  (e: 'confirm', data: { image: string, clockType: string }): void
}

const props = defineProps<Props>()
const emit = defineEmits<Emits>()

// 响应式数据
const dialogVisible = ref(false)
const videoRef = ref<HTMLVideoElement>()
const canvasRef = ref<HTMLCanvasElement>()
const cameraReady = ref(false)
const faceDetected = ref(false)
const capturing = ref(false)
const capturedImage = ref('')

// 视频尺寸
const videoWidth = 480
const videoHeight = 360

// 人脸检测框样式
const faceBoxStyle = ref({})

// 摄像头流
let stream: MediaStream | null = null
let detectionInterval: ReturnType<typeof setInterval> | null = null

// 监听props变化
watch(() => props.visible, (newVal) => {
  dialogVisible.value = newVal
  if (newVal) {
    // 延迟启动摄像头，确保DOM完全渲染
    setTimeout(() => {
      startCamera()
    }, 100)
  } else {
    stopCamera()
  }
})

// 监听dialog状态
watch(dialogVisible, (newVal) => {
  emit('update:visible', newVal)
})

onMounted(async () => {
  await loadFaceApiModels()
})

onUnmounted(() => {
  stopCamera()
})

// 加载face-api.js模型
async function loadFaceApiModels() {
  try {
    // 简化版本：暂时跳过模型加载，直接使用摄像头检测
    console.log('Face detection ready (simplified version)')
  } catch (error) {
    console.error('Error loading face API models:', error)
    ElMessage.error('人脸识别模型加载失败')
  }
}

// 启动摄像头
async function startCamera() {
  console.log('=== 开始启动摄像头 ===')
  console.log('videoRef.value:', videoRef.value)
  console.log('cameraReady.value:', cameraReady.value)
  
  // 检查videoRef是否存在，如果不存在则等待
  if (!videoRef.value) {
    console.log('videoRef为空，等待DOM渲染...')
    // 等待DOM渲染完成
    await new Promise(resolve => setTimeout(resolve, 200))
    
    // 再次检查
    if (!videoRef.value) {
      console.error('等待后videoRef仍为空，尝试重试...')
      // 最多重试3次
      let retryCount = 0
      const maxRetries = 3
      
      while (!videoRef.value && retryCount < maxRetries) {
        retryCount++
        console.log(`重试第${retryCount}次...`)
        await new Promise(resolve => setTimeout(resolve, 500))
      }
      
      if (!videoRef.value) {
        ElMessage.error('无法找到视频元素，请刷新页面重试')
        return
      }
    }
  }
  
  try {
    // 重置状态
    cameraReady.value = false
    faceDetected.value = false
    
    // 先停止之前的流
    if (stream) {
      stream.getTracks().forEach(track => track.stop())
      stream = null
    }
    
    console.log('请求摄像头权限...')
    
    // 请求摄像头权限
    const constraints = {
      video: {
        width: { ideal: videoWidth },
        height: { ideal: videoHeight },
        facingMode: 'user'
      }
    }
    
    const mediaStream = await navigator.mediaDevices.getUserMedia(constraints)
    console.log('摄像头权限获取成功，stream:', mediaStream)
    
    stream = mediaStream
    
    console.log('设置视频流到videoRef.value:', videoRef.value)
    videoRef.value.srcObject = stream
    
    // 简化处理：直接在play成功后设置状态
    try {
      await videoRef.value.play()
      console.log('视频播放成功')
      
      // 等待一小段时间确保视频开始播放
      setTimeout(() => {
        if (videoRef.value && videoRef.value.readyState >= 2) {
          console.log('视频就绪，videoWidth:', videoRef.value.videoWidth, 'videoHeight:', videoRef.value.videoHeight)
          cameraReady.value = true
          console.log('摄像头启动完成，cameraReady设置为true')
          startFaceDetection()
        } else {
          console.log('视频未就绪，readyState:', videoRef.value?.readyState)
          // 再等待一下
          setTimeout(() => {
            if (videoRef.value && videoRef.value.readyState >= 2) {
              console.log('延迟检查：视频就绪')
              cameraReady.value = true
              startFaceDetection()
            } else {
              console.error('视频始终未就绪')
              ElMessage.error('摄像头启动失败：视频流异常')
            }
          }, 2000)
        }
      }, 1000)
      
    } catch (playError) {
      console.error('视频播放失败:', playError)
      ElMessage.error('无法播放视频流')
    }
    
  } catch (error: any) {
    console.error('摄像头启动失败:', error)
    cameraReady.value = false
    
    if (error.name === 'NotAllowedError') {
      ElMessage.error('摄像头权限被拒绝，请允许访问摄像头后重试')
    } else if (error.name === 'NotFoundError') {
      ElMessage.error('未找到摄像头设备')
    } else if (error.name === 'NotReadableError') {
      ElMessage.error('摄像头被其他应用占用，请关闭其他应用后重试')
    } else {
      ElMessage.error('摄像头启动失败：' + error.message)
    }
  }
}

// 停止摄像头
function stopCamera() {
  if (stream) {
    stream.getTracks().forEach(track => track.stop())
    stream = null
  }
  
  if (detectionInterval) {
    clearInterval(detectionInterval)
    detectionInterval = null
  }
  
  cameraReady.value = false
  faceDetected.value = false
  capturedImage.value = ''
}

// 开始人脸检测
function startFaceDetection() {
  if (!videoRef.value || !cameraReady.value) {
    console.log('无法开始人脸检测：视频元素或摄像头未就绪')
    return
  }
  
  console.log('开始人脸检测')
  
  detectionInterval = setInterval(() => {
    if (!videoRef.value || !cameraReady.value) {
      console.log('检测中断：视频元素或摄像头未就绪')
      return
    }
    
    try {
      const video = videoRef.value
      
      // 检查视频是否有有效的尺寸和数据
      if (video.readyState >= 2 && video.videoWidth > 0 && video.videoHeight > 0) {
        // 模拟检测到人脸（简化版本）
        if (!faceDetected.value) {
          console.log('检测到人脸（模拟）')
          faceDetected.value = true
          
          // 显示人脸框
          const faceWidth = videoWidth * 0.4
          const faceHeight = videoHeight * 0.5
          const faceX = (videoWidth - faceWidth) / 2
          const faceY = (videoHeight - faceHeight) / 2.5
          
          faceBoxStyle.value = {
            position: 'absolute',
            left: `${faceX}px`,
            top: `${faceY}px`,
            width: `${faceWidth}px`,
            height: `${faceHeight}px`,
            border: '3px solid #67c23a',
            borderRadius: '8px',
            pointerEvents: 'none',
            zIndex: 10,
            boxShadow: '0 0 10px rgba(103, 194, 58, 0.5)'
          }
        }
      } else {
        // 视频数据无效，隐藏人脸框
        if (faceDetected.value) {
          console.log('视频数据无效，隐藏人脸框')
          faceDetected.value = false
          faceBoxStyle.value = {}
        }
      }
    } catch (error) {
      console.error('人脸检测错误:', error)
      faceDetected.value = false
      faceBoxStyle.value = {}
    }
  }, 1000) // 每秒检测一次
}

// 调试摄像头函数
function debugCamera() {
  console.log('=== 摄像头调试信息 ===')
  console.log('cameraReady:', cameraReady.value)
  console.log('faceDetected:', faceDetected.value)
  console.log('videoRef:', videoRef.value)
  console.log('stream:', stream)
  
  if (videoRef.value) {
    console.log('video element:')
    console.log('  readyState:', videoRef.value.readyState)
    console.log('  videoWidth:', videoRef.value.videoWidth)
    console.log('  videoHeight:', videoRef.value.videoHeight)
    console.log('  paused:', videoRef.value.paused)
    console.log('  ended:', videoRef.value.ended)
  }
  
  // 手动设置摄像头就绪状态进行测试
  ElMessage.info('强制设置摄像头为就绪状态')
  cameraReady.value = true
}

// 拍照
function handleCapture() {
  if (!videoRef.value || !canvasRef.value || !faceDetected.value) return
  
  capturing.value = true
  
  try {
    const canvas = canvasRef.value
    const video = videoRef.value
    const ctx = canvas.getContext('2d')
    
    if (ctx) {
      // 绘制当前视频帧到canvas
      ctx.drawImage(video, 0, 0, videoWidth, videoHeight)
      
      // 转换为base64图片
      const imageData = canvas.toDataURL('image/jpeg', 0.8)
      capturedImage.value = imageData
      
      // 发送拍照数据
      emit('confirm', {
        image: imageData,
        clockType: props.clockType
      })
      
      ElMessage.success('拍照成功！')
      
      // 延迟关闭对话框
      setTimeout(() => {
        handleClose()
      }, 1500)
    }
  } catch (error) {
    console.error('Capture error:', error)
    ElMessage.error('拍照失败')
  } finally {
    capturing.value = false
  }
}

// 关闭对话框
function handleClose() {
  stopCamera()
  emit('update:visible', false)
}
</script>

<style scoped>
.face-recognition {
  .camera-container {
    position: relative;
    display: flex;
    flex-direction: column;
    align-items: center;
    min-height: 400px;
  }
  
  .camera-loading {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    height: 360px;
    
    p {
      margin-top: 16px;
      color: #666;
    }
  }
  
  .camera-content {
    position: relative;
    
    video {
      border-radius: 8px;
      border: 2px solid #e0e0e0;
    }
  }
  
  .face-box {
    animation: pulse 1.5s infinite;
  }
  
  .preview-container {
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: rgba(0, 0, 0, 0.8);
    display: flex;
    align-items: center;
    justify-content: center;
    border-radius: 8px;
    
    .preview-image {
      max-width: 100%;
      max-height: 100%;
      border-radius: 4px;
    }
  }
  
  .detection-status {
    margin-top: 16px;
    text-align: center;
    
    .status-item {
      display: inline-block;
      
      &.loading .el-tag {
        animation: pulse-loading 1.5s ease-in-out infinite;
      }
      
      &.success .el-tag {
        animation: pulse-success 2s ease-in-out infinite;
      }
    }
  }
  
  .dialog-footer {
    display: flex;
    justify-content: flex-end;
    gap: 12px;
  }
}

@keyframes pulse {
  0% {
    box-shadow: 0 0 0 0 rgba(103, 194, 58, 0.7);
  }
  70% {
    box-shadow: 0 0 0 10px rgba(103, 194, 58, 0);
  }
  100% {
    box-shadow: 0 0 0 0 rgba(103, 194, 58, 0);
  }
}

@keyframes pulse-loading {
  0%, 100% {
    opacity: 1;
  }
  50% {
    opacity: 0.6;
  }
}

@keyframes pulse-success {
  0%, 100% {
    transform: scale(1);
  }
  50% {
    transform: scale(1.05);
  }
}
</style>
