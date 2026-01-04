<template>
  <div class="salary-management">
    <!-- 页面头部 -->
    <div class="page-header">
      <div class="header-content">
        <h2>薪资管理</h2>
        <el-button type="primary" :icon="Plus" @click="showCreateDialog = true">
          创建薪资记录
        </el-button>
      </div>
    </div>

    <!-- 搜索筛选 -->
    <el-card class="search-card">
      <el-form :model="searchForm" inline>
        <el-form-item label="年份">
          <el-select v-model="searchForm.year" style="width: 120px">
            <el-option 
              v-for="year in yearOptions" 
              :key="year" 
              :label="year" 
              :value="year" 
            />
          </el-select>
        </el-form-item>
        <el-form-item label="月份">
          <el-select v-model="searchForm.month" clearable placeholder="全部" style="width: 120px">
            <el-option 
              v-for="month in monthOptions" 
              :key="month" 
              :label="`${month}月`" 
              :value="month" 
            />
          </el-select>
        </el-form-item>
        <el-form-item label="员工">
          <el-select 
            v-model="searchForm.employeeId" 
            clearable 
            filterable
            placeholder="选择员工" 
            style="width: 200px"
          >
            <el-option 
              v-for="emp in departmentEmployees" 
              :key="emp.id" 
              :label="`${emp.name} (${emp.employee_id})`" 
              :value="emp.employee_id" 
            />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" :icon="Search" @click="loadSalaryRecords">搜索</el-button>
          <el-button @click="resetSearch">重置</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 薪资统计 -->
    <el-card class="stats-card" v-if="statistics">
      <template #header>
        <span>统计信息</span>
      </template>
      <el-row :gutter="20">
        <el-col :span="6">
          <div class="stat-item">
            <div class="stat-value">{{ statistics.total_records }}</div>
            <div class="stat-label">员工数量</div>
          </div>
        </el-col>
        <el-col :span="6">
          <div class="stat-item">
            <div class="stat-value">¥{{ formatAmount(statistics.total_gross_salary) }}</div>
            <div class="stat-label">应发总额</div>
          </div>
        </el-col>
        <el-col :span="6">
          <div class="stat-item">
            <div class="stat-value">¥{{ formatAmount(statistics.total_net_salary) }}</div>
            <div class="stat-label">实发总额</div>
          </div>
        </el-col>
        <el-col :span="6">
          <div class="stat-item">
            <div class="stat-value">¥{{ formatAmount(statistics.avg_gross_salary) }}</div>
            <div class="stat-label">平均薪资</div>
          </div>
        </el-col>
      </el-row>
    </el-card>

    <!-- 薪资记录表格 -->
    <el-card class="table-card">
      <template #header>
        <div class="card-header">
          <span>薪资记录</span>
          <div class="header-actions">
            <el-button :icon="Download" @click="exportSalaryData">导出数据</el-button>
            <el-button :icon="Refresh" @click="loadSalaryRecords">刷新</el-button>
          </div>
        </div>
      </template>
      
      <el-table 
        :data="salaryRecords" 
        v-loading="loading"
        stripe
        border
        :height="400"
      >
        <el-table-column prop="employee_id" label="员工编号" width="120" />
        <el-table-column prop="user_name" label="员工姓名" width="120" />
        <el-table-column prop="year" label="年份" width="80" />
        <el-table-column prop="month" label="月份" width="80">
          <template #default="{ row }">
            {{ row.month }}月
          </template>
        </el-table-column>
        <el-table-column prop="basic_salary" label="基本工资" align="right" width="120">
          <template #default="{ row }">
            ¥{{ formatAmount(row.basic_salary) }}
          </template>
        </el-table-column>
        <el-table-column prop="performance_bonus" label="绩效奖金" align="right" width="120">
          <template #default="{ row }">
            ¥{{ formatAmount(row.performance_bonus) }}
          </template>
        </el-table-column>
        <el-table-column prop="gross_salary" label="应发工资" align="right" width="120">
          <template #default="{ row }">
            ¥{{ formatAmount(row.gross_salary) }}
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
        </el-table-column>
        <el-table-column prop="pay_date" label="发放日期" width="120">
          <template #default="{ row }">
            {{ row.pay_date || '-' }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="180" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" size="small" @click="viewSalaryDetail(row)">
              详情
            </el-button>
            <el-button 
              type="warning" 
              size="small" 
              @click="editSalary(row)"
              v-if="row.status === 'draft'"
            >
              编辑
            </el-button>
            <el-dropdown @command="handleCommand" trigger="click">
              <el-button type="info" size="small">
                更多<el-icon class="el-icon--right"><arrow-down /></el-icon>
              </el-button>
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item :command="`approve-${row.id}`" v-if="row.status === 'draft'">
                    审批通过
                  </el-dropdown-item>
                  <el-dropdown-item :command="`pay-${row.id}`" v-if="row.status === 'approved'">
                    标记发放
                  </el-dropdown-item>
                  <el-dropdown-item :command="`export-${row.id}`">
                    导出工资单
                  </el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <div class="pagination-container">
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

    <!-- 创建薪资记录对话框 -->
    <el-dialog
      v-model="showCreateDialog"
      title="创建薪资记录"
      width="800px"
      @close="resetCreateForm"
    >
      <el-form :model="createForm" :rules="createRules" ref="createFormRef" label-width="120px">
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="员工" prop="userId">
              <el-select 
                v-model="createForm.userId" 
                filterable
                placeholder="选择员工"
                style="width: 100%"
                @change="onEmployeeChange"
              >
                <el-option 
                  v-for="emp in departmentEmployees" 
                  :key="emp.id" 
                  :label="`${emp.name} (${emp.employee_id})`" 
                  :value="emp.id"
                />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="6">
            <el-form-item label="年份" prop="year">
              <el-select v-model="createForm.year" style="width: 100%">
                <el-option 
                  v-for="year in yearOptions" 
                  :key="year" 
                  :label="year" 
                  :value="year" 
                />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="6">
            <el-form-item label="月份" prop="month">
              <el-select v-model="createForm.month" style="width: 100%">
                <el-option 
                  v-for="month in monthOptions" 
                  :key="month" 
                  :label="`${month}月`" 
                  :value="month" 
                />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="基本工资" prop="basicSalary">
              <el-input-number 
                v-model="createForm.basicSalary" 
                :min="0" 
                :precision="2"
                style="width: 100%" 
              />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="绩效奖金" prop="performanceBonus">
              <el-input-number 
                v-model="createForm.performanceBonus" 
                :min="0" 
                :precision="2"
                style="width: 100%" 
              />
            </el-form-item>
          </el-col>
        </el-row>
        
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="津贴补助" prop="allowances">
              <el-input-number 
                v-model="createForm.allowances" 
                :min="0" 
                :precision="2"
                style="width: 100%" 
              />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="加班费" prop="overtimePay">
              <el-input-number 
                v-model="createForm.overtimePay" 
                :min="0" 
                :precision="2"
                style="width: 100%" 
              />
            </el-form-item>
          </el-col>
        </el-row>
        
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="社保扣除" prop="socialSecurity">
              <el-input-number 
                v-model="createForm.socialSecurity" 
                :min="0" 
                :precision="2"
                style="width: 100%" 
              />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="公积金扣除" prop="housingFund">
              <el-input-number 
                v-model="createForm.housingFund" 
                :min="0" 
                :precision="2"
                style="width: 100%" 
              />
            </el-form-item>
          </el-col>
        </el-row>
        
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="个人所得税" prop="incomeTax">
              <el-input-number 
                v-model="createForm.incomeTax" 
                :min="0" 
                :precision="2"
                style="width: 100%" 
              />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="其他扣除" prop="otherDeductions">
              <el-input-number 
                v-model="createForm.otherDeductions" 
                :min="0" 
                :precision="2"
                style="width: 100%" 
              />
            </el-form-item>
          </el-col>
        </el-row>

        <!-- 计算预览 -->
        <el-card class="calculation-preview">
          <template #header>
            <span>薪资计算预览</span>
          </template>
          <el-row :gutter="20">
            <el-col :span="8">
              <div class="calc-item">
                <span class="calc-label">应发工资：</span>
                <span class="calc-value gross">¥{{ formatAmount(calculatedGrossSalary) }}</span>
              </div>
            </el-col>
            <el-col :span="8">
              <div class="calc-item">
                <span class="calc-label">扣除合计：</span>
                <span class="calc-value deduction">¥{{ formatAmount(calculatedDeductions) }}</span>
              </div>
            </el-col>
            <el-col :span="8">
              <div class="calc-item">
                <span class="calc-label">实发工资：</span>
                <span class="calc-value net">¥{{ formatAmount(calculatedNetSalary) }}</span>
              </div>
            </el-col>
          </el-row>
        </el-card>
      </el-form>
      
      <template #footer>
        <el-button @click="showCreateDialog = false">取消</el-button>
        <el-button type="primary" @click="createSalaryRecord" :loading="saving">
          创建
        </el-button>
      </template>
    </el-dialog>

    <!-- 薪资详情对话框 -->
    <el-dialog v-model="showDetailDialog" title="薪资详情" width="70%">
      <div v-if="selectedSalary" class="salary-detail">
        <el-descriptions border :column="2">
          <el-descriptions-item label="员工信息">
            {{ selectedSalary.user_name }} ({{ selectedSalary.employee_id }})
          </el-descriptions-item>
          <el-descriptions-item label="年月">
            {{ selectedSalary.year }}年{{ selectedSalary.month }}月
          </el-descriptions-item>
          <el-descriptions-item label="基本工资">
            ¥{{ formatAmount(selectedSalary.basic_salary) }}
          </el-descriptions-item>
          <el-descriptions-item label="绩效奖金">
            ¥{{ formatAmount(selectedSalary.performance_bonus) }}
          </el-descriptions-item>
          <el-descriptions-item label="津贴补助">
            ¥{{ formatAmount(selectedSalary.allowances) }}
          </el-descriptions-item>
          <el-descriptions-item label="加班费">
            ¥{{ formatAmount(selectedSalary.overtime_pay) }}
          </el-descriptions-item>
          <el-descriptions-item label="应发工资">
            <span style="color: #409EFF; font-weight: bold;">
              ¥{{ formatAmount(selectedSalary.gross_salary) }}
            </span>
          </el-descriptions-item>
          <el-descriptions-item label="社保扣除">
            ¥{{ formatAmount(selectedSalary.social_security) }}
          </el-descriptions-item>
          <el-descriptions-item label="公积金扣除">
            ¥{{ formatAmount(selectedSalary.housing_fund) }}
          </el-descriptions-item>
          <el-descriptions-item label="个人所得税">
            ¥{{ formatAmount(selectedSalary.income_tax) }}
          </el-descriptions-item>
          <el-descriptions-item label="其他扣除">
            ¥{{ formatAmount(selectedSalary.other_deductions) }}
          </el-descriptions-item>
          <el-descriptions-item label="实发工资">
            <span style="color: #67C23A; font-weight: bold; font-size: 16px;">
              ¥{{ formatAmount(selectedSalary.net_salary) }}
            </span>
          </el-descriptions-item>
          <el-descriptions-item label="状态">
            <el-tag :type="getSalaryStatusType(selectedSalary.status)">
              {{ getSalaryStatusLabel(selectedSalary.status) }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="发放日期">
            {{ selectedSalary.pay_date || '未发放' }}
          </el-descriptions-item>
        </el-descriptions>
      </div>
      <template #footer>
        <el-button @click="showDetailDialog = false">关闭</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted, nextTick } from 'vue'
import { useRoute } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Search,
  Download,
  Plus,
  Refresh,
  ArrowDown
} from '@element-plus/icons-vue'
import api from '@/utils/api'
import { salaryService } from '@/services/salary'

// 类型定义
interface DepartmentEmployee {
  id: number
  name: string
  employee_id: string
  base_salary?: number
}

interface SalaryRecord {
  id: number
  user_id: number
  user_name: string
  employee_id: string
  year: number
  month: number
  basic_salary: number
  performance_bonus: number
  allowances: number
  overtime_pay: number
  gross_salary: number
  social_security: number
  housing_fund: number
  income_tax: number
  other_deductions: number
  net_salary: number
  status: string
  pay_date?: string
}

interface SalaryStatistics {
  total_records: number
  total_gross_salary: number
  total_net_salary: number
  avg_gross_salary: number
}

// 响应式数据
const loading = ref(false)
const saving = ref(false)
const showCreateDialog = ref(false)
const showDetailDialog = ref(false)
const createFormRef = ref()

const currentPage = ref(1)
const pageSize = ref(20)
const total = ref(0)

const salaryRecords = ref<SalaryRecord[]>([])
const departmentEmployees = ref<DepartmentEmployee[]>([])
const statistics = ref<SalaryStatistics | null>(null)
const selectedSalary = ref<SalaryRecord | null>(null)
const route = useRoute()

// 搜索表单
const searchForm = reactive({
  year: new Date().getFullYear(),
  month: null as number | null,
  employeeId: null as string | null
})

// 创建表单
const createForm = reactive({
  userId: null,
  year: new Date().getFullYear(),
  month: new Date().getMonth() + 1,
  basicSalary: 0,
  performanceBonus: 0,
  allowances: 0,
  overtimePay: 0,
  socialSecurity: 0,
  housingFund: 0,
  incomeTax: 0,
  otherDeductions: 0
})

// 表单验证规则
const createRules = {
  userId: [{ required: true, message: '请选择员工', trigger: 'change' }],
  year: [{ required: true, message: '请选择年份', trigger: 'change' }],
  month: [{ required: true, message: '请选择月份', trigger: 'change' }],
  basicSalary: [{ required: true, message: '请输入基本工资', trigger: 'blur' }]
}

// 年份选项
const yearOptions = computed(() => {
  const currentYear = new Date().getFullYear()
  return Array.from({ length: 5 }, (_, i) => currentYear - i)
})

// 月份选项
const monthOptions = computed(() => {
  return Array.from({ length: 12 }, (_, i) => i + 1)
})

// 计算预览
const calculatedGrossSalary = computed(() => {
  return (createForm.basicSalary || 0) + 
         (createForm.performanceBonus || 0) + 
         (createForm.allowances || 0) + 
         (createForm.overtimePay || 0)
})

const calculatedDeductions = computed(() => {
  return (createForm.socialSecurity || 0) + 
         (createForm.housingFund || 0) + 
         (createForm.incomeTax || 0) + 
         (createForm.otherDeductions || 0)
})

const calculatedNetSalary = computed(() => {
  return calculatedGrossSalary.value - calculatedDeductions.value
})

// 方法
const formatAmount = (amount: number | string | null | undefined) => {
  return salaryService.formatAmount(amount)
}

const getSalaryStatusType = (status: string) => {
  return salaryService.getSalaryStatusType(status)
}

const getSalaryStatusLabel = (status: string) => {
  return salaryService.getSalaryStatusLabel(status)
}

// 加载部门员工
const loadDepartmentEmployees = async () => {
  try {
    const response = await api.get('/salary/records/department-employees/')
    departmentEmployees.value = response.data.employees
  } catch (error: any) {
    console.error('获取部门员工失败:', error)
  }
}

// 加载薪资记录
const loadSalaryRecords = async () => {
  loading.value = true
  try {
    const params = {
      year: searchForm.year,
      month: searchForm.month || undefined,
      employee_id: searchForm.employeeId || undefined,
      page: currentPage.value,
      page_size: pageSize.value
    }
    
    const response = await api.get('/salary/records/department-records/', { params })
    salaryRecords.value = response.data.results
    total.value = response.data.count
    
    // 加载统计信息
    await loadStatistics()
  } catch (error: any) {
    console.error('获取薪资记录失败:', error)
    ElMessage.error('获取薪资记录失败')
  } finally {
    loading.value = false
  }
}

// 加载统计信息
const loadStatistics = async () => {
  try {
    const params = {
      year: searchForm.year,
      month: searchForm.month || undefined,
      employee_id: searchForm.employeeId || undefined
    }
    
    const response = await api.get('/salary/statistics/', { params })
    statistics.value = response.data.statistics
  } catch (error: any) {
    console.error('获取统计信息失败:', error)
  }
}

// 重置搜索
const resetSearch = () => {
  searchForm.year = new Date().getFullYear()
  searchForm.month = null
  searchForm.employeeId = null
  currentPage.value = 1
  loadSalaryRecords()
}

// 创建薪资记录
const createSalaryRecord = async () => {
  if (!createFormRef.value) return
  
  await createFormRef.value.validate(async (valid: boolean) => {
    if (!valid) return
    
    saving.value = true
    try {
      const data = {
        user: createForm.userId,
        year: createForm.year,
        month: createForm.month,
        basic_salary: createForm.basicSalary,
        performance_bonus: createForm.performanceBonus,
        allowances: createForm.allowances,
        overtime_pay: createForm.overtimePay,
        social_security: createForm.socialSecurity,
        housing_fund: createForm.housingFund,
        income_tax: createForm.incomeTax,
        other_deductions: createForm.otherDeductions
      }
      
      await api.post('/salary/records/', data)
      ElMessage.success('创建成功')
      showCreateDialog.value = false
      resetCreateForm()
      await loadSalaryRecords()
    } catch (error: any) {
      console.error('创建薪资记录失败:', error)
      ElMessage.error(error.response?.data?.detail || '创建失败')
    } finally {
      saving.value = false
    }
  })
}

// 重置创建表单
const resetCreateForm = () => {
  Object.assign(createForm, {
    userId: null,
    year: new Date().getFullYear(),
    month: new Date().getMonth() + 1,
    basicSalary: 0,
    performanceBonus: 0,
    allowances: 0,
    overtimePay: 0,
    socialSecurity: 0,
    housingFund: 0,
    incomeTax: 0,
    otherDeductions: 0
  })
  nextTick(() => {
    createFormRef.value?.clearValidate()
  })
}

// 员工选择变化
const onEmployeeChange = (userId: number) => {
  const employee = departmentEmployees.value.find(emp => emp.id === userId)
  if (employee) {
    createForm.basicSalary = employee.base_salary || 0
  }
}

// 查看薪资详情
const viewSalaryDetail = (salary: any) => {
  selectedSalary.value = salary
  showDetailDialog.value = true
}

// 编辑薪资
const editSalary = (salary: any) => {
  // 填充编辑表单
  Object.assign(createForm, {
    userId: salary.user_id,
    year: salary.year,
    month: salary.month,
    basicSalary: salary.basic_salary,
    performanceBonus: salary.performance_bonus,
    allowances: salary.allowances,
    overtimePay: salary.overtime_pay,
    socialSecurity: salary.social_security,
    housingFund: salary.housing_fund,
    incomeTax: salary.income_tax,
    otherDeductions: salary.other_deductions
  })
  showCreateDialog.value = true
}

// 处理下拉菜单命令
const handleCommand = async (command: string) => {
  const [action, id] = command.split('-')
  const salaryId = parseInt(id)
  
  try {
    switch (action) {
      case 'approve':
        await ElMessageBox.confirm('确定要审批通过这条薪资记录吗？', '确认操作', {
          type: 'warning'
        })
        await api.patch(`/salary/records/${salaryId}/`, { status: 'approved' })
        ElMessage.success('审批成功')
        await loadSalaryRecords()
        break
          case 'pay':
        await ElMessageBox.confirm('确定要标记为已发放吗？', '确认操作', {
          type: 'warning'
        })
        await api.patch(`/salary/records/${salaryId}/`, { 
          status: 'paid',
          pay_date: new Date().toISOString().split('T')[0]
        })
        ElMessage.success('标记成功')
        await loadSalaryRecords()
        break
        
      case 'export':
        await salaryService.exportSingleSalary(salaryId)
        break
    }
  } catch (error: any) {
    if (error !== 'cancel') {
      console.error('操作失败:', error)
      ElMessage.error('操作失败')
    }
  }
}

// 导出薪资数据
const exportSalaryData = async () => {
  try {
    await salaryService.exportSalary({
      year: searchForm.year,
      month: searchForm.month || undefined,
      employee_id: searchForm.employeeId || undefined
    })
  } catch (error: any) {
    console.error('导出失败:', error)
    ElMessage.error('导出失败')
  }
}

// 分页处理
const handleSizeChange = (val: number) => {
  pageSize.value = val
  currentPage.value = 1
  loadSalaryRecords()
}

const handleCurrentChange = (val: number) => {
  currentPage.value = val
  loadSalaryRecords()
}

// 初始化
onMounted(() => {
  // 从路由查询中预填筛选条件，便于从员工列表跳转
  const { employee_id, year, month } = route.query
  if (typeof employee_id === 'string') {
    searchForm.employeeId = employee_id
  }
  if (typeof year === 'string' && !Number.isNaN(Number(year))) {
    searchForm.year = Number(year)
  }
  if (typeof month === 'string' && !Number.isNaN(Number(month))) {
    searchForm.month = Number(month)
  }
  loadDepartmentEmployees()
  loadSalaryRecords()
})
</script>

<style scoped>
.salary-management {
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

.search-card,
.stats-card,
.table-card {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-actions {
  display: flex;
  gap: 10px;
}

.stat-item {
  text-align: center;
  padding: 20px;
}

.stat-value {
  font-size: 24px;
  font-weight: bold;
  color: #409EFF;
  margin-bottom: 8px;
}

.stat-label {
  color: #909399;
  font-size: 14px;
}

.pagination-container {
  margin-top: 20px;
  text-align: right;
}

.calculation-preview {
  margin-top: 20px;
}

.calc-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 0;
}

.calc-label {
  font-weight: 500;
  color: #606266;
}

.calc-value {
  font-weight: bold;
  font-size: 16px;
}

.calc-value.gross {
  color: #409EFF;
}

.calc-value.deduction {
  color: #F56C6C;
}

.calc-value.net {
  color: #67C23A;
}

.salary-detail {
  padding: 20px 0;
}
</style>
