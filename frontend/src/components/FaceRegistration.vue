<template>
  <div class="face-registration">
    <el-card class="registration-card" shadow="hover">
      <template #header>
        <div class="card-header">
          <h2>
            <el-icon><Camera /></el-icon>
            人脸录入
          </h2>
          <el-text type="info">录入您的人脸信息用于考勤识别</el-text>
        </div>
      </template>

      <div class="registration-content">
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
          </div>
          
          <div class="camera-controls">
            <!-- 调试信息 -->
            <div style="margin-bottom: 10px; font-size: 12px; color: #666;">
              调试状态: cameraStarted={{ cameraStarted }}, startingCamera={{ startingCamera }}
              <br>
              媒体流状态: {{ mediaStream ? '已获取' : '未获取' }}
              <br>
              视频元素状态: {{ videoRef ? '已挂载' : '未挂载' }}
            </div>
            
            <el-button
              v-if="!cameraStarted"
              type="primary"
              size="large"
              @click="startCamera"
              :loading="startingCamera"
            >
              <el-icon><VideoPlay /></el-icon>
              启动摄像头
            </el-button>
            
            <div v-else class="control-buttons">
              <el-button
                type="success"
                size="large"
                @click="capturePhoto"
                :disabled="!cameraStarted"
              >
                <el-icon><Camera /></el-icon>
                拍照录入
              </el-button>
              
              <el-button
                type="info"
                size="large"
                @click="stopCamera"
              >
                <el-icon><VideoPause /></el-icon>
                关闭摄像头
              </el-button>
            </div>
          </div>
        </div>

        <!-- 拍摄的照片预览 -->
        <div v-if="capturedImage" class="captured-section">
          <h3>拍摄的照片：</h3>
          <div class="captured-image">
            <img :src="capturedImage" alt="拍摄的照片" />
          </div>
          
          <div class="action-buttons">
            <el-button
              type="primary"
              size="large"
              @click="submitRegistration"
              :loading="submitting"
            >
              <el-icon><Check /></el-icon>
              确认录入
            </el-button>
            
            <el-button
              type="default"
              size="large"
              @click="retakePhoto"
            >
              <el-icon><RefreshLeft /></el-icon>
              重新拍照
            </el-button>
          </div>
        </div>

        <!-- 当前状态显示 -->
        <div class="status-section">
          <el-alert
            v-if="faceStatus && faceStatus.registered"
            title="已录入人脸信息"
            type="success"
            :description="faceStatus.registeredAt ? `录入时间: ${faceStatus.registeredAt}` : '已录入人脸信息'"
            show-icon
            :closable="false"
          >
            <template #default>
              <div class="status-actions">
                <el-button
                  type="warning"
                  size="small"
                  @click="updateFace"
                >
                  更新人脸信息
                </el-button>
                <el-button
                  type="danger"
                  size="small"
                  @click="deleteFace"
                >
                  删除人脸信息
                </el-button>
              </div>
            </template>
          </el-alert>
          
          <el-alert
            v-else-if="faceStatus"
            title="尚未录入人脸信息"
            type="warning"
            description="请拍照录入您的人脸信息以启用人脸识别考勤"
            show-icon
            :closable="false"
          />
          
          <el-alert
            v-else
            title="正在加载状态..."
            type="info"
            description="正在获取人脸信息状态"
            show-icon
            :closable="false"
          />
        </div>

        <!-- 使用说明 -->
        <div class="instructions">
          <el-collapse>
            <el-collapse-item title="使用说明" name="instructions">
              <ol>
                <li>点击"启动摄像头"按钮开启摄像头</li>
                <li>将脸部对准摄像头，保持正面清晰</li>
                <li>点击"拍照录入"按钮拍摄照片</li>
                <li>确认照片清晰后点击"确认录入"</li>
                <li>录入成功后即可使用人脸识别进行考勤</li>
              </ol>
              
              <div class="tips">
                <h4>拍照建议：</h4>
                <ul>
                  <li>保持光线充足，避免背光</li>
                  <li>正面面对摄像头，表情自然</li>
                  <li>确保人脸清晰，无遮挡物</li>
                  <li>距离摄像头适中，脸部占画面1/3左右</li>
                </ul>
              </div>
            </el-collapse-item>
          </el-collapse>
        </div>
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, watchEffect } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Camera, VideoPlay, VideoPause, Check, RefreshLeft } from '@element-plus/icons-vue'
import { userService, type FaceStatusResponse } from '@/services/user'

// 响应式变量
const videoRef = ref<HTMLVideoElement>()
const canvasRef = ref<HTMLCanvasElement>()
const cameraStarted = ref(false)
const startingCamera = ref(false)
const capturedImage = ref('')
const submitting = ref(false)
const mediaStream = ref<MediaStream | null>(null)

// 人脸状态
const faceStatus = ref<FaceStatusResponse | null>(null)

// 启动摄像头
const startCamera = async () => {
  try {
    console.log('开始启动摄像头...')
    startingCamera.value = true
    
    const stream = await navigator.mediaDevices.getUserMedia({
      video: {
        width: { ideal: 640 },
        height: { ideal: 480 },
        facingMode: 'user'
      }
    })
    
    console.log('获取媒体流成功:', stream)
    mediaStream.value = stream
    
    if (videoRef.value) {
      console.log('找到video元素，设置srcObject')
      videoRef.value.srcObject = stream
      
      // 使用Promise来等待视频准备就绪
      await new Promise<void>((resolve, reject) => {
        const video = videoRef.value!
        
        const onCanPlay = () => {
          console.log('视频可以播放了')
          video.removeEventListener('canplay', onCanPlay)
          video.removeEventListener('error', onError)
          resolve()
        }
        
        const onError = (error: Event) => {
          console.error('视频加载错误:', error)
          video.removeEventListener('canplay', onCanPlay)
          video.removeEventListener('error', onError)
          reject(new Error('视频加载失败'))
        }
        
        video.addEventListener('canplay', onCanPlay)
        video.addEventListener('error', onError)
        
        // 开始播放
        video.play().catch(reject)
      })
      
      console.log('视频播放成功，设置cameraStarted为true')
      cameraStarted.value = true
      ElMessage.success('摄像头启动成功')
      console.log('摄像头启动流程完成，cameraStarted:', cameraStarted.value)
      
    } else {
      console.error('未找到video元素')
      ElMessage.error('未找到视频元素')
      throw new Error('未找到视频元素')
    }
    
  } catch (error) {
    console.error('启动摄像头失败:', error)
    ElMessage.error('启动摄像头失败，请检查摄像头权限')
    
    // 清理资源
    if (mediaStream.value) {
      mediaStream.value.getTracks().forEach(track => track.stop())
      mediaStream.value = null
    }
    cameraStarted.value = false
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
  ElMessage.info('摄像头已关闭')
}

// 拍照
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
}

// 重新拍照
const retakePhoto = () => {
  capturedImage.value = ''
}

// 提交注册
const submitRegistration = async () => {
  if (!capturedImage.value) {
    ElMessage.error('请先拍照')
    return
  }

  try {
    submitting.value = true
    
    const response = await userService.registerFace({
      face_image: capturedImage.value
    })

    ElMessage.success('人脸录入成功！')
    capturedImage.value = ''
    await checkFaceStatus()
    
  } catch (error: any) {
    console.error('人脸录入失败:', error)
    ElMessage.error(error.response?.data?.error || '人脸录入失败')
  } finally {
    submitting.value = false
  }
}

// 更新人脸信息
const updateFace = async () => {
  if (!capturedImage.value) {
    ElMessage.warning('请先拍照再更新')
    return
  }

  try {
    await ElMessageBox.confirm(
      '确定要更新人脸信息吗？',
      '确认更新',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning',
      }
    )

    await submitRegistration()
  } catch {
    // 用户取消
  }
}

// 删除人脸信息
const deleteFace = async () => {
  try {
    await ElMessageBox.confirm(
      '确定要删除人脸信息吗？删除后将无法使用人脸识别考勤。',
      '确认删除',
      {
        confirmButtonText: '确定删除',
        cancelButtonText: '取消',
        type: 'error',
      }
    )

    await userService.deleteFace()
    ElMessage.success('人脸信息删除成功')
    await checkFaceStatus()
    
  } catch (error: any) {
    if (error !== 'cancel') {
      console.error('删除人脸信息失败:', error)
      ElMessage.error(error.response?.data?.error || '删除失败')
    }
  }
}

// 检查人脸状态
const checkFaceStatus = async () => {
  try {
    const response = await userService.getFaceStatus()
    console.log('获取人脸状态成功:', response.data)
    faceStatus.value = response.data
  } catch (error) {
    console.error('获取人脸状态失败:', error)
    // 设置默认状态
    faceStatus.value = {
      registered: false
    }
  }
}

// 生命周期
onMounted(() => {
  checkFaceStatus()
})

onUnmounted(() => {
  stopCamera()
})

// 监控状态变化
watchEffect(() => {
  console.log('状态变化:', {
    cameraStarted: cameraStarted.value,
    startingCamera: startingCamera.value,
    hasMediaStream: !!mediaStream.value,
    hasVideoRef: !!videoRef.value
  })
})
</script>

<style scoped>
.face-registration {
  max-width: 800px;
  margin: 0 auto;
  padding: 20px;
}

.registration-card {
  border-radius: 12px;
}

.card-header {
  text-align: center;
}

.card-header h2 {
  margin: 0 0 8px 0;
  color: #409EFF;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}

.registration-content {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.camera-section {
  text-align: center;
}

.video-container {
  position: relative;
  display: inline-block;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.video-preview {
  width: 100%;
  max-width: 640px;
  height: auto;
  display: block;
}

.camera-controls {
  margin-top: 16px;
}

.control-buttons {
  display: flex;
  gap: 12px;
  justify-content: center;
}

.captured-section {
  text-align: center;
}

.captured-section h3 {
  margin-bottom: 16px;
  color: #303133;
}

.captured-image {
  display: inline-block;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  margin-bottom: 16px;
}

.captured-image img {
  max-width: 400px;
  width: 100%;
  height: auto;
  display: block;
}

.action-buttons {
  display: flex;
  gap: 12px;
  justify-content: center;
}

.status-section {
  margin: 20px 0;
}

.status-actions {
  margin-top: 12px;
  display: flex;
  gap: 8px;
}

.instructions {
  background: #f8f9fa;
  border-radius: 8px;
  padding: 16px;
}

.instructions ol {
  margin: 0 0 16px 0;
  padding-left: 20px;
}

.instructions li {
  margin-bottom: 8px;
  line-height: 1.6;
}

.tips h4 {
  margin: 0 0 8px 0;
  color: #409EFF;
}

.tips ul {
  margin: 0;
  padding-left: 20px;
}

.tips li {
  margin-bottom: 4px;
  line-height: 1.5;
}

@media (max-width: 768px) {
  .face-registration {
    padding: 16px;
  }
  
  .control-buttons,
  .action-buttons {
    flex-direction: column;
    align-items: center;
  }
  
  .status-actions {
    flex-direction: column;
  }
}
</style>
