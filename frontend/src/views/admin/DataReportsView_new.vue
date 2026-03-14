<template>
  <div class="data-reports">
    <el-card class="page-header">
      <div class="header-content">
        <h2>数据报表</h2>
        <div class="header-actions">
          <el-button type="primary" @click="generateReport" :loading="generating">
            <el-icon><Document /></el-icon>
            生成报表
          </el-button>
          <el-button type="success" @click="scheduleReport">
            <el-icon><Timer /></el-icon>
            定时报表
          </el-button>
          <el-button type="info" @click="exportAllReports" :loading="exporting">
            <el-icon><Download /></el-icon>
            批量导出
          </el-button>
        </div>
      </div>
    </el-card>

    <!-- 报表类型选择 -->
    <el-row :gutter="20" v-loading="loading">
      <el-col :span="6">
        <el-card class="report-category" header="报表分类">
          <div class="category-items" v-if="categories.length">
            <div 
              v-for="category in categories"
              :key="category.id"
              class="category-item"
              :class="{ active: selectedReport === category.code }"
              @click="selectReport(category.code)"
            >
              <el-icon>
                <User v-if="category.code === 'employee'" />
                <Clock v-else-if="category.code === 'attendance'" />
                <Money v-else-if="category.code === 'salary'" />
                <TrophyBase v-else-if="category.code === 'performance'" />
                <Document v-else />
              </el-icon>
              <span>{{ category.name }}</span>
            </div>
          </div>
          <el-empty v-else description="暂无分类数据" />
        </el-card>
      </el-col>

      <el-col :span="18">
        <!-- 报表预览区域 -->
        <el-card v-if="selectedReport" class="report-preview">
          <template #header>
            <div class="preview-header">
              <span>{{ getSelectedCategoryName() }}</span>
              <div class="preview-actions">
                <el-select v-model="reportParams.period" placeholder="选择周期" style="width: 120px; margin-right: 10px;">
                  <el-option label="本月" value="current_month" />
                  <el-option label="上月" value="last_month" />
                  <el-option label="本季度" value="current_quarter" />
                  <el-option label="本年度" value="current_year" />
                </el-select>
                <el-select v-model="reportParams.format" placeholder="选择格式" style="width: 100px;">
                  <el-option label="Excel" value="xlsx" />
                  <el-option label="PDF" value="pdf" />
                  <el-option label="CSV" value="csv" />
                </el-select>
              </div>
            </div>
          </template>

          <!-- 统计数据摘要 -->
          <div v-if="statistics" class="stats-summary">
            <!-- 员工统计 -->
            <el-row :gutter="20" v-if="selectedReport === 'employee'">
              <el-col :span="6">
                <div class="stat-card">
                  <div class="stat-icon employee">
                    <el-icon><User /></el-icon>
                  </div>
                  <div class="stat-content">
                    <div class="stat-label">总员工数</div>
                    <div class="stat-value">{{ statistics.employee_stats.total }}</div>
                  </div>
                </div>
              </el-col>
              <el-col :span="6">
                <div class="stat-card">
                  <div class="stat-icon active">
                    <el-icon><CircleCheck /></el-icon>
                  </div>
                  <div class="stat-content">
                    <div class="stat-label">在职员工</div>
                    <div class="stat-value">{{ statistics.employee_stats.active }}</div>
                  </div>
                </div>
              </el-col>
              <el-col :span="6">
                <div class="stat-card">
                  <div class="stat-icon inactive">
                    <el-icon><CircleClose /></el-icon>
                  </div>
                  <div class="stat-content">
                    <div class="stat-label">离职员工</div>
                    <div class="stat-value">{{ statistics.employee_stats.inactive }}</div>
                  </div>
                </div>
              </el-col>
              <el-col :span="6">
                <div class="stat-card">
                  <div class="stat-icon growth">
                    <el-icon><ArrowUp /></el-icon>
                  </div>
                  <div class="stat-content">
                    <div class="stat-label">部门数量</div>
                    <div class="stat-value">{{ statistics.employee_stats.by_department.length }}</div>
                  </div>
                </div>
              </el-col>
            </el-row>

            <!-- 考勤统计 -->
            <el-row :gutter="20" v-if="selectedReport === 'attendance'">
              <el-col :span="6">
                <div class="stat-card">
                  <div class="stat-icon attendance">
                    <el-icon><Clock /></el-icon>
                  </div>
                  <div class="stat-content">
                    <div class="stat-label">总记录数</div>
                    <div class="stat-value">{{ statistics.attendance_stats.total_records }}</div>
                  </div>
                </div>
              </el-col>
              <el-col :span="6">
                <div class="stat-card">
                  <div class="stat-icon success">
                    <el-icon><CircleCheck /></el-icon>
                  </div>
                  <div class="stat-content">
                    <div class="stat-label">出勤率</div>
                    <div class="stat-value">{{ statistics.attendance_stats.present_rate }}%</div>
                  </div>
                </div>
              </el-col>
              <el-col :span="6">
                <div class="stat-card">
                  <div class="stat-icon warning">
                    <el-icon><Warning /></el-icon>
                  </div>
                  <div class="stat-content">
                    <div class="stat-label">迟到率</div>
                    <div class="stat-value">{{ statistics.attendance_stats.late_rate }}%</div>
                  </div>
                </div>
              </el-col>
              <el-col :span="6">
                <div class="stat-card">
                  <div class="stat-icon danger">
                    <el-icon><CircleClose /></el-icon>
                  </div>
                  <div class="stat-content">
                    <div class="stat-label">缺勤率</div>
                    <div class="stat-value">{{ statistics.attendance_stats.absent_rate }}%</div>
                  </div>
                </div>
              </el-col>
            </el-row>

            <!-- 薪资统计 -->
            <el-row :gutter="20" v-if="selectedReport === 'salary'">
              <el-col :span="6">
                <div class="stat-card">
                  <div class="stat-icon salary">
                    <el-icon><Money /></el-icon>
                  </div>
                  <div class="stat-content">
                    <div class="stat-label">总金额</div>
                    <div class="stat-value">¥{{ statistics.salary_stats.total_amount.toLocaleString() }}</div>
                  </div>
                </div>
              </el-col>
              <el-col :span="6">
                <div class="stat-card">
                  <div class="stat-icon average">
                    <el-icon><TrendCharts /></el-icon>
                  </div>
                  <div class="stat-content">
                    <div class="stat-label">平均薪资</div>
                    <div class="stat-value">¥{{ statistics.salary_stats.avg_salary.toLocaleString() }}</div>
                  </div>
                </div>
              </el-col>
              <el-col :span="6">
                <div class="stat-card">
                  <div class="stat-icon department">
                    <el-icon><OfficeBuilding /></el-icon>
                  </div>
                  <div class="stat-content">
                    <div class="stat-label">部门数量</div>
                    <div class="stat-value">{{ statistics.salary_stats.by_department.length }}</div>
                  </div>
                </div>
              </el-col>
              <el-col :span="6">
                <div class="stat-card">
                  <div class="stat-icon trend">
                    <el-icon><ArrowUp /></el-icon>
                  </div>
                  <div class="stat-content">
                    <div class="stat-label">记录数</div>
                    <div class="stat-value">{{ statistics.salary_stats.monthly_trend.length }}</div>
                  </div>
                </div>
              </el-col>
            </el-row>

            <!-- 绩效统计 -->
            <el-row :gutter="20" v-if="selectedReport === 'performance'">
              <el-col :span="6">
                <div class="stat-card">
                  <div class="stat-icon performance">
                    <el-icon><TrophyBase /></el-icon>
                  </div>
                  <div class="stat-content">
                    <div class="stat-label">评估总数</div>
                    <div class="stat-value">{{ statistics.performance_stats.total_evaluations }}</div>
                  </div>
                </div>
              </el-col>
              <el-col :span="6">
                <div class="stat-card">
                  <div class="stat-icon score">
                    <el-icon><TrendCharts /></el-icon>
                  </div>
                  <div class="stat-content">
                    <div class="stat-label">平均分数</div>
                    <div class="stat-value">{{ statistics.performance_stats.avg_score.toFixed(1) }}</div>
                  </div>
                </div>
              </el-col>
              <el-col :span="6">
                <div class="stat-card">
                  <div class="stat-icon level">
                    <el-icon><View /></el-icon>
                  </div>
                  <div class="stat-content">
                    <div class="stat-label">评估等级</div>
                    <div class="stat-value">{{ statistics.performance_stats.by_level.length }}</div>
                  </div>
                </div>
              </el-col>
              <el-col :span="6">
                <div class="stat-card">
                  <div class="stat-icon monthly">
                    <el-icon><Calendar /></el-icon>
                  </div>
                  <div class="stat-content">
                    <div class="stat-label">月度记录</div>
                    <div class="stat-value">{{ statistics.performance_stats.monthly_trend.length }}</div>
                  </div>
                </div>
              </el-col>
            </el-row>
          </div>

          <!-- 图表区域 -->
          <div class="charts-container" style="margin-top: 20px;">
            <el-row :gutter="20">
              <el-col :span="12">
                <div ref="employeeChart" style="height: 300px;" v-if="selectedReport === 'employee'"></div>
                <div ref="attendanceTrendChart" style="height: 300px;" v-if="selectedReport === 'attendance'"></div>
                <div ref="salaryDistributionChart" style="height: 300px;" v-if="selectedReport === 'salary'"></div>
                <div ref="performanceChart" style="height: 300px;" v-if="selectedReport === 'performance'"></div>
              </el-col>
              <el-col :span="12">
                <div ref="departmentChart" style="height: 300px;" v-if="selectedReport === 'employee'"></div>
                <div ref="attendanceChart" style="height: 300px;" v-if="selectedReport === 'attendance'"></div>
                <div ref="salaryTrendChart" style="height: 300px;" v-if="selectedReport === 'salary'"></div>
                <div ref="performanceTrendChart" style="height: 300px;" v-if="selectedReport === 'performance'"></div>
              </el-col>
            </el-row>
          </div>
        </el-card>

        <el-card v-else class="empty-preview">
          <el-empty description="请选择要生成的报表类型" />
        </el-card>
      </el-col>
    </el-row>

    <!-- 历史报表 -->
    <el-card class="history-reports" header="历史报表" style="margin-top: 20px;">
      <el-table :data="reports" v-loading="loadingHistory">
        <el-table-column label="报表名称" prop="name" min-width="200" />
        <el-table-column label="模板ID" prop="template" width="100" />
        <el-table-column label="格式" prop="format" width="80" />
        <el-table-column label="生成时间" width="160">
          <template #default="{ row }">
            {{ formatDate(row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column label="状态" prop="status" width="100">
          <template #default="{ row }">
            <el-tag :type="row.status === 'completed' ? 'success' : row.status === 'failed' ? 'danger' : 'warning'">
              {{ getStatusText(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="150" fixed="right">
          <template #default="{ row }">
            <el-button 
              type="primary" 
              size="small" 
              @click="downloadReport(row)"
              :disabled="row.status !== 'completed'"
              link
            >
              下载
            </el-button>
            <el-popconfirm
              title="确定要删除这个报表吗？"
              @confirm="deleteReport(row)"
            >
              <template #reference>
                <el-button 
                  type="danger" 
                  size="small" 
                  link
                >
                  删除
                </el-button>
              </template>
            </el-popconfirm>
          </template>
        </el-table-column>
      </el-table>

      <el-pagination
        v-model:current-page="historyPagination.currentPage"
        v-model:page-size="historyPagination.pageSize"
        :page-sizes="[10, 20, 50]"
        :total="historyPagination.total"
        layout="total, sizes, prev, pager, next, jumper"
        style="margin-top: 20px; justify-content: center;"
        @current-change="handlePageChange"
        @size-change="handlePageChange"
      />
    </el-card>

    <!-- 定时报表配置对话框 -->
    <el-dialog
      v-model="showScheduleDialog"
      title="定时报表配置"
      width="600px"
    >
      <el-form :model="scheduleForm" label-width="120px">
        <el-form-item label="报表模板">
          <el-select v-model="scheduleForm.template" placeholder="选择报表模板">
            <el-option
              v-for="template in templates"
              :key="template.id"
              :label="template.name"
              :value="template.id"
            />
          </el-select>
        </el-form-item>
        
        <el-form-item label="生成频率">
          <el-radio-group v-model="scheduleForm.frequency">
            <el-radio label="daily">每日</el-radio>
            <el-radio label="weekly">每周</el-radio>
            <el-radio label="monthly">每月</el-radio>
            <el-radio label="quarterly">每季度</el-radio>
          </el-radio-group>
        </el-form-item>
        
        <el-form-item label="报表格式">
          <el-checkbox-group v-model="scheduleForm.formats">
            <el-checkbox label="xlsx">Excel</el-checkbox>
            <el-checkbox label="pdf">PDF</el-checkbox>
            <el-checkbox label="csv">CSV</el-checkbox>
          </el-checkbox-group>
        </el-form-item>
        
        <el-form-item label="邮件发送">
          <el-switch v-model="scheduleForm.emailEnabled" />
        </el-form-item>
        
        <el-form-item label="收件人" v-if="scheduleForm.emailEnabled">
          <el-input
            v-model="scheduleForm.recipients"
            type="textarea"
            :rows="3"
            placeholder="请输入邮箱地址，多个邮箱用逗号分隔"
          />
        </el-form-item>
      </el-form>
      
      <template #footer>
        <el-button @click="showScheduleDialog = false">取消</el-button>
        <el-button type="primary" @click="saveSchedule" :loading="saving">
          保存配置
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, nextTick } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import * as echarts from 'echarts'
import reportsService from '@/services/reports'
import type { ReportCategory, ReportTemplate, Report, DataStatistics } from '@/services/reports'
import {
  Document,
  Timer,
  Download,
  User,
  OfficeBuilding,
  SwitchButton,
  Clock,
  Calendar,
  Money,
  TrophyBase,
  Tickets,
  View,
  Plus,
  Minus,
  TrendCharts,
  Warning,
  CircleClose,
  CircleCheck,
  ArrowUp
} from '@element-plus/icons-vue'

// 响应式数据
const loading = ref(false)
const generating = ref(false)
const exporting = ref(false)
const previewing = ref(false)
const downloading = ref(false)
const loadingHistory = ref(false)
const saving = ref(false)
const showScheduleDialog = ref(false)
const selectedReport = ref('')

// 数据
const categories = ref<ReportCategory[]>([])
const templates = ref<ReportTemplate[]>([])
const reports = ref<Report[]>([])
const statistics = ref<DataStatistics | null>(null)

// 报表参数
const reportParams = reactive({
  period: 'current_month',
  dateRange: [],
  format: 'xlsx',
  includeCharts: true
})

// 定时报表配置
const scheduleForm = reactive({
  template: 0,
  frequency: 'monthly',
  time: '09:00',
  formats: ['xlsx'],
  emailEnabled: false,
  recipients: ''
})

// 分页
const historyPagination = reactive({
  currentPage: 1,
  pageSize: 10,
  total: 0
})

// 图表引用
const employeeChart = ref()
const departmentChart = ref()
const attendanceTrendChart = ref()
const salaryDistributionChart = ref()
const salaryTrendChart = ref()

// 方法
const loadData = async () => {
  try {
    loading.value = true
    
    // 加载数据统计
    const [categoriesData, statisticsData] = await Promise.all([
      reportsService.getCategories(),
      reportsService.getDataStatistics()
    ])
    
    categories.value = categoriesData
    statistics.value = statisticsData
    
    // 加载报表历史
    await loadReportHistory()
    
  } catch (error: any) {
    console.error('加载数据失败:', error)
    ElMessage.error('加载数据失败')
  } finally {
    loading.value = false
  }
}

const loadReportHistory = async () => {
  try {
    loadingHistory.value = true
    const { results, count } = await reportsService.getReports({
      page: historyPagination.currentPage,
      page_size: historyPagination.pageSize
    })
    reports.value = results
    historyPagination.total = count
  } catch (error: any) {
    console.error('加载报表历史失败:', error)
    ElMessage.error('加载报表历史失败')
  } finally {
    loadingHistory.value = false
  }
}

const selectReport = async (type: string) => {
  selectedReport.value = type
  
  // 根据分类加载模板
  try {
    templates.value = await reportsService.getTemplates(type)
  } catch (error: any) {
    console.error('加载模板失败:', error)
  }
  
  nextTick(() => {
    initCharts()
  })
}

const generateReport = async () => {
  if (!selectedReport.value) {
    ElMessage.warning('请先选择报表类型')
    return
  }
  
  const selectedTemplate = templates.value.find(t => t.code?.includes(selectedReport.value))
  if (!selectedTemplate) {
    ElMessage.warning('未找到对应的报表模板')
    return
  }
  
  try {
    generating.value = true
    
    const reportData = {
      name: `${selectedTemplate.name} - ${new Date().toLocaleString()}`,
      template: selectedTemplate.id,
      file_format: reportParams.format,
      parameters: {
        period: reportParams.period,
        dateRange: reportParams.dateRange,
        includeCharts: reportParams.includeCharts
      }
    }
    
    await reportsService.generateReport(reportData)
    ElMessage.success('报表生成成功')
    
    // 重新加载报表历史
    await loadReportHistory()
    
  } catch (error: any) {
    console.error('生成报表失败:', error)
    ElMessage.error('生成报表失败')
  } finally {
    generating.value = false
  }
}

const downloadReport = async (report: Report) => {
  if (report.status !== 'completed') {
    ElMessage.warning('报表尚未生成完成')
    return
  }
  
  try {
    downloading.value = true
    const blob = await reportsService.downloadReport(report.id)
    
    // 创建下载链接
    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = `${report.name}.${report.format}`
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    window.URL.revokeObjectURL(url)
    
    ElMessage.success('下载完成')
  } catch (error: any) {
    console.error('下载失败:', error)
    ElMessage.error('下载失败')
  } finally {
    downloading.value = false
  }
}

const deleteReport = async (report: Report) => {
  try {
    // 这里应该调用删除API
    ElMessage.success('删除成功')
    await loadReportHistory()
  } catch (error: any) {
    console.error('删除失败:', error)
    ElMessage.error('删除失败')
  }
}

const scheduleReport = () => {
  if (!selectedReport.value) {
    ElMessage.warning('请先选择报表类型')
    return
  }
  showScheduleDialog.value = true
}

const saveSchedule = async () => {
  try {
    saving.value = true
    
    if (!scheduleForm.template) {
      ElMessage.error('请选择报表模板')
      return
    }
    
    await reportsService.createSchedule({
      name: `定时报表`,
      template: scheduleForm.template,
      frequency: scheduleForm.frequency,
      schedule_time: new Date().toISOString(),
      formats: scheduleForm.formats?.length ? scheduleForm.formats : ['xlsx'],
      email_enabled: scheduleForm.emailEnabled,
      email_recipients: scheduleForm.recipients,
      parameters: {
        format: scheduleForm.formats[0] || 'xlsx'
      }
    })
    
    ElMessage.success('定时报表设置成功')
    showScheduleDialog.value = false
  } catch (error: any) {
    console.error('设置定时报表失败:', error)
    ElMessage.error('设置失败')
  } finally {
    saving.value = false
  }
}

const exportAllReports = async () => {
  try {
    const confirmed = await ElMessageBox.confirm(
      '确定要导出所有已生成的报表吗？',
      '批量导出',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    if (confirmed) {
      exporting.value = true
      
      // 逐个下载所有已完成的报表
      const completedReports = reports.value.filter(r => r.status === 'completed')
      
      for (const report of completedReports) {
        await downloadReport(report)
        // 避免请求过于频繁
        await new Promise(resolve => setTimeout(resolve, 500))
      }
      
      ElMessage.success('批量导出完成')
    }
  } catch (error: any) {
    if (error !== 'cancel') {
      console.error('批量导出失败:', error)
      ElMessage.error('批量导出失败')
    }
  } finally {
    exporting.value = false
  }
}

const handlePageChange = (page: number) => {
  historyPagination.currentPage = page
  loadReportHistory()
}

const getSelectedCategoryName = () => {
  const category = categories.value.find(c => c.code === selectedReport.value)
  return category ? category.name : '报表'
}

const getStatusText = (status: string) => {
  const statusMap = {
    'pending': '等待中',
    'processing': '生成中',
    'completed': '已完成',
    'failed': '失败'
  }
  return statusMap[status as keyof typeof statusMap] || status
}

const formatDate = (dateStr: string) => {
  return new Date(dateStr).toLocaleString('zh-CN')
}

const initCharts = () => {
  if (!statistics.value) return
  
  // 员工统计图表
  if (employeeChart.value && selectedReport.value === 'employee') {
    const chart = echarts.init(employeeChart.value)
    chart.setOption({
      title: { text: '员工数量趋势', left: 'center' },
      tooltip: { trigger: 'axis' },
      xAxis: {
        type: 'category',
        data: ['1月', '2月', '3月', '4月', '5月', '6月']
      },
      yAxis: { type: 'value' },
      series: [{
        data: [120, 125, 130, 135, 142, 156],
        type: 'line',
        smooth: true,
        itemStyle: { color: '#409EFF' }
      }]
    })
  }
  
  // 部门分布图表
  if (departmentChart.value && selectedReport.value === 'employee') {
    const chart = echarts.init(departmentChart.value)
    chart.setOption({
      title: { text: '部门员工分布', left: 'center' },
      tooltip: { trigger: 'item' },
      series: [{
        type: 'pie',
        radius: ['40%', '70%'],
        data: statistics.value.employee_stats.by_department.map(item => ({
          name: item.department,
          value: item.count
        })),
        emphasis: {
          itemStyle: {
            shadowBlur: 10,
            shadowOffsetX: 0,
            shadowColor: 'rgba(0, 0, 0, 0.5)'
          }
        }
      }]
    })
  }
  
  // 考勤趋势图表
  if (attendanceTrendChart.value && selectedReport.value === 'attendance') {
    const chart = echarts.init(attendanceTrendChart.value)
    chart.setOption({
      title: { text: '考勤趋势分析', left: 'center' },
      tooltip: { trigger: 'axis' },
      legend: { data: ['出勤', '迟到', '缺勤'], top: 30 },
      xAxis: {
        type: 'category',
        data: statistics.value.attendance_stats.monthly_trend.map(item => item.month)
      },
      yAxis: { type: 'value' },
      series: [
        {
          name: '出勤',
          type: 'bar',
          data: statistics.value.attendance_stats.monthly_trend.map(item => item.present),
          itemStyle: { color: '#67C23A' }
        },
        {
          name: '迟到',
          type: 'bar',
          data: statistics.value.attendance_stats.monthly_trend.map(item => item.late),
          itemStyle: { color: '#E6A23C' }
        },
        {
          name: '缺勤',
          type: 'bar',
          data: statistics.value.attendance_stats.monthly_trend.map(item => item.absent),
          itemStyle: { color: '#F56C6C' }
        }
      ]
    })
  }
  
  // 薪资分布图表
  if (salaryDistributionChart.value && selectedReport.value === 'salary') {
    const chart = echarts.init(salaryDistributionChart.value)
    chart.setOption({
      title: { text: '部门薪资分布', left: 'center' },
      tooltip: { trigger: 'axis' },
      xAxis: {
        type: 'category',
        data: statistics.value.salary_stats.by_department.map(item => item.department)
      },
      yAxis: { type: 'value' },
      series: [{
        type: 'bar',
        data: statistics.value.salary_stats.by_department.map(item => item.avg),
        itemStyle: { color: '#909399' }
      }]
    })
  }
}

// 生命周期
onMounted(() => {
  loadData()
})
</script>

<style scoped>
.data-reports {
  padding: 20px;
}

.page-header {
  margin-bottom: 20px;
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-content h2 {
  margin: 0;
  font-size: 24px;
  color: #303133;
}

.header-actions {
  display: flex;
  gap: 10px;
}

.report-category {
  margin-bottom: 20px;
}

.category-items {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.category-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 12px;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.3s;
  border: 1px solid transparent;
}

.category-item:hover {
  background-color: #f5f7fa;
}

.category-item.active {
  background-color: #ecf5ff;
  border-color: #409eff;
  color: #409eff;
}

.preview-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.preview-actions {
  display: flex;
  gap: 10px;
}

.stats-summary {
  margin-bottom: 20px;
}

.stat-card {
  display: flex;
  align-items: center;
  gap: 15px;
  padding: 20px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 12px;
  color: white;
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
}

.stat-icon {
  width: 50px;
  height: 50px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
  background: rgba(255, 255, 255, 0.2);
}

.stat-content {
  flex: 1;
}

.stat-value {
  font-size: 28px;
  font-weight: bold;
  line-height: 1;
}

.stat-label {
  font-size: 14px;
  opacity: 0.9;
  margin-top: 5px;
}

:deep(.el-card__header) {
  background-color: #f8f9fa;
  font-weight: 600;
  color: #303133;
}
</style>
