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
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, type FormInstance, type FormRules } from 'element-plus'
import { OfficeBuilding, InfoFilled } from '@element-plus/icons-vue'
import { useUserStore } from '@/stores/counter'

const router = useRouter()
const userStore = useUserStore()

const loginFormRef = ref<FormInstance>()
const loading = ref(false)

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
      
      ElMessage.success('登录成功')
      
      // 根据用户类型跳转到不同页面
      const userType = userStore.userType
      console.log('用户类型:', userType)
      if (userType === 'admin') {
        router.push('/admin')
      } else if (userType === 'manager') {
        router.push('/manager')
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
</script>

<style scoped>
@keyframes gradientShift {
  0% {
    background-position: 0% 50%;
  }
  50% {
    background-position: 100% 50%;
  }
  100% {
    background-position: 0% 50%;
  }
}

@keyframes float {
  0%, 100% {
    transform: translateY(0);
  }
  50% {
    transform: translateY(-20px);
  }
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(30px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes particle {
  0% {
    transform: translateY(100vh) rotate(0deg);
    opacity: 0;
  }
  10% {
    opacity: 1;
  }
  90% {
    opacity: 1;
  }
  100% {
    transform: translateY(-100vh) rotate(360deg);
    opacity: 0;
  }
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
  background: linear-gradient(-45deg, #667eea, #764ba2, #f093fb, #4facfe);
  background-size: 400% 400%;
  animation: gradientShift 15s ease infinite;
  margin: 0;
  padding: 0;
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
  width: 10px;
  height: 10px;
  background: rgba(255, 255, 255, 0.3);
  border-radius: 50%;
  animation: particle 15s linear infinite;
}

.particles::before {
  left: 20%;
  animation-delay: 0s;
  animation-duration: 20s;
}

.particles::after {
  left: 80%;
  animation-delay: 5s;
  animation-duration: 25s;
}

.login-container::before {
  content: '';
  position: absolute;
  width: 500px;
  height: 500px;
  background: radial-gradient(circle, rgba(255, 255, 255, 0.1), transparent);
  border-radius: 50%;
  top: -200px;
  right: -200px;
  animation: float 6s ease-in-out infinite;
}

.login-container::after {
  content: '';
  position: absolute;
  width: 400px;
  height: 400px;
  background: radial-gradient(circle, rgba(255, 255, 255, 0.08), transparent);
  border-radius: 50%;
  bottom: -150px;
  left: -150px;
  animation: float 8s ease-in-out infinite reverse;
}

.login-box {
  width: 420px;
  padding: 50px 45px;
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(20px);
  border-radius: 20px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3), 0 0 0 1px rgba(255, 255, 255, 0.2);
  animation: fadeIn 0.8s ease-out;
  z-index: 1;
  transition: transform 0.3s ease, box-shadow 0.3s ease;
}

.login-box:hover {
  transform: translateY(-5px);
  box-shadow: 0 25px 70px rgba(0, 0, 0, 0.4), 0 0 0 1px rgba(255, 255, 255, 0.3);
}

.login-header {
  text-align: center;
  margin-bottom: 40px;
}

.logo-icon {
  width: 80px;
  height: 80px;
  margin: 0 auto 20px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  box-shadow: 0 8px 24px rgba(102, 126, 234, 0.4);
  animation: float 3s ease-in-out infinite;
}

.login-header h1 {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  margin-bottom: 8px;
  font-size: 28px;
  font-weight: 700;
  letter-spacing: -0.5px;
}

.login-header p {
  color: #666;
  font-size: 14px;
  font-weight: 400;
}

.login-form {
  width: 100%;
}

.login-form :deep(.el-form-item) {
  margin-bottom: 24px;
}

.login-form :deep(.el-input__wrapper) {
  border-radius: 12px;
  padding: 12px 15px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
  transition: all 0.3s ease;
}

.login-form :deep(.el-input__wrapper:hover) {
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.15);
}

.login-form :deep(.el-input__wrapper.is-focus) {
  box-shadow: 0 4px 16px rgba(102, 126, 234, 0.25);
}

.login-btn {
  width: 100%;
  height: 48px;
  font-size: 16px;
  font-weight: 600;
  border-radius: 12px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border: none;
  box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
  transition: all 0.3s ease;
}

.login-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(102, 126, 234, 0.5);
}

.login-btn:active {
  transform: translateY(0);
}

.login-footer {
  margin-top: 30px;
  padding-top: 20px;
  border-top: 1px solid #e8e8e8;
  text-align: center;
}

.login-footer p {
  color: #999;
  font-size: 12px;
  margin: 8px 0;
  line-height: 1.6;
}

.login-footer .tips {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  color: #666;
  font-size: 12px;
}

.login-footer .tips .el-icon {
  color: #409eff;
  font-size: 14px;
}
</style>
