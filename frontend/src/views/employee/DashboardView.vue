<template>
  <div class="dashboard">
    <el-row :gutter="20" class="dashboard-header">
      <el-col :span="24">
        <el-card class="welcome-card">
          <div class="welcome-content">
            <h2>欢迎回来，{{ userStore.user?.first_name || '员工' }}！</h2>
            <p class="welcome-text">今天是 {{ currentDate }}，祝您工作愉快！</p>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" class="dashboard-stats">
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-icon attendance">
              <el-icon><Clock /></el-icon>
            </div>
            <div class="stat-text">
              <h3>{{ attendanceStats.thisMonth }}</h3>
              <p>本月出勤天数</p>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-icon leave">
              <el-icon><Calendar /></el-icon>
            </div>
            <div class="stat-text">
              <h3>{{ leaveStats.remaining }}</h3>
              <p>剩余年假天数</p>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-icon salary">
              <el-icon><Money /></el-icon>
            </div>
            <div class="stat-text">
              <h3>¥{{ salaryStats.lastMonth }}</h3>
              <p>上月薪资</p>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-icon performance">
              <el-icon><TrendCharts /></el-icon>
            </div>
            <div class="stat-text">
              <h3>{{ performanceStats.lastScore }}</h3>
              <p>最近绩效得分</p>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" class="dashboard-content">
      <el-col :span="12">
        <el-card>          <template #header>
            <div class="card-header">
              <span>今日考勤</span>
              <div class="clock-buttons">                <el-button 
                  type="primary" 
                  @click="handleClockIn" 
                  :disabled="!!todayAttendance.clock_in_time"
                  :loading="loading"
                  size="small"
                >
                  {{ todayAttendance.clock_in_time ? '已打卡' : '打卡上班' }}
                </el-button>
                <el-button 
                  type="success" 
                  @click="handleClockOut" 
                  :disabled="!todayAttendance.clock_in_time || !!todayAttendance.clock_out_time"
                  :loading="loading"
                  size="small"
                  style="margin-left: 10px;"
                >
                  {{ todayAttendance.clock_out_time ? '已下班' : '打卡下班' }}
                </el-button>
              </div>
            </div>
          </template>          <div class="attendance-info">
            <div class="attendance-item" v-if="todayAttendance.clock_in_time">
              <span class="label">上班时间：</span>
              <span class="value">{{ todayAttendance.clock_in_time }}</span>
            </div>
            <div class="attendance-item" v-if="todayAttendance.clock_out_time">
              <span class="label">下班时间：</span>
              <span class="value">{{ todayAttendance.clock_out_time }}</span>
            </div>
            <div class="attendance-item" v-if="!todayAttendance.clock_in_time">
              <span class="tip">请点击打卡按钮进行上班打卡</span>
            </div>
          </div>
        </el-card>
      </el-col>
      
      <el-col :span="12">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>最近请假申请</span>
              <el-button type="primary" @click="$router.push('/employee/leave')">申请请假</el-button>
            </div>
          </template>
          <div class="leave-list">            <div class="leave-item" v-for="leave in recentLeaves" :key="leave.id">
              <div class="leave-info">
                <span class="leave-type">{{ leave.leave_type_name }}</span>
                <span class="leave-date">{{ leave.start_date }} - {{ leave.end_date }}</span>
              </div>
              <el-tag :type="getLeaveStatusType(leave.status)">{{ getLeaveStatusText(leave.status) }}</el-tag>
            </div>
            <div v-if="recentLeaves.length === 0" class="no-data">
              暂无请假记录
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" class="dashboard-bottom">
      <el-col :span="24">
        <el-card>
          <template #header>
            <span>快捷操作</span>
          </template>
          <div class="quick-actions">
            <el-button-group>
              <el-button @click="$router.push('/employee/attendance')">
                <el-icon><Clock /></el-icon>
                考勤管理
              </el-button>
              <el-button @click="$router.push('/employee/leave')">
                <el-icon><Calendar /></el-icon>
                请假申请
              </el-button>
              <el-button @click="$router.push('/employee/salary')">
                <el-icon><Money /></el-icon>
                薪资查询
              </el-button>
              <el-button @click="$router.push('/employee/performance')">
                <el-icon><TrendCharts /></el-icon>
                绩效查询
              </el-button>
              <el-button @click="$router.push('/employee/profile')">
                <el-icon><User /></el-icon>
                个人资料
              </el-button>
            </el-button-group>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, computed } from 'vue'
import { useAuthStore } from '@/stores/counter'
import { ElMessage } from 'element-plus'
import { Clock, Calendar, Money, TrendCharts, User } from '@element-plus/icons-vue'
import dashboardService, { type DashboardStats, type TodayAttendance } from '@/services/dashboard'
import leaveService, { type LeaveApplication } from '@/services/leave'

// 类型定义
interface LeaveRecord {
  id: number
  leave_type_name: string
  start_date: string
  end_date: string
  status: string
}

const userStore = useAuthStore()

const currentDate = computed(() => {
  return new Date().toLocaleDateString('zh-CN', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
    weekday: 'long'
  })
})

const attendanceStats = reactive({
  thisMonth: 0
})

const leaveStats = reactive({
  remaining: 0
})

const salaryStats = reactive({
  lastMonth: 0
})

const performanceStats = reactive({
  lastScore: 0
})

const todayAttendance = reactive<TodayAttendance>({
  clock_in_time: null,
  clock_out_time: null,
  work_hours: null,
  status: 'absent',
  is_late: false,
  is_early_leave: false
})

const recentLeaves = ref<LeaveRecord[]>([])
const loading = ref(false)

const handleClockIn = async () => {
  if (todayAttendance.clock_in_time) {
    ElMessage.warning('今天已经打过上班卡了')
    return
  }

  loading.value = true
  try {
    const result = await dashboardService.clockIn()
    if (result.success) {
      ElMessage.success(result.message || '打卡成功！')
      // 刷新今日考勤状态
      await loadTodayAttendance()
      // 刷新统计数据
      await loadDashboardData()
    } else {
      ElMessage.error(result.message || '打卡失败')
    }
  } catch (error: any) {
    console.error('打卡失败:', error)
    const errorMessage = error.response?.data?.message || 
                        error.response?.data?.error || 
                        error.message || 
                        '打卡失败，请稍后重试'
    ElMessage.error(errorMessage)
  } finally {
    loading.value = false
  }
}

const handleClockOut = async () => {
  if (todayAttendance.clock_out_time) {
    ElMessage.warning('今天已经打过下班卡了')
    return
  }

  if (!todayAttendance.clock_in_time) {
    ElMessage.warning('请先打上班卡')
    return
  }

  loading.value = true
  try {
    const result = await dashboardService.clockOut()
    if (result.success) {
      ElMessage.success(result.message || '下班打卡成功！')
      // 刷新今日考勤状态
      await loadTodayAttendance()
    } else {
      ElMessage.error(result.message || '下班打卡失败')
    }
  } catch (error: any) {
    console.error('下班打卡失败:', error)
    const errorMessage = error.response?.data?.message || 
                        error.response?.data?.error || 
                        error.message || 
                        '下班打卡失败，请稍后重试'
    ElMessage.error(errorMessage)
  } finally {
    loading.value = false
  }
}

const getLeaveStatusType = (status: string) => {
  switch (status) {
    case 'approved':
      return 'success'
    case 'pending':
      return 'warning'
    case 'rejected':
      return 'danger'
    case 'cancelled':
      return 'info'
    default:
      return 'info'
  }
}

const getLeaveStatusText = (status: string) => {
  switch (status) {
    case 'approved':
      return '已批准'
    case 'pending':
      return '待审批'
    case 'rejected':
      return '已拒绝'
    case 'cancelled':
      return '已取消'
    default:
      return status
  }
}

const loadTodayAttendance = async () => {
  try {
    const attendance = await dashboardService.getTodayAttendance()
    Object.assign(todayAttendance, attendance)
  } catch (error: any) {
    console.error('加载今日考勤状态失败:', error)
  }
}

const loadRecentLeaves = async () => {
  try {
    const leaves = await leaveService.getRecentApplications(5)
    recentLeaves.value = leaves.map(leave => ({
      id: leave.id,
      leave_type_name: leave.leave_type_name,
      start_date: leave.start_date,
      end_date: leave.end_date,
      status: leave.status
    }))
  } catch (error: any) {
    console.error('加载最近请假记录失败:', error)
  }
}

const loadDashboardData = async () => {
  try {
    const stats = await dashboardService.getDashboardStats()
    
    attendanceStats.thisMonth = stats.attendance.work_days
    leaveStats.remaining = stats.leave.remaining
    salaryStats.lastMonth = stats.salary.lastMonth
    performanceStats.lastScore = stats.performance.lastScore
  } catch (error: any) {
    console.error('加载仪表板数据失败:', error)
  }
}

onMounted(async () => {
  await Promise.all([
    loadDashboardData(),
    loadTodayAttendance(),
    loadRecentLeaves()
  ])
})
</script>

<style scoped>
.dashboard {
  padding: 20px;
}

.dashboard-header {
  margin-bottom: 24px;
}

.welcome-card {
  background: linear-gradient(135deg, #4f6ef7 0%, #7c3aed 100%);
  color: white;
  border: none !important;
}

.welcome-card :deep(.el-card__body) {
  padding: 32px 36px;
}

.welcome-card :deep(.el-card__header) {
  display: none;
}

.welcome-content h2 {
  margin: 0 0 8px 0;
  font-size: 26px;
  font-weight: 700;
  letter-spacing: -0.3px;
}

.welcome-text {
  margin: 0;
  font-size: 15px;
  opacity: 0.85;
}

.dashboard-stats {
  margin-bottom: 24px;
}

.stat-card {
  height: 110px;
  border: none !important;
  transition: transform var(--hr-transition-slow), box-shadow var(--hr-transition-slow) !important;
}

.stat-card:hover {
  transform: translateY(-3px);
  box-shadow: var(--hr-shadow-card-hover) !important;
}

.stat-content {
  display: flex;
  align-items: center;
  height: 100%;
}

.stat-icon {
  width: 52px;
  height: 52px;
  border-radius: var(--hr-radius-md);
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 16px;
  font-size: 22px;
  color: white;
}

.stat-icon.attendance {
  background: linear-gradient(135deg, #4f6ef7 0%, #6366f1 100%);
}

.stat-icon.leave {
  background: linear-gradient(135deg, #ec4899 0%, #f43f5e 100%);
}

.stat-icon.salary {
  background: linear-gradient(135deg, #06b6d4 0%, #3b82f6 100%);
}

.stat-icon.performance {
  background: linear-gradient(135deg, #22c55e 0%, #10b981 100%);
}

.stat-text h3 {
  margin: 0 0 4px 0;
  font-size: 24px;
  font-weight: 700;
  color: var(--hr-gray-800);
}

.stat-text p {
  margin: 0;
  font-size: 13px;
  color: var(--hr-gray-500);
}

.dashboard-content {
  margin-bottom: 24px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-weight: 600;
  color: var(--hr-gray-800);
}

.clock-buttons {
  display: flex;
  align-items: center;
  gap: 8px;
}

.attendance-info {
  min-height: 80px;
}

.attendance-item {
  margin-bottom: 12px;
  display: flex;
  align-items: center;
}

.attendance-item .label {
  color: var(--hr-gray-500);
  margin-right: 8px;
  font-size: 14px;
}

.attendance-item .value {
  color: var(--hr-gray-800);
  font-weight: 600;
  font-size: 15px;
}

.attendance-item .tip {
  color: var(--hr-gray-400);
  font-style: italic;
  font-size: 14px;
}

.leave-list {
  min-height: 120px;
}

.leave-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 0;
  border-bottom: 1px solid var(--hr-gray-100);
  transition: background var(--hr-transition-fast);
}

.leave-item:last-child {
  border-bottom: none;
}

.leave-item:hover {
  background: var(--hr-gray-50);
  margin: 0 -12px;
  padding: 12px;
  border-radius: var(--hr-radius-sm);
}

.leave-info {
  display: flex;
  flex-direction: column;
}

.leave-type {
  font-weight: 600;
  margin-bottom: 4px;
  color: var(--hr-gray-800);
  font-size: 14px;
}

.leave-date {
  font-size: 12px;
  color: var(--hr-gray-400);
}

.no-data {
  text-align: center;
  color: var(--hr-gray-400);
  padding: 40px 0;
  font-size: 14px;
}

.quick-actions {
  text-align: center;
}

.quick-actions .el-button {
  margin: 0 8px 8px 0;
}
</style>
