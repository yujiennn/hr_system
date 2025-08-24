<template>
  <div class="login-container">
    <div class="login-box">
      <div class="login-header">
        <h1>智慧员工运营系统</h1>
        <p>欢迎登录</p>
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
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, type FormInstance, type FormRules } from 'element-plus'
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
.login-container {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  display: flex;
  justify-content: center;
  align-items: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  margin: 0;
  padding: 0;
}

.login-box {
  width: 400px;
  padding: 40px;
  background: white;
  border-radius: 10px;
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.1);
}

.login-header {
  text-align: center;
  margin-bottom: 30px;
}

.login-header h1 {
  color: #333;
  margin-bottom: 10px;
  font-size: 24px;
}

.login-header p {
  color: #666;
  font-size: 14px;
}

.login-form {
  width: 100%;
}

.login-btn {
  width: 100%;
  height: 45px;
  font-size: 16px;
}
</style>
