import api from '../utils/api'

// 绩效周期接口
export interface PerformancePeriod {
  id: number
  name: string
  period_type: 'monthly' | 'quarterly' | 'yearly'
  start_date: string
  end_date: string
  is_active: boolean
  created_at: string
}

// 绩效指标接口
export interface PerformanceIndicator {
  id: number
  name: string
  description: string
  weight: number
  max_score: number
  order: number
}

// 绩效模板接口
export interface PerformanceTemplate {
  id: number
  name: string
  description: string
  total_score: number
  is_active: boolean
  indicators: PerformanceIndicator[]
}

// 绩效目标明细接口
export interface PerformanceGoalDetail {
  id?: number
  indicator: number
  indicator_name?: string
  indicator_description?: string
  target_value: string
  weight: number
  max_score?: number
}

// 绩效目标接口
export interface PerformanceGoal {
  id: number
  user: number
  user_info?: any
  period: number
  period_name?: string
  template: number
  template_name?: string
  status: 'draft' | 'submitted' | 'approved' | 'rejected'
  approver?: number
  approver_name?: string
  approval_note: string
  approved_at?: string
  created_at: string
  updated_at: string
  details: PerformanceGoalDetail[]
}

// 绩效评估明细接口
export interface PerformanceEvaluationDetail {
  id: number
  indicator: number
  indicator_name?: string
  indicator_description?: string
  indicator_weight?: number
  max_score?: number
  self_score?: number
  self_comment: string
  manager_score?: number
  manager_comment: string
  final_score?: number
}

// 绩效评估接口
export interface PerformanceEvaluation {
  id: number
  goal: number
  goal_info?: PerformanceGoal
  user_name?: string
  period_name?: string
  template_name?: string
  self_evaluation_score?: number
  self_evaluation_comment: string
  self_evaluated_at?: string
  manager_evaluation_score?: number
  manager_evaluation_comment: string
  manager_evaluated_at?: string
  evaluator?: number
  evaluator_name?: string
  final_score?: number
  final_rating?: 'excellent' | 'good' | 'average' | 'poor'
  status: 'draft' | 'self_evaluated' | 'manager_evaluated' | 'finalized'
  created_at: string
  updated_at: string
  details: PerformanceEvaluationDetail[]
}

// 查询参数接口
export interface PerformanceQueryParams {
  period_id?: number
  status?: string
  page?: number
  page_size?: number
}

// 绩效统计接口
export interface PerformanceStatistics {
  total_evaluations: number
  completed_evaluations: number
  completion_rate: number
  average_score: number
  rating_distribution: Record<string, number>
  department_stats: Array<{
    department: string
    total_evaluations: number
    completed_evaluations: number
    completion_rate: number
    average_score: number
  }>
}

// 绩效服务类
class PerformanceService {
  // 获取绩效周期列表
  async getPeriods(): Promise<PerformancePeriod[]> {
    const response = await api.get('/performance/periods/')
    return response.data.results || response.data
  }

  // 获取绩效模板列表
  async getTemplates(): Promise<PerformanceTemplate[]> {
    const response = await api.get('/performance/templates/')
    return response.data.results || response.data
  }
  // 获取绩效目标列表
  async getGoals(params: PerformanceQueryParams = {}) {
    const response = await api.get('/performance/goals/', { params })
    // 处理分页格式的响应
    if (response.data && response.data.results) {
      return response.data.results
    }
    return response.data || []
  }

  // 获取我的绩效目标
  async getMyGoals(params: PerformanceQueryParams = {}): Promise<PerformanceGoal[]> {
    const response = await api.get('/performance/goals/my_goals/', { params })
    // 处理分页格式的响应
    if (response.data && response.data.results) {
      return response.data.results
    }
    return response.data || []
  }

  // 创建绩效目标
  async createGoal(goalData: Partial<PerformanceGoal>): Promise<PerformanceGoal> {
    const response = await api.post('/performance/goals/', goalData)
    return response.data
  }

  // 更新绩效目标
  async updateGoal(id: number, goalData: Partial<PerformanceGoal>): Promise<PerformanceGoal> {
    const response = await api.patch(`/performance/goals/${id}/`, goalData)
    return response.data
  }

  // 提交绩效目标
  async submitGoal(id: number): Promise<void> {
    await api.post(`/performance/goals/${id}/submit/`)
  }

  // 审批绩效目标
  async approveGoal(id: number, status: 'approved' | 'rejected', note: string = ''): Promise<void> {
    await api.post(`/performance/goals/${id}/approve/`, { status, note })
  }
  // 获取绩效评估列表
  async getEvaluations(params: PerformanceQueryParams = {}) {
    const response = await api.get('/performance/evaluations/', { params })
    // 处理分页格式的响应
    if (response.data && response.data.results) {
      return response.data.results
    }
    return response.data || []
  }

  // 获取我的绩效评估
  async getMyEvaluations(params: PerformanceQueryParams = {}): Promise<PerformanceEvaluation[]> {
    // 添加时间戳防止浏览器缓存
    const response = await api.get('/performance/evaluations/my_evaluations/', { 
      params: { ...params, _t: Date.now() }
    })
    // 处理分页格式的响应
    if (response.data && response.data.results) {
      return response.data.results
    }
    return response.data || []
  }

  // 获取绩效评估详情
  async getEvaluationDetail(id: number): Promise<PerformanceEvaluation> {
    const response = await api.get(`/performance/evaluations/${id}/`)
    return response.data
  }

  // 自评
  async selfEvaluate(id: number, evaluationData: {
    self_evaluation_score?: number
    self_evaluation_comment: string
    details: Array<{
      id: number
      self_score?: number
      self_comment: string
    }>
  }): Promise<void> {
    await api.post(`/performance/evaluations/${id}/self_evaluate/`, evaluationData)
  }

  // 上级评估
  async managerEvaluate(id: number, evaluationData: {
    manager_evaluation_score?: number
    manager_evaluation_comment: string
    final_score?: number
    final_rating?: string
    details: Array<{
      id: number
      manager_score?: number
      manager_comment: string
      final_score?: number
    }>
  }): Promise<void> {
    await api.post(`/performance/evaluations/${id}/manager_evaluate/`, evaluationData)
  }

  // 获取绩效统计
  async getStatistics(params: { period_id?: number; department_id?: number } = {}): Promise<PerformanceStatistics> {
    const response = await api.get('/performance/evaluations/statistics/', { params })
    return response.data
  }

  // 获取状态标签
  getStatusLabel(status: string): string {
    const statusMap: Record<string, string> = {
      'draft': '草稿',
      'submitted': '已提交',
      'approved': '已批准',
      'rejected': '已拒绝',
      'self_evaluated': '自评完成',
      'manager_evaluated': '上级评估完成',
      'finalized': '已完成'
    }
    return statusMap[status] || '未知'
  }

  // 获取状态类型（用于Element Plus标签样式）
  getStatusType(status: string): string {
    const typeMap: Record<string, string> = {
      'draft': 'info',
      'submitted': 'warning',
      'approved': 'success',
      'rejected': 'danger',
      'self_evaluated': 'warning',
      'manager_evaluated': 'primary',
      'finalized': 'success'
    }
    return typeMap[status] || 'info'
  }

  // 获取评级标签
  getRatingLabel(rating: string): string {
    const ratingMap: Record<string, string> = {
      'excellent': '优秀',
      'good': '良好',
      'average': '一般',
      'poor': '差'
    }
    return ratingMap[rating] || '未评级'
  }

  // 获取评级类型（用于Element Plus标签样式）
  getRatingType(rating: string): string {
    const typeMap: Record<string, string> = {
      'excellent': 'success',
      'good': 'primary',
      'average': 'warning',
      'poor': 'danger'
    }
    return typeMap[rating] || 'info'
  }

  // 格式化分数
  formatScore(score: number | null | undefined): string {
    return score !== null && score !== undefined ? score.toFixed(1) : '-'
  }

  // 计算加权分数
  calculateWeightedScore(details: PerformanceEvaluationDetail[]): number {
    let totalScore = 0
    let totalWeight = 0
    
    details.forEach(detail => {
      if (detail.final_score && detail.indicator_weight) {
        totalScore += detail.final_score * detail.indicator_weight / 100
        totalWeight += detail.indicator_weight
      }
    })
    
    return totalWeight > 0 ? (totalScore / totalWeight * 100) : 0
  }

  // 检查是否可以自评（需要传入当前用户ID来验证）
  canSelfEvaluate(evaluation: PerformanceEvaluation, currentUserId?: number): boolean {
    // 状态必须是 draft 或 self_evaluated
    const statusOk = ['draft', 'self_evaluated'].includes(evaluation.status)
    
    // 如果传入了用户ID，还需要检查是否是评估所属的用户
    if (currentUserId !== undefined && evaluation.goal_info?.user !== undefined) {
      return statusOk && evaluation.goal_info.user === currentUserId
    }
    
    // 如果没有传入用户ID，只检查状态（向后兼容）
    return statusOk
  }

  // 检查是否可以上级评估
  canManagerEvaluate(evaluation: PerformanceEvaluation): boolean {
    return ['self_evaluated', 'manager_evaluated'].includes(evaluation.status)
  }

  // 检查是否已完成
  isCompleted(evaluation: PerformanceEvaluation): boolean {
    return evaluation.status === 'finalized'
  }
}

// 导出单例
export const performanceService = new PerformanceService()
export default performanceService
