import { request } from '../utils/request'

export interface Department {
  id: number
  name: string
  description: string
  parent: number | null
  created_at: string
  updated_at: string
  children?: Department[]
  level?: number
  sort?: number
  status?: 'active' | 'inactive'
  employeeCount?: number
  manager?: {
    id: number
    name: string
    email: string
  } | null
  isRoot?: boolean
  hasChildren?: boolean
}

export interface DepartmentCreateRequest {
  name: string
  description?: string
  parent?: number | null
}

export interface DepartmentUpdateRequest extends Partial<DepartmentCreateRequest> {
  id: number
}

class DepartmentService {  // 获取所有部门
  async getDepartments(): Promise<Department[]> {
    try {
      console.log('发送部门API请求...')
      const response = await request.get('/auth/departments/')
      console.log('部门API响应:', response)
      console.log('响应状态:', response.status)
      console.log('响应数据:', response.data)
      
      // Django REST framework返回分页数据，需要提取results字段
      const data = response.data
      if (data && data.results) {
        console.log('提取results字段:', data.results)
        console.log('部门数量:', data.results.length)
        return data.results
      } else if (Array.isArray(data)) {
        // 如果直接返回数组
        console.log('直接返回数组:', data)
        return data
      } else {
        console.error('API返回的数据格式不正确:', data)
        return []
      }
    } catch (error: any) {
      console.error('获取部门列表失败:', error)
      console.error('错误类型:', typeof error)
      console.error('错误对象:', error)
      if (error instanceof Error) {
        console.error('错误消息:', error.message)
      }
      throw error
    }
  }
  // 获取单个部门详情
  async getDepartment(id: number): Promise<Department> {
    try {
      const response = await request.get(`/auth/departments/${id}/`)
      return response.data
    } catch (error: any) {
      console.error('获取部门详情失败:', error)
      throw error
    }
  }
  // 创建部门
  async createDepartment(data: DepartmentCreateRequest): Promise<Department> {
    try {
      const response = await request.post('/auth/departments/', data)
      return response.data
    } catch (error: any) {
      console.error('创建部门失败:', error)
      throw error
    }
  }
  // 更新部门
  async updateDepartment(id: number, data: Partial<DepartmentCreateRequest>): Promise<Department> {
    try {
      const response = await request.patch(`/auth/departments/${id}/`, data)
      return response.data
    } catch (error: any) {
      console.error('更新部门失败:', error)
      throw error
    }
  }
  // 删除部门
  async deleteDepartment(id: number): Promise<void> {
    try {
      await request.delete(`/auth/departments/${id}/`)
    } catch (error: any) {
      console.error('删除部门失败:', error)
      throw error
    }
  }  // 构建部门树结构
  buildDepartmentTree(departments: Department[]): Department[] {
    console.log('🌳🌳🌳 开始构建部门树，原始数据:', departments)
    console.log('🌳 原始数据数量:', departments.length)
    
    const departmentMap = new Map<number, Department>()
    const rootDepartments: Department[] = []

    // 先创建部门映射
    departments.forEach(dept => {
      console.log(`🌳 创建映射: ${dept.name} (ID: ${dept.id}, 父ID: ${dept.parent})`)
      departmentMap.set(dept.id, {
        ...dept,
        children: [],
        level: 1,
        hasChildren: false
      })
    })
    
    console.log('🌳 部门映射创建完成，映射大小:', departmentMap.size)
    
    // 检查是否包含所有需要的部门
    if (departmentMap.size !== departments.length) {
      console.warn(`映射大小 (${departmentMap.size}) 与部门数量 (${departments.length}) 不一致!`)
    }    // 构建树结构
    departments.forEach(dept => {
      const department = departmentMap.get(dept.id)!
      
      if (dept.parent) {
        const parentDept = departmentMap.get(dept.parent)
        if (parentDept) {
          parentDept.children!.push(department)
          parentDept.hasChildren = true
          department.level = (parentDept.level || 1) + 1
          console.log(`🌳 部门 ${dept.name} 添加到父部门 ${parentDept.name}`)
        } else {
          console.warn(`🌳 ⚠️ 找不到父部门 ID ${dept.parent} for 部门 ${dept.name}，作为根部门处理`)
          // 如果找不到父部门，将其作为根部门处理
          department.isRoot = true
          rootDepartments.push(department)
        }
      } else {
        department.isRoot = true
        rootDepartments.push(department)
        console.log(`🌳 根部门: ${dept.name}`)
      }
    })

    console.log('🌳 构建完成，根部门数量:', rootDepartments.length)
    console.log('🌳 根部门列表:', rootDepartments.map(d => d.name))
    
    // 验证树形结构是否包含所有部门
    let totalDeptCount = 0
    const countDepts = (depts: Department[]): number => {
      let count = depts.length
      depts.forEach(d => {
        if (d.children && d.children.length > 0) {
          count += countDepts(d.children)
        }
      })
      return count
    }
    
    totalDeptCount = countDepts(rootDepartments)
    console.log(`树形结构中的部门总数: ${totalDeptCount}，原始数据中的部门总数: ${departments.length}`)
    
    if (totalDeptCount !== departments.length) {
      console.warn(`树形结构中的部门总数与原始数据不一致，可能有部门未被正确添加到树中!`)
    }
    
    console.log('树形结构:', rootDepartments)
    return rootDepartments
  }
}

export const departmentService = new DepartmentService()
export default departmentService
