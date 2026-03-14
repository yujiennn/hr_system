<template>
  <div class="employee-management">
    <!-- 搜索和操作区域 -->
    <el-card class="search-card">
      <el-row :gutter="20">
        <el-col :span="6">
          <el-input
            v-model="searchForm.keyword"
            placeholder="搜索员工姓名、工号"
            clearable
            @keyup.enter="searchEmployees"
          >
            <template #prefix>
              <el-icon><Search /></el-icon>
            </template>
          </el-input>
        </el-col>
        <el-col :span="4">
          <el-select v-model="searchForm.status" placeholder="员工状态" clearable>
            <el-option label="在职" value="active" />
            <el-option label="离职" value="inactive" />
            <el-option label="试用期" value="probation" />
          </el-select>
        </el-col>        <el-col :span="4">
          <el-select v-model="searchForm.position" placeholder="职位" clearable>
            <el-option label="前端工程师" value="前端工程师" />
            <el-option label="后端工程师" value="后端工程师" />
            <el-option label="全栈工程师" value="全栈工程师" />
            <el-option label="产品经理" value="产品经理" />
            <el-option label="UI设计师" value="UI设计师" />
            <el-option label="测试工程师" value="测试工程师" />
            <el-option label="运维工程师" value="运维工程师" />
            <el-option label="数据分析师" value="数据分析师" />
          </el-select>
        </el-col>
        <el-col :span="6">
          <el-button type="primary" @click="searchEmployees">
            <el-icon><Search /></el-icon>
            搜索
          </el-button>
          <el-button @click="resetSearch">重置</el-button>
          <el-button type="success" @click="exportEmployees">
            <el-icon><Download /></el-icon>
            导出
          </el-button>
        </el-col>
      </el-row>
    </el-card>

    <!-- 员工列表 -->
    <el-card>
      <template #header>
        <div class="card-header">
          <span>员工列表 (共 {{ total }} 人)</span>
          <div>
            <el-button type="primary" @click="showAddDialog = true">
              <el-icon><Plus /></el-icon>
              添加员工
            </el-button>
          </div>
        </div>
      </template>

      <el-table
        :data="employeeList"
        stripe
        v-loading="loading"
        @selection-change="handleSelectionChange"
      >
        <el-table-column type="selection" width="55" />
        <el-table-column prop="avatar" label="头像" width="80">
          <template #default="{ row }">
            <el-avatar :src="row.avatar" :alt="row.name">{{ row.name.charAt(0) }}</el-avatar>
          </template>
        </el-table-column>
        <el-table-column prop="employeeId" label="工号" width="100" />
        <el-table-column prop="name" label="姓名" width="100" />
        <el-table-column prop="position" label="职位" width="120" />
        <el-table-column prop="phone" label="手机号" width="130" />
        <el-table-column prop="email" label="邮箱" width="180" show-overflow-tooltip />
        <el-table-column prop="hireDate" label="入职日期" width="120" />
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)">{{ getStatusText(row.status) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" size="small" @click="viewEmployee(row)">查看</el-button>
            <el-button type="warning" size="small" @click="editEmployee(row)">编辑</el-button>              <el-dropdown @command="(command: string) => handleCommand(command, row)">
              <el-button type="info" size="small">
                更多<el-icon class="el-icon--right"><ArrowDown /></el-icon>
              </el-button>
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item command="performance">绩效评估</el-dropdown-item>
                  <el-dropdown-item command="salary">薪资调整</el-dropdown-item>
                  <el-dropdown-item command="deactivate" divided>离职处理</el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
          </template>
        </el-table-column>
      </el-table>

      <div class="pagination-container">
        <el-pagination
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          :page-sizes="[10, 20, 50, 100]"
          :total="total"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
        />
      </div>
    </el-card>

    <!-- 添加/编辑员工对话框 -->
    <el-dialog
      v-model="showAddDialog"
      :title="editForm.id ? '编辑员工' : '添加员工'"
      width="600px"
      @close="resetForm"
    >
      <el-form :model="editForm" :rules="formRules" ref="formRef" label-width="100px">
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="员工姓名" prop="name">
              <el-input v-model="editForm.name" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="工号" prop="employeeId">
              <el-input v-model="editForm.employeeId" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="手机号" prop="phone">
              <el-input v-model="editForm.phone" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="邮箱" prop="email">
              <el-input v-model="editForm.email" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="12">            <el-form-item label="职位" prop="position">
              <el-select v-model="editForm.position" style="width: 100%">
                <el-option label="前端工程师" value="前端工程师" />
                <el-option label="后端工程师" value="后端工程师" />
                <el-option label="全栈工程师" value="全栈工程师" />
                <el-option label="产品经理" value="产品经理" />
                <el-option label="UI设计师" value="UI设计师" />
                <el-option label="测试工程师" value="测试工程师" />
                <el-option label="运维工程师" value="运维工程师" />
                <el-option label="数据分析师" value="数据分析师" />
                <el-option label="技术总监" value="技术总监" />
                <el-option label="项目经理" value="项目经理" />
              </el-select>
            </el-form-item>
          </el-col>        <el-col :span="12">
            <el-form-item label="入职日期" prop="hireDate">
              <el-date-picker
                v-model="editForm.hireDate"
                type="date"
                placeholder="选择日期"
                style="width: 100%"
              />
          </el-form-item>
        </el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="基础薪资" prop="baseSalary">
              <el-input-number v-model="editForm.baseSalary" :min="0" style="width: 100%" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="员工状态" prop="status">
              <el-select v-model="editForm.status" style="width: 100%">
                <el-option label="在职" value="active" />
                <el-option label="试用期" value="probation" />
                <el-option label="离职" value="inactive" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
      </el-form>
      <template #footer>
        <el-button @click="showAddDialog = false">取消</el-button>
        <el-button type="primary" @click="saveEmployee" :loading="saving">确定</el-button>
      </template>
    </el-dialog>

    <!-- 员工详情对话框 -->
    <el-dialog v-model="showDetailDialog" title="员工详情" width="800px">
      <div v-if="selectedEmployee" class="employee-detail">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="头像">
            <el-avatar :size="60" :src="selectedEmployee.avatar">
              {{ selectedEmployee.name.charAt(0) }}
            </el-avatar>
          </el-descriptions-item>
          <el-descriptions-item label="姓名">{{ selectedEmployee.name }}</el-descriptions-item>
          <el-descriptions-item label="工号">{{ selectedEmployee.employeeId }}</el-descriptions-item>
          <el-descriptions-item label="职位">{{ selectedEmployee.position }}</el-descriptions-item>
          <el-descriptions-item label="手机号">{{ selectedEmployee.phone }}</el-descriptions-item>
          <el-descriptions-item label="邮箱">{{ selectedEmployee.email }}</el-descriptions-item>
          <el-descriptions-item label="入职日期">{{ selectedEmployee.hireDate }}</el-descriptions-item>
          <el-descriptions-item label="状态">
            <el-tag :type="getStatusType(selectedEmployee.status)">
              {{ getStatusText(selectedEmployee.status) }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="基础薪资" :span="2">
            ¥{{ selectedEmployee.baseSalary?.toLocaleString() }}
          </el-descriptions-item>
        </el-descriptions>
      </div>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Search,
  Download,
  Plus,
  ArrowDown
} from '@element-plus/icons-vue'
import { 
  getUserList, 
  createUser, 
  updateUser, 
  deleteUser, 
  activateUser, 
  deactivateUser,
  getDepartmentList,
  type User,
  type UserCreateData,
  type UserListParams
} from '@/services/user'
import { useAuthStore } from '@/stores/counter'

// 使用用户状态管理
const authStore = useAuthStore()
const router = useRouter()

// 接口定义
interface Employee {
  id: number
  employeeId: string
  name: string
  phone: string
  email: string
  position: string
  hireDate: string
  status: string
  avatar?: string
  baseSalary?: number
}

// 响应式数据
const loading = ref(false)
const saving = ref(false)
const showAddDialog = ref(false)
const showDetailDialog = ref(false)
const selectedEmployee = ref<Employee | null>(null)
const currentPage = ref(1)
const pageSize = ref(20)
const total = ref(0)
const employeeList = ref<Employee[]>([])
const selectedEmployees = ref<Employee[]>([])

// 搜索表单
const searchForm = reactive({
  keyword: '',
  status: '',
  position: ''
})

// 编辑表单
const editForm = reactive({
  id: null as number | null,
  employeeId: '',
  name: '',
  phone: '',
  email: '',
  position: '',
  hireDate: '',
  status: 'active',
  baseSalary: 0
})

// 表单验证规则
const formRules = {
  name: [{ required: true, message: '请输入员工姓名', trigger: 'blur' }],
  employeeId: [{ required: true, message: '请输入工号', trigger: 'blur' }],
  phone: [
    { required: true, message: '请输入手机号', trigger: 'blur' },
    { pattern: /^1[3-9]\d{9}$/, message: '手机号格式不正确', trigger: 'blur' }
  ],
  email: [
    { required: true, message: '请输入邮箱', trigger: 'blur' },
    { type: 'email', message: '邮箱格式不正确', trigger: 'blur' }
  ],
  position: [{ required: true, message: '请选择职位', trigger: 'change' }],
  hireDate: [{ required: true, message: '请选择入职日期', trigger: 'change' }]
}

const formRef = ref()

// 获取员工列表
const getEmployeeList = async () => {
  loading.value = true
  try {
    const params: UserListParams = {
      page: currentPage.value,
      page_size: pageSize.value,
    }
    
    // 添加搜索条件
    if (searchForm.keyword) {
      params.search = searchForm.keyword
    }
    
    // 根据状态过滤
    if (searchForm.status) {
      if (searchForm.status === 'active') {
        params.is_active_employee = true
      } else if (searchForm.status === 'inactive') {
        params.is_active_employee = false
      }
    }
    
    const response = await getUserList(params)
    
    // 转换数据格式以匹配前端接口
    let filteredResults = response.results.map((user: User) => ({
      id: user.id,
      employeeId: user.employee_id,
      name: `${user.first_name} ${user.last_name}`.trim() || user.username,
      phone: user.phone,
      email: user.email,
      position: user.position || '未设置',
      hireDate: user.hire_date || '',
      status: user.is_active_employee ? 'active' : 'inactive',
      avatar: user.avatar,
      baseSalary: user.base_salary || 0
    }))
    
    // 前端职位过滤（因为后端API可能不支持职位过滤）
    if (searchForm.position) {
      filteredResults = filteredResults.filter(employee => 
        employee.position === searchForm.position
      )
    }
    
    employeeList.value = filteredResults
    total.value = filteredResults.length // 注意：这里应该是过滤后的数量
    
  } catch (error: any) {
    console.error('获取员工列表失败:', error)
    ElMessage.error('获取员工列表失败')
  } finally {
    loading.value = false
  }
}

// 搜索员工
const searchEmployees = () => {
  currentPage.value = 1
  getEmployeeList()
}

// 重置搜索
const resetSearch = () => {
  Object.assign(searchForm, {
    keyword: '',
    status: '',
    position: ''
  })
  searchEmployees()
}

// 查看员工详情
const viewEmployee = (employee: Employee) => {
  selectedEmployee.value = employee
  showDetailDialog.value = true
}

// 编辑员工
const editEmployee = (employee: Employee) => {
  Object.assign(editForm, {
    id: employee.id,
    employeeId: employee.employeeId,
    name: employee.name,
    phone: employee.phone,
    email: employee.email,
    position: employee.position,
    hireDate: employee.hireDate ? new Date(employee.hireDate) : '',
    status: employee.status,
    baseSalary: employee.baseSalary || 0
  })
  showAddDialog.value = true
}

// 保存员工
const saveEmployee = async () => {
  if (!formRef.value) return
  
  try {
    await formRef.value.validate()
    saving.value = true
    
    // 准备数据
    const userData: Partial<UserCreateData> = {
      employee_id: editForm.employeeId,
      first_name: editForm.name.split(' ')[0] || editForm.name,
      last_name: editForm.name.split(' ').slice(1).join(' ') || '',
      phone: editForm.phone,
      email: editForm.email,
      position: editForm.position,
      hire_date: editForm.hireDate ? new Date(editForm.hireDate).toISOString().split('T')[0] : undefined,
      base_salary: editForm.baseSalary,
      user_type: 'employee'
    }
    
    if (editForm.id) {
      // 更新员工
      await updateUser(editForm.id, userData)
      ElMessage.success('更新成功')    } else {
      // 添加新员工
      const newUserData: UserCreateData = {
        ...userData as UserCreateData,
        username: editForm.employeeId,
        password: 'temp123456', // 临时密码
        confirm_password: 'temp123456',
        department: (typeof authStore.user?.department === 'object' ? authStore.user?.department?.id : authStore.user?.department) || 1 // 使用当前用户的部门
      }
      await createUser(newUserData)
      ElMessage.success('添加成功')
    }
    
    showAddDialog.value = false
    await getEmployeeList()
  } catch (error: any) {
    console.error('操作失败:', error)
    ElMessage.error('操作失败')
  } finally {
    saving.value = false
  }
}

// 重置表单
const resetForm = () => {
  if (formRef.value) {
    formRef.value.resetFields()
  }
  Object.assign(editForm, {
    id: null,
    employeeId: '',
    name: '',
    phone: '',
    email: '',
    position: '',
    hireDate: '',
    status: 'active',
    baseSalary: 0
  })
}

// 处理命令操作
const handleCommand = async (command: string, employee: Employee) => {
  switch (command) {
    case 'performance':
      // 携带员工ID跳转绩效页面并让目标页读取查询参数进行预筛选
      router.push({
        path: '/manager/performance',
        query: { employee_id: employee.id.toString() }
      })
      break
    case 'salary':
      // 携带工号跳转薪资管理页，目标页会按 employee_id 查询
      router.push({
        path: '/manager/salary',
        query: { employee_id: employee.employeeId }
      })
      break
    case 'deactivate':
      try {
        await ElMessageBox.confirm('确定要将该员工离职吗？', '确认操作', {
          type: 'warning'
        })
        // 调用停用用户API
        await deactivateUser(employee.id)
        ElMessage.success('员工已离职')
        await getEmployeeList()
      } catch (error: any) {
        if (error !== 'cancel') {
          console.error('离职操作失败:', error)
          ElMessage.error('离职操作失败')
        }
      }
      break
  }
}

// 选择变化处理
const handleSelectionChange = (selection: Employee[]) => {
  selectedEmployees.value = selection
}

// 分页处理
const handleSizeChange = (val: number) => {
  pageSize.value = val
  getEmployeeList()
}

const handleCurrentChange = (val: number) => {
  currentPage.value = val
  getEmployeeList()
}

// 导出员工
const exportEmployees = () => {
  if (employeeList.value.length === 0) {
    ElMessage.warning('没有数据可导出')
    return
  }
  
  try {
    // 创建CSV数据
    const headers = ['工号', '姓名', '职位', '手机号', '邮箱', '入职日期', '状态', '基础薪资']
    const csvContent = [
      headers.join(','),
      ...employeeList.value.map(emp => [
        emp.employeeId,
        emp.name,
        emp.position,
        emp.phone,
        emp.email,
        emp.hireDate,
        getStatusText(emp.status),
        emp.baseSalary || 0
      ].join(','))
    ].join('\n')
    
    // 创建BOM头用于中文显示
    const bom = '\uFEFF'
    const blob = new Blob([bom + csvContent], { type: 'text/csv;charset=utf-8;' })
    
    // 创建下载链接
    const link = document.createElement('a')
    const url = URL.createObjectURL(blob)
    link.setAttribute('href', url)
    link.setAttribute('download', `员工列表_${new Date().toLocaleDateString()}.csv`)
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

// 获取状态类型
const getStatusType = (status: string) => {
  const typeMap: Record<string, string> = {
    active: 'success',
    probation: 'warning',
    inactive: 'danger'
  }
  return typeMap[status] || 'default'
}

// 获取状态文本
const getStatusText = (status: string) => {
  const textMap: Record<string, string> = {
    active: '在职',
    probation: '试用期',
    inactive: '离职'
  }
  return textMap[status] || status
}

onMounted(() => {
  getEmployeeList()
})
</script>

<style scoped>
.employee-management {
  padding: var(--hr-space-lg);
}

.search-card {
  margin-bottom: var(--hr-space-lg);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.pagination-container {
  margin-top: var(--hr-space-lg);
  text-align: right;
}

.employee-detail {
  padding: var(--hr-space-lg) 0;
}

:deep(.el-table) {
  font-size: 14px;
}

:deep(.el-dialog__body) {
  padding: var(--hr-space-lg);
}
</style>
