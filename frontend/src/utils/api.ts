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
    // 使用 sessionStorage 实现多标签页独立登录
    const token = sessionStorage.getItem('access_token')
    if (token && config.headers) {
      config.headers.Authorization = `Bearer ${token}`
    }
    console.log('[API] 📤 请求:', {
      method: config.method?.toUpperCase(),
      url: config.url,
      hasToken: !!token
    })
    return config
  },
  (error) => {
    console.error('[API] ❌ 请求配置错误:', error)
    return Promise.reject(error)
  }
)

// 响应拦截器
api.interceptors.response.use(
  (response: AxiosResponse) => {
    console.log('[API] ✅ 响应成功:', {
      url: response.config.url,
      status: response.status,
      statusText: response.statusText
    })
    return response
  },
  (error) => {
    console.error('[API] ❌ 请求错误详情:', {
      url: error.config?.url,
      method: error.config?.method,
      status: error.response?.status,
      statusText: error.response?.statusText,
      errorCode: error.code,
      message: error.message,
      responseData: error.response?.data
    })
    
    if (error.response?.status === 401) {
      // Token 过期或无效，清除本地存储
      sessionStorage.removeItem('access_token')
      sessionStorage.removeItem('refresh_token')
      // 暂时注释掉自动跳转，用于调试
      console.warn('[API] ⚠️ 401 Unauthorized - 可能需要登录')
      // window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

export default api
