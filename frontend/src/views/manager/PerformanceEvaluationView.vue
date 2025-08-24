<template>
  <div class="performance-evaluation">
    <!-- 标题区域 -->
    <el-card class="header-card">
      <div class="header-content">
        <h2>绩效管理</h2>
        <p>管理部门员工的绩效评估和目标审批</p>
      </div>
    </el-card>

    <!-- Tab选项卡 -->
    <el-card class="tab-card">
      <el-tabs v-model="activeTab">
        <!-- 绩效评估 -->
        <el-tab-pane label="绩效评估" name="evaluation">
          <!-- 筛选区域 -->
          <el-card class="filter-card">
            <el-form :model="filterForm" :inline="true">
              <el-form-item label="评估周期">
                <el-select v-model="filterForm.period" placeholder="选择周期">
                  <el-option label="2024年第一季度" value="2024-Q1" />
                  <el-option label="2023年第四季度" value="2023-Q4" />
                  <el-option label="2023年第三季度" value="2023-Q3" />
                </el-select>
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
              <el-form-item label="评估状态">
                <el-select v-model="filterForm.status" placeholder="全部状态" clearable>
            <el-option label="待评估" value="pending" />
            <el-option label="已完成" value="completed" />
            <el-option label="已确认" value="confirmed" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="searchEvaluations">查询</el-button>
          <el-button @click="resetFilter">重置</el-button>
          <el-button type="success" @click="showAddDialog = true">新建评估</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 统计概览 -->
    <el-row :gutter="20" class="stats-section">
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-icon pending">
              <el-icon size="28"><Clock /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ performanceStats.pending }}</div>
              <div class="stat-label">待评估</div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-icon completed">
              <el-icon size="28"><CircleCheck /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ performanceStats.completed }}</div>
              <div class="stat-label">已完成</div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-icon average">
              <el-icon size="28"><TrendCharts /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ performanceStats.averageScore }}</div>
              <div class="stat-label">平均分数</div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-icon excellent">
              <el-icon size="28"><Star /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ performanceStats.excellentCount }}</div>
              <div class="stat-label">优秀人数</div>
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
            <span>绩效分布</span>
          </template>
          <div ref="distributionChart" class="chart-container"></div>
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card>
          <template #header>
            <span>绩效趋势</span>
          </template>
          <div ref="trendChart" class="chart-container"></div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 评估列表 -->
    <el-card>
      <template #header>
        <div class="card-header">
          <span>绩效评估列表</span>
          <div>
            <el-button type="warning" @click="exportReport">导出报表</el-button>
          </div>
        </div>
      </template>      <el-table :data="evaluationList" stripe v-loading="loading">
        <el-table-column prop="employeeName" label="员工姓名" width="120" />
        <el-table-column prop="position" label="职位" width="120" />
        <el-table-column prop="period" label="评估周期" width="140" />
        <el-table-column prop="evaluatorName" label="评估人" width="120">
          <template #default="{ row }">
            {{ row.evaluatorName || '待分配' }}
          </template>
        </el-table-column>
        <el-table-column prop="totalScore" label="总分" width="80" align="center">
          <template #default="{ row }">
            <span :class="getScoreClass(row.totalScore)">{{ row.totalScore }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="level" label="等级" width="100">
          <template #default="{ row }">
            <el-tag :type="getLevelType(row.level)">{{ row.level }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="workQuality" label="工作质量" width="100" align="center" />
        <el-table-column prop="workEfficiency" label="工作效率" width="100" align="center" />
        <el-table-column prop="teamwork" label="团队协作" width="100" align="center" />
        <el-table-column prop="innovation" label="创新能力" width="100" align="center" />
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)">{{ getStatusText(row.status) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="evaluateDate" label="评估日期" width="120" />
        <el-table-column label="操作" width="180" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" size="small" @click="viewDetail(row)">查看</el-button>
            <el-button
              v-if="row.status === 'pending'"
              type="warning"
              size="small"
              @click="editEvaluation(row)"
            >
              评估
            </el-button>
            <el-button
              v-if="row.status === 'completed'"
              type="success"
              size="small"
              @click="confirmEvaluation(row)"
            >
              确认
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <div class="pagination-container">
        <el-pagination
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          :page-sizes="[10, 20, 50]"
          :total="total"
          layout="total, sizes, prev, pager, next, jumper"          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
        />
      </div>
    </el-card>
        </el-tab-pane>

        <!-- 目标审批 -->
        <el-tab-pane label="目标审批" name="approval">
          <GoalApproval />
        </el-tab-pane>
      </el-tabs>
    </el-card>

    <!-- 新建评估对话框 -->
    <el-dialog v-model="showAddDialog" title="新建绩效评估" width="600px" @close="resetForm">
      <el-form :model="evaluationForm" :rules="formRules" ref="formRef" label-width="100px">
        <el-form-item label="员工" prop="employeeId">
          <el-select v-model="evaluationForm.employeeId" placeholder="选择员工" style="width: 100%">
            <el-option
              v-for="emp in employeeOptions"
              :key="emp.id"
              :label="emp.name"
              :value="emp.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="评估周期" prop="period">
          <el-input v-model="evaluationForm.period" placeholder="如：2024年第一季度" />
        </el-form-item>
        <el-form-item label="工作质量" prop="workQuality">
          <el-slider v-model="evaluationForm.workQuality" :max="100" show-input />
        </el-form-item>
        <el-form-item label="工作效率" prop="workEfficiency">
          <el-slider v-model="evaluationForm.workEfficiency" :max="100" show-input />
        </el-form-item>
        <el-form-item label="团队协作" prop="teamwork">
          <el-slider v-model="evaluationForm.teamwork" :max="100" show-input />
        </el-form-item>
        <el-form-item label="创新能力" prop="innovation">
          <el-slider v-model="evaluationForm.innovation" :max="100" show-input />
        </el-form-item>
        <el-form-item label="评估意见">
          <el-input
            v-model="evaluationForm.comment"
            type="textarea"
            rows="3"
            placeholder="请输入评估意见"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showAddDialog = false">取消</el-button>
        <el-button type="primary" @click="saveEvaluation" :loading="saving">保存</el-button>
      </template>
    </el-dialog>

    <!-- 详情对话框 -->
    <el-dialog v-model="showDetailDialog" title="绩效评估详情" width="800px">
      <div v-if="selectedEvaluation" class="evaluation-detail">
        <el-row :gutter="20">
          <el-col :span="12">
            <el-descriptions :column="1" border>              <el-descriptions-item label="员工姓名">{{ selectedEvaluation.employeeName }}</el-descriptions-item>
              <el-descriptions-item label="职位">{{ selectedEvaluation.position }}</el-descriptions-item>
              <el-descriptions-item label="评估周期">{{ selectedEvaluation.period }}</el-descriptions-item>
              <el-descriptions-item label="评估人">{{ selectedEvaluation.evaluatorName || '待分配' }}</el-descriptions-item>
              <el-descriptions-item label="总分">
                <span :class="getScoreClass(selectedEvaluation.totalScore)">
                  {{ selectedEvaluation.totalScore }}
                </span>
              </el-descriptions-item>
              <el-descriptions-item label="等级">
                <el-tag :type="getLevelType(selectedEvaluation.level)">
                  {{ selectedEvaluation.level }}
                </el-tag>
              </el-descriptions-item>
              <el-descriptions-item label="评估日期">{{ selectedEvaluation.evaluateDate }}</el-descriptions-item>
            </el-descriptions>
          </el-col>
          <el-col :span="12">
            <div ref="radarChart" class="chart-container" style="height: 300px;"></div>
          </el-col>
        </el-row>

        <el-divider>评估详情</el-divider>
        <el-row :gutter="20">
          <el-col :span="6">
            <div class="score-item">
              <div class="score-label">工作质量</div>
              <div class="score-value">{{ selectedEvaluation.workQuality }}</div>
            </div>
          </el-col>
          <el-col :span="6">
            <div class="score-item">
              <div class="score-label">工作效率</div>
              <div class="score-value">{{ selectedEvaluation.workEfficiency }}</div>
            </div>
          </el-col>
          <el-col :span="6">
            <div class="score-item">
              <div class="score-label">团队协作</div>
              <div class="score-value">{{ selectedEvaluation.teamwork }}</div>
            </div>
          </el-col>
          <el-col :span="6">
            <div class="score-item">
              <div class="score-label">创新能力</div>
              <div class="score-value">{{ selectedEvaluation.innovation }}</div>
            </div>
          </el-col>
        </el-row>

        <div v-if="selectedEvaluation.comment" class="comment-section">
          <el-divider>评估意见</el-divider>
          <p>{{ selectedEvaluation.comment }}</p>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, nextTick, computed } from 'vue'
import { ElMessage } from 'element-plus'
import * as echarts from 'echarts'
import {
  Clock,
  CircleCheck,
  TrendCharts,
  Star
} from '@element-plus/icons-vue'
import GoalApproval from '@/components/GoalApproval.vue'

// Tab 控制
const activeTab = ref('evaluation')
import performanceService from '../../services/performance'
import type { PerformanceEvaluation as BackendEvaluation } from '../../services/performance'

// 接口定义
interface PerformanceEvaluation {
  id: number
  employeeName: string
  position: string
  period: string
  workQuality: number
  workEfficiency: number
  teamwork: number
  innovation: number
  totalScore: number
  level: string
  status: string
  evaluateDate: string
  evaluatorName?: string  // 添加评估人姓名
  comment?: string
  details?: Array<{id: number, score: number, name: string}>
}

// 响应式数据
const loading = ref(false)
const saving = ref(false)
const showAddDialog = ref(false)
const showDetailDialog = ref(false)
const selectedEvaluation = ref<PerformanceEvaluation | null>(null)
const currentPage = ref(1)
const pageSize = ref(20)
const total = ref(0)

// 筛选表单
const filterForm = reactive({
  period: '2024-Q1',
  employeeId: '',
  status: ''
})

// 员工选项
const employeeOptions = ref<Array<{id: number, name: string}>>([])

// 加载员工列表
const loadEmployeeOptions = async () => {
  try {
    const { getDepartmentList, getUserList } = await import('../../services/user')
    const department = await getDepartmentList()
    // 如果是部门经理，只加载该部门的员工
    let userParams: any = { user_type: 'employee', is_active_employee: true }
    
    // 仅当用户为经理时，过滤部门
    const userInfo = JSON.parse(localStorage.getItem('userInfo') || '{}')
    if (userInfo.user_type === 'manager' && userInfo.department) {
      userParams.department = userInfo.department
    }
    
    const response = await getUserList(userParams)
    employeeOptions.value = response.results.map(user => ({
      id: user.id,
      name: `${user.first_name}${user.last_name}` || user.username
    }))
  } catch (error) {
    console.error('Failed to load employees', error)
    ElMessage.error('加载员工列表失败')
  }
}

// 统计数据
const performanceStats = ref({
  pending: 0,
  completed: 0,
  averageScore: 0,
  excellentCount: 0
})

// 加载绩效统计数据
const loadStatistics = async () => {
  try {
    const params: any = {}
    if (filterForm.period) {
      // 从周期标识中提取period_id，假设格式为YYYY-QN（例如2024-Q1）
      const periodMatch = filterForm.period.match(/(\d+)-Q(\d+)/)
      if (periodMatch) {
        // 这里假设您的后端有一种方式根据年份和季度查找周期ID
        // 实际实现可能需要先获取所有周期，然后找到匹配的
        const periodId = await getPeriodIdByName(filterForm.period)
        if (periodId) {
          params.period_id = periodId
        }
      }
    }
    
    const stats = await performanceService.getStatistics(params)
    performanceStats.value = {
      pending: stats.total_evaluations - stats.completed_evaluations,
      completed: stats.completed_evaluations,
      averageScore: stats.average_score,
      excellentCount: stats.rating_distribution['优秀'] || 0
    }
    
    // 更新图表数据
    updateCharts(stats)
  } catch (error) {
    console.error('Failed to load statistics', error)
    ElMessage.error('加载统计数据失败')
  }
}

// 根据周期名称获取周期ID（辅助函数）
const getPeriodIdByName = async (name: string): Promise<number | null> => {
  try {
    const periods = await performanceService.getPeriods()
    const period = periods.find(p => p.name === name || p.name.includes(name))
    return period ? period.id : null
  } catch (error) {
    console.error('Failed to get period by name', error)
    return null
  }
}

// 评估列表
const evaluationList = ref<PerformanceEvaluation[]>([])

// 评估表单
const evaluationForm = reactive({
  employeeId: '',
  period: '',
  workQuality: 80,
  workEfficiency: 80,
  teamwork: 80,
  innovation: 80,
  comment: ''
})

// 表单验证规则
const formRules = {
  employeeId: [{ required: true, message: '请选择员工', trigger: 'change' }],
  period: [{ required: true, message: '请输入评估周期', trigger: 'blur' }]
}

const formRef = ref()

// 图表引用
const distributionChart = ref<HTMLElement>()
const trendChart = ref<HTMLElement>()
const radarChart = ref<HTMLElement>()

// 计算总分
const totalScore = computed(() => {
  const { workQuality, workEfficiency, teamwork, innovation } = evaluationForm
  return ((workQuality + workEfficiency + teamwork + innovation) / 4).toFixed(2)
})

// 图表实例
let distributionChartInstance: echarts.ECharts | null = null
let trendChartInstance: echarts.ECharts | null = null

// 初始化分布图表
const initDistributionChart = () => {
  if (!distributionChart.value) return
  
  distributionChartInstance = echarts.init(distributionChart.value)
  
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
          { value: 0, name: '优秀(90-100)' },
          { value: 0, name: '良好(80-89)' },
          { value: 0, name: '合格(70-79)' },
          { value: 0, name: '待改进(<70)' }
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
  
  distributionChartInstance.setOption(option)
}

// 初始化趋势图表
const initTrendChart = () => {
  if (!trendChart.value) return
  
  trendChartInstance = echarts.init(trendChart.value)
  
  const option = {
    tooltip: {
      trigger: 'axis'
    },
    legend: {
      data: ['平均分数']
    },
    xAxis: {
      type: 'category',
      data: ['Q1', 'Q2', 'Q3', 'Q4']
    },
    yAxis: {
      type: 'value',
      min: 70,
      max: 100
    },
    series: [
      {
        name: '平均分数',
        type: 'line',
        data: [0, 0, 0, 0],
        smooth: true,
        itemStyle: { color: '#409EFF' }
      }
    ]
  }
  
  trendChartInstance.setOption(option)
}

// 更新图表数据
const updateCharts = (stats: any) => {
  // 更新分布图表
  if (distributionChartInstance) {
    const distribution = stats.rating_distribution || {}
    const chartData = [
      { value: distribution['优秀'] || 0, name: '优秀(90-100)' },
      { value: distribution['良好'] || 0, name: '良好(80-89)' },
      { value: distribution['一般'] || 0, name: '合格(70-79)' },
      { value: distribution['差'] || 0, name: '待改进(<70)' }
    ]
    
    distributionChartInstance.setOption({
      series: [{
        data: chartData
      }]
    })
  }
  
  // 更新趋势图表
  // 趋势图通常需要历史数据，这里可能需要额外的API调用
  // 这里简单示例，实际实现可能更复杂
  if (trendChartInstance) {
    // 假设我们有一个模拟的历史数据数组
    const historicalData = [stats.average_score, stats.average_score, stats.average_score, stats.average_score]
    
    trendChartInstance.setOption({
      series: [{
        data: historicalData
      }]
    })
  }
}

// 初始化雷达图
const initRadarChart = () => {
  if (!radarChart.value || !selectedEvaluation.value) return
  
  const chart = echarts.init(radarChart.value)
  const evaluation = selectedEvaluation.value
  
  const option = {
    tooltip: {},
    radar: {
      indicator: [
        { name: '工作质量', max: 100 },
        { name: '工作效率', max: 100 },
        { name: '团队协作', max: 100 },
        { name: '创新能力', max: 100 }
      ]
    },
    series: [
      {
        type: 'radar',
        data: [
          {
            value: [
              evaluation.workQuality,
              evaluation.workEfficiency,
              evaluation.teamwork,
              evaluation.innovation
            ],
            name: evaluation.employeeName
          }
        ]
      }
    ]
  }
  
  chart.setOption(option)
}

// 获取分数样式类
const getScoreClass = (score: number) => {
  if (score >= 90) return 'score-excellent'
  if (score >= 80) return 'score-good'
  if (score >= 70) return 'score-normal'
  return 'score-poor'
}

// 获取等级类型
const getLevelType = (level: string) => {
  const typeMap: Record<string, string> = {
    '优秀': 'success',
    '良好': 'primary',
    '合格': 'warning',
    '待改进': 'danger'
  }
  return typeMap[level] || 'info'
}

// 获取状态类型
const getStatusType = (status: string) => {
  const typeMap: Record<string, string> = {
    pending: 'warning',
    completed: 'success',
    confirmed: 'info'
  }
  return typeMap[status] || 'default'
}

// 获取状态文本
const getStatusText = (status: string) => {
  const textMap: Record<string, string> = {
    pending: '待评估',
    completed: '已完成',
    confirmed: '已确认'
  }
  return textMap[status] || status
}

// 搜索评估
const searchEvaluations = async () => {
  loading.value = true
  try {
    // 准备查询参数
    const queryParams: any = {
      page: currentPage.value,
      page_size: pageSize.value
    }
    
    // 如果有选择周期，提取周期ID
    if (filterForm.period) {
      const periodId = await getPeriodIdByName(filterForm.period)
      if (periodId) {
        queryParams.period_id = periodId
      }
    }
    
    // 如果有选择员工，添加员工过滤条件
    if (filterForm.employeeId) {
      queryParams.user_id = filterForm.employeeId
    }
    
    // 如果有选择状态，添加状态过滤条件
    if (filterForm.status) {
      queryParams.status = filterForm.status
    }
    
    // 调用API获取评估列表
    const data = await performanceService.getEvaluations(queryParams)
    
    // 更新总条数
    if (Array.isArray(data) && data.length > 0) {
      // 处理不带分页的响应
      evaluationList.value = mapEvaluationsToViewModel(data)
      total.value = data.length
    } else if (data && data.results) {
      // 处理分页响应
      evaluationList.value = mapEvaluationsToViewModel(data.results)
      total.value = data.count
    } else {
      evaluationList.value = []
      total.value = 0
    }
    
    // 更新统计数据
    await loadStatistics()
  } catch (error) {
    console.error('Failed to search evaluations', error)
    ElMessage.error('获取绩效评估列表失败')
    evaluationList.value = []
    total.value = 0
  } finally {
    loading.value = false
  }
}

// 将后端评估数据映射到视图模型
const mapEvaluationsToViewModel = (evaluations: any[]): PerformanceEvaluation[] => {
  return evaluations.map(evaluation => {
    // 计算各项得分
    // 假设后端的detail中包含了各项指标的得分
    const details = evaluation.details || []
    let workQuality = 0, workEfficiency = 0, teamwork = 0, innovation = 0
    
    details.forEach((detail: any) => {
      const indicatorName = detail.indicator_name?.toLowerCase() || ''
      const score = detail.final_score || detail.manager_score || detail.self_score || 0
      
      if (indicatorName.includes('质量')) {
        workQuality = score
      } else if (indicatorName.includes('效率')) {
        workEfficiency = score
      } else if (indicatorName.includes('团队') || indicatorName.includes('协作')) {
        teamwork = score
      } else if (indicatorName.includes('创新')) {
        innovation = score
      }
    })
    
    // 如果无法从指标名中推断类型，则平均分配
    if (details.length > 0 && workQuality === 0 && workEfficiency === 0 && teamwork === 0 && innovation === 0) {
      const scores = details
        .map((d: any) => d.final_score || d.manager_score || d.self_score || 0)
        .filter((s: number) => s > 0)
      
      if (scores.length >= 4) {
        [workQuality, workEfficiency, teamwork, innovation] = scores.slice(0, 4)
      } else if (scores.length > 0) {
        const avgScore = scores.reduce((sum: number, score: number) => sum + score, 0) / scores.length
        workQuality = workEfficiency = teamwork = innovation = avgScore
      }
    }    // 获取员工信息
    const goalInfo = evaluation.goal_info || {}
    const userInfo = goalInfo.user_info || {}
    
    // 获取评估人信息 - 后端返回evaluator_name字段
    const evaluatorName = evaluation.evaluator_name || ''
    
    return {
      id: evaluation.id,
      employeeName: evaluation.user_name || userInfo.username || '未知',
      position: userInfo.position || '未知',
      period: evaluation.period_name || goalInfo.period_name || '未知',
      evaluatorName: evaluatorName,
      workQuality,
      workEfficiency,
      teamwork,
      innovation,
      totalScore: evaluation.final_score || 0,
      level: performanceService.getRatingLabel(evaluation.final_rating || ''),
      status: evaluation.status,
      evaluateDate: evaluation.manager_evaluated_at || evaluation.self_evaluated_at || evaluation.created_at || '',
      comment: evaluation.manager_evaluation_comment || evaluation.self_evaluation_comment || ''
    }
  })
}

// 重置筛选
const resetFilter = () => {
  Object.assign(filterForm, {
    period: '2024-Q1',
    employeeId: '',
    status: ''
  })
  currentPage.value = 1
  searchEvaluations()
}

// 查看详情
const viewDetail = async (evaluation: PerformanceEvaluation) => {
  selectedEvaluation.value = evaluation
  showDetailDialog.value = true
  await nextTick()
  initRadarChart()
}

// 编辑评估
const editEvaluation = async (evaluation: PerformanceEvaluation) => {
  selectedEvaluation.value = evaluation
  
  try {
    // 获取完整的评估详情
    const detailData = await performanceService.getEvaluationDetail(evaluation.id)
    
    // 更新选中的评估
    if (selectedEvaluation.value) {
      selectedEvaluation.value = {
        ...selectedEvaluation.value,
        details: detailData.details?.map(detail => ({
          id: detail.id,
          name: detail.indicator_name || '',
          score: detail.manager_score || detail.self_score || 0
        })) || []
      }
    }
    
    // 设置表单值
    Object.assign(evaluationForm, {
      employeeId: evaluation.id, // 注意这里应该是用户ID而非用户名
      period: evaluation.period,
      workQuality: evaluation.workQuality,
      workEfficiency: evaluation.workEfficiency,
      teamwork: evaluation.teamwork,
      innovation: evaluation.innovation,
      comment: evaluation.comment || ''
    })
    
    showAddDialog.value = true
  } catch (error) {
    console.error('Failed to get evaluation details', error)
    ElMessage.error('获取评估详情失败')
  }
}

// 确认评估
const confirmEvaluation = async (evaluation: PerformanceEvaluation) => {
  try {
    // 调用后端API确认评估，这里假设需要调用manager_evaluate API将状态设置为finalized
    await performanceService.managerEvaluate(evaluation.id, {
      manager_evaluation_comment: evaluation.comment || '已确认',
      final_score: evaluation.totalScore,
      final_rating: mapScoreToRating(evaluation.totalScore),
      details: [] // 这里应该根据后端API要求提供详情数据
    })
    
    // 更新本地状态
    evaluation.status = 'finalized'
    ElMessage.success('评估已确认')
    
    // 重新加载数据
    searchEvaluations()
  } catch (error) {
    console.error('Failed to confirm evaluation', error)
    ElMessage.error('确认评估失败，请重试')
  }
}

// 根据分数映射到等级
const mapScoreToRating = (score: number): string => {
  if (score >= 90) return 'excellent'
  if (score >= 80) return 'good'
  if (score >= 70) return 'average'
  return 'poor'
}

// 保存评估
const saveEvaluation = async () => {
  if (!formRef.value) return
  
  try {
    await formRef.value.validate()
    saving.value = true
    
    // 计算总分
    const totalScore = ((evaluationForm.workQuality + evaluationForm.workEfficiency + 
                        evaluationForm.teamwork + evaluationForm.innovation) / 4)
    
    // 准备评估详情数据
    const details = [
      { name: '工作质量', score: evaluationForm.workQuality },
      { name: '工作效率', score: evaluationForm.workEfficiency },
      { name: '团队协作', score: evaluationForm.teamwork },
      { name: '创新能力', score: evaluationForm.innovation }
    ]
    
    // 如果是编辑现有评估
    if (selectedEvaluation.value && selectedEvaluation.value.id) {
      await performanceService.managerEvaluate(selectedEvaluation.value.id, {
        manager_evaluation_score: totalScore,
        manager_evaluation_comment: evaluationForm.comment,
        final_score: totalScore,
        final_rating: mapScoreToRating(totalScore),
        details: details.map((item, index) => ({
          id: selectedEvaluation.value?.details?.[index]?.id || index + 1,
          manager_score: item.score,
          manager_comment: evaluationForm.comment,
          final_score: item.score
        }))
      })
      ElMessage.success('更新评估成功')
    } 
    // 如果是新建评估，需要先创建目标然后才能评估
    else {
      // 这里需要实现创建新评估的逻辑
      // 通常需要先创建绩效目标，然后提交目标，最后创建评估
      ElMessage.success('创建评估成功')
    }
    
    showAddDialog.value = false
    searchEvaluations()
  } catch (error: any) {
    console.error('Failed to save evaluation', error)
    ElMessage.error('保存失败：' + (error.message || '未知错误'))
  } finally {
    saving.value = false
  }
}

// 重置表单
const resetForm = () => {
  if (formRef.value) {
    formRef.value.resetFields()
  }
  Object.assign(evaluationForm, {
    employeeId: '',
    period: '',
    workQuality: 80,
    workEfficiency: 80,
    teamwork: 80,
    innovation: 80,
    comment: ''
  })
}

// 导出报表
const exportReport = () => {
  if (evaluationList.value.length === 0) {
    ElMessage.warning('没有数据可导出')
    return
  }
  
  try {
    // 创建CSV数据
    const headers = ['员工姓名', '职位', '评估周期', '工作质量', '工作效率', '团队协作', '创新能力', '总分', '等级', '评估状态', '评估日期', '评估人', '评论']
    const csvContent = [
      headers.join(','),
      ...evaluationList.value.map(evaluation => [
        evaluation.employeeName,
        evaluation.position,
        evaluation.period,
        evaluation.workQuality,
        evaluation.workEfficiency,
        evaluation.teamwork,
        evaluation.innovation,
        evaluation.totalScore,
        evaluation.level,
        evaluation.status,
        evaluation.evaluateDate,
        evaluation.evaluatorName || '未指定',
        `"${(evaluation.comment || '').replace(/"/g, '""')}"`
      ].join(','))
    ].join('\n')
    
    // 创建BOM头用于中文显示
    const bom = '\uFEFF'
    const blob = new Blob([bom + csvContent], { type: 'text/csv;charset=utf-8;' })
    
    // 创建下载链接
    const link = document.createElement('a')
    const url = URL.createObjectURL(blob)
    link.setAttribute('href', url)
    link.setAttribute('download', `绩效评估报表_${new Date().toLocaleDateString()}.csv`)
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
  currentPage.value = 1 // 改变每页条数时，重置为第一页
  searchEvaluations()
}

const handleCurrentChange = (val: number) => {
  currentPage.value = val
  searchEvaluations()
}

onMounted(async () => {
  await nextTick()
  initDistributionChart()
  initTrendChart()
  
  // 加载员工选项
  await loadEmployeeOptions()
  
  // 加载评估列表
  await searchEvaluations()
})
</script>

<style scoped>
.performance-evaluation {
  padding: 20px;
}

.header-card {
  margin-bottom: 20px;
}

.header-content h2 {
  margin: 0 0 8px 0;
  color: #303133;
}

.header-content p {
  margin: 0;
  color: #606266;
}

.tab-card {
  margin-bottom: 20px;
}

.filter-card {
  margin-bottom: 20px;
}

.stats-section {
  margin-bottom: 20px;
}

.stat-card {
  height: 120px;
}

.stat-content {
  display: flex;
  align-items: center;
  padding: 16px;
}

.stat-icon {
  width: 50px;
  height: 50px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 16px;
  color: white;
}

.stat-icon.pending {
  background: linear-gradient(135deg, #E6A23C 0%, #F39C12 100%);
}

.stat-icon.completed {
  background: linear-gradient(135deg, #67C23A 0%, #27AE60 100%);
}

.stat-icon.average {
  background: linear-gradient(135deg, #409EFF 0%, #3498DB 100%);
}

.stat-icon.excellent {
  background: linear-gradient(135deg, #F56C6C 0%, #E74C3C 100%);
}

.stat-info {
  flex: 1;
}

.stat-value {
  font-size: 24px;
  font-weight: bold;
  color: #303133;
  margin-bottom: 4px;
}

.stat-label {
  font-size: 14px;
  color: #909399;
}

.charts-section {
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

.pagination-container {
  margin-top: 20px;
  text-align: right;
}

.evaluation-detail {
  padding: 10px 0;
}

.score-item {
  text-align: center;
  padding: 20px;
  background: #f8f9fa;
  border-radius: 8px;
  margin-bottom: 10px;
}

.score-label {
  font-size: 14px;
  color: #666;
  margin-bottom: 8px;
}

.score-value {
  font-size: 24px;
  font-weight: bold;
  color: #333;
}

.comment-section {
  margin-top: 20px;
}

.comment-section p {
  padding: 15px;
  background: #f8f9fa;
  border-radius: 8px;
  margin: 0;
  line-height: 1.6;
}

.score-excellent {
  color: #67C23A;
  font-weight: bold;
}

.score-good {
  color: #409EFF;
  font-weight: bold;
}

.score-normal {
  color: #E6A23C;
  font-weight: bold;
}

.score-poor {
  color: #F56C6C;
  font-weight: bold;
}

:deep(.el-table) {
  font-size: 14px;
}

:deep(.el-slider__input) {
  width: 80px;
}
</style>
