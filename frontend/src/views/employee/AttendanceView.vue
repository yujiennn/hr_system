<template>
  <div class="attendance">
    <el-card class="header-card">
      <template #header>
        <div class="card-header">
          <span>考勤管理</span>
          <div class="header-actions">
            <el-date-picker
              v-model="selectedMonth"
              type="month"
              placeholder="选择月份"
              format="YYYY年MM月"
              value-format="YYYY-MM"
              @change="handleMonthChange"
            />
          </div>
        </div>
      </template>

      <el-row :gutter="20">
        <el-col :span="12">
          <div class="clock-section">
            <h3>今日打卡</h3>
            <div class="clock-time">
              <div class="current-time">{{ currentTime }}</div>
              <div class="current-date">{{ currentDate }}</div>
            </div>
            <div class="clock-buttons">
              <div class="button-group">
                <el-button 
                  type="primary" 
                  size="large" 
                  @click="handleFaceClockIn"
                  :disabled="todayRecord.clock_in_time"
                  :loading="clockLoading"
                >
                  <el-icon><Camera /></el-icon>
                  {{ todayRecord.clock_in_time ? '已完成上班打卡' : '人脸上班打卡' }}
                </el-button>
                <el-button 
                  type="primary" 
                  size="large" 
                  plain
                  @click="handleLocationClockIn"
                  :disabled="todayRecord.clock_in_time"
                  :loading="clockLoading"
                >
                  <el-icon><LocationInformation /></el-icon>
                  位置上班打卡
                </el-button>
              </div>
              
              <div class="button-group">
                <el-button 
                  type="danger" 
                  size="large" 
                  @click="handleFaceClockOut"
                  :disabled="!todayRecord.clock_in_time || todayRecord.clock_out_time"
                  :loading="clockLoading"
                >
                  <el-icon><Camera /></el-icon>
                  {{ todayRecord.clock_out_time ? '已完成下班打卡' : '人脸下班打卡' }}
                </el-button>
                <el-button 
                  type="danger" 
                  size="large" 
                  plain
                  @click="handleLocationClockOut"
                  :disabled="!todayRecord.clock_in_time || todayRecord.clock_out_time"
                  :loading="clockLoading"
                >
                  <el-icon><LocationInformation /></el-icon>
                  位置下班打卡
                </el-button>
              </div>
            </div>
          </div>
        </el-col>
        
        <el-col :span="12">
          <div class="today-status">
            <h3>今日状态</h3>
            <div class="status-item" v-if="todayRecord.clock_in_time">
              <span class="label">上班时间：</span>
              <span class="value">{{ formatTime(todayRecord.clock_in_time) }}</span>
              <el-tag :type="todayRecord.is_late ? 'warning' : 'success'" size="small">
                {{ todayRecord.is_late ? '迟到' : '正常' }}
              </el-tag>
            </div>
            <div class="status-item" v-if="todayRecord.clock_out_time">
              <span class="label">下班时间：</span>
              <span class="value">{{ formatTime(todayRecord.clock_out_time) }}</span>
              <el-tag v-if="todayRecord.is_early_leave" type="warning" size="small">早退</el-tag>
            </div>
            <div class="status-item" v-if="todayRecord.work_hours">
              <span class="label">工作时长：</span>
              <span class="value">{{ todayRecord.work_hours }} 小时</span>
            </div>
            <div class="status-item" v-if="!todayRecord.clock_in_time">
              <span class="no-record">今日尚未打卡</span>
            </div>
          </div>
        </el-col>
      </el-row>
    </el-card>

    <el-card class="statistics-card">
      <template #header>
        <span>本月统计</span>
      </template>
      <el-row :gutter="20">
        <el-col :span="6">
          <div class="stat-item">
            <div class="stat-value">{{ monthStats.workDays }}</div>
            <div class="stat-label">工作天数</div>
          </div>
        </el-col>
        <el-col :span="6">
          <div class="stat-item">
            <div class="stat-value">{{ monthStats.lateDays }}</div>
            <div class="stat-label">迟到次数</div>
          </div>
        </el-col>
        <el-col :span="6">
          <div class="stat-item">
            <div class="stat-value">{{ monthStats.absentDays }}</div>
            <div class="stat-label">缺勤天数</div>
          </div>
        </el-col>
        <el-col :span="6">
          <div class="stat-item">
            <div class="stat-value">{{ monthStats.totalHours }}</div>
            <div class="stat-label">总工时</div>
          </div>
        </el-col>
      </el-row>
    </el-card>

    <el-card>
      <template #header>
        <span>考勤记录</span>
      </template>
      <el-table :data="attendanceRecords" v-loading="loading">
        <el-table-column prop="date" label="日期" width="120" />
        <el-table-column label="上班时间" width="120">
          <template #default="{ row }">
            {{ row.clock_in_time ? formatTime(row.clock_in_time) : '-' }}
          </template>
        </el-table-column>
        <el-table-column label="下班时间" width="120">
          <template #default="{ row }">
            {{ row.clock_out_time ? formatTime(row.clock_out_time) : '-' }}
          </template>
        </el-table-column>
        <el-table-column label="工作时长" width="100">
          <template #default="{ row }">
            {{ row.work_hours ? row.work_hours + '小时' : '-' }}
          </template>
        </el-table-column>
        <el-table-column label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row)">
              {{ getStatusText(row) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="remarks" label="备注" />
      </el-table>
      
      <div class="pagination">
        <el-pagination
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          :page-sizes="[10, 20, 50]"
          :total="total"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
        />
      </div>
    </el-card>

    <!-- 人脸识别组件 -->
    <FaceRecognitionDialog
      v-model:visible="showFaceRecognition"
      :clock-type="faceClockType"
      @confirm="handleFaceRecognitionConfirm"
    />

    <!-- 位置打卡组件 -->
    <LocationClockDialog
      v-model:visible="showLocationClock"
      :clock-type="locationClockType"
      @success="handleLocationClockConfirm"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, onUnmounted, computed } from 'vue'
import { ElMessage } from 'element-plus'
import { Clock, Camera, LocationInformation } from '@element-plus/icons-vue'
import attendanceService, { type AttendanceRecord, type TodayAttendance, type MonthlyStats } from '@/services/attendance'
import FaceRecognitionDialog from '@/components/FaceRecognitionDialog.vue'
import LocationClockDialog from '@/components/LocationClockDialog.vue'

// 类型定义
interface TodayRecord {
  clock_in_time: string | null
  clock_out_time: string | null
  work_hours: number | null
  status: string
  is_late: boolean
  is_early_leave: boolean
}

const currentTime = ref('')
const clockLoading = ref(false)
const loading = ref(false)
const selectedMonth = ref(new Date().toISOString().slice(0, 7))
const currentPage = ref(1)
const pageSize = ref(10)
const total = ref(0)

// 人脸识别相关状态
const showFaceRecognition = ref(false)
const faceClockType = ref<'in' | 'out'>('in')

// 位置打卡相关状态
const showLocationClock = ref(false)
const locationClockType = ref<'in' | 'out'>('in')

const currentDate = computed(() => {
  return new Date().toLocaleDateString('zh-CN', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
    weekday: 'long'
  })
})

const todayRecord = reactive<TodayRecord>({
  clock_in_time: null,
  clock_out_time: null,
  work_hours: null,
  status: '',
  is_late: false,
  is_early_leave: false
})

const monthStats = reactive({
  workDays: 0,
  lateDays: 0,
  absentDays: 0,
  totalHours: 0
})

const attendanceRecords = ref<AttendanceRecord[]>([])

// 更新当前时间
const updateCurrentTime = () => {
  currentTime.value = new Date().toLocaleTimeString('zh-CN')
}

// 人脸识别上班打卡
const handleFaceClockIn = () => {
  faceClockType.value = 'in'
  showFaceRecognition.value = true
}

// 人脸识别下班打卡
const handleFaceClockOut = () => {
  faceClockType.value = 'out'
  showFaceRecognition.value = true
}

// 处理人脸识别确认
const handleFaceRecognitionConfirm = async (result: any) => {
  try {
    ElMessage.success('人脸识别打卡成功！')
    await loadTodayRecord()
    await loadAttendanceRecords()
  } catch (error: any) {
    console.error('刷新数据失败:', error)
    ElMessage.error('刷新数据失败')
  }
}

// 位置打卡上班
const handleLocationClockIn = () => {
  locationClockType.value = 'in'
  showLocationClock.value = true
}

// 位置打卡下班
const handleLocationClockOut = () => {
  locationClockType.value = 'out'
  showLocationClock.value = true
}

// 处理位置打卡确认
const handleLocationClockConfirm = async (result: any) => {
  try {
    await loadTodayRecord()
    await loadAttendanceRecords()
  } catch (error: any) {
    console.error('刷新数据失败:', error)
    ElMessage.error('刷新数据失败')
  }
}

// 获取当前位置
const getCurrentLocation = (): Promise<{address: string, latitude: number, longitude: number} | null> => {
  return new Promise((resolve) => {
    if (!navigator.geolocation) {
      resolve(null)
      return
    }
    
    navigator.geolocation.getCurrentPosition(
      (position) => {
        resolve({
          address: '当前位置',
          latitude: position.coords.latitude,
          longitude: position.coords.longitude
        })
      },
      (error) => {
        console.error('获取位置失败:', error)
        resolve(null)
      }
    )
  })
}

// 格式化时间
const formatTime = (timeStr: string) => {
  if (!timeStr) return '-'
  return new Date(timeStr).toLocaleTimeString('zh-CN', {
    hour: '2-digit',
    minute: '2-digit'
  })
}

// 获取状态类型
const getStatusType = (record: AttendanceRecord) => {
  if (record.is_absent) return 'danger'
  if (record.is_late) return 'warning'
  if (record.is_early_leave) return 'warning'
  return 'success'
}

// 获取状态文本
const getStatusText = (record: AttendanceRecord) => {
  if (record.is_absent) return '缺勤'
  if (record.is_late && record.is_early_leave) return '迟到早退'
  if (record.is_late) return '迟到'
  if (record.is_early_leave) return '早退'
  return '正常'
}

// 月份变化处理
const handleMonthChange = () => {
  loadAttendanceRecords()
  loadMonthStats()
}

// 分页处理
const handleSizeChange = (val: number) => {
  pageSize.value = val
  loadAttendanceRecords()
}

const handleCurrentChange = (val: number) => {
  currentPage.value = val
  loadAttendanceRecords()
}

// 加载今日考勤记录
const loadTodayRecord = async () => {
  try {
    const response = await attendanceService.getTodayAttendance()
    Object.assign(todayRecord, response)
  } catch (error: any) {
    console.error('加载今日考勤记录失败:', error)
  }
}

// 加载月度统计
const loadMonthStats = async () => {
  try {
    const [year, month] = selectedMonth.value.split('-')
    const response = await attendanceService.getMonthlyStats(parseInt(year), parseInt(month))
    monthStats.workDays = response.work_days
    monthStats.lateDays = response.late_days
    monthStats.absentDays = response.absent_days
    monthStats.totalHours = response.total_hours
  } catch (error: any) {
    console.error('加载月度统计失败:', error)
  }
}

// 加载考勤记录
const loadAttendanceRecords = async () => {
  loading.value = true
  try {
    const [year, month] = selectedMonth.value.split('-')
    console.log(`加载考勤记录，年份: ${year}, 月份: ${month}`)
    
    const params: any = {
      year: parseInt(year),
      page: currentPage.value,
      page_size: pageSize.value
    }
    
    if (month) {
      params.month = parseInt(month)
    }
    
    const response = await attendanceService.getMyRecords(params)
    console.log('API响应数据:', response)
    
    if (response && response.results) {
      attendanceRecords.value = response.results
      total.value = response.count || 0
      console.log(`成功加载 ${attendanceRecords.value.length} 条记录，总计: ${total.value}`)
    } else {
      attendanceRecords.value = []
      total.value = 0
      console.warn('API响应中没有results数组')
    }
  } catch (error: any) {
    console.error('加载考勤记录失败:', error)
    ElMessage.error('加载考勤记录失败')
    attendanceRecords.value = []
    total.value = 0
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  updateCurrentTime()
  setInterval(updateCurrentTime, 1000)
  loadTodayRecord()
  loadMonthStats()
  loadAttendanceRecords()
})
</script>

<style scoped>
.attendance {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-card {
  margin-bottom: 20px;
}

.clock-section {
  text-align: center;
  padding: 20px;
}

.clock-section h3 {
  margin-bottom: 20px;
  color: #303133;
}

.clock-time {
  margin-bottom: 30px;
}

.current-time {
  font-size: 48px;
  font-weight: bold;
  color: #409EFF;
  margin-bottom: 10px;
}

.current-date {
  font-size: 16px;
  color: #909399;
}

.clock-buttons {
  display: flex;
  flex-direction: column;
  gap: 15px;
  align-items: center;
}

.button-group {
  display: flex;
  gap: 10px;
  justify-content: center;
  align-items: center;
}

.clock-buttons .el-button {
  padding: 15px 30px;
  font-size: 16px;
  min-width: 140px;
}

.today-status {
  padding: 20px;
}

.today-status h3 {
  margin-bottom: 20px;
  color: #303133;
}

.status-item {
  display: flex;
  align-items: center;
  margin-bottom: 15px;
  gap: 10px;
}

.status-item .label {
  color: #909399;
  width: 80px;
}

.status-item .value {
  color: #303133;
  font-weight: 500;
  margin-right: 10px;
}

.no-record {
  color: #909399;
  font-style: italic;
}

.statistics-card {
  margin-bottom: 20px;
}

.stat-item {
  text-align: center;
  padding: 20px;
}

.stat-value {
  font-size: 32px;
  font-weight: bold;
  color: #409EFF;
  margin-bottom: 10px;
}

.stat-label {
  color: #909399;
  font-size: 14px;
}

.pagination {
  margin-top: 20px;
  text-align: right;
}
</style>
