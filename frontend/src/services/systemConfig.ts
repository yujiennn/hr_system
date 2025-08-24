import api from '@/utils/api'

// 系统配置接口
export interface SystemConfig {
  id: number
  key: string
  value: string
  json_value: any
  config_type: string
  description: string
  is_active: boolean
  created_at: string
  updated_at: string
}

// 批量更新配置接口
export interface BatchUpdateConfig {
  configs: Array<{
    id: number
    [key: string]: any
  }>
}

// 邮件测试接口
export interface EmailTestData {
  recipient: string
  subject?: string
  message?: string
}

// 系统维护接口
export interface SystemMaintenanceData {
  action: 'clear_logs' | 'clear_cache' | 'restart_system'
  confirm: boolean
}

// 系统配置服务类
class SystemConfigService {
  private baseURL = '/system'
  // 获取所有配置
  async getAllConfigs(): Promise<SystemConfig[]> {
    const response = await api.get(`${this.baseURL}/configs/`)
    return response.data.results || response.data
  }

  // 按类型获取配置
  async getConfigsByType(configType: string): Promise<SystemConfig[]> {
    const response = await api.get(`${this.baseURL}/configs/by_type/?type=${configType}`)
    return response.data
  }

  // 获取单个配置
  async getConfig(id: number): Promise<SystemConfig> {
    const response = await api.get(`${this.baseURL}/configs/${id}/`)
    return response.data
  }

  // 创建配置
  async createConfig(data: Partial<SystemConfig>): Promise<SystemConfig> {
    const response = await api.post(`${this.baseURL}/configs/`, data)
    return response.data
  }

  // 更新配置
  async updateConfig(id: number, data: Partial<SystemConfig>): Promise<SystemConfig> {
    const response = await api.patch(`${this.baseURL}/configs/${id}/`, data)
    return response.data
  }

  // 删除配置
  async deleteConfig(id: number): Promise<void> {
    await api.delete(`${this.baseURL}/configs/${id}/`)
  }

  // 批量更新配置
  async batchUpdateConfigs(data: BatchUpdateConfig): Promise<{ message: string, updated_count: number }> {
    const response = await api.post(`${this.baseURL}/configs/batch_update/`, data)
    return response.data
  }

  // 测试邮件配置
  async testEmail(data: EmailTestData): Promise<{ message: string }> {
    const response = await api.post(`${this.baseURL}/configs/test_email/`, data)
    return response.data
  }

  // 系统维护操作
  async performMaintenance(data: SystemMaintenanceData): Promise<{ message: string }> {
    const response = await api.post(`${this.baseURL}/configs/maintenance/`, data)
    return response.data
  }

  // 根据键名获取配置值
  async getConfigValue(key: string): Promise<any> {
    const configs = await this.getAllConfigs()
    const config = configs.find(c => c.key === key)
    return config ? config.json_value : null
  }
  // 根据键名设置配置值
  async setConfigValue(key: string, value: any): Promise<SystemConfig> {
    const configs = await this.getAllConfigs()
    const config = configs.find(c => c.key === key)
    
    if (config) {
      return await this.updateConfig(config.id, { 
        value: typeof value === 'string' ? value : JSON.stringify(value)
      })
    } else {
      throw new Error(`配置项 ${key} 不存在`)
    }
  }
}

// 导出单例实例
const systemConfigService = new SystemConfigService()
export default systemConfigService

// 导出配置类型枚举
export const CONFIG_TYPES = {
  BASIC: 'basic',
  ATTENDANCE: 'attendance', 
  EMAIL: 'email',
  SECURITY: 'security',
  NOTIFICATION: 'notification',
  MAINTENANCE: 'maintenance'
} as const

export type ConfigType = typeof CONFIG_TYPES[keyof typeof CONFIG_TYPES]
