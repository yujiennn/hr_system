import api from '@/utils/api'

export interface LoginData {
  username: string
  password: string
}

export interface UserInfo {
  id: number
  username: string
  email: string
  first_name: string
  last_name: string
  employee_id: string
  phone: string
  user_type: 'employee' | 'manager' | 'admin'
  department: number | { id: number; name: string } | null
  department_name: string
  avatar?: string
  position: string
  job_level: string
  gender?: string
  birth_date?: string
  id_card?: string
  address?: string
  emergency_contact?: string
  emergency_phone?: string
  hire_date?: string
  education?: string
  major?: string
  university?: string
  work_experience?: string
  skills?: string
  bio?: string
  is_finance_department?: boolean
}

export interface LoginResponse {
  access: string
  refresh: string
}

class AuthService {  // 登录
  async login(data: LoginData): Promise<LoginResponse> {
    try {
      console.log('AuthService: 发送登录请求:', data.username)
      console.log('AuthService: API基地址:', api.defaults.baseURL)
      console.log('AuthService: 请求数据:', data)
      
      // 先清除旧的 token，确保不会混淆
      localStorage.removeItem('access_token')
      localStorage.removeItem('refresh_token')
      
      const response = await api.post('/users/token/', data)
      console.log('AuthService: 登录响应状态:', response.status)
      console.log('AuthService: 登录响应数据:', response.data)
      
      const { access, refresh } = response.data
      
      if (!access) {
        throw new Error('服务器返回的数据格式不正确：缺少access token')
      }
      
      // 保存新 token 到 localStorage
      localStorage.setItem('access_token', access)
      localStorage.setItem('refresh_token', refresh)
      
      return response.data
    } catch (error: any) {
      console.error('AuthService: 登录错误:', error)
      console.error('AuthService: 错误类型:', error.constructor.name)
      console.error('AuthService: 错误代码:', error.code)
      console.error('AuthService: 错误消息:', error.message)
      if (error.response) {
        console.error('AuthService: 响应状态:', error.response.status)
        console.error('AuthService: 响应数据:', error.response.data)
        console.error('AuthService: 响应头:', error.response.headers)
      } else if (error.request) {
        console.error('AuthService: 请求对象:', error.request)
      }
      throw error
    }
  }

  // 登出
  async logout(): Promise<void> {
    const refreshToken = sessionStorage.getItem('refresh_token')
    if (refreshToken) {
      try {
        await api.post('/users/logout/', { refresh_token: refreshToken })
      } catch (error: any) {
        console.error('Logout error:', error)
      }
    }
    
    // 清除存储
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
  }

  // 获取当前用户信息
  async getCurrentUser(): Promise<UserInfo> {
    const response = await api.get('/users/profile/')
    return response.data
  }
  // 更新用户信息
  async updateProfile(data: Partial<UserInfo>): Promise<UserInfo> {
    console.log('AuthService.updateProfile - 发送数据:', data)
    console.log('AuthService.updateProfile - 数据类型检查:', typeof data)
    console.log('AuthService.updateProfile - 数据键值:', Object.keys(data))
    
    const response = await api.put('/users/profile/', data)
    console.log('AuthService.updateProfile - 响应:', response.data)
    return response.data
  }

  // 修改密码
  async changePassword(data: {
    old_password: string
    new_password: string
    confirm_password: string
  }): Promise<void> {
    await api.post('/users/change-password/', data)
  }

  // 检查是否已登录
  isAuthenticated(): boolean {
    return !!localStorage.getItem('access_token')
  }

  // 获取 token
  getToken(): string | null {
    return localStorage.getItem('access_token')
  }
}

export default new AuthService()
