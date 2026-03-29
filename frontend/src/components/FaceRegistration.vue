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
              <br>
              安全上下文: {{ envDiagnostics.isSecureContext ? '是' : '否' }}
              <br>
              mediaDevices: {{ envDiagnostics.hasMediaDevices ? '可用' : '不可用' }}
              <br>
              页面容器: {{ envDiagnostics.inIframe ? 'iframe/嵌入容器' : '浏览器顶层页面' }}
            </div>

            <div v-if="videoDevices.length" style="margin-bottom: 10px; display: flex; gap: 8px; justify-content: center; align-items: center;">
              <el-select
                v-model="selectedDeviceId"
                placeholder="选择摄像头设备"
                style="width: 300px;"
              >
                <el-option
                  v-for="device in videoDevices"
                  :key="device.deviceId"
                  :label="device.label || `摄像头 ${device.deviceId.slice(0, 6)}`"
                  :value="device.deviceId"
                />
              </el-select>
              <el-button size="default" @click="refreshVideoDevices">刷新设备</el-button>
            </div>

            <el-alert
              v-if="!envDiagnostics.hasMediaDevices"
              type="warning"
              :closable="false"
              title="当前运行环境未提供 mediaDevices 接口"
              description="请使用 Chrome/Edge 直接打开 localhost 页面（不要在内嵌预览容器中打开），或使用下方“上传照片录入”。"
              style="margin-bottom: 10px;"
            />
            
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

            <div v-if="!cameraStarted" style="margin-top: 10px;">
              <el-button
                type="default"
                size="large"
                @click="triggerFileUpload"
              >
                上传照片录入（无摄像头）
              </el-button>
              <input
                ref="fileInputRef"
                type="file"
                accept="image/*"
                style="display: none"
                @change="handleFileUpload"
              />
            </div>
            
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

type LegacyNavigator = Navigator & {
  webkitGetUserMedia?: (
    constraints: MediaStreamConstraints,
    successCallback: (stream: MediaStream) => void,
    errorCallback: (error: Error) => void
  ) => void
  mozGetUserMedia?: (
    constraints: MediaStreamConstraints,
    successCallback: (stream: MediaStream) => void,
    errorCallback: (error: Error) => void
  ) => void
  msGetUserMedia?: (
    constraints: MediaStreamConstraints,
    successCallback: (stream: MediaStream) => void,
    errorCallback: (error: Error) => void
  ) => void
}

// 响应式变量
const videoRef = ref<HTMLVideoElement>()
const canvasRef = ref<HTMLCanvasElement>()
const fileInputRef = ref<HTMLInputElement>()
const cameraStarted = ref(false)
const startingCamera = ref(false)
const capturedImage = ref('')
const submitting = ref(false)
const mediaStream = ref<MediaStream | null>(null)
const videoDevices = ref<MediaDeviceInfo[]>([])
const selectedDeviceId = ref('')
const envDiagnostics = ref({
  isSecureContext: false,
  hasMediaDevices: false,
  inIframe: false
})

// 人脸状态
const faceStatus = ref<FaceStatusResponse | null>(null)

const cameraConstraints: MediaStreamConstraints = {
  video: {
    width: { ideal: 640 },
    height: { ideal: 480 },
    facingMode: 'user'
  }
}

const cameraFallbackConstraints: MediaStreamConstraints[] = [
  cameraConstraints,
  { video: { facingMode: 'user' } },
  { video: true }
]

const listVideoInputDevices = async (): Promise<MediaDeviceInfo[]> => {
  if (!navigator.mediaDevices?.enumerateDevices) {
    return []
  }
  const devices = await navigator.mediaDevices.enumerateDevices()
  return devices.filter(device => device.kind === 'videoinput')
}

const refreshVideoDevices = async () => {
  const devices = await listVideoInputDevices()
  videoDevices.value = devices
  if (!selectedDeviceId.value && devices.length > 0) {
    selectedDeviceId.value = devices[0].deviceId
  }
}

const getLegacyUserMedia = async (): Promise<MediaStream> => {

  const legacyNavigator = navigator as LegacyNavigator
  const legacyGetUserMedia =
    legacyNavigator.webkitGetUserMedia ||
    legacyNavigator.mozGetUserMedia ||
    legacyNavigator.msGetUserMedia

  if (legacyGetUserMedia) {
    return new Promise<MediaStream>((resolve, reject) => {
      legacyGetUserMedia.call(legacyNavigator, cameraConstraints, resolve, reject)
    })
  }

  throw new Error('MEDIA_DEVICES_NOT_SUPPORTED')
}

const refreshEnvDiagnostics = () => {
  envDiagnostics.value = {
    isSecureContext: window.isSecureContext,
    hasMediaDevices: !!navigator.mediaDevices?.getUserMedia,
    inIframe: window.self !== window.top
  }
}

const requestCameraStream = async (
  modernGetUserMedia: ((constraints: MediaStreamConstraints) => Promise<MediaStream>) | null
): Promise<MediaStream> => {
  if (modernGetUserMedia) {
    let lastError: unknown = null

    // 优先尝试用户选择的设备
    if (selectedDeviceId.value) {
      try {
        return await modernGetUserMedia({
          video: {
            deviceId: { exact: selectedDeviceId.value },
            width: { ideal: 640 },
            height: { ideal: 480 }
          }
        })
      } catch (error) {
        lastError = error
      }
    }

    // 先尝试按设备ID逐个打开，规避默认设备不可读导致的 NotReadableError
    const devices = await listVideoInputDevices()
    for (const device of devices) {
      if (selectedDeviceId.value && device.deviceId === selectedDeviceId.value) {
        continue
      }
      try {
        return await modernGetUserMedia({
          video: {
            deviceId: { exact: device.deviceId },
            width: { ideal: 640 },
            height: { ideal: 480 }
          }
        })
      } catch (error) {
        lastError = error
      }
    }

    for (const constraints of cameraFallbackConstraints) {
      try {
        return await modernGetUserMedia(constraints)
      } catch (error) {
        lastError = error
      }
    }
    throw lastError ?? new Error('获取摄像头失败')
  }

  return getLegacyUserMedia()
}

// 启动摄像头
const startCamera = async () => {
  if (startingCamera.value) {
    return
  }

  try {
    console.log('开始启动摄像头...')
    startingCamera.value = true
    refreshEnvDiagnostics()

    // 重启摄像头前先释放旧流，避免设备占用导致 NotReadableError
    if (mediaStream.value) {
      mediaStream.value.getTracks().forEach(track => track.stop())
      mediaStream.value = null
      await new Promise(resolve => setTimeout(resolve, 120))
    }

    const localHosts = ['localhost', '127.0.0.1', '::1', '0.0.0.0']
    const isLocalHost = localHosts.includes(window.location.hostname)

    // 仅做提示，不在此处硬拦截；让浏览器返回真实错误原因
    if (!window.isSecureContext && !isLocalHost) {
      ElMessage.warning('当前页面可能不是安全上下文，浏览器可能拒绝摄像头访问')
    }

    const modernGetUserMedia =
      navigator.mediaDevices && typeof navigator.mediaDevices.getUserMedia === 'function'
        ? navigator.mediaDevices.getUserMedia.bind(navigator.mediaDevices)
        : null

    const stream = await requestCameraStream(modernGetUserMedia)
    
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

    const err = error as Error & { name?: string }
    if (err.message === 'MEDIA_DEVICES_NOT_SUPPORTED') {
      ElMessage.error('当前运行环境不支持摄像头接口，请在Chrome/Edge中通过localhost访问，或使用“上传照片录入”')
    } else if (err.name === 'NotReadableError' || err.name === 'TrackStartError' || err.name === 'AbortError') {
      ElMessage.error('摄像头被其他应用占用或启动失败，请关闭会议/录屏软件后重试')
    } else if (err.name === 'SecurityError') {
      ElMessage.error('浏览器因安全策略拒绝摄像头，请使用 HTTPS 或 localhost 访问')
    } else if (err.name === 'NotAllowedError' || err.name === 'PermissionDeniedError') {
      ElMessage.error('摄像头权限被拒绝，请在浏览器地址栏中允许摄像头访问')
    } else if (err.name === 'NotFoundError' || err.name === 'DevicesNotFoundError') {
      ElMessage.error('未检测到可用摄像头设备，请检查硬件连接')
    } else {
      ElMessage.error('启动摄像头失败，请检查浏览器权限与运行环境')
    }
    
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

const triggerFileUpload = () => {
  fileInputRef.value?.click()
}

const handleFileUpload = (event: Event) => {
  const input = event.target as HTMLInputElement
  const file = input.files?.[0]

  if (!file) {
    return
  }

  if (!file.type.startsWith('image/')) {
    ElMessage.error('请选择图片文件')
    input.value = ''
    return
  }

  const reader = new FileReader()
  reader.onload = () => {
    const result = reader.result
    if (typeof result === 'string') {
      capturedImage.value = result
      ElMessage.success('图片加载成功，可直接确认录入')
    }
  }
  reader.onerror = () => {
    ElMessage.error('图片读取失败，请重试')
  }
  reader.readAsDataURL(file)

  input.value = ''
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
  refreshEnvDiagnostics()
  refreshVideoDevices()
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
