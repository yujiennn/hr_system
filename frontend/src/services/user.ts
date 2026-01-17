import api from '@/utils/api'

export interface User {
  id: number
  username: string
  email: string
  first_name: string
  last_name: string
  employee_id: string
  phone: string
  user_type: 'admin' | 'manager' | 'employee'
  department: number
  department_name: string
  avatar?: string
  gender?: 'M' | 'F'
  birth_date?: string
  id_card?: string
  address?: string
  emergency_contact?: string
  emergency_phone?: string
  hire_date?: string
  position?: string
  job_level?: string
  base_salary?: number
  is_active_employee: boolean
  created_at: string
  updated_at: string
}

export interface UserCreateData {
  username: string
  email: string
  password: string
  confirm_password: string
  first_name: string
  last_name: string
  employee_id: string
  phone: string
  user_type: 'admin' | 'manager' | 'employee'
  department: number
  gender?: 'M' | 'F'
  birth_date?: string
  id_card?: string
  address?: string
  emergency_contact?: string
  emergency_phone?: string
  hire_date?: string
  position?: string
  job_level?: string
  base_salary?: number
}

export interface UserListParams {
  page?: number
  page_size?: number
  search?: string
  user_type?: string
  department?: number
  is_active_employee?: boolean
}

export interface UserListResponse {
  count: number
  next: string | null
  previous: string | null
  results: User[]
}

// 获取用户列表
export const getUserList = async (params?: UserListParams): Promise<UserListResponse> => {
  const response = await api.get('/users/users/', { params })
  return response.data
}

// 获取用户详情
export const getUserDetail = async (id: number): Promise<User> => {
  const response = await api.get(`/users/users/${id}/`)
  return response.data
}

// 创建用户
export const createUser = async (data: UserCreateData): Promise<User> => {
  const response = await api.post('/users/users/', data)
  return response.data
}

// 更新用户
export const updateUser = async (id: number, data: Partial<UserCreateData>): Promise<User> => {
  const response = await api.patch(`/users/users/${id}/`, data)
  return response.data
}

// 删除用户
export const deleteUser = async (id: number): Promise<void> => {
  await api.delete(`/users/users/${id}/`)
}

// 激活用户
export const activateUser = async (id: number): Promise<void> => {
  await api.post(`/users/users/${id}/activate/`)
}

// 停用用户
export const deactivateUser = async (id: number): Promise<void> => {
  await api.post(`/users/users/${id}/deactivate/`)
}

// 重置用户密码
export const resetUserPassword = async (id: number): Promise<{ password: string }> => {
  const response = await api.post(`/users/users/${id}/reset_password/`)
  return response.data
}

// 获取部门列表
export const getDepartmentList = async () => {
  const response = await api.get('/users/departments/')
  return response.data
}

// 更新个人资料
export const updateProfile = async (data: {
  email?: string
  first_name?: string
  last_name?: string
  phone?: string
  position?: string
  hire_date?: string
  [key: string]: any
}): Promise<User> => {
  const response = await api.patch('/users/profile/', data)
  return response.data
}

// 修改密码
export const changeUserPassword = async (data: {
  old_password: string
  new_password: string
}): Promise<void> => {
  await api.post('/users/change-password/', data)
}

// 上传头像
export const uploadAvatar = async (file: File): Promise<User> => {
  console.log('uploadAvatar 函数被调用，文件:', file.name)
  
  const formData = new FormData()
  formData.append('avatar', file)
  
  console.log('FormData 创建完成，开始发送请求...')
  
  try {
    const response = await api.put('/users/profile/', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })
    
    console.log('API响应成功:', response.status, response.data)
    return response.data
  } catch (error: any) {
    console.error('API请求失败:', error.response?.status, error.response?.data)
    throw error
  }
}

// 人脸识别相关接口
export interface FaceRegistrationData {
  face_image: string
}

export interface FaceRecognitionData {
  face_image: string
}

export interface FaceStatusResponse {
  registered: boolean
  registeredAt?: string
  user_name?: string
}

export interface FaceRecognitionResponse {
  success: boolean
  similarity?: string
  user_name?: string
  message?: string
}

// 人脸录入
export const registerFace = async (data: FaceRegistrationData): Promise<any> => {
  const response = await api.post('/users/face/register/', data)
  return response.data
}

// 人脸识别
export const recognizeFace = async (data: FaceRecognitionData): Promise<FaceRecognitionResponse> => {
  const response = await api.post('/users/face/recognize/', data)
  return response.data
}

// 获取人脸状态
export const getFaceStatus = async (): Promise<{ data: FaceStatusResponse }> => {
  const response = await api.get('/users/face/status/')
  return response.data
}

// 删除人脸信息
export const deleteFace = async (): Promise<void> => {
  await api.delete('/users/face/delete/')
}

// 导出用户服务对象
export const userService = {
  getUserList,
  getUserDetail,
  createUser,
  updateUser,
  deleteUser,
  activateUser,
  deactivateUser,
  resetUserPassword,
  getDepartmentList,
  updateProfile,
  changeUserPassword,
  uploadAvatar,
  registerFace,
  recognizeFace,
  getFaceStatus,
  deleteFace
}
