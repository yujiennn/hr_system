import api from '@/utils/api'

export interface CompanyLocation {
  id: number
  name: string
  address: string
  latitude: number
  longitude: number
  radius: number
  description: string
  is_active: boolean
  created_at: string
}

export interface LocationValidation {
  in_range: boolean
  distance: number
  allowed_radius: number
  location_name: string
  location_address: string
}

export interface UserLocation {
  latitude: number
  longitude: number
  accuracy?: number
  timestamp?: number
}

class LocationService {
  // 获取所有公司位置
  async getCompanyLocations(): Promise<{ success: boolean; data: CompanyLocation[] }> {
    const response = await api.get('/system/company-locations/')
    
    // 处理不同的响应格式
    let data: CompanyLocation[] = []
    
    if (response.data) {
      if (Array.isArray(response.data)) {
        // 直接返回数组
        data = response.data
      } else if (response.data.results && Array.isArray(response.data.results)) {
        // 分页格式：{results: [...], count: number, ...}
        data = response.data.results
      } else if (response.data.data && Array.isArray(response.data.data)) {
        // 自定义格式：{success: boolean, data: [...]}
        data = response.data.data
      } else if (response.data.success && response.data.data) {
        data = response.data.data
      }
    }
    
    return {
      success: true,
      data: data
    }
  }

  // 验证位置是否在打卡范围内
  async validateLocation(
    latitude: number, 
    longitude: number, 
    locationId?: number
  ): Promise<{ success: boolean; data: LocationValidation }> {
    const response = await api.post('/system/company-locations/validate_location/', {
      latitude,
      longitude,
      location_id: locationId
    })
    return response.data
  }

  // 获取最近的公司位置
  async getNearestLocation(
    latitude: number, 
    longitude: number
  ): Promise<{ success: boolean; data: CompanyLocation & { distance: number; in_range: boolean } }> {
    const response = await api.get('/system/company-locations/nearest/', {
      params: { latitude, longitude }
    })
    return response.data
  }

  // 创建公司位置
  async createCompanyLocation(locationData: Omit<CompanyLocation, 'id' | 'created_at'>): Promise<{ success: boolean; data: CompanyLocation }> {
    const response = await api.post('/system/company-locations/', locationData)
    return response.data
  }

  // 更新公司位置
  async updateCompanyLocation(id: number, locationData: Partial<CompanyLocation>): Promise<{ success: boolean; data: CompanyLocation }> {
    const response = await api.put(`/system/company-locations/${id}/`, locationData)
    return response.data
  }

  // 删除公司位置
  async deleteCompanyLocation(id: number): Promise<{ success: boolean }> {
    const response = await api.delete(`/system/company-locations/${id}/`)
    return response.data
  }

  // 获取用户当前位置
  getCurrentPosition(options?: PositionOptions): Promise<UserLocation> {
    return new Promise((resolve, reject) => {
      if (!navigator.geolocation) {
        reject(new Error('浏览器不支持地理位置获取'))
        return
      }

      const defaultOptions: PositionOptions = {
        enableHighAccuracy: true,
        timeout: 10000,
        maximumAge: 60000, // 1分钟内的缓存位置可用
        ...options
      }

      navigator.geolocation.getCurrentPosition(
        (position) => {
          resolve({
            latitude: position.coords.latitude,
            longitude: position.coords.longitude,
            accuracy: position.coords.accuracy,
            timestamp: position.timestamp
          })
        },
        (error) => {
          let message = '获取位置失败'
          switch (error.code) {
            case error.PERMISSION_DENIED:
              message = '用户拒绝了位置权限请求'
              break
            case error.POSITION_UNAVAILABLE:
              message = '位置信息不可用'
              break
            case error.TIMEOUT:
              message = '获取位置超时'
              break
          }
          reject(new Error(message))
        },
        defaultOptions
      )
    })
  }

  // 监听位置变化
  watchPosition(
    callback: (location: UserLocation) => void,
    errorCallback?: (error: Error) => void,
    options?: PositionOptions
  ): number | null {
    if (!navigator.geolocation) {
      if (errorCallback) {
        errorCallback(new Error('浏览器不支持地理位置获取'))
      }
      return null
    }

    const defaultOptions: PositionOptions = {
      enableHighAccuracy: true,
      timeout: 10000,
      maximumAge: 30000, // 30秒内的缓存位置可用
      ...options
    }

    return navigator.geolocation.watchPosition(
      (position) => {
        callback({
          latitude: position.coords.latitude,
          longitude: position.coords.longitude,
          accuracy: position.coords.accuracy,
          timestamp: position.timestamp
        })
      },
      (error) => {
        if (errorCallback) {
          let message = '获取位置失败'
          switch (error.code) {
            case error.PERMISSION_DENIED:
              message = '用户拒绝了位置权限请求'
              break
            case error.POSITION_UNAVAILABLE:
              message = '位置信息不可用'
              break
            case error.TIMEOUT:
              message = '获取位置超时'
              break
          }
          errorCallback(new Error(message))
        }
      },
      defaultOptions
    )
  }

  // 停止监听位置变化
  clearWatch(watchId: number): void {
    if (navigator.geolocation) {
      navigator.geolocation.clearWatch(watchId)
    }
  }

  // 计算两点间距离（米）
  calculateDistance(
    lat1: number, 
    lon1: number, 
    lat2: number, 
    lon2: number
  ): number {
    const R = 6371000 // 地球半径，单位：米
    const dLat = this.toRadians(lat2 - lat1)
    const dLon = this.toRadians(lon2 - lon1)
    const a = Math.sin(dLat / 2) * Math.sin(dLat / 2) +
              Math.cos(this.toRadians(lat1)) * Math.cos(this.toRadians(lat2)) *
              Math.sin(dLon / 2) * Math.sin(dLon / 2)
    const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a))
    return R * c
  }

  // 转换角度为弧度
  private toRadians(degrees: number): number {
    return degrees * (Math.PI / 180)
  }
}

export default new LocationService()
