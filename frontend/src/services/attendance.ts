import api from '@/utils/api'

export interface ClockData {
  location?: string
  note?: string
  latitude?: number
  longitude?: number
  location_id?: number
  force_clock?: boolean
}

export interface FaceClockData {
  face_image: string
  location?: string
  latitude?: number
  longitude?: number
  location_id?: number
  note?: string
}

export interface LocationClockData {
  latitude: number
  longitude: number
  location_id?: number
  location?: string
  note?: string
  force_clock?: boolean
}

export interface AttendanceRecord {
  id: number
  date: string
  clock_in_time: string | null
  clock_out_time: string | null
  work_hours: number | null
  status: string
  is_late: boolean
  is_early_leave: boolean
  is_absent: boolean
  remarks: string
  created_at: string
  updated_at: string
}

export interface TodayAttendance {
  clock_in_time: string | null
  clock_out_time: string | null
  work_hours: number | null
  status: string
  is_late: boolean
  is_early_leave: boolean
}

export interface MonthlyStats {
  work_days: number
  late_days: number
  early_leave_days: number
  absent_days: number
  total_hours: number
  attendance_rate: number
}

class AttendanceService {
  // 上班打卡
  async clockIn(data: ClockData = {}) {
    const response = await api.post('/attendance/clock-in/', data)
    return response.data
  }

  // 下班打卡
  async clockOut(data: ClockData = {}) {
    const response = await api.post('/attendance/clock-out/', data)
    return response.data
  }

  // 位置打卡 - 上班
  async locationClockIn(data: LocationClockData) {
    const response = await api.post('/attendance/clock-in/', data)
    return response.data
  }

  // 位置打卡 - 下班
  async locationClockOut(data: LocationClockData) {
    const response = await api.post('/attendance/clock-out/', data)
    return response.data
  }

  // 人脸识别上班打卡
  async faceClockIn(data: FaceClockData) {
    const response = await api.post('/attendance/face-clock-in/', data)
    return response.data
  }

  // 人脸识别下班打卡
  async faceClockOut(data: FaceClockData) {
    const response = await api.post('/attendance/face-clock-out/', data)
    return response.data
  }

  // 获取我的考勤记录
  async getMyRecords(params: {
    year?: number
    month?: number
    page?: number
    page_size?: number
  } = {}) {
    const response = await api.get('/attendance/my-records/', { params })
    // 返回完整的分页响应数据
    console.log('考勤记录API响应:', response.data)
    return response.data
  }

  // 获取考勤统计
  async getStatistics(params: {
    year?: number
    month?: number
    employee_id?: number
  } = {}) {
    try {
      const response = await api.get('/attendance/statistics/', { params })
      console.log('考勤统计API原始响应:', response)
      // 直接返回response.data，因为后端已经返回了正确的结构
      return response.data
    } catch (error: any) {
      console.error('考勤统计API调用失败:', error)
      throw error
    }
  }

  // 获取今日考勤状态
  async getTodayAttendance(): Promise<TodayAttendance> {
    const response = await api.get('/attendance/today-status/')
    return response.data
  }

  // 获取本月考勤统计
  async getMonthlyStats(year?: number, month?: number): Promise<MonthlyStats> {
    const params: any = {}
    if (year) params.year = year
    if (month) params.month = month
    
    const response = await api.get('/attendance/monthly-stats/', { params })
    return response.data
  }
}

export default new AttendanceService()
