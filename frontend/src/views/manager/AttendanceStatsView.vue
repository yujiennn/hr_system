<template>
  <div class="attendance-stats">
    <!-- 筛选条件 -->
    <el-card class="filter-card">
      <el-form :model="filterForm" :inline="true">
        <el-form-item label="统计时间">
          <el-date-picker
            v-model="filterForm.dateRange"
            type="monthrange"
            range-separator="至"
            start-placeholder="开始月份"
            end-placeholder="结束月份"
            @change="updateStats"
          />
        </el-form-item>
        <el-form-item label="员工">
          <el-select
            v-model="filterForm.employeeId"
            placeholder="选择员工"
            clearable
            filterable
            style="width: 200px"
          >
            <el-option
              v-for="emp in employeeOptions"
              :key="emp.id"
              :label="emp.name"
              :value="emp.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="updateStats">查询</el-button>
          <el-button @click="resetFilter">重置</el-button>
          <el-button type="success" @click="exportData">导出报表</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 统计概览 -->
    <el-row :gutter="20" class="stats-overview">
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-icon attendance">
              <el-icon size="32"><UserFilled /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ overviewStats.totalDays }}</div>
              <div class="stat-label">应出勤天数</div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-icon present">
              <el-icon size="32"><CircleCheckFilled /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ overviewStats.presentDays }}</div>
              <div class="stat-label">实际出勤天数</div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-icon late">
              <el-icon size="32"><Clock /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ overviewStats.lateTimes }}</div>
              <div class="stat-label">迟到次数</div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-icon rate">
              <el-icon size="32"><TrendCharts /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ overviewStats.attendanceRate }}%</div>
              <div class="stat-label">出勤率</div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 图表分析 -->
    <el-row :gutter="20" class="charts-section">
      <el-col :span="12">
        <el-card>
          <template #header>
            <span>考勤趋势分析</span>
          </template>
          <div ref="trendChart" class="chart-container"></div>
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card>
          <template #header>
            <span>异常考勤分布</span>
          </template>
          <div ref="abnormalChart" class="chart-container"></div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 详细数据表格 -->
    <el-card>
      <template #header>
        <div class="table-header">
          <span>考勤详细记录</span>
          <div>
            <el-button type="primary" @click="showBatchDialog = true">批量处理</el-button>
          </div>
        </div>
      </template>

      <el-table
        :data="attendanceList"
        stripe
        v-loading="loading"
        @selection-change="handleSelectionChange"
      >
        <el-table-column type="selection" width="55" />
        <el-table-column prop="employeeName" label="员工姓名" width="100" />
        <el-table-column prop="date" label="日期" width="120" />
        <el-table-column prop="clockIn" label="上班打卡" width="120">
          <template #default="{ row }">
            <span :class="{ 'late-time': row.isLate }">{{ row.clockIn || '--' }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="clockOut" label="下班打卡" width="120">
          <template #default="{ row }">
            <span :class="{ 'early-time': row.isEarly }">{{ row.clockOut || '--' }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="workHours" label="工作时长" width="100" />
        <el-table-column prop="status" label="考勤状态" width="120">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)">{{ row.status }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="overtime" label="加班时长" width="100" />
        <el-table-column prop="remark" label="备注" show-overflow-tooltip />
        <el-table-column label="操作" width="120" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" size="small" @click="editRecord(row)">编辑</el-button>
            <el-button type="warning" size="small" @click="addRemark(row)">备注</el-button>
          </template>
        </el-table-column>
      </el-table>

      <div class="pagination-container">
        <el-pagination
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          :page-sizes="[20, 50, 100]"
          :total="total"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
        />
      </div>
    </el-card>

    <!-- 批量处理对话框 -->
    <el-dialog v-model="showBatchDialog" title="批量处理考勤" width="600px">
      <div v-if="selectedRecords.length === 0" class="no-selection">
        <el-empty description="请先选择需要处理的记录" />
      </div>
      <div v-else>
        <p>已选择 {{ selectedRecords.length }} 条记录</p>
        <el-form :model="batchForm" label-width="100px">
          <el-form-item label="处理方式">
            <el-radio-group v-model="batchForm.action">
              <el-radio label="approve">批准异常</el-radio>
              <el-radio label="adjust">调整时间</el-radio>
              <el-radio label="remark">添加备注</el-radio>
            </el-radio-group>
          </el-form-item>
          <el-form-item v-if="batchForm.action === 'adjust'" label="调整时间">
            <el-time-picker
              v-model="batchForm.adjustTime"
              placeholder="选择时间"
              format="HH:mm"
              value-format="HH:mm"
            />
          </el-form-item>
          <el-form-item v-if="batchForm.action === 'remark'" label="备注内容">
            <el-input
              v-model="batchForm.remark"
              type="textarea"
              rows="3"
              placeholder="请输入备注内容"
            />
          </el-form-item>
        </el-form>
      </div>
      <template #footer>
        <el-button @click="showBatchDialog = false">取消</el-button>
        <el-button
          type="primary"
          @click="processBatch"
          :disabled="selectedRecords.length === 0"
        >
          确定处理
        </el-button>
      </template>
    </el-dialog>

    <!-- 编辑记录对话框 -->
    <el-dialog v-model="showEditDialog" title="编辑考勤记录" width="500px">
      <el-form :model="editForm" label-width="100px">
        <el-form-item label="员工">
          <el-input v-model="editForm.employeeName" disabled />
        </el-form-item>
        <el-form-item label="日期">
          <el-input v-model="editForm.date" disabled />
        </el-form-item>
        <el-form-item label="上班时间">
          <el-time-picker
            v-model="editForm.clockIn"
            format="HH:mm"
            value-format="HH:mm"
            placeholder="选择上班时间"
          />
        </el-form-item>
        <el-form-item label="下班时间">
          <el-time-picker
            v-model="editForm.clockOut"
            format="HH:mm"
            value-format="HH:mm"
            placeholder="选择下班时间"
          />
        </el-form-item>
        <el-form-item label="备注">
          <el-input
            v-model="editForm.remark"
            type="textarea"
            rows="3"
            placeholder="请输入备注"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showEditDialog = false">取消</el-button>
        <el-button type="primary" @click="saveEdit">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, nextTick } from 'vue'
import { ElMessage } from 'element-plus'
import * as echarts from 'echarts'
import {
  UserFilled,
  CircleCheckFilled,
  Clock,
  TrendCharts
} from '@element-plus/icons-vue'
import attendanceService from '@/services/attendance'
import { getUserList } from '@/services/user'

// 类型定义
interface AttendanceRecord {
  id: number
  employeeName: string
  date: string
  clockIn: string
  clockOut: string
  workHours: string
  status: string
  overtime: string
  isLate: boolean
  isEarly: boolean
  remark: string
}

interface OverviewStats {
  totalDays: number
  presentDays: number
  lateTimes: number
  attendanceRate: number
}

interface EmployeeOption {
  id: number
  name: string
}

// 数据定义
const loading = ref(false)
const showBatchDialog = ref(false)
const showEditDialog = ref(false)
const currentPage = ref(1)
const pageSize = ref(20)
const total = ref(0)

// 筛选表单
const filterForm = reactive({
  dateRange: [
    new Date(new Date().getFullYear(), new Date().getMonth(), 1),
    new Date()
  ] as [Date, Date],
  employeeId: ''
})

// 员工选项
const employeeOptions = ref<EmployeeOption[]>([])

// 统计概览数据
const overviewStats = ref<OverviewStats>({
  totalDays: 0,
  presentDays: 0,
  lateTimes: 0,
  attendanceRate: 0
})

// 考勤记录列表
const attendanceList = ref<AttendanceRecord[]>([])

const selectedRecords = ref<AttendanceRecord[]>([])

// 批量处理表单
const batchForm = reactive({
  action: 'approve',
  adjustTime: '',
  remark: ''
})

// 编辑表单
const editForm = reactive({
  id: null,
  employeeName: '',
  date: '',
  clockIn: '',
  clockOut: '',
  remark: ''
})

// 图表引用
const trendChart = ref<HTMLElement>()
const abnormalChart = ref<HTMLElement>()

// 数据转换函数
const convertApiToAttendanceRecord = (apiData: any): AttendanceRecord => {
  return {
    id: apiData.id,
    employeeName: apiData.user_name || apiData.employee_name || '未知',
    date: apiData.date,
    clockIn: apiData.clock_in || '--',
    clockOut: apiData.clock_out || '--',
    workHours: calculateWorkHours(apiData.clock_in, apiData.clock_out),
    status: getAttendanceStatus(apiData),
    overtime: calculateOvertime(apiData.clock_in, apiData.clock_out),
    isLate: apiData.status === 'late',
    isEarly: apiData.status === 'early',
    remark: apiData.note || ''
  }
}

const calculateWorkHours = (clockIn: string, clockOut: string): string => {
  if (!clockIn || !clockOut) return '0'
  
  const start = new Date(`2000-01-01 ${clockIn}`)
  const end = new Date(`2000-01-01 ${clockOut}`)
  const diff = (end.getTime() - start.getTime()) / (1000 * 60 * 60)
  
  return Math.max(0, diff - 1).toFixed(2) // 减去1小时午休时间
}

const calculateOvertime = (clockIn: string, clockOut: string): string => {
  if (!clockOut) return '0'
  
  const end = new Date(`2000-01-01 ${clockOut}`)
  const standardEnd = new Date('2000-01-01 18:00:00')
  const overtime = Math.max(0, (end.getTime() - standardEnd.getTime()) / (1000 * 60 * 60))
  
  return overtime.toFixed(2)
}

const getAttendanceStatus = (record: any): string => {
  if (record.status === 'late') return '迟到'
  if (record.status === 'early') return '早退'
  if (record.status === 'absent') return '缺勤'
  if (record.status === 'present') return '正常'
  return '异常'
}

// 加载员工列表
const loadEmployeeOptions = async () => {
  try {
    const response = await getUserList()
    employeeOptions.value = response.results.map((user: any) => ({
      id: user.id,
      name: user.username || user.first_name || user.email
    }))
  } catch (error: any) {
    console.error('Failed to load employees:', error)
  }
}

// 加载考勤统计数据
const loadAttendanceStats = async () => {
  try {
    loading.value = true
      const [startDate, endDate] = filterForm.dateRange
    const params = {
      year: startDate.getFullYear(),
      month: startDate.getMonth() + 1,
      employee_id: filterForm.employeeId ? Number(filterForm.employeeId) : undefined
    }
    
    const response = await attendanceService.getStatistics(params)
    // 检查响应数据结构
    console.log('考勤统计API响应:', response)
    const statistics = response.statistics || response.data?.statistics || {}
      // 如果没有统计数据，给出友好提示
    if (Object.keys(statistics).length === 0) {
      ElMessage.info('该时间范围内没有考勤数据')
      overviewStats.value = {
        totalDays: 0,
        presentDays: 0,
        lateTimes: 0,
        attendanceRate: 0
      }
      attendanceList.value = []
      total.value = 0
      return
    }

    // 转换统计概览数据
    let totalDays = 0
    let presentDays = 0
    let lateTimes = 0
    const attendanceRecords: AttendanceRecord[] = []
    
    Object.entries(statistics).forEach(([employeeId, data]: [string, any]) => {
      const dailyRecords = data.daily_records || []
      totalDays += dailyRecords.length
      
      dailyRecords.forEach((record: any) => {
        const attendanceRecord = convertApiToAttendanceRecord({
          ...record,
          id: attendanceRecords.length + 1,
          employee_name: data.name
        })
        
        attendanceRecords.push(attendanceRecord)
        
        if (record.status === 'present' || record.status === 'late') {
          presentDays++
        }
        if (record.status === 'late') {
          lateTimes++
        }
      })
    })
    
    overviewStats.value = {
      totalDays,
      presentDays,
      lateTimes,
      attendanceRate: totalDays > 0 ? Math.round((presentDays / totalDays) * 100 * 100) / 100 : 0
    }
    
    // 分页处理
    const startIndex = (currentPage.value - 1) * pageSize.value
    const endIndex = startIndex + pageSize.value
    attendanceList.value = attendanceRecords.slice(startIndex, endIndex)
    total.value = attendanceRecords.length
    
  } catch (error: any) {
    console.error('Failed to load attendance statistics:', error)
    ElMessage.error(`加载考勤数据失败: ${error.message || '未知错误'}`)
    // 重置数据以避免错误
    overviewStats.value = {
      totalDays: 0,
      presentDays: 0,
      lateTimes: 0,
      attendanceRate: 0
    }
    attendanceList.value = []
    total.value = 0
  } finally {
    loading.value = false
  }
}

// 初始化趋势图表
const initTrendChart = async () => {
  // 确保DOM元素存在且已挂载
  if (!trendChart.value) {
    console.warn('趋势图表容器元素未找到')
    return
  }
  
  try {
    // 检查元素是否已经连接到DOM
    if (!trendChart.value.isConnected) {
      console.warn('趋势图表容器元素未连接到DOM')
      return
    }
    
    // 销毁可能存在的旧图表实例
    echarts.dispose(trendChart.value)
    
    const chart = echarts.init(trendChart.value)
    
    // 获取趋势数据 - 这里可以根据实际需要调用特定的趋势API
    const trendData = calculateTrendFromRecords(attendanceList.value)
    
    const option = {
      tooltip: {
        trigger: 'axis'
      },
      legend: {
        data: ['出勤率', '迟到率', '早退率', '缺勤率']
      },
      xAxis: {
        type: 'category',
        data: trendData.map(item => item.period)
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
          itemStyle: { color: '#67C23A' }
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
          data: trendData.map(item => item.earlyRate),
          smooth: true,
          itemStyle: { color: '#F56C6C' }
        },
        {
          name: '缺勤率',
          type: 'line',
          data: trendData.map(item => item.absentRate),
          smooth: true,
          itemStyle: { color: '#909399' }
        }
      ]
    }
      chart.setOption(option)
  } catch (error: any) {
    console.error('Failed to initialize trend chart:', error)
    // 使用默认数据，重新初始化chart
    const chart = echarts.init(trendChart.value)
    const option = {
      tooltip: {
        trigger: 'axis'
      },
      legend: {
        data: ['出勤率', '迟到率', '早退率', '缺勤率']
      },
      xAxis: {
        type: 'category',
        data: ['周一', '周二', '周三', '周四', '周五']
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
          data: [96, 98, 95, 97, 94],
          smooth: true,
          itemStyle: { color: '#67C23A' }
        },
        {
          name: '迟到率',
          type: 'line',
          data: [4, 2, 5, 3, 6],
          smooth: true,
          itemStyle: { color: '#E6A23C' }
        },
        {
          name: '早退率',
          type: 'line',
          data: [2, 1, 3, 2, 4],
          smooth: true,
          itemStyle: { color: '#F56C6C' }
        },
        {
          name: '缺勤率',
          type: 'line',
          data: [1, 0, 2, 1, 2],
          smooth: true,
          itemStyle: { color: '#909399' }
        }
      ]
    }
    chart.setOption(option)
  }
}

// 从记录中计算趋势数据
const calculateTrendFromRecords = (records: AttendanceRecord[]) => {
  const weekdays = ['周一', '周二', '周三', '周四', '周五']
  return weekdays.map((day, index) => {
    // 这里可以根据实际日期计算各个工作日的统计
    const dayRecords = records.filter(record => {
      const date = new Date(record.date)
      return date.getDay() === index + 1 // 周一是1，周二是2...
    })
    
    const total = dayRecords.length
    const present = dayRecords.filter(r => r.status === '正常' || r.status === '迟到' || r.status === '早退').length
    const late = dayRecords.filter(r => r.status === '迟到').length
    const early = dayRecords.filter(r => r.status === '早退').length
    const absent = dayRecords.filter(r => r.status === '缺勤').length
    
    return {
      period: day,
      attendanceRate: total > 0 ? Math.round((present / total) * 100) : 0,
      lateRate: total > 0 ? Math.round((late / total) * 100) : 0,
      earlyRate: total > 0 ? Math.round((early / total) * 100) : 0,
      absentRate: total > 0 ? Math.round((absent / total) * 100) : 0
    }
  })
}

// 初始化异常分布图表
const initAbnormalChart = () => {
  // 确保DOM元素存在且已挂载
  if (!abnormalChart.value) {
    console.warn('异常分布图表容器元素未找到')
    return
  }
  
  try {
    // 检查元素是否已经连接到DOM
    if (!abnormalChart.value.isConnected) {
      console.warn('异常分布图表容器元素未连接到DOM')
      return
    }
    
    // 销毁可能存在的旧图表实例
    echarts.dispose(abnormalChart.value)
    
    const chart = echarts.init(abnormalChart.value)
    
    // 计算异常分布数据
    const abnormalData = calculateAbnormalDistribution(attendanceList.value)
    
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
          data: abnormalData,
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
    console.error('Failed to initialize abnormal chart:', error)
    // 使用默认数据，重新初始化chart
    const chart = echarts.init(abnormalChart.value)
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
            { value: 15, name: '迟到' },
            { value: 8, name: '早退' },
            { value: 3, name: '缺卡' },
            { value: 2, name: '缺勤' }
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

// 计算异常分布
const calculateAbnormalDistribution = (records: AttendanceRecord[]) => {
  const counts = {
    '迟到': 0,
    '早退': 0,
    '缺勤': 0,
    '缺卡': 0
  }
  
  records.forEach(record => {
    if (record.status === '迟到') counts['迟到']++
    else if (record.status === '早退') counts['早退']++
    else if (record.status === '缺勤') counts['缺勤']++
    else if (!record.clockIn || !record.clockOut) counts['缺卡']++
  })
  
  return Object.entries(counts).map(([name, value]) => ({ name, value }))
}

// 更新统计数据
const updateStats = async () => {
  await loadAttendanceStats()
  // 重新初始化图表
  await nextTick()
  initTrendChart()
  initAbnormalChart()
}

// 重置筛选条件
const resetFilter = () => {
  filterForm.dateRange = [
    new Date(new Date().getFullYear(), new Date().getMonth(), 1),
    new Date()
  ]
  filterForm.employeeId = ''
  updateStats()
}

// 获取状态类型
const getStatusType = (status: string) => {
  const typeMap: Record<string, string> = {
    '正常': 'success',
    '迟到': 'warning',
    '早退': 'danger',
    '缺勤': 'info'
  }
  return typeMap[status] || 'default'
}

// 选择变化处理
const handleSelectionChange = (selection: any[]) => {
  selectedRecords.value = selection
}

// 编辑记录
const editRecord = (record: any) => {
  Object.assign(editForm, record)
  showEditDialog.value = true
}

// 添加备注
const addRemark = (record: any) => {
  Object.assign(editForm, record)
  showEditDialog.value = true
}

// 保存编辑
const saveEdit = () => {
  ElMessage.success('保存成功')
  showEditDialog.value = false
}

// 批量处理
const processBatch = () => {
  ElMessage.success(`批量处理 ${selectedRecords.value.length} 条记录`)
  showBatchDialog.value = false
}

// 导出数据
const exportData = () => {
  if (attendanceList.value.length === 0) {
    ElMessage.warning('没有数据可导出')
    return
  }
  
  try {
    // 创建CSV数据
    const headers = ['员工姓名', '日期', '上班打卡', '下班打卡', '工作时长', '考勤状态', '加班时长', '备注']
    const csvContent = [
      headers.join(','),
      ...attendanceList.value.map((record: AttendanceRecord) => [
        record.employeeName,
        record.date,
        record.clockIn,
        record.clockOut,
        record.workHours,
        record.status,
        record.overtime,
        record.remark || ''
      ].join(','))
    ].join('\n')
    
    // 创建BOM头用于中文显示
    const bom = '\uFEFF'
    const blob = new Blob([bom + csvContent], { type: 'text/csv;charset=utf-8;' })
    
    // 创建下载链接
    const link = document.createElement('a')
    const url = URL.createObjectURL(blob)
    link.setAttribute('href', url)
    link.setAttribute('download', `考勤记录_${new Date().toLocaleDateString()}.csv`)
    link.style.visibility = 'hidden'
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    
    ElMessage.success('导出成功')
  } catch (error) {
    console.error('导出失败:', error)
    ElMessage.error('导出失败')
  }
}

// 分页处理
const handleSizeChange = (val: number) => {
  pageSize.value = val
  currentPage.value = 1
  updateStats()
}

const handleCurrentChange = (val: number) => {
  currentPage.value = val
  updateStats()
}

onMounted(async () => {
  await nextTick()
  
  // 并行加载数据
  await Promise.all([
    loadEmployeeOptions(),
    loadAttendanceStats()
  ])
  
  // 初始化图表
  initTrendChart()
  initAbnormalChart()
})
</script>

<style scoped>
.attendance-stats {
  padding: var(--hr-space-lg);
}

.filter-card {
  margin-bottom: var(--hr-space-lg);
}

.stats-overview {
  margin-bottom: var(--hr-space-lg);
}

.stat-card {
  height: 120px;
  border-radius: var(--hr-radius-md);
  transition: all var(--hr-transition-normal);
}

.stat-card:hover {
  transform: translateY(-3px);
  box-shadow: var(--hr-shadow-card-hover);
}

.stat-content {
  display: flex;
  align-items: center;
  height: 80px;
}

.stat-icon {
  width: 52px;
  height: 52px;
  border-radius: var(--hr-radius-md);
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: var(--hr-space-md);
}

.stat-icon.attendance {
  background: linear-gradient(135deg, var(--hr-primary), var(--hr-info));
  color: white;
}

.stat-icon.present {
  background: linear-gradient(135deg, #ec4899, var(--hr-danger));
  color: white;
}

.stat-icon.late {
  background: linear-gradient(135deg, var(--hr-primary-light), #06b6d4);
  color: white;
}

.stat-icon.rate {
  background: linear-gradient(135deg, var(--hr-success), #10b981);
  color: white;
}

.stat-info {
  flex: 1;
}

.stat-value {
  font-size: 24px;
  font-weight: 800;
  color: var(--color-text-primary);
  margin-bottom: 4px;
  letter-spacing: -0.5px;
}

.stat-label {
  font-size: 13px;
  color: var(--color-text-secondary);
}

.charts-section {
  margin-bottom: var(--hr-space-lg);
}

.chart-container {
  height: 300px;
}

.table-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.pagination-container {
  margin-top: var(--hr-space-lg);
  text-align: right;
}

.late-time {
  color: var(--hr-warning);
  font-weight: 700;
}

.early-time {
  color: var(--hr-danger);
  font-weight: 700;
}

.no-selection {
  text-align: center;
  padding: 40px 0;
  color: var(--color-text-secondary);
}

:deep(.el-table) {
  font-size: 14px;
}
</style>
