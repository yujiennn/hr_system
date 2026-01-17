import { ref, computed } from 'vue'
import { defineStore } from 'pinia'
import authService, { type UserInfo } from '@/services/auth'

export const useAuthStore = defineStore('auth', () => {
  const user = ref<UserInfo | null>(null)
  const isAuthenticated = ref(false)

  // 计算属性 - 基础角色
  const userType = computed(() => user.value?.user_type)
  const isEmployee = computed(() => user.value?.user_type === 'employee')
  const isManager = computed(() => user.value?.user_type === 'manager')
  const isAdmin = computed(() => user.value?.user_type === 'admin')

  // 计算属性 - 部门基权限（NEW）
  // 判断是否是财务部员工
  const isFinanceDepartment = computed(() => {
    if (!user.value) return false
    // 优先使用后端返回的is_finance_department属性
    if ((user.value as any).is_finance_department !== undefined) {
      return (user.value as any).is_finance_department
    }
    // 备用：本地检查部门名称
    const deptName = user.value.department?.name || ''
    return ['财务部', '财务', 'Finance', 'FINANCE'].includes(deptName)
  })

  // 薪资权限检查
  const salaryPermissions = computed(() => {
    return {
      canCreate: isFinanceDepartment.value || isAdmin.value,
      canEdit: isFinanceDepartment.value || isAdmin.value,
      canDelete: isFinanceDepartment.value || isAdmin.value,
      canReview: isManager.value || isAdmin.value,
      canApprove: isFinanceDepartment.value || isAdmin.value,
      canPay: isFinanceDepartment.value || isAdmin.value,
      canViewAll: isFinanceDepartment.value || isAdmin.value
    }
  })

  // 登录
  async function login(username: string, password: string) {
    try {
      console.log('Store: 开始登录请求, 用户名:', username)
      
      // 先清除旧用户数据，防止数据混淆
      user.value = null
      isAuthenticated.value = false
      
      const response = await authService.login({ username, password })
      console.log('Store: 登录响应:', response)
      
      // JWT token已保存到localStorage，现在获取用户信息
      const userInfo = await authService.getCurrentUser()
      console.log('Store: 用户信息:', userInfo)
      
      if (!userInfo) {
        throw new Error('无法获取用户信息')
      }
      
      user.value = userInfo
      isAuthenticated.value = true
      console.log('Store: 用户状态已更新:', user.value)
      return { ...response, user: userInfo }
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
  async function initAuth() {
    if (authService.isAuthenticated()) {
      await fetchUserInfo()
    }
  }

  return {
    user,
    isAuthenticated,
    userType,
    isEmployee,
    isManager,
    isAdmin,
    isFinanceDepartment,
    salaryPermissions,
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
