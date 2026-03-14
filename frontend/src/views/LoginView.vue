<template>
  <div class="login-container">
    <div class="particles"></div>
    <div class="login-box">
      <div class="login-header">
        <div class="logo-icon">
          <el-icon :size="48"><OfficeBuilding /></el-icon>
        </div>
        <h1>智慧员工运营系统</h1>
        <p>企业级人力资源管理平台</p>
      </div>
      
      <el-form
        ref="loginFormRef"
        :model="loginForm"
        :rules="loginRules"
        class="login-form"
        size="large"
      >
        <el-form-item prop="username">
          <el-input
            v-model="loginForm.username"
            placeholder="请输入用户名"
            prefix-icon="User"
            clearable
          />
        </el-form-item>
        
        <el-form-item prop="password">
          <el-input
            v-model="loginForm.password"
            type="password"
            placeholder="请输入密码"
            prefix-icon="Lock"
            show-password
            clearable
            @keyup.enter="handleLogin"
          />
        </el-form-item>
        
        <el-form-item>
          <el-checkbox v-model="rememberPassword">记住密码</el-checkbox>
        </el-form-item>
        
        <el-form-item>
          <el-button
            type="primary"
            class="login-btn"
            :loading="loading"
            @click="handleLogin"
          >
            登录
          </el-button>
        </el-form-item>
      </el-form>
      
      <div class="login-footer">
        <p>© 2025 智慧员工运营系统. All rights reserved.</p>
        <p class="tips">
          <el-icon><InfoFilled /></el-icon>
          <span>建议使用 Chrome、Edge 或 Firefox 浏览器以获得最佳体验</span>
        </p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, type FormInstance, type FormRules } from 'element-plus'
import { OfficeBuilding, InfoFilled } from '@element-plus/icons-vue'
import { useUserStore } from '@/stores/counter'

const router = useRouter()
const userStore = useUserStore()

const loginFormRef = ref<FormInstance>()
const loading = ref(false)
const rememberPassword = ref(false)

// 存储密钥（用于简单加密）
const STORAGE_KEY = 'hr_login_credentials'

// 表单数据
const loginForm = reactive({
  username: '',
  password: ''
})

// 表单验证规则
const loginRules: FormRules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, message: '密码长度不能少于6位', trigger: 'blur' }
  ]
}

// 简单的加密解密函数（支持中文）
const encodeCredentials = (username: string, password: string): string => {
  const data = JSON.stringify({ username, password })
  // 先用 encodeURIComponent 处理，再用 btoa
  return btoa(encodeURIComponent(data))
}

const decodeCredentials = (encoded: string): { username: string; password: string } | null => {
  try {
    const data = decodeURIComponent(atob(encoded))
    return JSON.parse(data)
  } catch {
    return null
  }
}

// 保存密码
const saveCredentials = () => {
  if (rememberPassword.value) {
    const encoded = encodeCredentials(loginForm.username, loginForm.password)
    localStorage.setItem(STORAGE_KEY, encoded)
  } else {
    localStorage.removeItem(STORAGE_KEY)
  }
}

// 恢复保存的密码
const loadSavedCredentials = () => {
  const saved = localStorage.getItem(STORAGE_KEY)
  if (saved) {
    const credentials = decodeCredentials(saved)
    if (credentials) {
      loginForm.username = credentials.username
      loginForm.password = credentials.password
      rememberPassword.value = true
    }
  }
}

// 登录处理
const handleLogin = async () => {
  if (!loginFormRef.value) return
  
  await loginFormRef.value.validate(async (valid) => {
    if (!valid) return
    
    loading.value = true
    try {
      console.log('开始登录:', loginForm.username)
      console.log('API基地址检查:', import.meta.env.VITE_API_BASE_URL || 'http://localhost:8001/api')
      
      const result = await userStore.login(loginForm.username, loginForm.password)
      console.log('登录成功，用户信息:', result)
      
      // 保存或清除密码
      saveCredentials()
      
      ElMessage.success('登录成功')
      
      // 根据用户类型跳转到不同页面
      const userType = result.user?.user_type
      const isFinanceDept = result.user?.is_finance_department
      console.log('用户类型:', userType, '是财务部:', isFinanceDept)
      
      if (userType === 'admin') {
        router.push('/admin')
      } else if (userType === 'manager') {
        router.push('/manager')
      } else if (isFinanceDept) {
        // 财务部员工进入财务布局
        router.push('/finance')
      } else {
        router.push('/employee')
      }
    } catch (error: any) {
      console.error('登录错误详情:', error)
      console.error('错误状态码:', error.response?.status)
      console.error('错误响应:', error.response?.data)
      console.error('网络错误:', error.code)
      
      let errorMessage = '登录失败'
      
      if (error.code === 'NETWORK_ERROR' || error.message === 'Network Error') {
        errorMessage = '网络连接失败，请检查后端服务是否启动'
      } else if (error.response?.status === 401) {
        errorMessage = '用户名或密码错误'
      } else if (error.response?.data?.detail) {
        errorMessage = error.response.data.detail
      } else if (error.response?.data?.message) {
        errorMessage = error.response.data.message
      } else if (error.message) {
        errorMessage = error.message
      }
      
      ElMessage.error(errorMessage)
    } finally {
      loading.value = false
    }
  })
}

// 页面加载时恢复保存的密码
onMounted(() => {
  loadSavedCredentials()
})
</script>

<style scoped>
@keyframes gradientShift {
  0% { background-position: 0% 50%; }
  50% { background-position: 100% 50%; }
  100% { background-position: 0% 50%; }
}

@keyframes float {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-16px); }
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(24px) scale(0.98); }
  to { opacity: 1; transform: translateY(0) scale(1); }
}

@keyframes particle {
  0% { transform: translateY(100vh) rotate(0deg); opacity: 0; }
  10% { opacity: 0.6; }
  90% { opacity: 0.6; }
  100% { transform: translateY(-100vh) rotate(360deg); opacity: 0; }
}

@keyframes pulse {
  0%, 100% { box-shadow: 0 0 0 0 rgba(79, 110, 247, 0.3); }
  50% { box-shadow: 0 0 0 12px rgba(79, 110, 247, 0); }
}

.login-container {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  display: flex;
  justify-content: center;
  align-items: center;
  background: linear-gradient(-45deg, #4f6ef7, #7c3aed, #ec4899, #3b82f6);
  background-size: 400% 400%;
  animation: gradientShift 18s ease infinite;
  overflow: hidden;
}

/* 粒子效果 */
.particles {
  position: absolute;
  width: 100%;
  height: 100%;
  overflow: hidden;
}

.particles::before,
.particles::after {
  content: '';
  position: absolute;
  width: 8px;
  height: 8px;
  background: rgba(255, 255, 255, 0.25);
  border-radius: 50%;
  animation: particle 18s linear infinite;
}

.particles::before {
  left: 15%;
  width: 6px;
  height: 6px;
  animation-duration: 22s;
}

.particles::after {
  left: 75%;
  animation-delay: 6s;
  animation-duration: 28s;
}

.login-container::before {
  content: '';
  position: absolute;
  width: 450px;
  height: 450px;
  background: radial-gradient(circle, rgba(255, 255, 255, 0.08), transparent 70%);
  border-radius: 50%;
  top: -180px;
  right: -180px;
  animation: float 7s ease-in-out infinite;
}

.login-container::after {
  content: '';
  position: absolute;
  width: 350px;
  height: 350px;
  background: radial-gradient(circle, rgba(255, 255, 255, 0.06), transparent 70%);
  border-radius: 50%;
  bottom: -120px;
  left: -120px;
  animation: float 9s ease-in-out infinite reverse;
}

.login-box {
  width: 420px;
  padding: 48px 42px;
  background: rgba(255, 255, 255, 0.97);
  backdrop-filter: blur(24px) saturate(1.2);
  border-radius: var(--hr-radius-xl);
  box-shadow:
    0 24px 64px rgba(0, 0, 0, 0.25),
    0 0 0 1px rgba(255, 255, 255, 0.15),
    inset 0 1px 0 rgba(255, 255, 255, 0.6);
  animation: fadeIn 0.7s cubic-bezier(0.22, 1, 0.36, 1);
  z-index: 1;
  transition: transform 0.4s cubic-bezier(0.22, 1, 0.36, 1), box-shadow 0.4s cubic-bezier(0.22, 1, 0.36, 1);
}

.login-box:hover {
  transform: translateY(-4px);
  box-shadow:
    0 28px 72px rgba(0, 0, 0, 0.3),
    0 0 0 1px rgba(255, 255, 255, 0.2),
    inset 0 1px 0 rgba(255, 255, 255, 0.6);
}

.login-header {
  text-align: center;
  margin-bottom: 36px;
}

.logo-icon {
  width: 72px;
  height: 72px;
  margin: 0 auto 18px;
  background: linear-gradient(135deg, #4f6ef7 0%, #7c3aed 100%);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  box-shadow: 0 8px 24px rgba(79, 110, 247, 0.35);
  animation: pulse 3s ease-in-out infinite;
}

.login-header h1 {
  background: linear-gradient(135deg, #4f6ef7 0%, #7c3aed 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  margin-bottom: 6px;
  font-size: 26px;
  font-weight: 800;
  letter-spacing: -0.5px;
}

.login-header p {
  color: var(--hr-gray-500);
  font-size: 14px;
  font-weight: 400;
  letter-spacing: 0.5px;
}

.login-form {
  width: 100%;
}

.login-form :deep(.el-form-item) {
  margin-bottom: 22px;
}

.login-form :deep(.el-input__wrapper) {
  border-radius: 10px !important;
  padding: 10px 15px;
  box-shadow: 0 0 0 1px var(--hr-gray-200) inset, 0 1px 3px rgba(0, 0, 0, 0.04) !important;
  transition: all 0.25s ease !important;
}

.login-form :deep(.el-input__wrapper:hover) {
  box-shadow: 0 0 0 1px var(--hr-gray-300) inset, 0 2px 8px rgba(79, 110, 247, 0.08) !important;
}

.login-form :deep(.el-input__wrapper.is-focus) {
  box-shadow: 0 0 0 2px rgba(79, 110, 247, 0.2), 0 0 0 1px var(--hr-primary) inset !important;
}

.login-btn {
  width: 100%;
  height: 46px;
  font-size: 15px;
  font-weight: 600;
  border-radius: 10px !important;
  background: linear-gradient(135deg, #4f6ef7 0%, #7c3aed 100%) !important;
  border: none !important;
  box-shadow: 0 4px 14px rgba(79, 110, 247, 0.35);
  transition: all 0.3s cubic-bezier(0.22, 1, 0.36, 1) !important;
  letter-spacing: 1px;
}

.login-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(79, 110, 247, 0.45) !important;
  background: linear-gradient(135deg, #6382f9 0%, #8b5cf6 100%) !important;
}

.login-btn:active {
  transform: translateY(0);
  box-shadow: 0 2px 8px rgba(79, 110, 247, 0.3) !important;
}

.login-footer {
  margin-top: 28px;
  padding-top: 18px;
  border-top: 1px solid var(--hr-gray-100);
  text-align: center;
}

.login-footer p {
  color: var(--hr-gray-400);
  font-size: 12px;
  margin: 6px 0;
  line-height: 1.6;
}

.login-footer .tips {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  color: var(--hr-gray-500);
  font-size: 12px;
}

.login-footer .tips .el-icon {
  color: var(--hr-primary);
  font-size: 14px;
}
</style>
