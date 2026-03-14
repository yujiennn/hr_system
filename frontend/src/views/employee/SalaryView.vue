<template>
  <div class="salary">
    <el-card class="filter-card">
      <el-form :inline="true" :model="filterForm" class="filter-form">
        <el-form-item label="年份">
          <el-select v-model="filterForm.year" @change="handleFilterChange">
            <el-option
              v-for="year in yearOptions"
              :key="year"
              :label="year"
              :value="year"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="月份">
          <el-select v-model="filterForm.month" @change="handleFilterChange">
            <el-option label="全年" value="" />
            <el-option
              v-for="month in 12"
              :key="month"
              :label="`${month}月`"
              :value="month"
            />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="exportSalary">导出工资单</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 当前月份薪资概览 -->
    <el-card class="current-salary" v-if="currentSalary">
      <template #header>
        <span>{{ currentSalary.year }}年{{ currentSalary.month }}月薪资</span>
      </template>
      <el-row :gutter="20">
        <el-col :span="6">
          <div class="salary-item gross">
            <div class="amount">¥{{ formatAmount(currentSalary.gross_salary) }}</div>
            <div class="label">应发工资</div>
          </div>
        </el-col>
        <el-col :span="6">
          <div class="salary-item deduction">
            <div class="amount">¥{{ currentTotalDeductions }}</div>
            <div class="label">扣除合计</div>
          </div>
        </el-col>
        <el-col :span="6">
          <div class="salary-item net">
            <div class="amount">¥{{ formatAmount(currentSalary.net_salary) }}</div>
            <div class="label">实发工资</div>
          </div>
        </el-col>
        <el-col :span="6">
          <div class="salary-item status">
            <div class="status-text">
              <el-tag :type="getSalaryStatusType(currentSalary.status)">
                {{ getSalaryStatusLabel(currentSalary.status) }}
              </el-tag>
            </div>
            <div class="label">发放状态</div>
          </div>
        </el-col>
      </el-row>
    </el-card>

    <!-- 薪资详情 -->
    <el-card v-if="currentSalary">
      <template #header>
        <span>薪资详情</span>
      </template>
      <el-row :gutter="20">
        <el-col :span="12">
          <h4>收入项目</h4>
          <el-table :data="incomeItems" style="width: 100%">
            <el-table-column prop="name" label="项目" />
            <el-table-column prop="amount" label="金额" align="right">
              <template #default="{ row }">
                ¥{{ formatAmount(row.amount) }}
              </template>
            </el-table-column>
          </el-table>
        </el-col>
        <el-col :span="12">
          <h4>扣除项目</h4>
          <el-table :data="deductionItems" style="width: 100%">
            <el-table-column prop="name" label="项目" />
            <el-table-column prop="amount" label="金额" align="right">
              <template #default="{ row }">
                ¥{{ formatAmount(row.amount) }}
              </template>
            </el-table-column>
          </el-table>
        </el-col>
      </el-row>
    </el-card>

    <!-- 历史薪资记录 -->
    <el-card>
      <template #header>
        <span>历史薪资记录</span>
      </template>
      <el-table :data="salaryRecords" v-loading="loading">
        <el-table-column prop="year" label="年份" width="100" />
        <el-table-column prop="month" label="月份" width="100">
          <template #default="{ row }">
            {{ row.month }}月
          </template>
        </el-table-column>
        <el-table-column prop="gross_salary" label="应发工资" align="right" width="120">
          <template #default="{ row }">
            ¥{{ formatAmount(row.gross_salary) }}
          </template>
        </el-table-column>        <el-table-column label="扣除合计" align="right" width="120">
          <template #default="{ row }">
            ¥{{ formatAmount(getTotalDeductions(row as SalaryRecord)) }}
          </template>
        </el-table-column>
        <el-table-column prop="net_salary" label="实发工资" align="right" width="120">
          <template #default="{ row }">
            ¥{{ formatAmount(row.net_salary) }}
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getSalaryStatusType(row.status)">
              {{ getSalaryStatusLabel(row.status) }}
            </el-tag>
          </template>
        </el-table-column>        <el-table-column prop="pay_date" label="发放日期" width="120">
          <template #default="{ row }">
            {{ row.pay_date || '-' }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="120">
          <template #default="{ row }">
            <el-button type="primary" size="small" @click="viewSalaryDetail(row)">
              查看详情
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

    <!-- 薪资趋势图 -->
    <el-card class="chart-card">
      <template #header>
        <span>薪资趋势</span>
      </template>
      <div ref="chartRef" style="height: 400px;"></div>
    </el-card>

    <!-- 薪资详情对话框 -->
    <el-dialog v-model="detailVisible" title="薪资详情" width="70%">
      <div v-if="selectedSalary" class="salary-detail">
        <!-- 基本信息 -->
        <el-descriptions title="基本信息" border :column="2">
          <el-descriptions-item label="年月">
            {{ selectedSalary.year }}年{{ selectedSalary.month }}月
          </el-descriptions-item>
          <el-descriptions-item label="状态">
            <el-tag :type="getSalaryStatusType(selectedSalary.status)">
              {{ getSalaryStatusLabel(selectedSalary.status) }}
            </el-tag>
          </el-descriptions-item>
        </el-descriptions>
        
        <!-- 绩效信息 -->
        <el-descriptions title="绩效信息" border :column="3" style="margin-top: 20px;">
          <el-descriptions-item label="绩效得分">
            {{ selectedSalary.performance_score ? selectedSalary.performance_score.toFixed(1) : '未评定' }}
          </el-descriptions-item>
          <el-descriptions-item label="绩效等级">
            <el-tag v-if="selectedSalary.performance_level" 
                   :type="getPerformanceLevelType(selectedSalary.performance_level)">
              {{ selectedSalary.performance_level_display || selectedSalary.performance_level }}
            </el-tag>
            <span v-else>未评定</span>
          </el-descriptions-item>
          <el-descriptions-item label="绩效系数">
            {{ selectedSalary.performance_coefficient || 1.0 }}
          </el-descriptions-item>
          <el-descriptions-item label="绩效奖金">
            ¥{{ formatAmount(selectedSalary.performance_bonus) }}
          </el-descriptions-item>
          <el-descriptions-item label="考核周期">
            {{ selectedSalary.performance_period_name || '-' }}
          </el-descriptions-item>
        </el-descriptions>
        
        <!-- 考勤信息 -->
        <el-descriptions title="考勤信息" border :column="4" style="margin-top: 20px;">
          <el-descriptions-item label="全勤状态">
            <el-tag :type="selectedSalary.is_full_attendance ? 'success' : 'info'">
              {{ selectedSalary.is_full_attendance ? '全勤' : '非全勤' }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="全勤奖">
            ¥{{ formatAmount(selectedSalary.full_attendance_bonus) }}
          </el-descriptions-item>
          <el-descriptions-item label="迟到次数">
            {{ selectedSalary.late_count || 0 }} 次
          </el-descriptions-item>
          <el-descriptions-item label="早退次数">
            {{ selectedSalary.early_leave_count || 0 }} 次
          </el-descriptions-item>
          <el-descriptions-item label="缺勤次数">
            {{ selectedSalary.absence_count || 0 }} 次
          </el-descriptions-item>
          <el-descriptions-item label="请假天数">
            {{ selectedSalary.leave_days || 0 }} 天
          </el-descriptions-item>
          <el-descriptions-item label="病假天数">
            {{ selectedSalary.sick_leave_days || 0 }} 天
          </el-descriptions-item>
          <el-descriptions-item label="事假天数">
            {{ selectedSalary.personal_leave_days || 0 }} 天
          </el-descriptions-item>
        </el-descriptions>
        
        <!-- 薪资明细 -->
        <el-descriptions title="薪资明细" border :column="2" style="margin-top: 20px;">
          <el-descriptions-item label="基本工资">
            ¥{{ formatAmount(selectedSalary.basic_salary) }}
          </el-descriptions-item>
          <el-descriptions-item label="绩效奖金">
            ¥{{ formatAmount(selectedSalary.performance_bonus) }}
          </el-descriptions-item>
          <el-descriptions-item label="加班费">
            ¥{{ formatAmount(selectedSalary.overtime_pay) }}
          </el-descriptions-item>
          <el-descriptions-item label="津贴补助">
            ¥{{ formatAmount(selectedSalary.allowances) }}
          </el-descriptions-item>
          <el-descriptions-item label="全勤奖">
            ¥{{ formatAmount(selectedSalary.full_attendance_bonus) }}
          </el-descriptions-item>
          <el-descriptions-item label="应发工资">
            <span style="color: #67C23A; font-weight: bold;">
              ¥{{ formatAmount(selectedSalary.gross_salary) }}
            </span>
          </el-descriptions-item>
        </el-descriptions>
        
        <!-- 扣款明细 -->
        <el-descriptions title="扣款明细" border :column="2" style="margin-top: 20px;">
          <el-descriptions-item label="社保个人">
            ¥{{ formatAmount(selectedSalary.social_security) }}
          </el-descriptions-item>
          <el-descriptions-item label="公积金个人">
            ¥{{ formatAmount(selectedSalary.housing_fund) }}
          </el-descriptions-item>
          <el-descriptions-item label="个人所得税">
            ¥{{ formatAmount(selectedSalary.income_tax) }}
          </el-descriptions-item>
          <el-descriptions-item label="其他扣除">
            ¥{{ formatAmount(selectedSalary.other_deductions) }}
          </el-descriptions-item>
          <el-descriptions-item label="请假扣款">
            <span style="color: #F56C6C;">
              ¥{{ formatAmount(selectedSalary.leave_deduction) }}
            </span>
          </el-descriptions-item>
          <el-descriptions-item label="迟到扣款">
            <span style="color: #F56C6C;">
              ¥{{ formatAmount(selectedSalary.late_deduction) }}
            </span>
          </el-descriptions-item>
          <el-descriptions-item label="缺勤扣款">
            <span style="color: #F56C6C;">
              ¥{{ formatAmount(selectedSalary.absence_deduction) }}
            </span>
          </el-descriptions-item>
          <el-descriptions-item label="扣除合计">
            <span style="color: #F56C6C; font-weight: bold;">
              ¥{{ formatAmount(getTotalDeductions(selectedSalary)) }}
            </span>
          </el-descriptions-item>
        </el-descriptions>
        
        <!-- 薪资计算说明 -->
        <el-card style="margin-top: 20px;">
          <template #header>
            <span>薪资计算说明</span>
          </template>
          
          <div v-if="selectedSalary && (selectedSalary as any).salary_config" class="calc-explanation">
            <!-- 应发工资计算 -->
            <div class="calc-section">
              <h4>📊 应发工资计算</h4>
              <div class="calc-formula">
                <p><strong>基本公式：</strong></p>
                <p style="background: #f5f7fa; padding: 10px; border-radius: 4px; margin: 10px 0;">
                  应发工资 = 基本工资 + 绩效奖金 + 加班费 + 津贴补助 + 全勤奖
                </p>
              </div>
              
              <div class="calc-detail">
                <p><strong>本月计算过程：</strong></p>
                <table class="calc-table">
                  <tbody>
                    <tr>
                      <td>基本工资</td>
                      <td class="value">¥{{ formatAmount(selectedSalary.basic_salary) }}</td>
                    </tr>
                    <tr>
                      <td>绩效奖金</td>
                      <td class="value">
                        ¥{{ formatAmount(selectedSalary.performance_bonus) }}
                        <span class="note">
                          (基本工资 × {{ selectedSalary.performance_coefficient }} × {{ ((selectedSalary.salary_config?.performance_bonus_base_rate || 0) * 100).toFixed(0) }}%)
                        </span>
                      </td>
                    </tr>
                    <tr>
                      <td>加班费</td>
                      <td class="value">¥{{ formatAmount(selectedSalary.overtime_pay) }}</td>
                    </tr>
                    <tr>
                      <td>津贴补助</td>
                      <td class="value">¥{{ formatAmount(selectedSalary.allowances) }}</td>
                    </tr>
                    <tr v-if="(selectedSalary?.full_attendance_bonus || 0) > 0">
                      <td>全勤奖</td>
                      <td class="value">¥{{ formatAmount(selectedSalary.full_attendance_bonus) }}</td>
                    </tr>
                    <tr class="total-row">
                      <td><strong>应发工资合计</strong></td>
                      <td class="value"><strong>¥{{ formatAmount(selectedSalary.gross_salary) }}</strong></td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>
            
            <!-- 绩效系数说明 -->
            <div class="calc-section" style="margin-top: 20px;">
              <h4>⭐ 绩效等级说明</h4>
              <div class="calc-detail">
                <table class="calc-table">
                  <thead>
                    <tr>
                      <th>等级</th>
                      <th>绩效系数</th>
                      <th>说明</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr :class="{ highlight: selectedSalary.performance_level === 'A' }">
                      <td>A 优秀</td>
                      <td>{{ selectedSalary.salary_config?.performance_level_a_coefficient || '-' }}</td>
                      <td>绩效得分 ≥ 90 分</td>
                    </tr>
                    <tr :class="{ highlight: selectedSalary.performance_level === 'B' }">
                      <td>B 良好</td>
                      <td>{{ selectedSalary.salary_config?.performance_level_b_coefficient || '-' }}</td>
                      <td>绩效得分 ≥ 80 分</td>
                    </tr>
                    <tr :class="{ highlight: selectedSalary.performance_level === 'C' }">
                      <td>C 合格</td>
                      <td>{{ selectedSalary.salary_config?.performance_level_c_coefficient || '-' }}</td>
                      <td>绩效得分 ≥ 60 分</td>
                    </tr>
                    <tr :class="{ highlight: selectedSalary.performance_level === 'D' }">
                      <td>D 待改进</td>
                      <td>{{ selectedSalary.salary_config?.performance_level_d_coefficient || '-' }}</td>
                      <td>绩效得分 < 60 分</td>
                    </tr>
                  </tbody>
                </table>
                <p style="margin-top: 10px; color: #606266; font-size: 12px;">
                  本月绩效等级: <el-tag :type="getPerformanceLevelType(selectedSalary.performance_level)">
                    {{ selectedSalary.performance_level_display || selectedSalary.performance_level || '未评定' }}
                  </el-tag>
                </p>
              </div>
            </div>
            
            <!-- 扣款规则说明 -->
            <div class="calc-section" style="margin-top: 20px;">
              <h4>📋 扣款规则说明</h4>
              <div class="calc-detail">
                <p><strong>迟到扣款规则：</strong></p>
                <ul>
                  <li>迟到 ≤ {{ selectedSalary.salary_config?.late_threshold_minutes || '-' }} 分钟：扣 ¥{{ formatAmount(selectedSalary.salary_config?.late_deduction_minor || 0) }}</li>
                  <li>迟到 > {{ selectedSalary.salary_config?.late_threshold_minutes || '-' }} 分钟：扣 ¥{{ formatAmount(selectedSalary.salary_config?.late_deduction_major || 0) }}</li>
                </ul>
                <p><strong>请假扣款规则：</strong></p>
                <ul>
                  <li>病假：超出 2 天后，按 {{ ((selectedSalary.salary_config?.sick_leave_deduction_rate || 0) * 100).toFixed(0) }}% 日薪扣除</li>
                  <li>事假：按 {{ ((selectedSalary.salary_config?.personal_leave_deduction_rate || 0) * 100).toFixed(0) }}% 日薪扣除</li>
                  <li>缺勤：按 100% 日薪扣除</li>
                </ul>
                <p style="margin-top: 10px; color: #606266; font-size: 12px;">
                  日薪 = 基本工资 ÷ {{ selectedSalary.salary_config?.work_days_per_month || 22 }} 天
                </p>
              </div>
            </div>
            
            <!-- 全勤奖说明 -->
            <div class="calc-section" style="margin-top: 20px;">
              <h4>🎁 全勤奖说明</h4>
              <div class="calc-detail">
                <p>当月无迟到、早退、缺勤、请假，即可获得全勤奖：<strong>¥{{ formatAmount(selectedSalary.salary_config?.full_attendance_bonus || 0) }}</strong></p>
                <p style="margin-top: 10px;">本月全勤状态：
                  <el-tag :type="selectedSalary.is_full_attendance ? 'success' : 'info'">
                    {{ selectedSalary.is_full_attendance ? '✓ 已获得全勤奖' : '✗ 未获得全勤奖' }}
                  </el-tag>
                </p>
              </div>
            </div>
          </div>
        </el-card>
        
        <!-- 最终结算 -->
        <el-descriptions title="最终结算" border :column="2" style="margin-top: 20px;">
          <el-descriptions-item label="实发工资">
            <span style="color: #409EFF; font-weight: bold; font-size: 18px;">
              ¥{{ formatAmount(selectedSalary.net_salary) }}
            </span>
          </el-descriptions-item>
          <el-descriptions-item label="发放日期">
            {{ selectedSalary.pay_date || '未发放' }}
          </el-descriptions-item>
        </el-descriptions>
      </div>
      <template #footer>
        <el-button type="primary" @click="exportSingleSalary">导出工资单</el-button>
        <el-button @click="detailVisible = false">关闭</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, onActivated, computed, nextTick, watch } from 'vue'
import { ElMessage } from 'element-plus'
import * as echarts from 'echarts'
import salaryService, { type SalaryRecord } from '../../services/salary'

// 类型定义
interface FilterForm {
  year: number
  month: string
}

interface IncomeItem {
  name: string
  amount: number
}

const loading = ref(false)
const currentPage = ref(1)
const pageSize = ref(10)
const total = ref(0)
const detailVisible = ref(false)
const selectedSalary = ref<SalaryRecord | null>(null)
const chartRef = ref()
let chartInstance: echarts.ECharts | null = null

const filterForm = reactive<FilterForm>({
  year: new Date().getFullYear(),
  month: ''
})

const currentSalary = ref<SalaryRecord | null>(null)
const salaryRecords = ref<SalaryRecord[]>([])

// 年份选项
const yearOptions = computed(() => {
  const currentYear = new Date().getFullYear()
  const years = []
  for (let i = currentYear; i >= currentYear - 10; i--) {
    years.push(i)
  }
  return years
})

// 收入项目
const incomeItems = computed(() => {
  if (!currentSalary.value) return []
  return [
    { name: '基本工资', amount: currentSalary.value.basic_salary },
    { name: '绩效奖金', amount: currentSalary.value.performance_bonus },
    { name: '加班费', amount: currentSalary.value.overtime_pay },
    { name: '津贴补助', amount: currentSalary.value.allowances },
    { name: '全勤奖', amount: currentSalary.value.full_attendance_bonus || 0 }
  ].filter(item => item.amount > 0)
})

// 扣除项目
const deductionItems = computed(() => {
  if (!currentSalary.value) return []
  return [
    { name: '社保个人', amount: currentSalary.value.social_security },
    { name: '公积金个人', amount: currentSalary.value.housing_fund },
    { name: '个人所得税', amount: currentSalary.value.income_tax },
    { name: '其他扣除', amount: currentSalary.value.other_deductions },
    { name: '请假扣款', amount: currentSalary.value.leave_deduction || 0 },
    { name: '迟到扣款', amount: currentSalary.value.late_deduction || 0 },
    { name: '缺勤扣款', amount: currentSalary.value.absence_deduction || 0 }
  ].filter(item => item.amount > 0)
})

// 当前月份扣除合计（计算属性）
const currentTotalDeductions = computed(() => {
  if (!currentSalary.value) return '0.00'
  const total = 
    (parseFloat(currentSalary.value.social_security as any) || 0) +
    (parseFloat(currentSalary.value.housing_fund as any) || 0) +
    (parseFloat(currentSalary.value.income_tax as any) || 0) +
    (parseFloat(currentSalary.value.other_deductions as any) || 0) +
    (parseFloat(currentSalary.value.leave_deduction as any) || 0) +
    (parseFloat(currentSalary.value.late_deduction as any) || 0) +
    (parseFloat(currentSalary.value.absence_deduction as any) || 0)
  return salaryService.formatAmount(total)
})

// 格式化金额
const formatAmount = (amount: number | string | null | undefined) => {
  return salaryService.formatAmount(amount)
}

// 获取薪资状态类型
const getSalaryStatusType = (status: string) => {
  return salaryService.getSalaryStatusType(status)
}

// 获取薪资状态标签
const getSalaryStatusLabel = (status: string) => {
  return salaryService.getSalaryStatusLabel(status)
}

// 获取绩效等级类型
const getPerformanceLevelType = (level: string | null | undefined) => {
  return salaryService.getPerformanceLevelType(level)
}

// 计算扣除合计
const getTotalDeductions = (salary: SalaryRecord) => {
  return (
    (salary.social_security || 0) +
    (salary.housing_fund || 0) +
    (salary.income_tax || 0) +
    (salary.other_deductions || 0) +
    (salary.leave_deduction || 0) +
    (salary.late_deduction || 0) +
    (salary.absence_deduction || 0)
  )
}

// 筛选变化处理
const handleFilterChange = () => {
  loadSalaryRecords()
  loadCurrentSalary()
}

// 查看薪资详情
const viewSalaryDetail = (salary: any) => {
  selectedSalary.value = salary
  detailVisible.value = true
}

// 导出工资单
const exportSalary = async () => {
  try {
    await salaryService.exportSalary({
      year: filterForm.year,
      month: filterForm.month ? parseInt(filterForm.month) : undefined
    })
    ElMessage.success('工资单导出成功')
  } catch (error: any) {
    console.error('导出工资单失败:', error)
    ElMessage.error('导出工资单失败')
  }
}

// 导出单个工资单
const exportSingleSalary = async () => {
  if (!selectedSalary.value) return
  
  try {
    await salaryService.exportSingleSalary(selectedSalary.value.id)
    ElMessage.success('工资单导出成功')
  } catch (error: any) {
    console.error('导出工资单失败:', error)
    ElMessage.error('导出工资单失败')
  }
}

// 分页处理
const handleSizeChange = (val: number) => {
  pageSize.value = val
  loadSalaryRecords()
}

const handleCurrentChange = (val: number) => {
  currentPage.value = val
  loadSalaryRecords()
}

// 加载当前月份薪资
const loadCurrentSalary = async () => {
  try {
    currentSalary.value = await salaryService.getCurrentSalary()  } catch (error: any) {
    console.error('加载当前薪资失败:', error)
    ElMessage.error('加载当前薪资失败')
  }
}

// 加载薪资记录
const loadSalaryRecords = async () => {
  loading.value = true
  try {
    const params = {
      year: filterForm.year,
      month: filterForm.month ? parseInt(filterForm.month) : undefined,
      page: currentPage.value,
      page_size: pageSize.value
    }
    
    const response = await salaryService.getMySalaryRecords(params)
    salaryRecords.value = response.results || []
    total.value = response.count || 0
    
    // 更新图表
    nextTick(() => {
      updateChart()
    })
  } catch (error: any) {
    console.error('加载薪资记录失败:', error)
    // 如果是认证错误（401），不显示提示，系统会自动处理
    if (error.response?.status !== 401) {
      ElMessage.error('加载薪资记录失败')
    }
    // 清空数据，避免显示过期数据
    salaryRecords.value = []
    total.value = 0
  } finally {
    loading.value = false
  }
}

// 初始化图表
const initChart = () => {
  if (!chartRef.value) return
  
  chartInstance = echarts.init(chartRef.value)
  updateChart()
}

// 更新图表
const updateChart = async () => {
  if (!chartInstance) return
  
  try {
    // 获取薪资趋势数据
    const trendsData = await salaryService.getSalaryTrends({ months: 12 })
    
    if (!trendsData.length) {
      // 如果没有数据，显示空图表
      const option = {
        title: {
          text: '薪资趋势',
          left: 'center'
        },
        xAxis: {
          type: 'category',
          data: []
        },
        yAxis: {
          type: 'value',
          axisLabel: {
            formatter: '¥{value}'
          }
        },
        series: []
      }
      chartInstance.setOption(option)
      return
    }
    
    const data = trendsData.slice().reverse()
    const months = data.map(item => `${item.year}-${String(item.month).padStart(2, '0')}`)
    const grossSalary = data.map(item => item.gross_salary)
    const netSalary = data.map(item => item.net_salary)
    
    const option = {
      title: {
        text: '薪资趋势',
        left: 'center'
      },
      tooltip: {
        trigger: 'axis',
        formatter: function (params: any) {
          let result = params[0].name + '<br/>'
          params.forEach((param: any) => {
            result += param.marker + param.seriesName + ': ¥' + param.value.toFixed(2) + '<br/>'
          })
          return result
        }
      },
      legend: {
        data: ['应发工资', '实发工资'],
        top: 30
      },
      grid: {
        left: '3%',
        right: '4%',
        bottom: '3%',
        top: 80,
        containLabel: true
      },
      xAxis: {
        type: 'category',
        boundaryGap: false,
        data: months
      },
      yAxis: {
        type: 'value',
        axisLabel: {
          formatter: '¥{value}'
        }
      },
      series: [
        {
          name: '应发工资',
          type: 'line',
          smooth: true,
          data: grossSalary,
          itemStyle: {
            color: '#409EFF'
          }
        },
        {
          name: '实发工资',
          type: 'line',
          smooth: true,
          data: netSalary,
          itemStyle: {
            color: '#67C23A'
          }
        }
      ]
    }
    
    chartInstance.setOption(option)
  } catch (error: any) {
    console.error('更新图表失败:', error)
  }
}

// 监听窗口大小变化
const handleResize = () => {
  if (chartInstance) {
    chartInstance.resize()
  }
}

onMounted(() => {
  loadCurrentSalary()
  loadSalaryRecords()
  
  nextTick(() => {
    initChart()
    window.addEventListener('resize', handleResize)
  })
})

// 当组件被激活时重新加载数据（支持keep-alive缓存）
onActivated(() => {
  console.log('[SalaryView] 页面激活，重新加载数据')
  loadCurrentSalary()
  loadSalaryRecords()
})

// 清理
watch(() => detailVisible.value, (newVal) => {
  if (!newVal) {
    selectedSalary.value = null
  }
})
</script>

<style scoped>
.salary {
  padding: var(--hr-space-lg);
}

.filter-card {
  margin-bottom: var(--hr-space-lg);
}

.filter-form {
  margin: 0;
}

.current-salary {
  margin-bottom: var(--hr-space-lg);
}

.salary-item {
  text-align: center;
  padding: var(--hr-space-lg);
}

.salary-item.gross .amount {
  color: var(--hr-primary);
}

.salary-item.deduction .amount {
  color: var(--hr-danger);
}

.salary-item.net .amount {
  color: var(--hr-success);
}

.salary-item .amount {
  font-size: 28px;
  font-weight: 800;
  margin-bottom: 8px;
  letter-spacing: -0.5px;
}

.salary-item .label {
  color: var(--color-text-secondary);
  font-size: 13px;
}

.salary-item .status-text {
  margin-bottom: 10px;
}

.chart-card {
  margin-top: var(--hr-space-lg);
}

.pagination {
  margin-top: var(--hr-space-lg);
  text-align: right;
}

.salary-detail {
  padding: var(--hr-space-lg) 0;
}

h4 {
  margin-bottom: 10px;
  color: var(--color-text-primary);
  font-weight: 600;
}

/* 薪资计算说明样式 */
.calc-explanation {
  font-size: 14px;
  line-height: 1.7;
}

.calc-section {
  margin-bottom: var(--hr-space-lg);
}

.calc-section h4 {
  color: var(--hr-primary);
  border-bottom: 2px solid var(--hr-primary);
  padding-bottom: 8px;
  margin-bottom: 15px;
}

.calc-formula {
  background: var(--hr-primary-bg);
  border-left: 3px solid var(--hr-primary);
  padding: 12px 16px;
  border-radius: var(--hr-radius-sm);
}

.calc-detail {
  background: var(--hr-gray-50);
  padding: 15px;
  border-radius: var(--hr-radius-sm);
}

.calc-table {
  width: 100%;
  border-collapse: collapse;
  margin: 10px 0;
}

.calc-table th,
.calc-table td {
  padding: 10px 12px;
  text-align: left;
  border-bottom: 1px solid var(--color-border);
}

.calc-table th {
  background: var(--hr-primary-bg);
  font-weight: 600;
  color: var(--hr-primary);
  font-size: 13px;
}

.calc-table tr:hover {
  background: var(--hr-gray-50);
}

.calc-table td.value {
  text-align: right;
  font-weight: 700;
}

.calc-table .note {
  display: block;
  font-size: 12px;
  color: var(--color-text-secondary);
  font-weight: normal;
}

.calc-table .total-row {
  background: var(--hr-primary-bg);
  font-weight: 700;
}

.calc-detail ul {
  margin: 10px 0;
  padding-left: 20px;
}

.calc-detail li {
  margin: 8px 0;
}

.calc-detail p {
  margin: 10px 0;
}

.calc-table tr.highlight {
  background: var(--hr-danger-bg);
  border-left: 3px solid var(--hr-danger);
}
</style>
