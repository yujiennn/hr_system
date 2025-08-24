// 报表服务
import api from '@/utils/api'

// 报表分类接口
export interface ReportCategory {
  id: number
  name: string
  code: string
  description: string
  created_at: string
  updated_at: string
}

// 报表模板接口
export interface ReportTemplate {
  id: number
  name: string
  code: string
  category: number
  description: string
  default_format: string
  created_by: number
  is_active: boolean
  created_at: string
  updated_at: string
}

// 报表接口
export interface Report {
  id: number
  name: string
  template: number
  format: string
  parameters: any
  status: string
  file_path?: string
  created_by: number
  generated_at?: string
  created_at: string
  updated_at: string
}

// 报表调度接口
export interface ReportSchedule {
  id: number
  name: string
  template: number
  frequency: string
  parameters: any
  next_run_time?: string
  is_active: boolean
  created_by: number
  created_at: string
  updated_at: string
}

// 系统日志接口
export interface SystemLog {
  id: number
  level: string
  module: string
  user?: number
  message: string
  full_message: string
  ip_address: string
  created_at: string
}

// 数据统计接口
export interface DataStatistics {
  employee_stats: {
    total: number
    active: number
    inactive: number
    by_department: Array<{
      department: string
      count: number
    }>
    by_position: Array<{
      position: string
      count: number
    }>
  }
  attendance_stats: {
    total_records: number
    present_rate: number
    late_rate: number
    absent_rate: number
    monthly_trend: Array<{
      month: string
      present: number
      late: number
      absent: number
    }>
  }
  salary_stats: {
    total_amount: number
    avg_salary: number
    by_department: Array<{
      department: string
      total: number
      avg: number
    }>
    monthly_trend: Array<{
      month: string
      total: number
      avg: number
    }>
  }
  performance_stats: {
    total_evaluations: number
    avg_score: number
    by_level: Array<{
      level: string
      count: number
      avg_score: number
    }>
    monthly_trend: Array<{
      month: string
      count: number
      avg_score: number
    }>
  }
}

class ReportsService {
  // 获取报表分类列表
  async getCategories(): Promise<ReportCategory[]> {
    const response = await api.get('/reports/categories/')
    return response.data.results || response.data
  }

  // 获取报表模板列表
  async getTemplates(categoryCode?: string): Promise<ReportTemplate[]> {
    const params = categoryCode ? { category__code: categoryCode } : {}
    const response = await api.get('/reports/templates/', { params })
    return response.data.results || response.data
  }

  // 获取报表列表
  async getReports(params?: any): Promise<{ results: Report[], count: number }> {
    const response = await api.get('/reports/reports/', { params })
    return response.data
  }

  // 生成报表
  async generateReport(data: {
    name: string
    template: number
    format: string
    parameters?: any
  }): Promise<Report> {
    const response = await api.post('/reports/reports/', data)
    return response.data
  }

  // 下载报表
  async downloadReport(reportId: number): Promise<Blob> {
    const response = await api.get(`/reports/reports/${reportId}/download/`, {
      responseType: 'blob'
    })
    return response.data
  }

  // 获取报表调度列表
  async getSchedules(params?: any): Promise<{ results: ReportSchedule[], count: number }> {
    const response = await api.get('/reports/schedules/', { params })
    return response.data
  }

  // 创建报表调度
  async createSchedule(data: {
    name: string
    template: number
    frequency: string
    parameters?: any
  }): Promise<ReportSchedule> {
    const response = await api.post('/reports/schedules/', data)
    return response.data
  }

  // 更新报表调度
  async updateSchedule(id: number, data: Partial<ReportSchedule>): Promise<ReportSchedule> {
    const response = await api.patch(`/reports/schedules/${id}/`, data)
    return response.data
  }

  // 删除报表调度
  async deleteSchedule(id: number): Promise<void> {
    await api.delete(`/reports/schedules/${id}/`)
  }

  // 获取系统日志
  async getSystemLogs(params?: {
    level?: string
    module?: string
    start_date?: string
    end_date?: string
    search?: string
    page?: number
    page_size?: number
  }): Promise<{ results: SystemLog[], count: number }> {
    const response = await api.get('/reports/logs/', { params })
    return response.data
  }

  // 获取数据统计
  async getDataStatistics(): Promise<DataStatistics> {
    const response = await api.get('/reports/statistics/')
    return response.data
  }

  // 清理日志
  async cleanLogs(data: {
    before_date?: string
    level?: string
    module?: string
  }): Promise<{ message: string, deleted_count: number }> {
    const response = await api.post('/reports/logs/clean/', data)
    return response.data
  }
}

export default new ReportsService()
