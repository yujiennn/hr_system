import api from '../utils/api'

// 薪资配置接口
export interface SalaryConfig {
  id: number
  name: string
  is_active: boolean
  full_attendance_bonus: number
  performance_level_a_min: number
  performance_level_b_min: number
  performance_level_c_min: number
  performance_level_a_coefficient: number
  performance_level_b_coefficient: number
  performance_level_c_coefficient: number
  performance_level_d_coefficient: number
  performance_bonus_base_rate: number
  sick_leave_free_days: number
  sick_leave_deduction_rate: number
  personal_leave_deduction_rate: number
  late_deduction_minor: number
  late_deduction_major: number
  late_threshold_minutes: number
  absence_deduction_rate: number
  work_days_per_month: number
  created_at: string
  updated_at: string
}

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
  status: 'draft' | 'manager_reviewed' | 'finance_approved' | 'paid' | 'rejected'
  status_display?: string
  pay_date: string | null
  created_at: string
  updated_at: string
  
  // === 绩效关联字段 ===
  performance_evaluation?: number | null
  performance_score?: number | null
  performance_level?: 'A' | 'B' | 'C' | 'D' | null
  performance_level_display?: string | null
  performance_coefficient?: number
  performance_period_name?: string | null
  
  // === 全勤奖字段 ===
  full_attendance_bonus?: number
  is_full_attendance?: boolean
  
  // === 考勤扣款字段 ===
  leave_deduction?: number
  late_deduction?: number
  absence_deduction?: number
  
  // === 考勤统计字段 ===
  leave_days?: number
  sick_leave_days?: number
  personal_leave_days?: number
  other_leave_days?: number
  late_count?: number
  early_leave_count?: number
  absence_count?: number
  actual_work_days?: number
  
  // 审批信息
  manager?: {
    id: number
    username: string
    get_full_name: string
  }
  manager_reviewed_at?: string
  manager_note?: string
  finance_approver?: {
    id: number
    username: string
    get_full_name: string
  }
  finance_approved_at?: string
  finance_note?: string
  paid_by?: {
    id: number
    username: string
    get_full_name: string
  }
  rejected_by?: {
    id: number
    username: string
    get_full_name: string
  }
  rejection_reason?: string
  rejected_at?: string
  // 用户信息
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

// 计算工资请求参数
export interface CalculateSalaryParams {
  user_id: number
  year: number
  month: number
  basic_salary?: number
  allowances?: number
  overtime_pay?: number
  social_security?: number
  housing_fund?: number
  income_tax?: number
  other_deductions?: number
}

// 批量计算请求参数
export interface BatchCalculateParams {
  year: number
  month: number
  department_id?: number
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
class SalaryService {  // 获取部门薪资记录（经理专用）
  async getDepartmentRecords(params: SalaryQueryParams = {}) {
    const response = await api.get('/salary/records/department-records/', { params })
    if (response.data && response.data.results) {
      return response.data
    }
    return response.data || []
  }

  // 获取待经理审核的薪资
  async getPendingReview(params: SalaryQueryParams = {}) {
    const response = await api.get('/salary/records/pending-review/', { params })
    if (response.data && response.data.results) {
      return response.data
    }
    return response.data || []
  }

  // 获取待财务部批准的薪资（财务部专用）
  async getPendingApproval(params: SalaryQueryParams = {}) {
    const response = await api.get('/salary/records/pending-approval/', { params })
    if (response.data && response.data.results) {
      return response.data
    }
    return response.data || []
  }

  // 创建薪资记录（财务部员工专用）
  async createSalary(data: Partial<SalaryRecord>) {
    const response = await api.post('/salary/records/', data)
    return response.data
  }

  // 更新薪资记录（财务部员工专用）
  async updateSalary(id: number, data: Partial<SalaryRecord>) {
    const response = await api.patch(`/salary/records/${id}/`, data)
    return response.data
  }

  // 经理审核薪资
  async reviewSalary(id: number, action: 'approve' | 'reject', managerNote: string = '') {
    const response = await api.post(`/salary/records/${id}/manager-review/`, {
      action,
      manager_note: managerNote
    })
    return response.data
  }

  // 财务部门批准薪资
  async approveSalary(id: number, action: 'approve' | 'reject', financeNote: string = '') {
    const response = await api.post(`/salary/records/${id}/finance-approve/`, {
      action,
      finance_note: financeNote
    })
    return response.data
  }

  // 财务部门发放薪资
  async paySalary(id: number, payDate: string) {
    const response = await api.post(`/salary/records/${id}/pay/`, {
      pay_date: payDate
    })
    return response.data
  }

  // 获取部门员工列表（用于创建薪资）
  async getDepartmentEmployees() {
    const response = await api.get('/salary/records/department-employees/')
    return response.data.employees || []
  }

  // === 新增：薪资计算相关方法 ===
  
  // 计算单个员工工资
  async calculateSalary(params: CalculateSalaryParams) {
    const response = await api.post('/salary/records/calculate/', params)
    return response.data
  }

  // 批量计算员工工资
  async batchCalculateSalary(params: BatchCalculateParams) {
    const response = await api.post('/salary/records/batch-calculate/', params)
    return response.data
  }

  // 重新计算工资
  async recalculateSalary(id: number) {
    const response = await api.post(`/salary/records/${id}/recalculate/`)
    return response.data
  }

  // 获取考勤汇总
  async getAttendanceSummary(id: number) {
    const response = await api.get(`/salary/records/${id}/attendance-summary/`)
    return response.data
  }

  // 获取绩效汇总
  async getPerformanceSummary(id: number) {
    const response = await api.get(`/salary/records/${id}/performance-summary/`)
    return response.data
  }

  // === 薪资配置相关方法 ===
  
  // 获取当前启用的配置
  async getActiveConfig(): Promise<SalaryConfig> {
    const response = await api.get('/salary/config/active/')
    return response.data
  }

  // 获取所有配置
  async getAllConfigs(): Promise<SalaryConfig[]> {
    const response = await api.get('/salary/config/')
    return response.data.results || response.data
  }

  // 创建配置
  async createConfig(data: Partial<SalaryConfig>): Promise<SalaryConfig> {
    const response = await api.post('/salary/config/', data)
    return response.data
  }

  // 更新配置
  async updateConfig(id: number, data: Partial<SalaryConfig>): Promise<SalaryConfig> {
    const response = await api.patch(`/salary/config/${id}/`, data)
    return response.data
  }

  // 激活配置
  async activateConfig(id: number) {
    const response = await api.post(`/salary/config/${id}/activate/`)
    return response.data
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
  getSalaryStatusType(status: string): 'success' | 'warning' | 'info' | 'danger' {
    switch (status) {
      case 'draft':
        return 'info'
      case 'manager_reviewed':
        return 'warning'
      case 'finance_approved':
        return 'success'
      case 'paid':
        return 'success'
      case 'rejected':
        return 'danger'
      default:
        return 'info'
    }
  }

  // 获取薪资状态标签文字
  getSalaryStatusLabel(status: string): string {
    switch (status) {
      case 'draft':
        return '草稿'
      case 'manager_reviewed':
        return '经理已审核'
      case 'finance_approved':
        return '财务已批准'
      case 'paid':
        return '已发放'
      case 'rejected':
        return '已拒绝'
      default:
        return '未知'
    }
  }

  // 获取绩效等级类型（用于Element Plus标签样式）
  getPerformanceLevelType(level: string | null | undefined): 'success' | 'warning' | 'info' | 'danger' {
    switch (level) {
      case 'A':
        return 'success'
      case 'B':
        return 'success'
      case 'C':
        return 'warning'
      case 'D':
        return 'danger'
      default:
        return 'info'
    }
  }

  // 获取绩效等级标签文字
  getPerformanceLevelLabel(level: string | null | undefined): string {
    switch (level) {
      case 'A':
        return '优秀'
      case 'B':
        return '良好'
      case 'C':
        return '合格'
      case 'D':
        return '待改进'
      default:
        return '未评定'
    }
  }
}

// 导出单例
export const salaryService = new SalaryService()
export default salaryService
