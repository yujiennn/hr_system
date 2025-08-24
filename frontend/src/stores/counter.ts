import { ref, computed } from 'vue'
import { defineStore } from 'pinia'
import authService, { type UserInfo } from '@/services/auth'

export const useAuthStore = defineStore('auth', () => {
  const user = ref<UserInfo | null>(null)
  const isAuthenticated = ref(false)

  // 计算属性
  const userType = computed(() => user.value?.user_type)
  const isEmployee = computed(() => user.value?.user_type === 'employee')
  const isManager = computed(() => user.value?.user_type === 'manager')
  const isAdmin = computed(() => user.value?.user_type === 'admin')

  // 登录
  async function login(username: string, password: string) {
    try {
      console.log('Store: 开始登录请求, 用户名:', username)
      const response = await authService.login({ username, password })
      console.log('Store: 登录响应:', response)
      
      if (!response.user) {
        throw new Error('登录响应中缺少用户信息')
      }
      
      user.value = response.user
      isAuthenticated.value = true
      console.log('Store: 用户状态已更新:', user.value)
      return response
    } catch (error: any) {
      console.error('Store: 登录错误:', error)
      user.value = null
      isAuthenticated.value = false
      throw error
    }
  }

  // 登出
  async function logout() {
    try {
      await authService.logout()
    } catch (error: any) {
      console.error('Logout error:', error)
    } finally {
      user.value = null
      isAuthenticated.value = false
    }
  }

  // 获取用户信息
  async function fetchUserInfo() {
    try {
      if (authService.isAuthenticated()) {
        user.value = await authService.getCurrentUser()
        isAuthenticated.value = true
      }
    } catch (error: any) {
      console.error('Fetch user info error:', error)
      user.value = null
      isAuthenticated.value = false
    }
  }

  // 更新用户信息
  async function updateProfile(data: Partial<UserInfo>) {
    try {
      const updatedUser = await authService.updateProfile(data)
      user.value = updatedUser
      return updatedUser
    } catch (error: any) {
      throw error
    }
  }

  // 初始化用户状态
  function initAuth() {
    if (authService.isAuthenticated()) {
      fetchUserInfo()
    }
  }

  return {
    user,
    isAuthenticated,
    userType,
    isEmployee,
    isManager,
    isAdmin,
    login,
    logout,
    fetchUserInfo,
    updateProfile,
    initAuth
  }
})

export {
  useAuthStore as useUserStore
}
