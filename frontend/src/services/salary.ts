import api from '../utils/api'

// 薪资记录接口
export interface SalaryRecord {
  id: number
  year: number
  month: number
  basic_salary: number
  performance_bonus: number
  overtime_pay: number
  allowances: number
  gross_salary: number
  social_security: number
  housing_fund: number
  income_tax: number
  other_deductions: number
  net_salary: number
  status: string
  pay_date: string | null
  created_at: string
  updated_at: string
  user_name?: string
  employee_id?: string
  department_name?: string
  user?: {
    id: number
    username: string
    employee?: {
      name: string
      employee_id: string
      department: {
        name: string
      }
    }
  }
}

// 薪资查询参数
export interface SalaryQueryParams {
  year?: number
  month?: number
  page?: number
  page_size?: number
  employee_id?: string
  department_id?: number
}

// 薪资统计接口
export interface SalaryStatistics {
  total_employees: number
  total_gross_salary: number
  total_net_salary: number
  total_deductions: number
  average_gross_salary: number
  average_net_salary: number
  department_stats?: Array<{
    department: string
    employee_count: number
    total_gross: number
    total_net: number
    average_gross: number
    average_net: number
  }>
}

// 薪资服务类
class SalaryService {  // 获取薪资记录列表
  async getSalaryRecords(params: SalaryQueryParams = {}) {
    const response = await api.get('/salary/records/', { params })
    // 处理分页格式的响应
    if (response.data && response.data.results) {
      return response.data.results
    }
    return response.data || []
  }
  // 获取当前用户的薪资记录
  async getMySalaryRecords(params: SalaryQueryParams = {}) {
    const response = await api.get('/salary/records/my-records/', { params })
    // 处理分页格式的响应
    if (response.data && response.data.results) {
      return response.data
    }
    return response.data || []
  }
  // 获取薪资详情
  async getSalaryDetail(id: number): Promise<SalaryRecord> {
    const response = await api.get(`/salary/records/${id}/`)
    return response.data
  }

  // 获取当前月份薪资
  async getCurrentSalary(): Promise<SalaryRecord | null> {
    try {
      const currentDate = new Date()
      const year = currentDate.getFullYear()
      const month = currentDate.getMonth() + 1
      
      const response = await this.getMySalaryRecords({ year, month, page_size: 1 })
      return response.results?.[0] || null
    } catch (error: any) {
      console.error('获取当前薪资失败:', error)
      return null
    }
  }

  // 获取薪资统计
  async getSalaryStatistics(params: { year?: number; month?: number; department_id?: number } = {}) {
    const response = await api.get('/salary/statistics/', { params })
    return response.data
  }

  // 导出工资单
  async exportSalary(params: { year?: number; month?: number; employee_id?: string } = {}) {
    const response = await api.get('/salary/export/', {
      params,
      responseType: 'blob'
    })
    
    // 创建下载链接
    const blob = new Blob([response.data], { 
      type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' 
    })
    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    
    // 生成文件名
    const filename = params.employee_id 
      ? `工资单_${params.year || ''}年${params.month || ''}月_${params.employee_id}.xlsx`
      : `工资单_${params.year || ''}年${params.month || ''}月.xlsx`
    
    link.download = filename
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    window.URL.revokeObjectURL(url)
  }

  // 导出单个员工工资单
  async exportSingleSalary(salaryId: number) {
    const response = await api.get(`/salary/records/${salaryId}/export/`, {
      responseType: 'blob'
    })
    
    // 创建下载链接
    const blob = new Blob([response.data], { 
      type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' 
    })
    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = `工资单_${salaryId}.xlsx`
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    window.URL.revokeObjectURL(url)
  }

  // 获取薪资趋势数据（用于图表）
  async getSalaryTrends(params: { months?: number; year?: number } = {}) {
    const { months = 12, year } = params
    const currentDate = new Date()
    const currentYear = year || currentDate.getFullYear()
    const currentMonth = currentDate.getMonth() + 1
    
    const trends = []
    
    // 获取最近几个月的数据
    for (let i = months - 1; i >= 0; i--) {
      const targetDate = new Date(currentYear, currentMonth - 1 - i, 1)
      const targetYear = targetDate.getFullYear()
      const targetMonth = targetDate.getMonth() + 1
      
      try {
        const response = await this.getMySalaryRecords({ 
          year: targetYear, 
          month: targetMonth, 
          page_size: 1 
        })
        
        if (response.results && response.results.length > 0) {
          trends.push(response.results[0])
        }
      } catch (error: any) {
        console.warn(`获取${targetYear}年${targetMonth}月薪资数据失败:`, error)
      }
    }
    
    return trends
  }
  // 格式化金额
  formatAmount(amount: number | string | null | undefined): string {
    if (amount === null || amount === undefined || amount === '') {
      return '0.00'
    }
    
    const numAmount = typeof amount === 'string' ? parseFloat(amount) : amount
    
    if (isNaN(numAmount)) {
      return '0.00'
    }
    
    return numAmount.toFixed(2)
  }

  // 获取薪资状态类型（用于Element Plus标签样式）
  getSalaryStatusType(status: string): string {
    switch (status) {
      case 'paid':
        return 'success'
      case 'pending':
        return 'warning'
      case 'processing':
        return 'info'
      default:
        return 'info'
    }
  }

  // 获取薪资状态标签文字
  getSalaryStatusLabel(status: string): string {
    switch (status) {
      case 'paid':
        return '已发放'
      case 'pending':
        return '待发放'
      case 'processing':
        return '处理中'
      default:
        return '未知'
    }
  }
}

// 导出单例
export const salaryService = new SalaryService()
export default salaryService
