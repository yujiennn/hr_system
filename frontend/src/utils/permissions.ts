/**
 * 权限检查工具函数
 * 用于前端判断用户权限和数据可见性
 * 
 * 背景: 系统采用部门基权限模型，而非角色基权限
 * - 财务部员工: 创建、编辑、批准、发放薪资
 * - 部门经理: 审核本部门薪资（需要额外检查部门匹配）
 * - 普通员工: 只能查看自己的薪资
 */

export interface User {
  id: number
  username: string
  first_name: string
  last_name: string
  email: string
  user_type: 'employee' | 'manager' | 'admin'
  department?: {
    id: number
    name: string
  }
  is_finance_department?: boolean
  employee_id?: string
  get_full_name?: string
}

/**
 * 检查用户是否是财务部员工
 * 后端在User model中实现: is_finance_department属性
 * 判断逻辑: department.name in ['财务部', '财务', 'Finance', 'FINANCE']
 */
export const isFinanceDepartment = (user: User | null): boolean => {
  if (!user) return false
  // 如果后端返回了is_finance_department属性，直接使用
  if (user.is_finance_department !== undefined) {
    return user.is_finance_department
  }
  // 备用: 本地检查（以防is_finance_department未返回）
  if (!user.department) return false
  const deptName = user.department.name
  return deptName === '财务部' || deptName === '财务' || deptName === 'Finance' || deptName === 'FINANCE'
}

/**
 * 检查用户是否是经理
 */
export const isManager = (user: User | null): boolean => {
  if (!user) return false
  return user.user_type === 'manager'
}

/**
 * 检查用户是否是管理员
 */
export const isAdmin = (user: User | null): boolean => {
  if (!user) return false
  return user.user_type === 'admin'
}

/**
 * 检查用户是否是普通员工（非经理非管理员）
 */
export const isRegularEmployee = (user: User | null): boolean => {
  if (!user) return false
  return user.user_type === 'employee'
}

/**
 * 检查用户是否能创建薪资
 * 权限: 财务部员工 + 管理员
 */
export const canCreateSalary = (user: User | null): boolean => {
  if (!user) return false
  return isFinanceDepartment(user) || isAdmin(user)
}

/**
 * 检查用户是否能编辑薪资
 * 权限: 财务部员工 + 管理员（仅限草稿状态）
 */
export const canEditSalary = (user: User | null, status?: string): boolean => {
  if (!user) return false
  if (status && status !== 'draft') return false
  return isFinanceDepartment(user) || isAdmin(user)
}

/**
 * 检查用户是否能删除薪资
 * 权限: 财务部员工 + 管理员（仅限草稿状态）
 */
export const canDeleteSalary = (user: User | null, status?: string): boolean => {
  if (!user) return false
  if (status && status !== 'draft') return false
  return isFinanceDepartment(user) || isAdmin(user)
}

/**
 * 检查用户是否能审核薪资
 * 权限: 
 * - 部门经理可审核本部门的薪资
 * - 管理员可审核所有薪资
 * 
 * @param user 当前用户
 * @param salaryUserId 薪资记录的员工ID
 * @param salaryUserDeptId 薪资记录的员工所在部门ID
 */
export const canReviewSalary = (
  user: User | null,
  salaryUserId?: number,
  salaryUserDeptId?: number
): boolean => {
  if (!user) return false

  // 管理员可以审核所有
  if (isAdmin(user)) {
    return true
  }

  // 必须是经理
  if (!isManager(user)) {
    return false
  }

  // 经理只能审核本部门
  if (salaryUserDeptId && user.department && user.department.id === salaryUserDeptId) {
    return true
  }

  // 如果没有提供部门信息，允许经理进入审核页面（具体权限由后端检查）
  return salaryUserDeptId === undefined
}

/**
 * 检查用户是否能批准薪资
 * 权限: 财务部员工 + 管理员（仅限待批准状态）
 */
export const canApproveSalary = (user: User | null, status?: string): boolean => {
  if (!user) return false
  if (status && status !== 'manager_reviewed') return false
  return isFinanceDepartment(user) || isAdmin(user)
}

/**
 * 检查用户是否能发放薪资
 * 权限: 财务部员工 + 管理员（仅限已批准状态）
 */
export const canPaySalary = (user: User | null, status?: string): boolean => {
  if (!user) return false
  if (status && status !== 'finance_approved') return false
  return isFinanceDepartment(user) || isAdmin(user)
}

/**
 * 获取用户可见的薪资列表
 * 
 * @param allSalaries 所有薪资记录
 * @param user 当前用户
 * @returns 过滤后的薪资列表
 * 
 * 规则:
 * - 管理员: 看全部
 * - 财务部员工: 看全部（用于创建/管理）
 * - 经理: 只看本部门
 * - 普通员工: 只看自己的
 */
export const getVisibleSalaries = (allSalaries: any[], user: User | null): any[] => {
  if (!user || !allSalaries) {
    return []
  }

  if (isAdmin(user)) {
    // 管理员看全部
    return allSalaries
  }

  if (isFinanceDepartment(user)) {
    // 财务部员工看全部（用于管理）
    return allSalaries
  }

  if (isManager(user)) {
    // 经理只看本部门
    if (!user.department) return []
    return allSalaries.filter(salary => {
      return salary.user?.department?.id === user.department?.id
    })
  }

  // 普通员工只看自己的
  return allSalaries.filter(salary => salary.user?.id === user.id)
}

/**
 * 获取用户的待处理项目统计
 * 
 * @param allSalaries 所有薪资记录
 * @param user 当前用户
 * @returns { pendingReview: 待审核数, pendingApproval: 待批准数 }
 */
export const getPendingCounts = (
  allSalaries: any[],
  user: User | null
): { pendingReview: number; pendingApproval: number } => {
  if (!user || !allSalaries) {
    return { pendingReview: 0, pendingApproval: 0 }
  }

  let pendingReview = 0
  let pendingApproval = 0

  if (isManager(user) && !isFinanceDepartment(user)) {
    // 部门经理：看本部门待审核（状态=draft）
    pendingReview = allSalaries.filter(salary => {
      return (
        salary.user?.department?.id === user.department?.id &&
        salary.status === 'draft'
      )
    }).length
  }

  if (isFinanceDepartment(user)) {
    // 财务部员工：看待批准（状态=manager_reviewed）
    pendingApproval = allSalaries.filter(salary => {
      return salary.status === 'manager_reviewed'
    }).length
  }

  return { pendingReview, pendingApproval }
}

/**
 * 获取用户的操作权限汇总
 * 用于组件中快速判断所有权限
 */
export const getSalaryPermissions = (user: User | null, salary?: any) => {
  return {
    // 创建
    canCreate: canCreateSalary(user),
    // 编辑
    canEdit: canEditSalary(user, salary?.status),
    // 删除
    canDelete: canDeleteSalary(user, salary?.status),
    // 审核
    canReview: salary
      ? canReviewSalary(user, salary.user?.id, salary.user?.department?.id)
      : canReviewSalary(user),
    // 批准
    canApprove: canApproveSalary(user, salary?.status),
    // 发放
    canPay: canPaySalary(user, salary?.status),
    // 查看全部（仅财务部/管理员）
    canViewAll: isFinanceDepartment(user) || isAdmin(user)
  }
}

/**
 * 获取用户的角色标签（用于前端显示）
 */
export const getRoleLabel = (user: User | null): string => {
  if (!user) return '未知角色'

  if (isAdmin(user)) {
    return '系统管理员'
  }

  if (isFinanceDepartment(user)) {
    return `财务部员工${isManager(user) ? '（经理）' : ''}`
  }

  if (isManager(user)) {
    return `部门经理${user.department ? `（${user.department.name}）` : ''}`
  }

  return `普通员工${user.department ? `（${user.department.name}）` : ''}`
}

/**
 * 获取操作错误消息（用于权限拒绝时的提示）
 */
export const getPermissionErrorMessage = (operation: string, userRole: string): string => {
  const messages: Record<string, Record<string, string>> = {
    create: {
      manager: '您没有权限创建薪资。仅财务部员工可以创建。',
      employee: '您没有权限创建薪资。仅财务部员工可以创建。'
    },
    review: {
      employee: '您没有权限审核薪资。仅部门经理可以审核。',
      finance: '您没有权限审核薪资。仅部门经理可以审核。'
    },
    approve: {
      manager: '您没有权限批准薪资。仅财务部员工可以批准。',
      employee: '您没有权限批准薪资。仅财务部员工可以批准。'
    },
    pay: {
      manager: '您没有权限发放薪资。仅财务部员工可以发放。',
      employee: '您没有权限发放薪资。仅财务部员工可以发放。'
    }
  }

  return (
    messages[operation]?.[userRole] || `您没有权限执行此操作：${operation}`
  )
}
