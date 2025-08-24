import api from '@/utils/api'
import attendanceService from './attendance'
import leaveService from './leave'
import performanceService from './performance'

export interface ManagerDashboardStats {
  totalEmployees: number
  attendanceRate: number
  pendingLeaves: number
  avgPerformance: number
}

export interface PendingLeave {
  id: number
  employeeName: string
  leaveType: string
  startDate: string
  days: number
  reason: string
}

export interface AbnormalAttendance {
  id: number
  employeeName: string
  date: string
  type: string
  description: string
}

export interface AttendanceTrend {
  week: string
  attendanceRate: number
  lateRate: number
  earlyLeaveRate: number
}

export interface PerformanceDistribution {
  name: string
  value: number
}

class ManagerDashboardService {
  // 获取部门概览统计
  async getDepartmentStats(): Promise<ManagerDashboardStats> {
    try {
      // 并行获取各项统计数据
      const [attendanceStats, leaveStats, performanceStats] = await Promise.all([
        this.getAttendanceOverview(),
        this.getLeaveOverview(),
        this.getPerformanceOverview()
      ])

      return {
        totalEmployees: attendanceStats.totalEmployees,
        attendanceRate: attendanceStats.attendanceRate,
        pendingLeaves: leaveStats.pendingCount,
        avgPerformance: performanceStats.avgScore
      }
    } catch (error: any) {
      console.error('获取部门统计失败:', error)
      // 返回默认数据
      return {
        totalEmployees: 0,
        attendanceRate: 0,
        pendingLeaves: 0,
        avgPerformance: 0
      }
    }
  }

  // 获取考勤概览
  private async getAttendanceOverview() {
    try {
      const response = await api.get('/attendance/statistics/', {
        params: {
          year: new Date().getFullYear(),
          month: new Date().getMonth() + 1
        }
      })
      
      const stats = response.data.statistics
      const totalEmployees = Object.keys(stats).length
      
      // 计算平均出勤率
      let totalAttendanceRate = 0
      for (const employeeId in stats) {
        const employeeStats = stats[employeeId]
        const totalDays = employeeStats.summary.total_days
        const attendedDays = employeeStats.summary.attended_days
        const attendanceRate = totalDays > 0 ? (attendedDays / totalDays * 100) : 0
        totalAttendanceRate += attendanceRate
      }
      
      const avgAttendanceRate = totalEmployees > 0 ? (totalAttendanceRate / totalEmployees) : 0

      return {
        totalEmployees,
        attendanceRate: Math.round(avgAttendanceRate * 10) / 10
      }
    } catch (error: any) {
      console.error('获取考勤概览失败:', error)
      return {
        totalEmployees: 0,
        attendanceRate: 0
      }
    }
  }

  // 获取请假概览
  private async getLeaveOverview() {
    try {
      const pendingApplications = await leaveService.getAllApplications({ status: 'pending' })
      
      return {
        pendingCount: pendingApplications.length
      }
    } catch (error: any) {
      console.error('获取请假概览失败:', error)
      return {
        pendingCount: 0
      }
    }
  }

  // 获取绩效概览
  private async getPerformanceOverview() {
    try {
      const stats = await performanceService.getStatistics()
      
      return {
        avgScore: stats.average_score || 0
      }
    } catch (error: any) {
      console.error('获取绩效概览失败:', error)
      return {
        avgScore: 0
      }
    }
  }

  // 获取待审批请假列表
  async getPendingLeaves(): Promise<PendingLeave[]> {
    try {
      const applications = await leaveService.getAllApplications({ status: 'pending' })
      
      return applications.slice(0, 5).map(app => ({
        id: app.id,
        employeeName: app.user_name,
        leaveType: this.getLeaveTypeDisplayName(app.leave_type_name),
        startDate: app.start_date,
        days: app.days,
        reason: app.reason
      }))
    } catch (error: any) {
      console.error('获取待审批请假列表失败:', error)
      return []
    }
  }

  // 获取异常考勤记录
  async getAbnormalAttendance(): Promise<AbnormalAttendance[]> {
    try {
      const response = await api.get('/attendance/statistics/', {
        params: {
          year: new Date().getFullYear(),
          month: new Date().getMonth() + 1
        }
      })
      
      const stats = response.data.statistics
      const abnormalRecords: AbnormalAttendance[] = []
      
      // 提取异常考勤记录
      for (const employeeId in stats) {
        const employeeData = stats[employeeId]
        const dailyRecords = employeeData.daily_records || []
        
        dailyRecords.forEach((record: any) => {
          if (record.status === 'late' || record.status === 'early') {
            abnormalRecords.push({
              id: abnormalRecords.length + 1,
              employeeName: employeeData.name,
              date: record.date,
              type: record.status === 'late' ? '迟到' : '早退',
              description: this.getAbnormalDescription(record)
            })
          }
        })
      }
      
      // 返回最近的5条记录
      return abnormalRecords.slice(0, 5)
    } catch (error: any) {
      console.error('获取异常考勤记录失败:', error)
      return []
    }
  }

  // 获取考勤趋势数据
  async getAttendanceTrend(): Promise<AttendanceTrend[]> {
    try {
      // 获取最近4周的数据
      const trends: AttendanceTrend[] = []
      
      for (let i = 3; i >= 0; i--) {
        const weekStart = new Date()
        weekStart.setDate(weekStart.getDate() - (i * 7))
        
        // 模拟周度数据 - 实际应该调用API获取
        trends.push({
          week: `第${4-i}周`,
          attendanceRate: 95 + Math.random() * 5,
          lateRate: 2 + Math.random() * 3,
          earlyLeaveRate: 1 + Math.random() * 2
        })
      }
      
      return trends
    } catch (error: any) {
      console.error('获取考勤趋势失败:', error)
      return []
    }
  }

  // 获取绩效分布数据
  async getPerformanceDistribution(): Promise<PerformanceDistribution[]> {
    try {
      const stats = await performanceService.getStatistics()
      
      if (stats.rating_distribution) {
        return Object.entries(stats.rating_distribution).map(([name, value]) => ({
          name: name,
          value: value as number
        }))
      }
      
      // 返回默认分布
      return [
        { name: '优秀(90-100)', value: 8 },
        { name: '良好(80-89)', value: 12 },
        { name: '合格(70-79)', value: 4 },
        { name: '待改进(<70)', value: 1 }
      ]
    } catch (error: any) {
      console.error('获取绩效分布失败:', error)
      return []
    }
  }

  // 审批请假申请
  async approveLeave(id: number, note: string = ''): Promise<void> {
    await leaveService.approveApplication(id, {
      status: 'approved',
      approval_note: note
    })
  }

  // 拒绝请假申请
  async rejectLeave(id: number, note: string): Promise<void> {
    await leaveService.approveApplication(id, {
      status: 'rejected',
      approval_note: note
    })
  }

  // 获取请假类型显示名称
  private getLeaveTypeDisplayName(typeName: string): string {
    const typeMap: Record<string, string> = {
      '年假': '年假',
      '病假': '病假',
      '事假': '事假',
      '调休': '调休',
      '产假': '产假',
      '陪产假': '陪产假'
    }
    
    for (const [key, value] of Object.entries(typeMap)) {
      if (typeName.includes(key)) {
        return value
      }
    }
    return '其他'
  }

  // 获取异常考勤描述
  private getAbnormalDescription(record: any): string {
    if (record.status === 'late') {
      const clockIn = record.clock_in
      if (clockIn) {
        const time = new Date(`2000-01-01 ${clockIn}`)
        const standardTime = new Date('2000-01-01 09:00:00')
        const diff = Math.round((time.getTime() - standardTime.getTime()) / (1000 * 60))
        return `迟到${diff}分钟`
      }
      return '迟到'
    } else if (record.status === 'early') {
      return '早退'
    }
    return record.note || '异常考勤'
  }
}

export default new ManagerDashboardService()
