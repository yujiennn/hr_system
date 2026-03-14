<template>  <div class="user-management">
    <!-- 搜索和操作区域 -->
    <el-card class="search-card">
      <el-row :gutter="20">        <el-col :span="6">
          <el-input
            v-model="searchForm.keyword"
            placeholder="搜索用户名、邮箱、手机号"
            clearable
            @keyup.enter="onSearchKeyPress"
          >
            <template #prefix>
              <el-icon><Search /></el-icon>
            </template>
          </el-input>
        </el-col>
        <el-col :span="4">
          <el-select v-model="searchForm.role" placeholder="用户角色" clearable>
            <el-option label="系统管理员" value="admin" />
            <el-option label="部门经理" value="manager" />
            <el-option label="普通员工" value="employee" />
          </el-select>
        </el-col>
        <el-col :span="4">
          <el-select v-model="searchForm.status" placeholder="用户状态" clearable>
            <el-option label="启用" value="active" />
            <el-option label="禁用" value="disabled" />
            <el-option label="锁定" value="locked" />
          </el-select>
        </el-col>
        <el-col :span="4">
          <el-select v-model="searchForm.department" placeholder="部门" clearable>
            <el-option label="技术部" value="tech" />
            <el-option label="产品部" value="product" />
            <el-option label="销售部" value="sales" />
            <el-option label="人事部" value="hr" />
          </el-select>
        </el-col>
        <el-col :span="6">          <el-button type="primary" @click="searchUsers">
            <el-icon><Search /></el-icon>
            搜索
          </el-button>
          <el-button @click="resetSearch">重置</el-button>
          <el-button type="success" @click="openAddDialog">
            <el-icon><Plus /></el-icon>
            新增用户
          </el-button>
        </el-col>
      </el-row>
    </el-card>

    <!-- 用户列表 -->
    <el-card>
      <template #header>
        <div class="card-header">
          <span>用户列表 (共 {{ total }} 人)</span>
          <div>
            <el-button type="warning" @click="batchDisable" :disabled="selectedUsers.length === 0">
              批量禁用
            </el-button>
            <el-button type="success" @click="batchEnable" :disabled="selectedUsers.length === 0">
              批量启用
            </el-button>
            <el-button type="info" @click="exportUsers">
              <el-icon><Download /></el-icon>
              导出
            </el-button>
          </div>
        </div>
      </template>

      <el-table
        :data="userList"
        stripe
        v-loading="loading"
        element-loading-text="加载中..."
        element-loading-background="rgba(255, 255, 255, 0.8)"
        :default-sort="{ prop: 'createTime', order: 'descending' }"
        highlight-current-row
        @selection-change="handleSelectionChange"
        class="user-table"
      >
        <el-table-column type="selection" width="55" />
        <el-table-column prop="avatar" label="头像" width="80">
          <template #default="{ row }">
            <el-avatar :src="row.avatar" :alt="row.username">{{ row.username.charAt(0).toUpperCase() }}</el-avatar>
          </template>
        </el-table-column>
        <el-table-column prop="username" label="用户名" width="120" sortable />
        <el-table-column prop="realName" label="真实姓名" width="120" sortable />
        <el-table-column prop="email" label="邮箱" width="200" show-overflow-tooltip sortable />
        <el-table-column prop="phone" label="手机号" width="130" />
        <el-table-column prop="role" label="角色" width="120" sortable>
          <template #default="{ row }">
            <el-tag :type="getRoleType(row.role)">{{ getRoleText(row.role) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="department" label="部门" width="120" sortable />
        <el-table-column prop="status" label="状态" width="100" sortable>
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)">{{ getStatusText(row.status) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="lastLogin" label="最后登录" width="160" sortable />
        <el-table-column prop="createTime" label="创建时间" width="160" sortable />
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" size="small" @click="viewUser(row)">查看</el-button>
            <el-button type="warning" size="small" @click="editUser(row)">编辑</el-button>              <el-dropdown @command="(command: string) => handleCommand(command, row)">
              <el-button type="info" size="small">
                更多<el-icon class="el-icon--right"><ArrowDown /></el-icon>
              </el-button>
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item command="resetPassword">重置密码</el-dropdown-item>
                  <el-dropdown-item command="permissions">权限设置</el-dropdown-item>
                  <el-dropdown-item 
                    :command="row.status === 'active' ? 'disable' : 'enable'"
                    divided
                  >
                    {{ row.status === 'active' ? '禁用用户' : '启用用户' }}
                  </el-dropdown-item>
                  <el-dropdown-item command="delete">删除用户</el-dropdown-item>
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
    </el-card>    <!-- 新增/编辑用户对话框 - 简化版本 -->
    <Teleport to="body">
      <div v-if="showAddDialog" class="dialog-overlay" @click.self="closeDialog">
        <div class="dialog-content">
          <div class="dialog-header">
            <h3>{{ editForm.id ? '编辑用户' : '新增用户' }}</h3>
            <button class="close-btn" @click="closeDialog">×</button>
          </div>
            <div class="dialog-body">
            <form @submit.prevent="saveUser">
              <div class="form-row">
                <div class="form-group">
                  <label>用户名 *</label>
                  <input 
                    v-model="editForm.username" 
                    type="text" 
                    placeholder="请输入用户名"
                    required
                  />
                </div>
                <div class="form-group">
                  <label>员工工号 *</label>
                  <input 
                    v-model="editForm.employee_id" 
                    type="text" 
                    placeholder="请输入员工工号"
                    required
                  />
                </div>
              </div>
              
              <div class="form-row">
                <div class="form-group">
                  <label>姓</label>
                  <input 
                    v-model="editForm.first_name" 
                    type="text" 
                    placeholder="请输入姓"
                  />
                </div>
                <div class="form-group">
                  <label>名</label>
                  <input 
                    v-model="editForm.last_name" 
                    type="text" 
                    placeholder="请输入名"
                  />
                </div>
              </div>
              
              <div class="form-row">
                <div class="form-group">
                  <label>邮箱 *</label>
                  <input 
                    v-model="editForm.email" 
                    type="email" 
                    placeholder="请输入邮箱"
                    required
                  />
                </div>
                <div class="form-group">
                  <label>手机号 *</label>
                  <input 
                    v-model="editForm.phone" 
                    type="text" 
                    placeholder="请输入手机号"
                    required
                  />
                </div>
              </div>
              
              <div class="form-row">
                <div class="form-group">
                  <label>用户角色 *</label>
                  <select v-model="editForm.user_type" required>
                    <option value="employee">普通员工</option>
                    <option value="manager">部门经理</option>
                    <option value="admin">系统管理员</option>
                  </select>
                </div>
                <div class="form-group">
                  <label>职位</label>
                  <input 
                    v-model="editForm.position" 
                    type="text" 
                    placeholder="请输入职位"
                  />
                </div>
              </div>

              <div class="form-row">
                <div class="form-group">
                  <label>所属部门 *</label>
                  <select v-model="editForm.department" required>
                    <option disabled value="">请选择部门</option>
                    <option v-for="dept in departmentList" :key="dept.id" :value="dept.id">
                      {{ dept.name }}
                    </option>
                  </select>
                </div>
              </div>
              
              <div class="form-row" v-if="!editForm.id">
                <div class="form-group">
                  <label>初始密码 *</label>
                  <input 
                    v-model="editForm.password" 
                    type="password" 
                    placeholder="请输入初始密码"
                    required
                  />
                </div>
                <div class="form-group">
                  <label>确认密码 *</label>
                  <input 
                    v-model="editForm.confirm_password" 
                    type="password" 
                    placeholder="再次输入密码"
                    required
                  />
                </div>
              </div>
            </form>
          </div>
          
          <div class="dialog-footer">
            <button type="button" class="btn btn-default" @click="closeDialog">
              取消
            </button>
            <button type="button" class="btn btn-primary" @click="saveUser" :disabled="saving">
              {{ saving ? '保存中...' : '确定' }}
            </button>
          </div>
        </div>
      </div>
    </Teleport>
    
    <!-- 原始Element Plus对话框（备用） -->
    <el-dialog
      v-model="showAddDialog"
      :title="editForm.id ? '编辑用户' : '新增用户'"
      width="700px"
      @close="resetForm"
      :close-on-click-modal="false"
      :close-on-press-escape="false"
      style="display: none;"
    >      <el-form :model="editForm" :rules="formRules" ref="formRef" label-width="100px"><el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="用户名" prop="username">
              <el-input v-model="editForm.username" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="员工工号" prop="employee_id">
              <el-input v-model="editForm.employee_id" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="姓" prop="first_name">
              <el-input v-model="editForm.first_name" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="名" prop="last_name">
              <el-input v-model="editForm.last_name" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="邮箱" prop="email">
              <el-input v-model="editForm.email" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="手机号" prop="phone">
              <el-input v-model="editForm.phone" />
            </el-form-item>
          </el-col>
        </el-row>        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="用户角色" prop="user_type">
              <el-select v-model="editForm.user_type" style="width: 100%">
                <el-option label="系统管理员" value="admin" />
                <el-option label="部门经理" value="manager" />
                <el-option label="普通员工" value="employee" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="所属部门" prop="department">
              <el-select v-model="editForm.department" style="width: 100%">
                <el-option 
                  v-for="dept in departmentList" 
                  :key="dept.id" 
                  :label="dept.name" 
                  :value="dept.id" 
                />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="职位" prop="position">
              <el-input v-model="editForm.position" />
            </el-form-item>
          </el-col>
          <el-col :span="12" v-if="!editForm.id">
            <el-form-item label="初始密码" prop="password">
              <el-input
                v-model="editForm.password"
                type="password"
                placeholder="请输入初始密码"
                show-password
              />
            </el-form-item>
          </el-col>
          <el-col :span="12" v-if="!editForm.id">
            <el-form-item label="确认密码" prop="confirm_password">
              <el-input
                v-model="editForm.confirm_password"
                type="password"
                placeholder="再次输入密码"
                show-password
              />
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="用户权限">
          <el-checkbox-group v-model="editForm.permissions">
            <el-checkbox label="user:read">查看用户</el-checkbox>
            <el-checkbox label="user:write">编辑用户</el-checkbox>
            <el-checkbox label="user:delete">删除用户</el-checkbox>
            <el-checkbox label="dept:read">查看部门</el-checkbox>
            <el-checkbox label="dept:write">编辑部门</el-checkbox>
            <el-checkbox label="system:config">系统配置</el-checkbox>
          </el-checkbox-group>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showAddDialog = false">取消</el-button>
        <el-button type="primary" @click="saveUser" :loading="saving">确定</el-button>
      </template>
    </el-dialog>

    <!-- 用户详情对话框 -->
    <el-dialog v-model="showDetailDialog" title="用户详情" width="800px">
      <div v-if="selectedUser" class="user-detail">
        <el-row :gutter="20">
          <el-col :span="8">
            <div class="user-avatar-section">
              <el-avatar :size="120" :src="selectedUser.avatar">
                {{ selectedUser.username.charAt(0).toUpperCase() }}
              </el-avatar>
              <div class="user-basic-info">
                <h3>{{ selectedUser.realName }}</h3>
                <p>@{{ selectedUser.username }}</p>
                <el-tag :type="getRoleType(selectedUser.role)">{{ getRoleText(selectedUser.role) }}</el-tag>
              </div>
            </div>
          </el-col>
          <el-col :span="16">
            <el-descriptions :column="2" border>
              <el-descriptions-item label="邮箱">{{ selectedUser.email }}</el-descriptions-item>
              <el-descriptions-item label="手机号">{{ selectedUser.phone }}</el-descriptions-item>
              <el-descriptions-item label="部门">{{ selectedUser.department }}</el-descriptions-item>
              <el-descriptions-item label="状态">
                <el-tag :type="getStatusType(selectedUser.status)">{{ getStatusText(selectedUser.status) }}</el-tag>
              </el-descriptions-item>
              <el-descriptions-item label="最后登录">{{ selectedUser.lastLogin }}</el-descriptions-item>
              <el-descriptions-item label="创建时间">{{ selectedUser.createTime }}</el-descriptions-item>
              <el-descriptions-item label="登录次数" :span="2">{{ selectedUser.loginCount || 0 }} 次</el-descriptions-item>
            </el-descriptions>
          </el-col>
        </el-row>

        <el-divider>用户权限</el-divider>
        <div class="permissions-section">
          <el-tag
            v-for="permission in selectedUser.permissions"
            :key="permission"
            class="permission-tag"
          >
            {{ getPermissionText(permission) }}
          </el-tag>
        </div>

        <el-divider>登录历史</el-divider>
        <el-table :data="loginHistory" size="small">
          <el-table-column prop="loginTime" label="登录时间" width="160" />
          <el-table-column prop="loginIp" label="登录IP" width="120" />
          <el-table-column prop="userAgent" label="设备信息" show-overflow-tooltip />
          <el-table-column prop="status" label="状态" width="80">
            <template #default="{ row }">
              <el-tag :type="row.status === 'success' ? 'success' : 'danger'" size="small">
                {{ row.status === 'success' ? '成功' : '失败' }}
              </el-tag>
            </template>
          </el-table-column>
        </el-table>
      </div>
    </el-dialog>

    <!-- 权限设置对话框 -->
    <el-dialog v-model="showPermissionDialog" title="权限设置" width="600px">
      <div v-if="selectedUser">
        <p>为用户 <strong>{{ selectedUser.realName }}</strong> 设置权限</p>
        <el-form label-width="100px">
          <el-form-item label="用户权限">
            <el-checkbox-group v-model="userPermissions">
              <div class="permission-group">
                <div class="permission-category">
                  <h4>用户管理</h4>
                  <el-checkbox label="user:read">查看用户</el-checkbox>
                  <el-checkbox label="user:write">编辑用户</el-checkbox>
                  <el-checkbox label="user:delete">删除用户</el-checkbox>
                </div>
                <div class="permission-category">
                  <h4>部门管理</h4>
                  <el-checkbox label="dept:read">查看部门</el-checkbox>
                  <el-checkbox label="dept:write">编辑部门</el-checkbox>
                  <el-checkbox label="dept:delete">删除部门</el-checkbox>
                </div>
                <div class="permission-category">
                  <h4>系统管理</h4>
                  <el-checkbox label="system:config">系统配置</el-checkbox>
                  <el-checkbox label="system:backup">数据备份</el-checkbox>
                  <el-checkbox label="system:log">日志查看</el-checkbox>
                </div>
              </div>
            </el-checkbox-group>
          </el-form-item>
        </el-form>
      </div>
      <template #footer>
        <el-button @click="showPermissionDialog = false">取消</el-button>
        <el-button type="primary" @click="savePermissions">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, nextTick } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { showConfirm, showDeleteConfirm, showBatchDeleteConfirm } from '@/utils/confirm'
import {
  Search,
  Plus,
  Download,
  ArrowDown
} from '@element-plus/icons-vue'
import {
  getUserList as fetchUserList,
  createUser,
  updateUser,
  deleteUser,
  activateUser,
  deactivateUser,
  resetUserPassword,
  getDepartmentList,
  type User as ApiUser,
  type UserCreateData,
  type UserListParams
} from '@/services/user'

// 前端用户接口定义（基于后端API数据结构）
interface User {
  id: number
  username: string
  realName: string  // 映射为 first_name + last_name
  email: string
  phone: string
  role: string  // 映射为 user_type
  department: string  // 映射为 department_name
  departmentId: number  // department id
  status: string  // 映射为 is_active_employee
  lastLogin: string
  createTime: string  // 映射为 created_at
  avatar?: string
  permissions: string[]
  loginCount?: number
}

// 响应式数据
const loading = ref(false)
const saving = ref(false)
const showAddDialog = ref(false)
const showDetailDialog = ref(false)
const showPermissionDialog = ref(false)
const selectedUser = ref<User | null>(null)
const selectedUsers = ref<User[]>([])
const currentPage = ref(1)
const pageSize = ref(20)
const total = ref(0)
const userPermissions = ref<string[]>([])

// 搜索表单
const searchForm = reactive({
  keyword: '',
  role: '',
  status: '',
  department: ''
})

// 用户列表
const userList = ref<User[]>([])
const departmentList = ref<any[]>([])  // 部门列表

// 编辑表单
const editForm = reactive({
  id: null as number | null,
  username: '',
  first_name: '',
  last_name: '',
  email: '',
  phone: '',
  user_type: 'employee' as 'admin' | 'manager' | 'employee',
  department: null as number | null,
  password: '',
  confirm_password: '',
  employee_id: '',
  position: '',
  permissions: [] as string[]
})

// 登录历史
const loginHistory = ref([
  {
    loginTime: '2024-01-15 10:30:25',
    loginIp: '192.168.1.100',
    userAgent: 'Chrome 120.0.0.0 Windows',
    status: 'success'
  },
  {
    loginTime: '2024-01-14 09:15:30',
    loginIp: '192.168.1.100',
    userAgent: 'Chrome 120.0.0.0 Windows',
    status: 'success'
  },
  {
    loginTime: '2024-01-13 08:45:12',
    loginIp: '192.168.1.101',
    userAgent: 'Firefox 121.0 Windows',
    status: 'failed'
  }
])

// 表单验证规则
const formRules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 3, max: 20, message: '用户名长度在 3 到 20 个字符', trigger: 'blur' }
  ],
  first_name: [{ required: true, message: '请输入姓', trigger: 'blur' }],
  last_name: [{ required: true, message: '请输入名', trigger: 'blur' }],
  email: [
    { required: true, message: '请输入邮箱', trigger: 'blur' },
    { type: 'email', message: '邮箱格式不正确', trigger: 'blur' }
  ],
  phone: [
    { required: true, message: '请输入手机号', trigger: 'blur' },
    { pattern: /^1[3-9]\d{9}$/, message: '手机号格式不正确', trigger: 'blur' }
  ],
  user_type: [{ required: true, message: '请选择用户角色', trigger: 'change' }],
  department: [{ required: true, message: '请选择所属部门', trigger: 'change' }],
  employee_id: [{ required: true, message: '请输入员工工号', trigger: 'blur' }],
  password: [
    { required: true, message: '请输入初始密码', trigger: 'blur' },
    { min: 6, max: 20, message: '密码长度在 6 到 20 个字符', trigger: 'blur' }
  ],
  confirm_password: [
    { required: true, message: '请确认密码', trigger: 'blur' },
    { 
      validator: (rule: any, value: any, callback: any) => {
        if (value !== editForm.password) {
          callback(new Error('两次输入的密码不一致'))
        } else {
          callback()
        }
      }, 
      trigger: 'blur' 
    }
  ]
}

const formRef = ref()

// 数据转换函数：将API数据转换为前端使用的格式
const transformApiUserToFrontendUser = (apiUser: ApiUser): User => {
  return {
    id: apiUser.id,
    username: apiUser.username,
    realName: `${apiUser.first_name} ${apiUser.last_name}`.trim() || apiUser.username,
    email: apiUser.email,
    phone: apiUser.phone || '',
    role: apiUser.user_type,
    department: apiUser.department_name || '',
    departmentId: apiUser.department,
    status: apiUser.is_active_employee ? 'active' : 'disabled',
    lastLogin: '暂无记录', // API暂时没有这个字段
    createTime: new Date(apiUser.created_at).toLocaleString('zh-CN'),
    avatar: apiUser.avatar,
    permissions: getDefaultPermissions(apiUser.user_type),
    loginCount: 0 // API暂时没有这个字段
  }
}

// 根据用户类型获取默认权限
const getDefaultPermissions = (userType: string): string[] => {
  switch (userType) {
    case 'admin':
      return ['user:read', 'user:write', 'user:delete', 'system:config']
    case 'manager':
      return ['user:read', 'dept:read']
    case 'employee':
      return ['user:read']
    default:
      return []
  }
}

// 获取用户列表
const getUserList = async () => {
  loading.value = true
  try {
    const params: UserListParams = {
      page: currentPage.value,
      page_size: pageSize.value
    }

    // 添加搜索条件
    if (searchForm.keyword) {
      params.search = searchForm.keyword
    }
    if (searchForm.role) {
      params.user_type = searchForm.role
    }
    if (searchForm.status) {
      params.is_active_employee = searchForm.status === 'active'
    }

    const response = await fetchUserList(params)
    
    // 转换API数据为前端格式
    userList.value = response.results.map(transformApiUserToFrontendUser)
    total.value = response.count
    
  } catch (error: any) {
    console.error('获取用户列表失败:', error)
    ElMessage.error('获取用户列表失败')
  } finally {
    loading.value = false
  }
}

// 获取部门列表
const getDepartments = async () => {
  try {
    const response = await getDepartmentList()
    // 兼容返回结构：可能是数组、或 {results: [...]}
    if (Array.isArray(response)) {
      departmentList.value = response
    } else if (Array.isArray(response?.results)) {
      departmentList.value = response.results
    } else {
      departmentList.value = []
      console.warn('部门列表返回格式异常，已置为空数组', response)
    }
  } catch (error: any) {
    console.error('获取部门列表失败:', error)
    ElMessage.error('获取部门列表失败')
  }
}

// 回车键搜索处理
const onSearchKeyPress = () => {
  searchUsers()
}

// 搜索用户
const searchUsers = () => {
  currentPage.value = 1
  getUserList()
}

// 重置搜索
const resetSearch = () => {
  Object.assign(searchForm, {
    keyword: '',
    role: '',
    status: '',
    department: ''
  })
  searchUsers()
}

// 打开新增用户对话框
const openAddDialog = () => {
  // 直接设置对话框状态，不调用resetForm
  showAddDialog.value = true
}

// 查看用户详情
const viewUser = (user: User) => {
  selectedUser.value = user
  showDetailDialog.value = true
}

// 编辑用户
const editUser = (user: User) => {
  Object.assign(editForm, {
    id: user.id,
    username: user.username,
    first_name: user.realName.split(' ')[0] || '',
    last_name: user.realName.split(' ')[1] || '',
    email: user.email,
    phone: user.phone,
    user_type: user.role as 'admin' | 'manager' | 'employee',
    department: user.departmentId,
    employee_id: '',  // 从API获取时需要补充
    position: '',     // 从API获取时需要补充
    password: '',
    confirm_password: '',
    permissions: user.permissions
  })
  showAddDialog.value = true
}

// 自定义表单验证
const validateForm = () => {
  const errors: string[] = []
  
  // 验证必填字段
  if (!editForm.username.trim()) {
    errors.push('用户名不能为空')
  }
  
  if (!editForm.employee_id.trim()) {
    errors.push('员工工号不能为空')
  }
  
  if (!editForm.email.trim()) {
    errors.push('邮箱不能为空')
  } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(editForm.email)) {
    errors.push('邮箱格式不正确')
  }
  
  if (!editForm.phone.trim()) {
    errors.push('手机号不能为空')
  } else if (!/^1[3-9]\d{9}$/.test(editForm.phone)) {
    errors.push('手机号格式不正确')
  }
  
  if (!editForm.user_type) {
    errors.push('用户角色不能为空')
  }

  if (!editForm.department) {
    errors.push('所属部门不能为空')
  }
  
  // 新增用户时验证密码
  if (!editForm.id) {
    if (!editForm.password.trim()) {
      errors.push('密码不能为空')
    } else if (editForm.password.length < 6) {
      errors.push('密码长度不能少于6位')
    }
    
    if (editForm.password !== editForm.confirm_password) {
      errors.push('两次输入的密码不一致')
    }
  }
  
  return {
    isValid: errors.length === 0,
    errors
  }
}

// 保存用户
const saveUser = async () => {
  // 使用自定义验证而不是Element Plus表单验证
  const validation = validateForm()
  if (!validation.isValid) {
    ElMessage.error('表单验证失败: ' + validation.errors.join(', '))
    return
  }  
  try {
    saving.value = true
    
    const userData: UserCreateData = {
      username: editForm.username,
      email: editForm.email,
      password: editForm.password,
      confirm_password: editForm.confirm_password,
      first_name: editForm.first_name,
      last_name: editForm.last_name,
      employee_id: editForm.employee_id,      phone: editForm.phone,
      user_type: editForm.user_type,
      department: editForm.department!,
      position: editForm.position
    }
    
    if (editForm.id) {
      // 更新用户 - 编辑时不需要密码字段
      const { password, confirm_password, ...updateData } = userData
      await updateUser(editForm.id, updateData)
      ElMessage.success('更新成功')
    } else {
      // 创建新用户
      const result = await createUser(userData)
      ElMessage.success('添加成功')
    }    
    showAddDialog.value = false
    await getUserList()  } catch (error: any) {
    const errorMessage = error instanceof Error ? error.message : String(error)
    ElMessage.error('操作失败: ' + errorMessage)
  } finally {
    saving.value = false
  }
}

// 关闭对话框
const closeDialog = () => {
  showAddDialog.value = false
  resetForm()
}

// 重置表单
const resetForm = () => {
  // 只在Element Plus表单存在时重置
  if (formRef.value) {
    formRef.value.resetFields()
  }
  
  // 重置表单数据
  Object.assign(editForm, {
    id: null,
    username: '',
    first_name: '',
    last_name: '',
    email: '',
    phone: '',
    user_type: 'employee' as 'admin' | 'manager' | 'employee',
    department: null,
    employee_id: '',
    position: '',
    password: '',
    confirm_password: '',
    permissions: []
  })
}

// 处理命令操作
const handleCommand = async (command: string, user: User) => {
  switch (command) {
    case 'resetPassword':
      try {
        await ElMessageBox.confirm('确定要重置该用户的密码吗？', '确认操作', {
          type: 'warning'
        })
        const result = await resetUserPassword(user.id)
        ElMessage.success(`密码重置成功，新密码为: ${result.password}`)
      } catch (error: any) {
        if (error !== 'cancel') {
          ElMessage.error('重置密码失败')
        }      }
      break
    case 'permissions':
      selectedUser.value = user
      userPermissions.value = [...user.permissions]
      showPermissionDialog.value = true
      break
    case 'enable':
      try {
        await activateUser(user.id)
        user.status = 'active'
        ElMessage.success('用户已启用')
      } catch (error: any) {
        ElMessage.error('启用用户失败')
      }
      break
    case 'disable':
      try {
        await deactivateUser(user.id)
        user.status = 'disabled'
        ElMessage.success('用户已禁用')
      } catch (error: any) {
        ElMessage.error('禁用用户失败')
      }
      break
    case 'delete':
      try {
        await showDeleteConfirm(`用户 "${user.username}"`)
        await deleteUser(user.id)
        ElMessage.success('用户已删除')
        await getUserList()
      } catch (error: any) {
        if (error !== 'cancel') {
          ElMessage.error('删除用户失败')
        }
      }
      break
  }
}

// 保存权限
const savePermissions = () => {
  if (selectedUser.value) {
    selectedUser.value.permissions = [...userPermissions.value]
    ElMessage.success('权限设置成功')
    showPermissionDialog.value = false
  }
}

// 选择变化处理
const handleSelectionChange = (selection: User[]) => {
  selectedUsers.value = selection
}

// 批量启用
const batchEnable = async () => {
  try {
    await showConfirm({
      title: '批量启用用户',
      message: `确定要启用选中的 ${selectedUsers.value.length} 个用户吗？`,
      description: '启用后用户将可以正常登录系统。',
      type: 'info',
      confirmButtonText: '确认启用'
    })
    
    const promises = selectedUsers.value.map(user => activateUser(user.id))
    await Promise.all(promises)
    
    ElMessage.success(`已启用 ${selectedUsers.value.length} 个用户`)
    selectedUsers.value = []
    await getUserList()  } catch (error: any) {
    if (error !== 'cancel') {
      ElMessage.error('批量启用失败')
    }
  }
}

// 批量禁用
const batchDisable = async () => {
  try {
    await showConfirm({
      title: '批量禁用用户',
      message: `确定要禁用选中的 ${selectedUsers.value.length} 个用户吗？`,
      description: '禁用后用户将无法登录系统，但数据仍会保留。',
      type: 'warning',
      confirmButtonText: '确认禁用'
    })
    
    const promises = selectedUsers.value.map(user => deactivateUser(user.id))
    await Promise.all(promises)
    
    ElMessage.success(`已禁用 ${selectedUsers.value.length} 个用户`)
    selectedUsers.value = []
    await getUserList()  } catch (error: any) {
    if (error !== 'cancel') {
      ElMessage.error('批量禁用失败')
    }
  }
}

// 导出用户
const exportUsers = () => {
  try {
    const exportData = selectedUsers.value.length > 0 ? selectedUsers.value : userList.value
    
    if (exportData.length === 0) {
      ElMessage.warning('没有可导出的数据')
      return
    }

    // 构建CSV数据
    const headers = ['用户名', '姓名', '邮箱', '角色', '部门', '电话', '状态', '最后登录', '创建时间']
    const csvContent = [
      headers.join(','),
      ...exportData.map((user: User) => [
        user.username,
        user.realName || '',
        user.email,
        user.role === 'admin' ? '管理员' : user.role === 'manager' ? '经理' : '员工',
        user.department || '',
        user.phone || '',
        user.status === 'active' ? '激活' : '禁用',
        user.lastLogin || '',
        user.createTime || ''
      ].map(field => `"${field}"`).join(','))
    ].join('\n')

    // 创建并下载文件
    const blob = new Blob(['\ufeff' + csvContent], { type: 'text/csv;charset=utf-8;' })
    const link = document.createElement('a')
    link.href = URL.createObjectURL(blob)
    const timestamp = new Date().toISOString().slice(0, 19).replace(/[:]/g, '-')
    const exportType = selectedUsers.value.length > 0 ? '选中用户' : '全部用户'
    link.download = `${exportType}_${timestamp}.csv`
    link.click()
    
    ElMessage.success(`成功导出 ${exportData.length} 条数据`)
  } catch (error) {
    console.error('导出失败:', error)
    ElMessage.error('导出失败，请稍后重试')
  }
}

// 获取角色类型
const getRoleType = (role: string) => {
  const typeMap: Record<string, string> = {
    admin: 'danger',
    manager: 'warning',
    employee: 'success'
  }
  return typeMap[role] || 'default'
}

// 获取角色文本
const getRoleText = (role: string) => {
  const textMap: Record<string, string> = {
    admin: '系统管理员',
    manager: '部门经理',
    employee: '普通员工'
  }
  return textMap[role] || role
}

// 获取状态类型
const getStatusType = (status: string) => {
  const typeMap: Record<string, string> = {
    active: 'success',
    disabled: 'danger',
    locked: 'warning'
  }
  return typeMap[status] || 'default'
}

// 获取状态文本
const getStatusText = (status: string) => {
  const textMap: Record<string, string> = {
    active: '启用',
    disabled: '禁用',
    locked: '锁定'
  }
  return textMap[status] || status
}

// 获取权限文本
const getPermissionText = (permission: string) => {
  const textMap: Record<string, string> = {
    'user:read': '查看用户',
    'user:write': '编辑用户',
    'user:delete': '删除用户',
    'dept:read': '查看部门',
    'dept:write': '编辑部门',
    'dept:delete': '删除部门',
    'system:config': '系统配置',
    'system:backup': '数据备份',
    'system:log': '日志查看'
  }
  return textMap[permission] || permission
}

// 分页处理
const handleSizeChange = (val: number) => {
  pageSize.value = val
  getUserList()
}

const handleCurrentChange = (val: number) => {
  currentPage.value = val
  getUserList()
}

onMounted(() => {
  getUserList()
  getDepartments()
})
</script>

<style scoped>
.user-management {
  padding: var(--hr-space-lg);
}

.search-card {
  margin-bottom: var(--hr-space-lg);
  border-radius: var(--hr-radius-lg);
  box-shadow: var(--hr-shadow-card);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

/* 表格优化样式 */
.user-table {
  border-radius: var(--hr-radius-md);
  overflow: hidden;
}

.user-table :deep(.el-table__header-wrapper) {
  background: linear-gradient(to bottom, var(--hr-gray-50), var(--hr-gray-100));
}

.user-table :deep(.el-table__header th) {
  background: transparent;
  font-weight: 600;
  color: var(--color-text-primary);
  font-size: 13px;
}

.user-table :deep(.el-table__row) {
  transition: all var(--hr-transition-normal);
  cursor: pointer;
}

.user-table :deep(.el-table__row:hover) {
  background-color: var(--hr-gray-50) !important;
  transform: translateY(-1px);
  box-shadow: var(--hr-shadow-sm);
}

.user-table :deep(.current-row) {
  background-color: var(--hr-primary-bg) !important;
}

.user-table :deep(.el-table__body-wrapper) {
  min-height: 400px;
}

.pagination-container {
  margin-top: var(--hr-space-lg);
  text-align: right;
  padding: var(--hr-space-md) 0;
}

.user-detail {
  padding: var(--hr-space-sm) 0;
}

.user-avatar-section {
  text-align: center;
  padding: var(--hr-space-lg);
}

.user-basic-info {
  margin-top: var(--hr-space-lg);
}

.user-basic-info h3 {
  margin: 10px 0 5px;
  color: var(--color-text-primary);
  font-weight: 600;
}

.user-basic-info p {
  margin: 5px 0 15px;
  color: var(--color-text-secondary);
  font-size: 14px;
}

.permissions-section {
  padding: var(--hr-space-sm) 0;
}

.permission-tag {
  margin: 4px 8px 4px 0;
}

.permission-group {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: var(--hr-space-lg);
}

.permission-category h4 {
  margin: 0 0 10px;
  color: var(--color-text-primary);
  font-size: 14px;
  font-weight: 600;
}

.permission-category .el-checkbox {
  display: block;
  margin: 8px 0;
}

:deep(.el-table) {
  font-size: 14px;
}

:deep(.el-dialog__body) {
  padding: var(--hr-space-lg);
}

:deep(.el-descriptions__body) {
  background-color: var(--hr-gray-50);
}

/* 自定义对话框样式 */
.dialog-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.45);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 9999;
  backdrop-filter: blur(4px);
}

.dialog-content {
  background: white;
  border-radius: var(--hr-radius-lg);
  box-shadow: var(--hr-shadow-xl);
  max-width: 700px;
  width: 90%;
  max-height: 80vh;
  overflow-y: auto;
}

.dialog-header {
  padding: var(--hr-space-lg) var(--hr-space-lg) 0 var(--hr-space-lg);
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: 1px solid var(--color-border);
  margin-bottom: var(--hr-space-lg);
}

.dialog-header h3 {
  margin: 0;
  font-size: 17px;
  font-weight: 600;
  color: var(--color-text-primary);
}

.close-btn {
  background: none;
  border: none;
  font-size: 20px;
  cursor: pointer;
  color: var(--color-text-placeholder);
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: var(--hr-radius-sm);
  transition: all var(--hr-transition-fast);
}

.close-btn:hover {
  background: var(--hr-gray-100);
  color: var(--color-text-primary);
}

.dialog-body {
  padding: 0 var(--hr-space-lg) var(--hr-space-lg) var(--hr-space-lg);
}

.form-row {
  display: flex;
  gap: 15px;
  margin-bottom: 15px;
}

.form-group {
  flex: 1;
}

.form-group label {
  display: block;
  margin-bottom: 6px;
  font-weight: 500;
  color: var(--color-text-regular);
  font-size: 13px;
}

.form-group input,
.form-group select {
  width: 100%;
  padding: 9px 12px;
  border: 1px solid var(--color-border);
  border-radius: var(--hr-radius-sm);
  font-size: 14px;
  box-sizing: border-box;
  transition: all var(--hr-transition-fast);
}

.form-group input:focus,
.form-group select:focus {
  outline: none;
  border-color: var(--hr-primary);
  box-shadow: 0 0 0 3px rgba(79, 110, 247, 0.12);
}

.dialog-footer {
  padding: var(--hr-space-md) var(--hr-space-lg);
  border-top: 1px solid var(--color-border);
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}

.btn {
  padding: 9px 20px;
  border: 1px solid var(--color-border);
  border-radius: var(--hr-radius-sm);
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
  transition: all var(--hr-transition-fast);
}

.btn-default {
  background: white;
  color: var(--color-text-regular);
}

.btn-default:hover {
  background: var(--hr-gray-50);
  border-color: var(--hr-gray-300);
}

.btn-primary {
  background: var(--hr-primary);
  color: white;
  border-color: var(--hr-primary);
}

.btn-primary:hover {
  background: var(--hr-primary-dark);
  border-color: var(--hr-primary-dark);
}

.btn-primary:disabled {
  background: var(--hr-gray-300);
  border-color: var(--hr-gray-300);
  cursor: not-allowed;
}
</style>
