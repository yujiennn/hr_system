import axios from 'axios'
import type { AxiosInstance, InternalAxiosRequestConfig, AxiosResponse } from 'axios'

// 创建 axios 实例
const baseURL = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000/api'

const api: AxiosInstance = axios.create({
  baseURL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
})

// 请求拦截器
api.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    const token = localStorage.getItem('access_token')
    if (token && config.headers) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// 响应拦截器
api.interceptors.response.use(
  (response: AxiosResponse) => {
    console.log('API响应成功:', response.config.url, response.status)
    return response
  },
  (error) => {
  console.error('API请求错误详情:')
  console.error('- URL:', error.config?.url)
  console.error('- 方法:', error.config?.method)
  console.error('- 状态码:', error.response?.status)
  console.error('- 状态文本:', error.response?.statusText)
  console.error('- 响应数据:', error.response?.data)
  console.error('- 错误消息:', error.message)
    
    if (error.response?.status === 401) {
      // Token 过期或无效，清除本地存储
      localStorage.removeItem('access_token')
      localStorage.removeItem('refresh_token')
      // 暂时注释掉自动跳转，用于调试
      console.warn('401 Unauthorized - 可能需要登录')
      // window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

export default api
