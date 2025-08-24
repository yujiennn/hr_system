import api from '@/utils/api'

export interface LeaveType {
  id: number
  name: string
  description: string
  max_days_per_year: number
  is_paid: boolean
  is_active: boolean
}

export interface LeaveApplication {
  id: number
  user: number
  user_name: string
  leave_type: number
  leave_type_name: string
  start_date: string
  end_date: string
  days: number
  reason: string
  status: 'pending' | 'approved' | 'rejected' | 'cancelled'
  approver: number | null
  approver_name: string
  approval_note: string
  approved_at: string | null
  attachment: string | null
  created_at: string
  updated_at: string
}

export interface LeaveBalance {
  id: number
  user: number
  user_name: string
  leave_type: number
  leave_type_name: string
  year: number
  total_days: number
  used_days: number
  remaining_days: number
}

export interface CreateLeaveApplicationData {
  leave_type: number
  start_date: string
  end_date: string
  reason: string
  attachment?: File
}

export interface LeaveApprovalData {
  status: 'approved' | 'rejected'
  approval_note?: string
}

class LeaveService {  // 获取请假类型列表
  async getLeaveTypes(): Promise<LeaveType[]> {
    const response = await api.get('/leave/types/')
    // 处理分页格式的响应
    if (response.data && response.data.results) {
      return response.data.results
    }
    return response.data || []
  }
  // 获取我的请假申请
  async getMyApplications(year?: number): Promise<LeaveApplication[]> {
    const params = year ? { year } : {}
    const response = await api.get('/leave/my-applications/', { params })
    // 检查响应格式 - 如果有分页格式就使用results，否则使用原数据
    if (response.data && response.data.results) {
      return response.data.results
    }
    // 如果有applications字段也支持
    if (response.data && response.data.applications) {
      return response.data.applications
    }
    return response.data || []
  }

  // 创建请假申请
  async createApplication(data: CreateLeaveApplicationData): Promise<LeaveApplication> {
    const formData = new FormData()
    formData.append('leave_type', data.leave_type.toString())
    formData.append('start_date', data.start_date)
    formData.append('end_date', data.end_date)
    formData.append('reason', data.reason)
    
    if (data.attachment) {
      formData.append('attachment', data.attachment)
    }

    const response = await api.post('/leave/applications/', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })
    return response.data
  }

  // 取消请假申请
  async cancelApplication(id: number): Promise<void> {
    await api.post(`/leave/applications/${id}/cancel/`)
  }

  // 审批请假申请
  async approveApplication(id: number, data: LeaveApprovalData): Promise<void> {
    await api.post(`/leave/applications/${id}/approve/`, data)
  }
  // 获取请假余额
  async getLeaveBalances(year?: number): Promise<LeaveBalance[]> {
    const params = year ? { year } : {}
    const response = await api.get('/leave/balances/', { params })
    // 处理分页格式的响应
    if (response.data && response.data.results) {
      return response.data.results
    }
    return response.data || []
  }

  // 获取请假统计
  async getLeaveStatistics(params: {
    year?: number
    department?: number
    employee?: string
  } = {}) {
    const response = await api.get('/leave/statistics/', { params })
    return response.data
  }  // 获取待审批的请假申请 (管理员/经理)
  async getPendingApplications(): Promise<LeaveApplication[]> {
    const response = await api.get('/leave/applications/', {
      params: { status: 'pending' }
    })
    // 处理分页格式的响应
    if (response.data && response.data.results) {
      return response.data.results
    }
    return response.data || []
  }
  // 获取所有请假申请 (管理员/经理) - 用于管理界面
  async getAllApplications(params: {
    status?: string
    user?: string  
    leave_type?: string
    start_date?: string
    end_date?: string
  } = {}): Promise<LeaveApplication[]> {
    const response = await api.get('/leave/applications/', { params })
    // 处理分页格式的响应
    if (response.data && response.data.results) {
      return response.data.results
    }
    return response.data || []
  }

  // 获取最近的请假申请（限制数量）
  async getRecentApplications(limit: number = 5): Promise<LeaveApplication[]> {
    const applications = await this.getMyApplications()
    return applications.slice(0, limit)
  }

  // 获取剩余年假天数
  async getRemainingAnnualLeave(): Promise<number> {
    const currentYear = new Date().getFullYear()
    const balances = await this.getLeaveBalances(currentYear)
    
    // 查找年假余额 (假设年假的name为"年假")
    const annualLeaveBalance = balances.find(balance => 
      balance.leave_type_name.includes('年假') || 
      balance.leave_type_name.includes('年假')
    )
    
    return annualLeaveBalance ? annualLeaveBalance.remaining_days : 0
  }
}

export default new LeaveService()
