<template>
  <div class="manager-dashboard">
    <!-- 统计卡片 -->
    <el-row :gutter="20" class="stats-row">
      <el-col :span="6">
        <el-card class="stats-card">
          <div class="stats-content">
            <div class="stats-icon">
              <el-icon color="#409EFF" size="32"><User /></el-icon>
            </div>
            <div class="stats-info">
              <div class="stats-value">{{ departmentStats.totalEmployees }}</div>
              <div class="stats-label">部门总人数</div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stats-card">
          <div class="stats-content">
            <div class="stats-icon">
              <el-icon color="#67C23A" size="32"><CircleCheck /></el-icon>
            </div>
            <div class="stats-info">
              <div class="stats-value">{{ departmentStats.attendanceRate }}%</div>
              <div class="stats-label">今日出勤率</div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stats-card">
          <div class="stats-content">
            <div class="stats-icon">
              <el-icon color="#E6A23C" size="32"><Clock /></el-icon>
            </div>
            <div class="stats-info">
              <div class="stats-value">{{ departmentStats.pendingLeaves }}</div>
              <div class="stats-label">待审批请假</div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stats-card">
          <div class="stats-content">
            <div class="stats-icon">
              <el-icon color="#F56C6C" size="32"><TrendCharts /></el-icon>
            </div>
            <div class="stats-info">
              <div class="stats-value">{{ departmentStats.avgPerformance }}</div>
              <div class="stats-label">平均绩效分</div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 图表区域 -->
    <el-row :gutter="20" class="charts-row">
      <el-col :span="12">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>部门考勤趋势</span>
              <el-date-picker
                v-model="chartDateRange"
                type="monthrange"
                range-separator="至"
                start-placeholder="开始月份"
                end-placeholder="结束月份"
                size="small"
                @change="updateAttendanceChart"
              />
            </div>
          </template>
          <div ref="attendanceChart" class="chart-container"></div>
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card>
          <template #header>
            <span>绩效分布</span>
          </template>
          <div ref="performanceChart" class="chart-container"></div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 待处理事项 -->
    <el-row :gutter="20" class="pending-row">
      <el-col :span="12">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>待审批请假申请</span>
              <el-button type="primary" size="small" @click="goToLeaveApproval">查看全部</el-button>
            </div>
          </template>
          <el-table :data="pendingLeaves" stripe>
            <el-table-column prop="employeeName" label="员工姓名" width="100" />
            <el-table-column prop="leaveType" label="请假类型" width="80" />
            <el-table-column prop="startDate" label="开始日期" width="100" />
            <el-table-column prop="days" label="天数" width="60" />
            <el-table-column prop="reason" label="原因" show-overflow-tooltip />
            <el-table-column label="操作" width="120">
              <template #default="{ row }">
                <el-button type="success" size="small" @click="approveLeave(row.id)">通过</el-button>
                <el-button type="danger" size="small" @click="rejectLeave(row.id)">拒绝</el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>异常考勤记录</span>
              <el-button type="primary" size="small" @click="goToAttendanceManagement">查看全部</el-button>
            </div>
          </template>
          <el-table :data="abnormalAttendance" stripe>
            <el-table-column prop="employeeName" label="员工姓名" width="100" />
            <el-table-column prop="date" label="日期" width="100" />
            <el-table-column prop="type" label="异常类型" width="80">
              <template #default="{ row }">
                <el-tag :type="getAbnormalTypeColor(row.type)">{{ row.type }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="description" label="描述" show-overflow-tooltip />
            <el-table-column label="操作" width="80">
              <template #default="{ row }">
                <el-button type="primary" size="small" @click="handleAbnormal(row.id)">处理</el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import * as echarts from 'echarts'
import { ElMessage } from 'element-plus'
import {
  User,
  CircleCheck,
  Clock,
  TrendCharts
} from '@element-plus/icons-vue'
import managerDashboardService from '@/services/managerDashboard'
import type { 
  ManagerDashboardStats, 
  PendingLeave, 
  AbnormalAttendance,
  AttendanceTrend,
  PerformanceDistribution
} from '@/services/managerDashboard'

const router = useRouter()

// 数据定义
const departmentStats = ref<ManagerDashboardStats>({
  totalEmployees: 0,
  attendanceRate: 0,
  pendingLeaves: 0,
  avgPerformance: 0
})

const chartDateRange = ref<[Date, Date]>([
  new Date(new Date().getFullYear(), new Date().getMonth() - 2, 1),
  new Date(new Date().getFullYear(), new Date().getMonth(), 0)
])

const pendingLeaves = ref<PendingLeave[]>([])
const abnormalAttendance = ref<AbnormalAttendance[]>([])
const loading = ref(false)

// 图表引用
const attendanceChart = ref<HTMLElement>()
const performanceChart = ref<HTMLElement>()

// 初始化考勤趋势图表
const initAttendanceChart = async () => {
  if (!attendanceChart.value) return
  
  const chart = echarts.init(attendanceChart.value)
  
  try {
    const trendData = await managerDashboardService.getAttendanceTrend()
    
    const option = {
      tooltip: {
        trigger: 'axis'
      },
      legend: {
        data: ['出勤率', '迟到率', '早退率']
      },      xAxis: {
        type: 'category',
        data: trendData.map(item => item.week)
      },
      yAxis: {
        type: 'value',
        axisLabel: {
          formatter: '{value}%'
        }
      },
      series: [
        {
          name: '出勤率',
          type: 'line',
          data: trendData.map(item => item.attendanceRate),
          smooth: true,
          itemStyle: { color: '#409EFF' }
        },
        {
          name: '迟到率',
          type: 'line',
          data: trendData.map(item => item.lateRate),
          smooth: true,
          itemStyle: { color: '#E6A23C' }
        },
        {
          name: '早退率',
          type: 'line',
          data: trendData.map(item => item.earlyLeaveRate),
          smooth: true,
          itemStyle: { color: '#F56C6C' }
        }
      ]
    }
    
    chart.setOption(option)
  } catch (error: any) {
    console.error('Failed to load attendance trend:', error)
    // 使用默认数据
    const option = {
      tooltip: {
        trigger: 'axis'
      },
      legend: {
        data: ['出勤率', '迟到率', '早退率']
      },
      xAxis: {
        type: 'category',
        data: ['第1周', '第2周', '第3周', '第4周']
      },
      yAxis: {
        type: 'value',
        axisLabel: {
          formatter: '{value}%'
        }
      },
      series: [
        {
          name: '出勤率',
          type: 'line',
          data: [95, 97, 96, 98],
          smooth: true,
          itemStyle: { color: '#409EFF' }
        },
        {
          name: '迟到率',
          type: 'line',
          data: [3, 2, 3, 1],
          smooth: true,
          itemStyle: { color: '#E6A23C' }
        },
        {
          name: '早退率',
          type: 'line',
          data: [2, 1, 1, 1],
          smooth: true,
          itemStyle: { color: '#F56C6C' }
        }
      ]
    }
    chart.setOption(option)
  }
}

// 初始化绩效分布图表
const initPerformanceChart = async () => {
  if (!performanceChart.value) return
  
  const chart = echarts.init(performanceChart.value)
  
  try {
    const distributionData = await managerDashboardService.getPerformanceDistribution()
    
    const option = {
      tooltip: {
        trigger: 'item'
      },
      legend: {
        orient: 'vertical',
        left: 'left'
      },
      series: [
        {
          type: 'pie',
          radius: '50%',
          data: distributionData,
          emphasis: {
            itemStyle: {
              shadowBlur: 10,
              shadowOffsetX: 0,
              shadowColor: 'rgba(0, 0, 0, 0.5)'
            }
          }
        }
      ]
    }
    
    chart.setOption(option)
  } catch (error: any) {
    console.error('Failed to load performance distribution:', error)
    // 使用默认数据
    const option = {
      tooltip: {
        trigger: 'item'
      },
      legend: {
        orient: 'vertical',
        left: 'left'
      },
      series: [
        {
          type: 'pie',
          radius: '50%',
          data: [
            { value: 8, name: '优秀(90-100)' },
            { value: 12, name: '良好(80-89)' },
            { value: 4, name: '合格(70-79)' },
            { value: 1, name: '待改进(<70)' }
          ],
          emphasis: {
            itemStyle: {
              shadowBlur: 10,
              shadowOffsetX: 0,
              shadowColor: 'rgba(0, 0, 0, 0.5)'
            }
          }
        }
      ]
    }
    
    chart.setOption(option)
  }
}

// 更新考勤图表
const updateAttendanceChart = () => {
  // 这里可以根据选择的日期范围重新获取数据
  console.log('更新考勤图表', chartDateRange.value)
  initAttendanceChart()
}

// 加载仪表板数据
const loadDashboardData = async () => {
  try {
    loading.value = true
    
    // 并行加载所有数据
    const [stats, leaves, attendance] = await Promise.all([
      managerDashboardService.getDepartmentStats(),
      managerDashboardService.getPendingLeaves(),
      managerDashboardService.getAbnormalAttendance()
    ])
    
    departmentStats.value = stats
    pendingLeaves.value = leaves
    abnormalAttendance.value = attendance
  } catch (error: any) {
    console.error('Failed to load dashboard data:', error)
    ElMessage.error('数据加载失败')
  } finally {
    loading.value = false
  }
}

// 获取异常类型颜色
const getAbnormalTypeColor = (type: string) => {
  const colorMap: Record<string, string> = {
    '迟到': 'warning',
    '早退': 'danger',
    '缺卡': 'info'
  }
  return colorMap[type] || 'default'
}

// 审批请假
const approveLeave = async (id: number) => {
  try {
    await managerDashboardService.approveLeave(id)
    ElMessage.success('审批通过')
    // 刷新数据
    await loadDashboardData()
  } catch (error: any) {
    console.error('Failed to approve leave:', error)
    ElMessage.error('操作失败')
  }
}

// 拒绝请假
const rejectLeave = async (id: number) => {
  try {
    await managerDashboardService.rejectLeave(id, '管理员拒绝')
    ElMessage.success('已拒绝')
    // 刷新数据
    await loadDashboardData()
  } catch (error: any) {
    console.error('Failed to reject leave:', error)
    ElMessage.error('操作失败')
  }
}

// 处理异常考勤
const handleAbnormal = (id: number) => {
  // 跳转到详细处理页面或打开处理弹窗
  console.log('处理异常考勤', id)
}

// 跳转到请假审批页面
const goToLeaveApproval = () => {
  router.push('/manager/leave-approval')
}

// 跳转到考勤管理页面
const goToAttendanceManagement = () => {
  router.push('/manager/attendance')
}

onMounted(async () => {
  await nextTick()
  
  // 并行初始化图表和加载数据
  await Promise.all([
    initAttendanceChart(),
    initPerformanceChart(),
    loadDashboardData()
  ])
})
</script>

<style scoped>
.manager-dashboard {
  padding: 20px;
}

.stats-row {
  margin-bottom: 20px;
}

.stats-card {
  height: 120px;
}

.stats-content {
  display: flex;
  align-items: center;
  height: 80px;
}

.stats-icon {
  margin-right: 16px;
}

.stats-info {
  flex: 1;
}

.stats-value {
  font-size: 28px;
  font-weight: bold;
  color: #303133;
  margin-bottom: 4px;
}

.stats-label {
  font-size: 14px;
  color: #909399;
}

.charts-row {
  margin-bottom: 20px;
}

.pending-row {
  margin-bottom: 20px;
}

.chart-container {
  height: 300px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

:deep(.el-table) {
  font-size: 14px;
}

:deep(.el-card__body) {
  padding: 16px;
}
</style>
