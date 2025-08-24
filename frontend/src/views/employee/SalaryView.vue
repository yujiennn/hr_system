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
        </el-col>        <el-col :span="6">
          <div class="salary-item deduction">
            <div class="amount">¥{{ formatAmount((currentSalary.social_security || 0) + (currentSalary.housing_fund || 0) + (currentSalary.income_tax || 0) + (currentSalary.other_deductions || 0)) }}</div>
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
        </el-table-column>        <el-table-column prop="total_deductions" label="扣除合计" align="right" width="120">
          <template #default="{ row }">
            ¥{{ formatAmount((row.social_security || 0) + (row.housing_fund || 0) + (row.income_tax || 0) + (row.other_deductions || 0)) }}
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
        <el-descriptions border :column="2">
          <el-descriptions-item label="年月">
            {{ selectedSalary.year }}年{{ selectedSalary.month }}月
          </el-descriptions-item>
          <el-descriptions-item label="状态">
            <el-tag :type="getSalaryStatusType(selectedSalary.status)">
              {{ getSalaryStatusLabel(selectedSalary.status) }}
            </el-tag>
          </el-descriptions-item>          <el-descriptions-item label="基本工资">
            ¥{{ formatAmount(selectedSalary.basic_salary) }}
          </el-descriptions-item>
          <el-descriptions-item label="绩效工资">
            ¥{{ formatAmount(selectedSalary.performance_bonus) }}
          </el-descriptions-item>
          <el-descriptions-item label="加班费">
            ¥{{ formatAmount(selectedSalary.overtime_pay) }}
          </el-descriptions-item>
          <el-descriptions-item label="津贴补助">
            ¥{{ formatAmount(selectedSalary.allowances) }}
          </el-descriptions-item>
          <el-descriptions-item label="应发工资">
            ¥{{ formatAmount(selectedSalary.gross_salary) }}
          </el-descriptions-item>
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
          <el-descriptions-item label="扣除合计">
            ¥{{ formatAmount((selectedSalary.social_security || 0) + (selectedSalary.housing_fund || 0) + (selectedSalary.income_tax || 0) + (selectedSalary.other_deductions || 0)) }}
          </el-descriptions-item>
          <el-descriptions-item label="实发工资">
            <span style="color: #409EFF; font-weight: bold; font-size: 16px;">
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
import { ref, reactive, onMounted, computed, nextTick, watch } from 'vue'
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
    { name: '绩效工资', amount: currentSalary.value.performance_bonus },
    { name: '加班费', amount: currentSalary.value.overtime_pay },
    { name: '津贴补助', amount: currentSalary.value.allowances }
  ].filter(item => item.amount > 0)
})

// 扣除项目
const deductionItems = computed(() => {
  if (!currentSalary.value) return []
  return [
    { name: '社保个人', amount: currentSalary.value.social_security },
    { name: '公积金个人', amount: currentSalary.value.housing_fund },
    { name: '个人所得税', amount: currentSalary.value.income_tax },
    { name: '其他扣除', amount: currentSalary.value.other_deductions }
  ].filter(item => item.amount > 0)
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
    })  } catch (error: any) {
    console.error('加载薪资记录失败:', error)
    ElMessage.error('加载薪资记录失败')
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

// 清理
watch(() => detailVisible.value, (newVal) => {
  if (!newVal) {
    selectedSalary.value = null
  }
})
</script>

<style scoped>
.salary {
  padding: 20px;
}

.filter-card {
  margin-bottom: 20px;
}

.filter-form {
  margin: 0;
}

.current-salary {
  margin-bottom: 20px;
}

.salary-item {
  text-align: center;
  padding: 20px;
}

.salary-item.gross .amount {
  color: #409EFF;
}

.salary-item.deduction .amount {
  color: #F56C6C;
}

.salary-item.net .amount {
  color: #67C23A;
}

.salary-item .amount {
  font-size: 32px;
  font-weight: bold;
  margin-bottom: 10px;
}

.salary-item .label {
  color: #909399;
  font-size: 14px;
}

.salary-item .status-text {
  margin-bottom: 10px;
}

.chart-card {
  margin-top: 20px;
}

.pagination {
  margin-top: 20px;
  text-align: right;
}

.salary-detail {
  padding: 20px 0;
}

h4 {
  margin-bottom: 10px;
  color: #303133;
}
</style>
