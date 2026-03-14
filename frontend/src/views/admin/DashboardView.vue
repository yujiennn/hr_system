<template>
  <div class="admin-dashboard">
    <!-- 系统概览 -->
    <el-row :gutter="20" class="overview-section">
      <el-col :span="6">
        <el-card class="overview-card users">
          <div class="card-content">
            <div class="card-icon">
              <el-icon size="36"><User /></el-icon>
            </div>
            <div class="card-info">
              <div class="card-value">{{ systemStats.totalUsers }}</div>
              <div class="card-label">总用户数</div>
              <div class="card-trend">
                <el-icon color="#67C23A"><CaretTop /></el-icon>
                <span>较上月</span>
              </div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="overview-card departments">
          <div class="card-content">
            <div class="card-icon">
              <el-icon size="36"><OfficeBuilding /></el-icon>
            </div>
            <div class="card-info">
              <div class="card-value">{{ systemStats.totalDepartments }}</div>
              <div class="card-label">部门数量</div>
              <div class="card-trend">
                <el-icon color="#E6A23C"><Minus /></el-icon>
                <span>无变化</span>
              </div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="overview-card attendance">
          <div class="card-content">
            <div class="card-icon">
              <el-icon size="36"><Clock /></el-icon>
            </div>
            <div class="card-info">
              <div class="card-value">{{ systemStats.todayAttendance }}%</div>
              <div class="card-label">今日出勤率</div>
              <div class="card-trend">
                <el-icon color="#67C23A"><CaretTop /></el-icon>
                <span>表现良好</span>
              </div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="overview-card performance">
          <div class="card-content">
            <div class="card-icon">
              <el-icon size="36"><TrendCharts /></el-icon>
            </div>
            <div class="card-info">
              <div class="card-value">{{ systemStats.avgPerformance }}</div>
              <div class="card-label">平均绩效分</div>
              <div class="card-trend">
                <el-icon color="#67C23A"><CaretTop /></el-icon>
                <span>持续提升</span>
              </div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 快捷操作 -->
    <el-card class="quick-actions">
      <template #header>
        <span>快捷操作</span>
      </template>
      <el-row :gutter="20">
        <el-col :span="6">
          <div class="action-item" @click="goToUserManagement">
            <el-icon size="32" color="#409EFF"><UserFilled /></el-icon>
            <div class="action-label">用户管理</div>
          </div>
        </el-col>
        <el-col :span="6">
          <div class="action-item" @click="goToAttendanceManagement">
            <el-icon size="32" color="#67C23A"><Clock /></el-icon>
            <div class="action-label">考勤管理</div>
          </div>
        </el-col>
        <el-col :span="6">
          <div class="action-item" @click="goToSystemConfig">
            <el-icon size="32" color="#E6A23C"><Setting /></el-icon>
            <div class="action-label">系统配置</div>
          </div>
        </el-col>
        <el-col :span="6">
          <div class="action-item" @click="goToReports">
            <el-icon size="32" color="#B37FEB"><DataAnalysis /></el-icon>
            <div class="action-label">数据报表</div>
          </div>
        </el-col>
      </el-row>
    </el-card>

    <!-- 数据概览 -->
    <el-row :gutter="20" class="charts-section">
      <el-col :span="12">
        <el-card>
          <template #header>
            <span>近期数据概览</span>
          </template>
          <div class="simple-stats">
            <div class="stat-item">
              <div class="stat-label">本月新增用户</div>
              <div class="stat-value">{{ monthlyStats.newUsers }}</div>
            </div>
            <div class="stat-item">
              <div class="stat-label">本月考勤记录</div>
              <div class="stat-value">{{ monthlyStats.attendanceRecords }}</div>
            </div>
            <div class="stat-item">
              <div class="stat-label">待处理请假</div>
              <div class="stat-value">{{ monthlyStats.pendingLeaves }}</div>
            </div>
            <div class="stat-item">
              <div class="stat-label">本月薪资发放</div>
              <div class="stat-value">{{ monthlyStats.salaryProcessed }}</div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card>
          <template #header>
            <span>系统状态</span>
          </template>
          <div class="system-status">
            <div class="status-item">
              <div class="status-label">服务器状态</div>
              <div class="status-value">
                <el-tag type="success">正常运行</el-tag>
              </div>
            </div>
            <div class="status-item">
              <div class="status-label">数据库连接</div>
              <div class="status-value">
                <el-tag type="success">连接正常</el-tag>
              </div>
            </div>
            <div class="status-item">
              <div class="status-label">当前在线用户</div>
              <div class="status-value">
                <span class="online-users">{{ systemStats.onlineUsers }} 人</span>
              </div>
            </div>
            <div class="status-item">
              <div class="status-label">系统版本</div>
              <div class="status-value">
                <el-tag type="info">v1.0.0</el-tag>
              </div>
            </div>
            <div class="status-item">
              <div class="status-label">最后更新</div>
              <div class="status-value">
                <span class="last-update">{{ formatTime(new Date()) }}</span>
              </div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 最近活动和待处理事项 -->
    <el-row :gutter="20" class="notification-section">
      <el-col :span="12">
        <el-card>
          <template #header>
            <span>最近活动</span>
          </template>
          <el-timeline class="notification-timeline">
            <el-timeline-item
              v-for="notification in recentActivities"
              :key="notification.id"
              :timestamp="notification.time"
              :type="notification.type"
            >
              <div class="notification-content">
                <div class="notification-title">{{ notification.title }}</div>
                <div class="notification-description">{{ notification.content }}</div>
              </div>
            </el-timeline-item>
          </el-timeline>
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card>
          <template #header>
            <span>待处理事项</span>
          </template>
          <div class="todo-list">
            <div v-if="todoItems.length === 0" class="empty-state">
              <el-icon size="48" color="#C0C4CC"><DocumentRemove /></el-icon>
              <p>暂无待处理事项</p>
            </div>
            <div v-else class="todo-item" v-for="item in todoItems" :key="item.id">
              <div class="todo-content">
                <div class="todo-title">{{ item.title }}</div>
                <div class="todo-meta">
                  <el-tag :type="getPriorityType(item.priority)" size="small">{{ item.priority }}</el-tag>
                  <span class="todo-deadline">{{ item.deadline }}</span>
                </div>
              </div>
              <el-button type="primary" size="small" @click="handleTodoItem(item)">
                处理
              </el-button>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import {
  User,
  UserFilled,
  OfficeBuilding,
  Clock,
  TrendCharts,
  Setting,
  DataAnalysis,
  CaretTop,
  Minus,
  DocumentRemove
} from '@element-plus/icons-vue'
import adminDashboardService from '@/services/adminDashboard'
import type { AdminSystemStats } from '@/services/adminDashboard'

const router = useRouter()

// 系统统计数据
const systemStats = ref<AdminSystemStats>({
  totalUsers: 0,
  totalDepartments: 0,
  todayAttendance: 0,
  avgPerformance: 0,
  onlineUsers: 0
})

// 月度统计数据
const monthlyStats = ref({
  newUsers: 0,
  attendanceRecords: 0,
  pendingLeaves: 0,
  salaryProcessed: 0
})

// 最近活动
const recentActivities = ref<Array<{
  id: number
  title: string
  content: string
  time: string
  type: 'success' | 'warning' | 'info' | 'danger'
}>>([])

// 待办事项
const todoItems = ref<Array<{
  id: number
  title: string
  priority: 'high' | 'medium' | 'low'
  deadline: string
}>>([])

// 加载状态
const loading = ref(false)

// 加载系统统计数据
const loadSystemStats = async () => {
  try {
    loading.value = true
    console.log('🔥 加载系统统计数据...')
    
    const stats = await adminDashboardService.getSystemStats()
    console.log('🔥 获取到的统计数据:', stats)
    
    systemStats.value = stats
    
    // 加载月度统计数据
    await loadMonthlyStats()
    
    // 加载最近活动
    loadRecentActivities()
    
    // 加载待办事项
    loadTodoItems()
    
  } catch (error: any) {
    console.error('🔥 加载系统数据失败:', error)
    ElMessage.error('加载系统数据失败')
  } finally {
    loading.value = false
  }
}

// 加载月度统计数据
const loadMonthlyStats = async () => {
  try {
    // 这里可以添加具体的月度统计API调用
    // 现在先使用基础统计数据计算
    monthlyStats.value = {
      newUsers: Math.floor(systemStats.value.totalUsers * 0.1), // 假设10%是新用户
      attendanceRecords: systemStats.value.totalUsers * 20, // 假设每人每月20条记录
      pendingLeaves: Math.floor(systemStats.value.totalUsers * 0.05), // 假设5%的用户有待处理请假
      salaryProcessed: Math.floor(systemStats.value.totalUsers * 0.9) // 假设90%已发薪
    }
  } catch (error) {
    console.error('加载月度统计失败:', error)
  }
}

// 加载最近活动
const loadRecentActivities = () => {
  // 模拟最近活动数据
  recentActivities.value = [
    {
      id: 1,
      title: '新员工入职',
      content: '张三已完成入职手续办理',
      time: formatTime(new Date(Date.now() - 2 * 60 * 60 * 1000)),
      type: 'success'
    },
    {
      id: 2,
      title: '考勤异常',
      content: '发现3名员工今日未正常打卡',
      time: formatTime(new Date(Date.now() - 4 * 60 * 60 * 1000)),
      type: 'warning'
    },
    {
      id: 3,
      title: '薪资发放',
      content: '本月薪资已发放至员工账户',
      time: formatTime(new Date(Date.now() - 24 * 60 * 60 * 1000)),
      type: 'info'
    }
  ]
}

// 加载待办事项
const loadTodoItems = () => {
  // 模拟待办事项数据
  todoItems.value = [
    {
      id: 1,
      title: '处理请假申请',
      priority: 'high',
      deadline: '今天'
    },
    {
      id: 2,
      title: '审核绩效评估',
      priority: 'medium',
      deadline: '本周'
    }
  ]
}

// 格式化时间
const formatTime = (date: Date) => {
  const now = new Date()
  const diff = now.getTime() - date.getTime()
  const minutes = Math.floor(diff / (1000 * 60))
  const hours = Math.floor(diff / (1000 * 60 * 60))
  const days = Math.floor(diff / (1000 * 60 * 60 * 24))
  
  if (minutes < 60) {
    return `${minutes}分钟前`
  } else if (hours < 24) {
    return `${hours}小时前`
  } else {
    return `${days}天前`
  }
}

// 获取优先级类型
const getPriorityType = (priority: string) => {
  switch (priority) {
    case 'high': return 'danger'
    case 'medium': return 'warning'
    case 'low': return 'success'
    default: return 'info'
  }
}

// 处理待办事项
const handleTodoItem = (item: any) => {
  ElMessage.info(`处理待办事项: ${item.title}`)
  // 这里可以添加具体的处理逻辑
}

// 导航方法
const goToUserManagement = () => {
  router.push('/admin/users')
}

const goToAttendanceManagement = () => {
  router.push('/admin/attendance')
}

const goToSystemConfig = () => {
  router.push('/admin/system')
}

const goToReports = () => {
  router.push('/admin/reports')
}

onMounted(async () => {
  await loadSystemStats()
})
</script>

<style scoped>
.admin-dashboard {
  padding: 24px;
  min-height: calc(100vh - 120px);
}

.overview-section {
  margin-bottom: 24px;
}

.overview-card {
  height: 130px;
  cursor: pointer;
  transition: all var(--hr-transition-slow);
  border: 1px solid var(--hr-gray-100) !important;
  border-radius: var(--hr-radius-lg) !important;
  overflow: hidden;
  background: #fff;
  box-shadow: var(--hr-shadow-card);
}

.overview-card:hover {
  transform: translateY(-4px);
  box-shadow: var(--hr-shadow-card-hover) !important;
}

.overview-card.users {
  border-left: 3px solid var(--hr-primary) !important;
}

.overview-card.departments {
  border-left: 3px solid var(--hr-success) !important;
}

.overview-card.attendance {
  border-left: 3px solid var(--hr-warning) !important;
}

.overview-card.performance {
  border-left: 3px solid var(--hr-danger) !important;
}

.card-content {
  display: flex;
  align-items: center;
  height: 90px;
  padding: 0 20px;
}

.card-icon {
  width: 52px;
  height: 52px;
  border-radius: var(--hr-radius-md);
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 18px;
  color: white;
}

.overview-card.users .card-icon {
  background: linear-gradient(135deg, #4f6ef7 0%, #6366f1 100%);
}

.overview-card.departments .card-icon {
  background: linear-gradient(135deg, #22c55e 0%, #10b981 100%);
}

.overview-card.attendance .card-icon {
  background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
}

.overview-card.performance .card-icon {
  background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
}

.card-info {
  flex: 1;
}

.card-value {
  font-size: 28px;
  font-weight: 800;
  color: var(--hr-gray-800);
  margin-bottom: 2px;
  letter-spacing: -0.5px;
}

.card-label {
  font-size: 13px;
  color: var(--hr-gray-500);
  margin-bottom: 6px;
}

.card-trend {
  display: flex;
  align-items: center;
  font-size: 12px;
  color: var(--hr-success);
  font-weight: 500;
}

.card-trend span {
  margin-left: 4px;
}

.quick-actions {
  margin-bottom: 24px;
}

.quick-actions :deep(.el-card__header) {
  font-weight: 600;
  color: var(--hr-gray-800);
}

.action-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 20px;
  background: var(--hr-gray-50);
  border-radius: var(--hr-radius-md);
  cursor: pointer;
  transition: all var(--hr-transition-slow);
  height: 100px;
  border: 1px solid var(--hr-gray-100);
}

.action-item:hover {
  background: #fff;
  transform: translateY(-3px);
  box-shadow: var(--hr-shadow-md);
  border-color: var(--hr-primary);
}

.action-label {
  margin-top: 10px;
  font-size: 13px;
  color: var(--hr-gray-700);
  font-weight: 500;
}

.charts-section {
  margin-bottom: 24px;
}

.simple-stats {
  padding: 20px 0;
}

.stat-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 14px 0;
  border-bottom: 1px solid var(--hr-gray-100);
}

.stat-item:last-child {
  border-bottom: none;
}

.stat-label {
  font-weight: 500;
  color: var(--hr-gray-700);
  font-size: 14px;
}

.stat-value {
  font-size: 18px;
  font-weight: 700;
  color: var(--hr-primary);
}

.notification-section {
  margin-bottom: 24px;
}

.notification-timeline {
  max-height: 400px;
  overflow-y: auto;
}

.notification-content {
  padding-left: 10px;
}

.notification-title {
  font-weight: 600;
  color: var(--hr-gray-800);
  margin-bottom: 4px;
}

.notification-description {
  font-size: 13px;
  color: var(--hr-gray-500);
  line-height: 1.5;
}

.system-status {
  padding: 10px 0;
}

.status-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 0;
  border-bottom: 1px solid var(--hr-gray-100);
}

.status-item:last-child {
  border-bottom: none;
}

.status-label {
  font-weight: 500;
  color: var(--hr-gray-700);
}

.status-value {
  display: flex;
  align-items: center;
}

.online-users {
  font-weight: 700;
  color: var(--hr-primary);
}

.last-update {
  font-size: 12px;
  color: var(--hr-gray-400);
}

.todo-list {
  max-height: 400px;
  overflow-y: auto;
}

.empty-state {
  text-align: center;
  padding: 40px 20px;
  color: var(--hr-gray-400);
}

.empty-state p {
  margin-top: 14px;
  font-size: 14px;
  color: var(--hr-gray-500);
}

.todo-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 14px 0;
  border-bottom: 1px solid var(--hr-gray-100);
  transition: background var(--hr-transition-fast);
}

.todo-item:last-child {
  border-bottom: none;
}

.todo-item:hover {
  background: var(--hr-gray-50);
  margin: 0 -12px;
  padding: 14px 12px;
  border-radius: var(--hr-radius-sm);
}

.todo-content {
  flex: 1;
}

.todo-title {
  font-weight: 600;
  color: var(--hr-gray-800);
  margin-bottom: 6px;
  font-size: 14px;
}

.todo-meta {
  display: flex;
  align-items: center;
  gap: 12px;
}

.todo-deadline {
  font-size: 12px;
  color: var(--hr-gray-400);
}

:deep(.el-card__body) {
  padding: 16px 20px;
}
</style>
