import attendanceService from './attendance'
import leaveService from './leave'

export interface DashboardStats {
  attendance: {
    work_days: number
    late_days: number
    early_leave_days: number
    absent_days: number
    total_hours: number
    attendance_rate: number
  }
  leave: {
    remaining: number
    usedThisYear: number
    pendingApplications: number
  }
  salary: {
    lastMonth: number
    thisYear: number
  }
  performance: {
    lastScore: number
    averageScore: number
  }
}

export interface TodayAttendance {
  clock_in_time: string | null
  clock_out_time: string | null
  work_hours: number | null
  status: string
  is_late: boolean
  is_early_leave: boolean
}

class DashboardService {
  // 获取仪表板统计数据
  async getDashboardStats(): Promise<DashboardStats> {
    try {
      // 并行请求多个数据
      const [attendanceStats, leaveBalance, recentLeaves] = await Promise.all([
        attendanceService.getMonthlyStats(),
        leaveService.getRemainingAnnualLeave(),
        leaveService.getRecentApplications(10)
      ])

      // 计算今年已用请假天数
      const currentYear = new Date().getFullYear()
      const approvedLeaves = recentLeaves.filter(leave => 
        leave.status === 'approved' && 
        new Date(leave.start_date).getFullYear() === currentYear
      )
      const usedThisYear = approvedLeaves.reduce((total, leave) => total + leave.days, 0)

      // 计算待审批的请假申请数量
      const pendingApplications = recentLeaves.filter(leave => leave.status === 'pending').length

      return {
        attendance: attendanceStats,
        leave: {
          remaining: leaveBalance,
          usedThisYear,
          pendingApplications
        },
        salary: {
          lastMonth: 8500, // TODO: 从薪资服务获取
          thisYear: 85000 // TODO: 从薪资服务获取
        },
        performance: {
          lastScore: 85, // TODO: 从绩效服务获取
          averageScore: 88 // TODO: 从绩效服务获取
        }
      }
    } catch (error: any) {
      console.error('获取仪表板数据失败:', error)      // 返回默认数据
      return {
        attendance: {
          work_days: 0,
          late_days: 0,
          early_leave_days: 0,
          absent_days: 0,
          total_hours: 0,
          attendance_rate: 0
        },
        leave: {
          remaining: 0,
          usedThisYear: 0,
          pendingApplications: 0
        },
        salary: {
          lastMonth: 0,
          thisYear: 0
        },
        performance: {
          lastScore: 0,
          averageScore: 0
        }
      }
    }
  }

  // 获取今日考勤状态
  async getTodayAttendance(): Promise<TodayAttendance> {
    try {
      return await attendanceService.getTodayAttendance()    } catch (error: any) {
      console.error('获取今日考勤状态失败:', error)
      return {
        clock_in_time: null,
        clock_out_time: null,
        work_hours: null,
        status: 'absent',
        is_late: false,
        is_early_leave: false
      }
    }
  }

  // 执行打卡
  async clockIn(location?: string, note?: string) {
    try {
      const data: any = {}
      if (location) data.location = location
      if (note) data.note = note

      // 尝试获取地理位置
      if (navigator.geolocation) {
        const position = await new Promise<GeolocationPosition>((resolve, reject) => {
          navigator.geolocation.getCurrentPosition(resolve, reject, {
            timeout: 5000,
            enableHighAccuracy: true
          })
        })
        
        data.latitude = position.coords.latitude
        data.longitude = position.coords.longitude
        
        if (!location) {
          // 如果没有提供位置信息，可以使用反向地理编码获取地址
          data.location = `纬度: ${position.coords.latitude.toFixed(6)}, 经度: ${position.coords.longitude.toFixed(6)}`
        }
      }

      return await attendanceService.clockIn(data)
    } catch (error: any) {
      console.error('打卡失败:', error)
      throw error
    }
  }

  // 执行下班打卡
  async clockOut(location?: string, note?: string) {
    try {
      const data: any = {}
      if (location) data.location = location
      if (note) data.note = note

      // 尝试获取地理位置
      if (navigator.geolocation) {
        const position = await new Promise<GeolocationPosition>((resolve, reject) => {
          navigator.geolocation.getCurrentPosition(resolve, reject, {
            timeout: 5000,
            enableHighAccuracy: true
          })
        })
        
        data.latitude = position.coords.latitude
        data.longitude = position.coords.longitude
        
        if (!location) {
          data.location = `纬度: ${position.coords.latitude.toFixed(6)}, 经度: ${position.coords.longitude.toFixed(6)}`
        }
      }

      return await attendanceService.clockOut(data)
    } catch (error: any) {
      console.error('下班打卡失败:', error)
      throw error
    }
  }
}

export default new DashboardService()
