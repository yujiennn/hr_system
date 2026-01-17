<template>
  <div class="performance">
    <!-- 筛选器 -->
    <el-card class="filter-card">
      <el-form :inline="true" :model="filterForm" class="filter-form">
        <el-form-item label="评估周期">
          <el-select v-model="filterForm.period_id" placeholder="选择评估周期" clearable @change="handleFilterChange">
            <el-option
              v-for="period in periods"
              :key="period.id"
              :label="period.name"
              :value="period.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="filterForm.status" placeholder="选择状态" clearable @change="handleFilterChange">
            <el-option label="全部" value="" />
            <el-option label="草稿" value="draft" />
            <el-option label="自评完成" value="self_evaluated" />
            <el-option label="上级评估完成" value="manager_evaluated" />
            <el-option label="已完成" value="finalized" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="showCreateGoalDialog">创建绩效目标</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 流程指引 -->
    <el-card class="process-guide" v-if="latestEvaluation">
      <template #header>
        <div class="process-header">
          <span>📋 绩效评估进度</span>
        </div>
      </template>
      <el-steps :active="getCurrentStep()" align-center>
        <el-step title="目标设定" :status="getStepStatus('goal')">
          <template #description>
            <span v-if="getStepStatus('goal') === 'finish'">已完成</span>
            <span v-else-if="getStepStatus('goal') === 'process'">等待经理批准</span>
          </template>
        </el-step>
        <el-step title="自我评估" :status="getStepStatus('self_eval')">
          <template #description>
            <span v-if="getStepStatus('self_eval') === 'finish'">已完成</span>
            <span v-else-if="getStepStatus('self_eval') === 'process'">进行中</span>
            <span v-else>等待目标批准</span>
          </template>
        </el-step>
        <el-step title="上级评估" :status="getStepStatus('manager_eval')">
          <template #description>
            <span v-if="getStepStatus('manager_eval') === 'finish'">已完成</span>
            <span v-else-if="getStepStatus('manager_eval') === 'process'">待处理</span>
            <span v-else>等待自评完成</span>
          </template>
        </el-step>
        <el-step title="评估完成" :status="getStepStatus('complete')">
          <template #description>
            <span v-if="getStepStatus('complete') === 'finish'">已完成</span>
            <span v-else>待完成</span>
          </template>
        </el-step>
      </el-steps>

      <!-- 下一步操作提示 -->
      <el-alert v-if="nextActionText" :title="nextActionText" type="info" :closable="false" style="margin-top: 16px" />
    </el-card>

    <!-- 最新绩效概览 -->
    <el-card class="latest-performance" v-if="latestEvaluation">
      <template #header>
        <span>{{ latestEvaluation.period_name }}绩效评估</span>
      </template>
      <el-row :gutter="20">
        <el-col :span="6">
          <div class="performance-item total">
            <div class="score">{{ performanceService.formatScore(latestEvaluation.final_score) }}</div>
            <div class="label">总分</div>
            <div class="grade">{{ performanceService.getRatingLabel(latestEvaluation.final_rating || '') }}</div>
          </div>
        </el-col>
        <el-col :span="6">
          <div class="performance-item self">
            <div class="score">{{ performanceService.formatScore(latestEvaluation.self_evaluation_score) }}</div>
            <div class="label">自评分数</div>
          </div>
        </el-col>
        <el-col :span="6">
          <div class="performance-item manager">
            <div class="score">{{ performanceService.formatScore(latestEvaluation.manager_evaluation_score) }}</div>
            <div class="label">上级评分</div>
          </div>
        </el-col>
        <el-col :span="6">
          <div class="performance-item status">
            <div class="status-text">
              <el-tag :type="performanceService.getStatusType(latestEvaluation.status)">
                {{ performanceService.getStatusLabel(latestEvaluation.status) }}
              </el-tag>
            </div>
            <div class="label">评估状态</div>
          </div>
        </el-col>
      </el-row>
    </el-card>

    <!-- 绩效雷达图 -->
    <el-card class="chart-card" v-if="latestEvaluation && latestEvaluation.details.length > 0">
      <template #header>
        <span>绩效雷达图</span>
      </template>
      <div ref="radarChartRef" style="height: 400px;"></div>
    </el-card>

    <el-row :gutter="20">
      <!-- 绩效评估记录 -->
      <el-col :span="16">
        <el-card>
          <template #header>
            <span>绩效评估记录</span>
          </template>
          <el-table :data="evaluations" v-loading="loading">
            <el-table-column prop="period_name" label="评估周期" width="120" />
            <el-table-column prop="template_name" label="评估模板" width="120" />
            <el-table-column prop="final_score" label="最终得分" width="100" align="center">
              <template #default="{ row }">
                {{ performanceService.formatScore(row.final_score) }}
              </template>
            </el-table-column>
            <el-table-column prop="final_rating" label="等级" width="80" align="center">
              <template #default="{ row }">
                <el-tag v-if="row.final_rating" :type="performanceService.getRatingType(row.final_rating)">
                  {{ performanceService.getRatingLabel(row.final_rating) }}
                </el-tag>
                <span v-else>-</span>
              </template>
            </el-table-column>
            <el-table-column prop="status" label="状态" width="120">
              <template #default="{ row }">
                <el-tag :type="performanceService.getStatusType(row.status)">
                  {{ performanceService.getStatusLabel(row.status) }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="evaluator_name" label="评估人" width="100" />
            <el-table-column prop="updated_at" label="更新时间" width="120">
              <template #default="{ row }">
                {{ new Date(row.updated_at).toLocaleDateString() }}
              </template>
            </el-table-column>
            <el-table-column label="操作" width="200">
              <template #default="{ row }">
                <el-button type="primary" size="small" @click="viewEvaluationDetail(row)">
                  详情
                </el-button>
                <el-button 
                  v-if="performanceService.canSelfEvaluate(row, currentUserId)" 
                  type="warning" 
                  size="small" 
                  @click="startSelfEvaluation(row)"
                >
                  自评
                </el-button>
              </template>
            </el-table-column>
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
      </el-col>

      <!-- 绩效目标列表 -->
      <el-col :span="8">
        <el-card>
          <template #header>
            <span>绩效目标</span>
          </template>
          <el-table :data="goals" size="small" style="width: 100%">
            <el-table-column prop="period_name" label="周期" />
            <el-table-column prop="status" label="状态" width="80">
              <template #default="{ row }">
                <el-tag :type="performanceService.getStatusType(row.status)" size="small">
                  {{ performanceService.getStatusLabel(row.status) }}
                </el-tag>
              </template>
            </el-table-column>            <el-table-column label="操作" width="120">
              <template #default="{ row }">
                <el-button type="text" size="small" @click="viewGoalDetail(row)">
                  查看
                </el-button>
                <el-button 
                  v-if="row.status === 'draft'" 
                  type="primary" 
                  size="small" 
                  @click="submitGoal(row)"
                  :loading="submittingGoalId === row.id"
                >
                  提交
                </el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-card>

        <el-card style="margin-top: 20px;">
          <template #header>
            <span>绩效统计</span>
          </template>
          <div class="performance-stats">
            <div class="stat-item">
              <span class="label">评估总数：</span>
              <span class="value">{{ statistics.total_evaluations }}</span>
            </div>
            <div class="stat-item">
              <span class="label">已完成：</span>
              <span class="value">{{ statistics.completed_evaluations }}</span>
            </div>
            <div class="stat-item">
              <span class="label">完成率：</span>
              <span class="value">{{ statistics.completion_rate }}%</span>
            </div>
            <div class="stat-item">
              <span class="label">平均分：</span>
              <span class="value">{{ statistics.average_score }}</span>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 绩效详情对话框 -->
    <el-dialog v-model="detailVisible" title="绩效评估详情" width="80%">
      <div v-if="selectedEvaluation" class="evaluation-detail">
        <el-descriptions border :column="2">
          <el-descriptions-item label="评估周期">
            {{ selectedEvaluation.period_name }}
          </el-descriptions-item>
          <el-descriptions-item label="评估模板">
            {{ selectedEvaluation.template_name }}
          </el-descriptions-item>
          <el-descriptions-item label="自评分数">
            {{ performanceService.formatScore(selectedEvaluation.self_evaluation_score) }}
          </el-descriptions-item>
          <el-descriptions-item label="上级评分">
            {{ performanceService.formatScore(selectedEvaluation.manager_evaluation_score) }}
          </el-descriptions-item>
          <el-descriptions-item label="最终得分">
            {{ performanceService.formatScore(selectedEvaluation.final_score) }}
          </el-descriptions-item>
          <el-descriptions-item label="最终等级">
            <el-tag v-if="selectedEvaluation.final_rating" :type="performanceService.getRatingType(selectedEvaluation.final_rating)">
              {{ performanceService.getRatingLabel(selectedEvaluation.final_rating) }}
            </el-tag>
            <span v-else>-</span>
          </el-descriptions-item>
          <el-descriptions-item label="状态">
            <el-tag :type="performanceService.getStatusType(selectedEvaluation.status)">
              {{ performanceService.getStatusLabel(selectedEvaluation.status) }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="评估人">
            {{ selectedEvaluation.evaluator_name || '-' }}
          </el-descriptions-item>
        </el-descriptions>

        <div style="margin-top: 20px;">
          <h4>评估明细</h4>
          <el-table :data="selectedEvaluation.details" border>
            <el-table-column prop="indicator_name" label="指标名称" />
            <el-table-column prop="indicator_weight" label="权重(%)" width="100" align="center" />
            <el-table-column prop="self_score" label="自评分" width="100" align="center">
              <template #default="{ row }">
                {{ performanceService.formatScore(row.self_score) }}
              </template>
            </el-table-column>
            <el-table-column prop="manager_score" label="上级评分" width="100" align="center">
              <template #default="{ row }">
                {{ performanceService.formatScore(row.manager_score) }}
              </template>
            </el-table-column>
            <el-table-column prop="final_score" label="最终分数" width="100" align="center">
              <template #default="{ row }">
                {{ performanceService.formatScore(row.final_score) }}
              </template>
            </el-table-column>
          </el-table>
        </div>

        <div style="margin-top: 20px;" v-if="selectedEvaluation.self_evaluation_comment">
          <h4>自评意见</h4>
          <p>{{ selectedEvaluation.self_evaluation_comment }}</p>
        </div>

        <div style="margin-top: 20px;" v-if="selectedEvaluation.manager_evaluation_comment">
          <h4>上级评估意见</h4>
          <p>{{ selectedEvaluation.manager_evaluation_comment }}</p>
        </div>
      </div>
      <template #footer>
        <el-button @click="detailVisible = false">关闭</el-button>
      </template>
    </el-dialog>

    <!-- 自评对话框 -->
    <el-dialog v-model="selfEvaluationVisible" title="绩效自评" width="80%">
      <div v-if="currentEvaluation">
        <el-form :model="selfEvaluationForm" label-width="120px">
          <el-form-item label="总体自评分数">
            <el-input-number 
              v-model="selfEvaluationForm.self_evaluation_score" 
              :min="0" 
              :max="100" 
              :precision="1"
            />
          </el-form-item>
          <el-form-item label="自评意见">
            <el-input 
              v-model="selfEvaluationForm.self_evaluation_comment" 
              type="textarea" 
              :rows="4"
              placeholder="请输入自评意见..."
            />
          </el-form-item>
        </el-form>

        <h4>指标评分</h4>
        <el-table :data="selfEvaluationForm.details" border>
          <el-table-column prop="indicator_name" label="指标名称" />
          <el-table-column prop="indicator_description" label="指标描述" />
          <el-table-column prop="indicator_weight" label="权重(%)" width="100" align="center" />
          <el-table-column label="自评分数" width="150">
            <template #default="{ row, $index }">
              <el-input-number 
                v-model="row.self_score" 
                :min="0" 
                :max="row.max_score || 100" 
                :precision="1"
                size="small"
              />
            </template>
          </el-table-column>
          <el-table-column label="自评说明" width="200">
            <template #default="{ row, $index }">
              <el-input 
                v-model="row.self_comment" 
                type="textarea" 
                :rows="2"
                size="small"
                placeholder="说明..."
              />
            </template>
          </el-table-column>
        </el-table>
      </div>
      <template #footer>
        <el-button @click="selfEvaluationVisible = false">取消</el-button>
        <el-button type="primary" @click="submitSelfEvaluation" :loading="submitting">提交自评</el-button>
      </template>
    </el-dialog>

    <!-- 创建目标对话框 -->
    <el-dialog v-model="createGoalVisible" title="创建绩效目标" width="60%">
      <el-form :model="goalForm" label-width="120px">
        <el-form-item label="评估周期" required>
          <el-select v-model="goalForm.period" placeholder="选择评估周期">
            <el-option
              v-for="period in periods"
              :key="period.id"
              :label="period.name"
              :value="period.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="评估模板" required>
          <el-select v-model="goalForm.template" placeholder="选择评估模板" @change="onTemplateChange">
            <el-option
              v-for="template in templates"
              :key="template.id"
              :label="template.name"
              :value="template.id"
            />
          </el-select>
        </el-form-item>
      </el-form>

      <div v-if="goalForm.details.length > 0">
        <h4>目标设定</h4>
        <el-table :data="goalForm.details" border>
          <el-table-column prop="indicator_name" label="指标名称" />
          <el-table-column prop="indicator_description" label="指标描述" />
          <el-table-column label="目标值" width="200">
            <template #default="{ row, $index }">
              <el-input 
                v-model="row.target_value" 
                placeholder="设定目标值..."
              />
            </template>
          </el-table-column>
          <el-table-column prop="weight" label="权重(%)" width="100" align="center" />
        </el-table>
      </div>

      <template #footer>
        <el-button @click="createGoalVisible = false">取消</el-button>
        <el-button type="primary" @click="createGoal" :loading="submitting">创建目标</el-button>
      </template>
    </el-dialog>

    <!-- 目标详情对话框 -->
    <el-dialog v-model="goalDetailVisible" title="绩效目标详情" width="80%">
      <div v-if="selectedGoal" class="goal-detail">
        <el-descriptions border :column="2">
          <el-descriptions-item label="评估周期">
            {{ selectedGoal.period_name }}
          </el-descriptions-item>
          <el-descriptions-item label="评估模板">
            {{ selectedGoal.template_name }}
          </el-descriptions-item>
          <el-descriptions-item label="状态">
            <el-tag :type="performanceService.getStatusType(selectedGoal.status)">
              {{ performanceService.getStatusLabel(selectedGoal.status) }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="创建时间">
            {{ new Date(selectedGoal.created_at).toLocaleString() }}
          </el-descriptions-item>
          <el-descriptions-item label="更新时间">
            {{ new Date(selectedGoal.updated_at).toLocaleString() }}
          </el-descriptions-item>
        </el-descriptions>

        <div style="margin-top: 20px;">
          <h4>指标目标值</h4>
          <el-table :data="selectedGoal.details" border>
            <el-table-column prop="indicator_name" label="指标名称" />
            <el-table-column prop="indicator_description" label="指标描述" />
            <el-table-column prop="target_value" label="目标值" width="120" align="center">
              <template #default="{ row }">
                {{ row.target_value }}
              </template>
            </el-table-column>
            <el-table-column prop="weight" label="权重(%)" width="100" align="center" />
          </el-table>
        </div>
      </div>
      <template #footer>
        <el-button @click="goalDetailVisible = false">关闭</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, onActivated, computed, nextTick } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import * as echarts from 'echarts'
import performanceService from '../../services/performance'
import { useAuthStore } from '@/stores/counter'
import type { 
  PerformanceEvaluation, 
  PerformancePeriod, 
  PerformanceTemplate,
  PerformanceGoal,
  PerformanceStatistics
} from '../../services/performance'

// 获取当前用户信息
const authStore = useAuthStore()
const currentUserId = computed(() => authStore.user?.id)

// 类型定义
interface FilterForm {
  period_id?: number
  status: string
}

interface SelfEvaluationForm {
  self_evaluation_score?: number
  self_evaluation_comment: string
  details: Array<{
    id: number
    indicator_name?: string
    indicator_description?: string
    indicator_weight?: number
    max_score?: number
    self_score?: number
    self_comment: string
  }>
}

interface GoalForm {
  period?: number
  template?: number
  details: Array<{
    indicator: number
    indicator_name?: string
    indicator_description?: string
    target_value: string
    weight: number
  }>
}

const loading = ref(false)
const submitting = ref(false)
const submittingGoalId = ref<number | null>(null)
const currentPage = ref(1)
const pageSize = ref(10)
const total = ref(0)

// 对话框状态
const detailVisible = ref(false)
const goalDetailVisible = ref(false)
const selfEvaluationVisible = ref(false)
const createGoalVisible = ref(false)

// 选中的数据
const selectedEvaluation = ref<PerformanceEvaluation | null>(null)
const selectedGoal = ref<PerformanceGoal | null>(null)
const currentEvaluation = ref<PerformanceEvaluation | null>(null)

// 图表引用
const radarChartRef = ref()
let radarChartInstance: echarts.ECharts | null = null

// 表单数据
const filterForm = reactive<FilterForm>({
  period_id: undefined,
  status: ''
})

const selfEvaluationForm = reactive<SelfEvaluationForm>({
  self_evaluation_score: undefined,
  self_evaluation_comment: '',
  details: []
})

const goalForm = reactive<GoalForm>({
  period: undefined,
  template: undefined,
  details: []
})

// 数据状态
const latestEvaluation = ref<PerformanceEvaluation | null>(null)
const evaluations = ref<PerformanceEvaluation[]>([])
const goals = ref<PerformanceGoal[]>([])
const periods = ref<PerformancePeriod[]>([])
const templates = ref<PerformanceTemplate[]>([])
const statistics = reactive<PerformanceStatistics>({
  total_evaluations: 0,
  completed_evaluations: 0,
  completion_rate: 0,
  average_score: 0,
  rating_distribution: {},
  department_stats: []
})

// 筛选变化处理
const handleFilterChange = () => {
  loadEvaluations()
}

// 加载数据方法
const loadPeriods = async () => {
  try {
    periods.value = await performanceService.getPeriods()
  } catch (error: any) {
    console.error('加载绩效周期失败:', error)
    ElMessage.error('加载绩效周期失败')
  }
}

const loadTemplates = async () => {
  try {
    templates.value = await performanceService.getTemplates()
  } catch (error: any) {
    console.error('加载绩效模板失败:', error)
    ElMessage.error('加载绩效模板失败')
  }
}

const loadEvaluations = async () => {
  loading.value = true
  try {
    const params = {
      period_id: filterForm.period_id,
      status: filterForm.status || undefined,
      page: currentPage.value,
      page_size: pageSize.value
    }
    
    const response = await performanceService.getMyEvaluations(params)
    evaluations.value = response
    
    // 获取最新评估
    if (response.length > 0) {
      latestEvaluation.value = response[0]
      nextTick(() => {
        initRadarChart()
      })
    }
  } catch (error: any) {
    console.error('加载绩效评估失败:', error)
    ElMessage.error('加载绩效评估失败')
  } finally {
    loading.value = false
  }
}

const loadGoals = async () => {
  try {
    goals.value = await performanceService.getMyGoals()
  } catch (error: any) {
    console.error('加载绩效目标失败:', error)
    ElMessage.error('加载绩效目标失败')
  }
}

const loadStatistics = async () => {
  try {
    const stats = await performanceService.getStatistics({
      period_id: filterForm.period_id
    })
    Object.assign(statistics, stats)
  } catch (error: any) {
    console.error('加载绩效统计失败:', error)
    ElMessage.error('加载绩效统计失败')
  }
}

// 流程计算方法
const getCurrentStep = (): number => {
  if (!latestEvaluation.value) return 0
  const status = latestEvaluation.value.status
  
  // 返回当前进度（0-3）
  // 注意：PerformanceEvaluation 只有这些状态：draft | self_evaluated | manager_evaluated | finalized
  if (status === 'draft') return 0
  if (status === 'self_evaluated') return 1
  if (status === 'manager_evaluated') return 2
  if (status === 'finalized') return 3
  return 0
}

const getStepStatus = (step: string): string => {
  if (!latestEvaluation.value) return 'wait'
  const status = latestEvaluation.value.status as 'draft' | 'self_evaluated' | 'manager_evaluated' | 'finalized'
  
  switch (step) {
    case 'goal':
      // 目标设定完成：从 draft 到 manager_evaluated 及以后
      if (status === 'draft') return 'process'
      if (['self_evaluated', 'manager_evaluated', 'finalized'].includes(status)) return 'finish'
      return 'wait'
      
    case 'self_eval':
      // 自评：从 draft 到 finalized
      if (status === 'draft') return 'wait'
      if (status === 'self_evaluated' || status === 'manager_evaluated' || status === 'finalized') return 'process'
      if (status === 'finalized') return 'finish'
      return 'wait'
      
    case 'manager_eval':
      // 经理评估：从 self_evaluated 到 finalized
      if (status === 'self_evaluated' || status === 'manager_evaluated') return 'process'
      if (status === 'finalized') return 'finish'
      return 'wait'
      
    case 'complete':
      // 完成：finalized
      if (status === 'finalized') return 'finish'
      return 'wait'
      
    default:
      return 'wait'
  }
}

const nextActionText = computed(() => {
  if (!latestEvaluation.value) return ''
  
  const status = latestEvaluation.value.status as 'draft' | 'self_evaluated' | 'manager_evaluated' | 'finalized'
  
  switch (status) {
    case 'draft':
      return '📝 下一步：请完成目标设定，然后点击"提交"按钮提交审批'
    case 'self_evaluated':
      return '⌛ 自评已完成，等待经理进行上级评估。您可以查看自评详情'
    case 'manager_evaluated':
      return '📊 系统正在计算最终分数...'
    case 'finalized':
      return '🎉 绩效评估已完成！您可以查看最终评分和等级'
    default:
      return ''
  }
})

// 事件处理方法
const showCreateGoalDialog = () => {
  goalForm.period = undefined
  goalForm.template = undefined
  goalForm.details = []
  createGoalVisible.value = true
}

const viewEvaluationDetail = (evaluation: PerformanceEvaluation) => {
  selectedEvaluation.value = evaluation
  detailVisible.value = true
}

const viewGoalDetail = (goal: PerformanceGoal) => {
  selectedGoal.value = goal
  goalDetailVisible.value = true
}

const startSelfEvaluation = (evaluation: PerformanceEvaluation) => {
  currentEvaluation.value = evaluation
  
  // 初始化自评表单
  selfEvaluationForm.self_evaluation_score = evaluation.self_evaluation_score
  selfEvaluationForm.self_evaluation_comment = evaluation.self_evaluation_comment || ''
  selfEvaluationForm.details = evaluation.details.map(detail => ({
    id: detail.id,
    indicator_name: detail.indicator_name,
    indicator_description: detail.indicator_description,
    indicator_weight: detail.indicator_weight,
    max_score: detail.max_score,
    self_score: detail.self_score,
    self_comment: detail.self_comment || ''
  }))
  
  selfEvaluationVisible.value = true
}

const submitSelfEvaluation = async () => {
  if (!currentEvaluation.value) return
  
  submitting.value = true
  try {
    await performanceService.selfEvaluate(currentEvaluation.value.id, {
      self_evaluation_score: selfEvaluationForm.self_evaluation_score,
      self_evaluation_comment: selfEvaluationForm.self_evaluation_comment,
      details: selfEvaluationForm.details.map(detail => ({
        id: detail.id,
        self_score: detail.self_score,
        self_comment: detail.self_comment
      }))
    })
    
    ElMessage.success('自评提交成功')
    selfEvaluationVisible.value = false
    
    // 使用 await 确保数据加载完成后再结束 loading 状态
    await loadEvaluations()
    await loadStatistics()
  } catch (error: any) {
    console.error('提交自评失败:', error)
    ElMessage.error('提交自评失败')
  } finally {
    submitting.value = false
  }
}

const onTemplateChange = async (templateId: number) => {
  const template = templates.value.find(t => t.id === templateId)
  if (template) {
    goalForm.details = template.indicators.map(indicator => ({
      indicator: indicator.id,
      indicator_name: indicator.name,
      indicator_description: indicator.description,
      target_value: '',
      weight: indicator.weight
    }))
  }
}

const createGoal = async () => {
  if (!goalForm.period || !goalForm.template) {
    ElMessage.warning('请选择评估周期和模板')
    return
  }
  
  submitting.value = true
  try {
    await performanceService.createGoal({
      period: goalForm.period,
      template: goalForm.template,
      details: goalForm.details
    })
      ElMessage.success('绩效目标创建成功')
    createGoalVisible.value = false
    loadGoals()  } catch (error: any) {
    console.error('创建绩效目标失败:', error)
      // 提取具体的错误信息
    let errorMessage = '创建绩效目标失败'
    if (error.response && error.response.data) {
      if (typeof error.response.data === 'string') {
        errorMessage = error.response.data
      } else if (error.response.data.error) {
        errorMessage = error.response.data.error
      } else if (error.response.data.detail) {
        errorMessage = error.response.data.detail
      } else if (error.response.data.message) {
        errorMessage = error.response.data.message
      } else if (error.response.data.non_field_errors) {
        errorMessage = error.response.data.non_field_errors[0]
      } else {
        errorMessage = `创建失败: ${JSON.stringify(error.response.data)}`
      }
    } else if (error.message) {
      errorMessage = error.message
    }
    
    ElMessage.error(errorMessage)
  }finally {
    submitting.value = false
  }
}

// 提交绩效目标
const submitGoal = async (goal: any) => {
  try {
    await ElMessageBox.confirm('确定要提交这个绩效目标吗？提交后将无法修改。', '确认提交', {
      type: 'warning'
    })
    
    submittingGoalId.value = goal.id
    
    await performanceService.submitGoal(goal.id)
    ElMessage.success('绩效目标提交成功，等待审批')
    
    // 重新加载目标列表
    loadGoals()
  } catch (error: any) {
    if (error !== 'cancel') { // 用户取消不显示错误
      console.error('提交绩效目标失败:', error)
      let errorMessage = '提交失败'
      if (error.response?.data?.error) {
        errorMessage = error.response.data.error
      } else if (error.response?.data?.message) {
        errorMessage = error.response.data.message
      }
      ElMessage.error(errorMessage)
    }
  } finally {
    submittingGoalId.value = null
  }
}

// 分页处理
const handleSizeChange = (val: number) => {
  pageSize.value = val
  loadEvaluations()
}

const handleCurrentChange = (val: number) => {
  currentPage.value = val
  loadEvaluations()
}

// 初始化雷达图
const initRadarChart = () => {
  if (!radarChartRef.value || !latestEvaluation.value || !latestEvaluation.value.details.length) return
  
  radarChartInstance = echarts.init(radarChartRef.value)
  
  const indicators = latestEvaluation.value.details.map(detail => ({
    name: detail.indicator_name || '',
    max: detail.max_score || 100
  }))
  
  const selfData = latestEvaluation.value.details.map(detail => detail.self_score || 0)
  const managerData = latestEvaluation.value.details.map(detail => detail.manager_score || 0)
  
  const option = {
    title: {
      text: '绩效能力雷达图',
      left: 'center'
    },
    tooltip: {
      trigger: 'item'
    },
    legend: {
      orient: 'vertical',
      left: 'left',
      data: ['自评分数', '上级评分']
    },
    radar: {
      indicator: indicators
    },
    series: [
      {
        name: '绩效评分',
        type: 'radar',
        data: [
          {
            value: selfData,
            name: '自评分数',
            itemStyle: { color: '#409EFF' }
          },
          {
            value: managerData,
            name: '上级评分',
            itemStyle: { color: '#67C23A' }
          }
        ]
      }
    ]
  }
  
  radarChartInstance.setOption(option)
}

// 监听窗口大小变化
const handleResize = () => {
  if (radarChartInstance) {
    radarChartInstance.resize()
  }
}

onMounted(() => {
  // 加载基础数据
  loadPeriods()
  loadTemplates()
  loadEvaluations()
  loadGoals()
  loadStatistics()
  
  nextTick(() => {
    window.addEventListener('resize', handleResize)
  })
})

// 当组件被 keep-alive 缓存后重新激活时，重新加载数据
onActivated(() => {
  console.log('[PerformanceView] 页面激活，重新加载数据')
  loadEvaluations()
  loadGoals()
  loadStatistics()
})
</script>

<style scoped>
.performance {
  padding: 20px;
}

.filter-card {
  margin-bottom: 20px;
}

.filter-form {
  margin: 0;
}

.latest-performance {
  margin-bottom: 20px;
}

.performance-item {
  text-align: center;
  padding: 20px;
}

.performance-item.total .score {
  color: #409EFF;
  font-size: 36px;
}

.performance-item.work .score {
  color: #67C23A;
}

.performance-item.efficiency .score {
  color: #E6A23C;
}

.performance-item.teamwork .score {
  color: #F56C6C;
}

.performance-item .score {
  font-size: 28px;
  font-weight: bold;
  margin-bottom: 10px;
}

.performance-item .label {
  color: #909399;
  font-size: 14px;
  margin-bottom: 5px;
}

.performance-item .grade {
  font-size: 16px;
  font-weight: bold;
  color: #409EFF;
}

.chart-card {
  margin-bottom: 20px;
}

.pagination {
  margin-top: 20px;
  text-align: right;
}

.performance-stats {
  padding: 10px 0;
}

.stat-item {
  display: flex;
  justify-content: space-between;
  margin-bottom: 15px;
}

.stat-item .label {
  color: #909399;
}

.stat-item .value {
  color: #303133;
  font-weight: 500;
}

.performance-detail {
  padding: 20px 0;
}
</style>
