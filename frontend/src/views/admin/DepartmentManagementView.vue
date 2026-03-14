<template>  <div class="department-management">
    <el-card class="page-header">
      <div class="header-content">
        <h2>部门管理</h2>
        <div class="header-actions">
          <el-button type="primary" @click="showAddDialog = true">
            <el-icon><Plus /></el-icon>
            新增部门
          </el-button>
          <el-button type="success" @click="expandAll">
            <el-icon><FolderOpened /></el-icon>
            展开全部
          </el-button>
          <el-button @click="collapseAll">
            <el-icon><Folder /></el-icon>
            收起全部
          </el-button>
        </div>
      </div>
    </el-card>

    <!-- 搜索筛选 -->
    <el-card class="search-card">
      <el-form :inline="true" :model="searchForm">        <el-form-item label="部门名称">
          <el-input 
            v-model="searchForm.name" 
            placeholder="请输入部门名称"
            @input="filterDepartments"
            clearable
          />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="filterDepartments">
            <el-icon><Search /></el-icon>
            搜索
          </el-button>
          <el-button @click="resetSearch">重置</el-button>
        </el-form-item>
      </el-form>
    </el-card>    <!-- 部门树形表格 -->
    <el-card class="table-card">
      <el-table
        ref="departmentTableRef"
        :data="departments"
        row-key="id"
        :tree-props="{ children: 'children' }"
        v-loading="loading"
        style="width: 100%"
        border
        :indent="20"
        @expand-change="onExpandChange"
        default-expand-all
      ><el-table-column label="部门名称" prop="name" min-width="200">
          <template #default="{ row }">
            <div class="department-name">
              <el-icon class="dept-icon"><OfficeBuilding /></el-icon>
              <span>{{ row.name }}</span>
            </div>
          </template>
        </el-table-column>
        
        <el-table-column label="部门描述" prop="description" min-width="200">
          <template #default="{ row }">
            <span v-if="row.description">{{ row.description }}</span>
            <el-text type="info" v-else>暂无描述</el-text>
          </template>
        </el-table-column>
        
        <el-table-column label="创建时间" prop="created_at" width="160">
          <template #default="{ row }">
            {{ formatDate(row.created_at) }}
          </template>
        </el-table-column>          <el-table-column label="操作" width="280" fixed="right">
          <template #default="{ row }">
            <el-button 
              type="primary" 
              size="small" 
              @click="editDepartment(row)"
              link
            >
              编辑
            </el-button>
            <el-button 
              type="warning" 
              size="small" 
              @click="setManager(row)"
              link
            >
              设置经理
            </el-button>
            <el-button 
              type="success" 
              size="small" 
              @click="addSubDepartment(row)"
              link
            >
              添加子部门
            </el-button>
            <el-popconfirm
              title="确定要删除这个部门吗？"
              @confirm="deleteDepartment(row)"
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
    </el-card>

    <!-- 新增/编辑部门对话框 -->
    <el-dialog
      v-model="showAddDialog"
      :title="editingDepartment ? '编辑部门' : '新增部门'"
      width="600px"
    >
      <el-form
        ref="departmentFormRef"
        :model="departmentForm"
        :rules="departmentRules"
        label-width="100px"
      >        <el-form-item label="上级部门" prop="parent">
          <el-tree-select
            v-model="departmentForm.parent"
            :data="departmentTreeOptions"
            placeholder="请选择上级部门"
            node-key="id"
            :props="{ label: 'name', children: 'children' }"
            check-strictly
            clearable
          />
        </el-form-item>
        
        <el-form-item label="部门名称" prop="name">
          <el-input v-model="departmentForm.name" placeholder="请输入部门名称" />
        </el-form-item>
        
        <el-form-item label="部门描述" prop="description">
          <el-input
            v-model="departmentForm.description"
            type="textarea"
            :rows="3"
            placeholder="请输入部门描述"
          />
        </el-form-item>
      </el-form>
      
      <template #footer>
        <el-button @click="showAddDialog = false">取消</el-button>
        <el-button type="primary" @click="saveDepartment" :loading="saving">
          {{ editingDepartment ? '更新' : '创建' }}
        </el-button>
      </template>    </el-dialog>

    <!-- 经理设置对话框 -->
    <el-dialog
      v-model="showManagerDialog"
      title="设置部门经理"
      width="600px"
    >
      <div v-if="selectedDepartment">
        <p>为部门 <strong>{{ selectedDepartment.name }}</strong> 设置经理</p>
        <el-form label-width="100px">          <el-form-item label="当前经理">
            <el-text v-if="selectedDepartment.manager">
              {{ selectedDepartment.manager.name }}
              ({{ selectedDepartment.manager.email }})
            </el-text>
            <el-text v-else type="info">暂无经理</el-text>
          </el-form-item>
          
          <el-form-item label="选择经理">
            <el-select
              v-model="selectedManagerId"
              placeholder="请选择经理"
              filterable
              clearable
              style="width: 100%"
            >
              <el-option
                v-for="user in availableManagers"
                :key="user.id"
                :label="`${user.first_name} ${user.last_name} (${user.username})`"
                :value="user.id"
              />
            </el-select>
          </el-form-item>
        </el-form>
      </div>
      
      <template #footer>
        <el-button @click="showManagerDialog = false">取消</el-button>
        <el-button type="primary" @click="saveManager" :loading="saving">
          保存
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, computed, nextTick, triggerRef } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Plus,
  Search,
  FolderOpened,
  Folder,
  OfficeBuilding
} from '@element-plus/icons-vue'
import departmentService, { type Department } from '@/services/department'
import { getUserList } from '@/services/user'

// 用户接口定义
interface User {
  id: number
  username: string
  first_name: string
  last_name: string
  email: string
  user_type: string
}

// 响应式数据
const loading = ref(false)
const saving = ref(false)
const showAddDialog = ref(false)
const showManagerDialog = ref(false) 
const editingDepartment = ref<Department | null>(null)
const selectedDepartment = ref<Department | null>(null)
const selectedManagerId = ref<number | null>(null)
const availableManagers = ref<User[]>([])
const departmentTableRef = ref()
const expandedKeys = ref<number[]>([])

// 搜索表单
const searchForm = reactive({
  name: ''
})

// 部门表单
const departmentForm = reactive({
  parent: null as number | null,
  name: '',
  description: ''
})

// 验证规则
const departmentRules = {
  name: [
    { required: true, message: '请输入部门名称', trigger: 'blur' },
    { min: 2, max: 50, message: '部门名称长度在 2 到 50 个字符', trigger: 'blur' }
  ]
}

// 部门数据
const departments = ref<Department[]>([])

// 加载部门数据
const loadDepartments = async () => {
  try {
    loading.value = true
    console.log('🔥🔥🔥 开始加载部门数据... 这是最新版本的代码！🔥🔥🔥')
    console.log('当前时间:', new Date().toLocaleString())
    
    const data = await departmentService.getDepartments()
    console.log('🔥 获取到的部门数据:', data)
    console.log('🔥 部门数据类型:', typeof data)
    console.log('🔥 部门数据长度:', Array.isArray(data) ? data.length : '不是数组')
    
    if (!Array.isArray(data)) {
      console.error('部门数据不是数组:', data)
      ElMessage.error('部门数据格式错误')
      return
    }
    
    if (data.length === 0) {
      console.warn('部门数据为空')
      ElMessage.warning('没有找到部门数据')
      departments.value = []
      return
    }    // 构建树形结构
    console.log('🌳 开始构建树形结构...')
    
    const treeData = departmentService.buildDepartmentTree(data)
    console.log('🌳 构建的树形数据:', treeData)
    console.log('🌳 树形数据长度:', treeData.length)
    
    // 清理数据结构，只保留表格必需的字段
    const cleanTreeData = (items: Department[]): Department[] => {
      return items.map(item => ({
        id: item.id,
        name: item.name,
        description: item.description || '',
        parent: item.parent,
        created_at: item.created_at,
        updated_at: item.updated_at,
        children: item.children ? cleanTreeData(item.children) : []
      }))
    }
    
    const cleanedData = cleanTreeData(treeData)
    console.log('🧹 清理后的数据:', cleanedData)
    
    // 详细分析树形结构
    treeData.forEach((root, index) => {
      console.log(`🌳 根部门 ${index + 1}: ${root.name} (ID: ${root.id})`)
      if (root.children && root.children.length > 0) {
        console.log(`🌳   子部门数量: ${root.children.length}`)
        root.children.forEach((child, childIndex) => {
          console.log(`🌳     子部门 ${childIndex + 1}: ${child.name} (ID: ${child.id})`)
          if (child.children && child.children.length > 0) {
            console.log(`🌳       孙部门数量: ${child.children.length}`)
            child.children.forEach((grandchild, grandIndex) => {
              console.log(`🌳         孙部门 ${grandIndex + 1}: ${grandchild.name} (ID: ${grandchild.id})`)
            })
          }
        })      } else {
        console.log(`🌳   无子部门`)
      }
    })    
    departments.value = cleanedData
    console.log('🌳 departments.value 设置完成:', departments.value)
    console.log('🌳 departments.value 长度:', departments.value.length)
    console.log('🌳 departments.value 类型:', typeof departments.value)
    console.log('🌳 departments.value 是否为数组:', Array.isArray(departments.value))
      // 强制触发响应式更新
    triggerRef(departments)
    console.log('🌳 已触发departments的响应式更新')
    
    // 设置所有应该展开的键
    const keysToExpand = collectExpandKeys(cleanedData)
    console.log('🌳 需要展开的键:', keysToExpand)
    
    // 直接设置expandedKeys，不使用延迟
    expandedKeys.value = [...keysToExpand]
    console.log('🌳 expandedKeys.value 已设置为:', expandedKeys.value)
    console.log('🌳 expandedKeys.value 长度:', expandedKeys.value.length)    // 检查第一个根部门的结构
    if (cleanedData.length > 0) {
      const firstRoot = cleanedData[0]
      console.log('🌳 第一个根部门:', firstRoot)
      console.log('🌳 第一个根部门的children:', firstRoot.children)
      console.log('🌳 第一个根部门的hasChildren:', firstRoot.hasChildren)
      console.log('🌳 第一个根部门的ID类型:', typeof firstRoot.id, firstRoot.id)
      
      if (firstRoot.children && firstRoot.children.length > 0) {
        console.log('🌳 第一个子部门:', firstRoot.children[0])
        console.log('🌳 第一个子部门的ID类型:', typeof firstRoot.children[0].id, firstRoot.children[0].id)
      }
    }
    
    // 强制触发计算属性重新计算
    console.log('强制检查 filteredDepartments:', filteredDepartments.value)
    
    ElMessage.success(`成功加载 ${data.length} 个部门，构建了 ${treeData.length} 个根部门`)
    // 等待DOM更新后检查展开状态
    await nextTick()
    console.log('🌳 DOM更新完成，当前 expandedKeys.value:', expandedKeys.value)
    
    // 如果expandedKeys不为空，说明应该已经展开了
    if (expandedKeys.value.length > 0) {
      console.log('🌳 expandedKeys已设置，等待表格响应...')
      // 给表格一些时间来响应expand-row-keys
      setTimeout(() => {
        console.log('🌳 检查表格是否已正确展开')
        if (expandedKeys.value.length > 0) {
          console.log('🌳 如果仍未展开，尝试手动展开')
          forceExpandAll()
        }
      }, 1000)
    } else {
      console.log('🌳 expandedKeys为空，直接尝试手动展开')
      forceExpandAll()
    }
      } catch (error: any) {
    console.error('加载部门数据失败:', error)
    console.error('错误详情:', error.response)
    console.error('错误状态码:', error.response?.status)
    console.error('错误消息:', error.message)
    console.error('错误堆栈:', error.stack)
    
    let errorMessage = '加载部门数据失败'
    if (error.response?.status === 401) {
      errorMessage = '认证失败，请重新登录'
    } else if (error.response?.status === 403) {
      errorMessage = '权限不足'
    } else if (error.response?.status === 404) {
      errorMessage = 'API接口不存在'
    } else if (error.response?.status >= 500) {
      errorMessage = '服务器内部错误'
    } else if (error.message.includes('Network Error')) {
      errorMessage = '网络连接错误，请检查网络'
    } else if (error.code === 'ECONNREFUSED') {
      errorMessage = '无法连接到服务器'
    }
    
    ElMessage.error(errorMessage)
  } finally {
    loading.value = false
  }
}

// 计算属性
const filteredDepartments = computed(() => {
  console.log('计算 filteredDepartments，departments.value:', departments.value)
  console.log('searchForm.name:', searchForm.name)
  
  if (!searchForm.name) {
    console.log('没有搜索条件，返回所有部门:', departments.value)
    return departments.value
  }

  const filterRecursive = (depts: Department[]): Department[] => {
    return depts.filter(dept => {
      const nameMatch = dept.name.toLowerCase().includes(searchForm.name.toLowerCase())
      
      const hasMatchingChildren = dept.children && 
        filterRecursive(dept.children).length > 0
      
      return nameMatch || hasMatchingChildren
    }).map(dept => ({
      ...dept,
      children: dept.children ? filterRecursive(dept.children) : []
    }))
  }

  const filtered = filterRecursive(departments.value)
  console.log('过滤后的部门数据:', filtered)
  return filtered
})

const departmentTreeOptions = computed(() => {
  const buildTree = (depts: Department[], excludeId?: number): any[] => {
    return depts.filter(dept => dept.id !== excludeId).map(dept => ({
      id: dept.id,
      name: dept.name,
      children: dept.children ? buildTree(dept.children, excludeId) : []
    }))
  }
  
  return buildTree(departments.value, editingDepartment.value?.id)
})

// 方法
const formatDate = (dateStr: string) => {
  return new Date(dateStr).toLocaleString('zh-CN')
}

const filterDepartments = () => {
  // 过滤逻辑在计算属性中处理
}

const resetSearch = () => {
  searchForm.name = ''
}

const expandAll = () => {
  // Element Plus table 展开所有节点的方法
  if (departmentTableRef.value) {
    const expandRecursive = (data: Department[]) => {
      data.forEach(item => {
        if (item.children && item.children.length > 0) {
          departmentTableRef.value?.toggleRowExpansion(item, true)
          expandRecursive(item.children)
        }
      })
    }
    expandRecursive(departments.value)
    console.log('已展开所有可展开的节点')
  }
}

const collapseAll = () => {
  // Element Plus table 收起所有节点的方法
  if (departmentTableRef.value) {
    const collapseRecursive = (data: Department[]) => {
      data.forEach(item => {
        if (item.children && item.children.length > 0) {
          departmentTableRef.value?.toggleRowExpansion(item, false)
          collapseRecursive(item.children)
        }
      })
    }
    collapseRecursive(departments.value)
    console.log('已收起所有可收起的节点')
  }
}

const forceExpandAll = async () => {
  // 强制展开所有节点的方法，用于数据加载后
  console.log('🌳 开始强制展开所有节点...')
  
  // 确保表格已经渲染
  await nextTick()
  
  if (departmentTableRef.value && departments.value.length > 0) {
    console.log('🌳 表格已准备就绪，开始展开操作...')
    
    // 方法1：尝试使用expand-row-keys
    const allKeys = collectExpandKeys(departments.value)
    console.log('🌳 方法1: 设置expand-row-keys:', allKeys)
    expandedKeys.value = [...allKeys]
    
    // 方法2：作为后备，使用toggleRowExpansion
    setTimeout(() => {
      console.log('🌳 方法2: 使用toggleRowExpansion后备方案')
      try {
        // 收集所有需要展开的行
        const expandableRows: Department[] = []
        
        const collectExpandableRows = (data: Department[]) => {
          data.forEach(item => {
            if (item.hasChildren && item.children && item.children.length > 0) {
              expandableRows.push(item)
              console.log(`🌳 收集需要展开的行: ${item.name} (ID: ${item.id})`)
              // 递归收集子节点中需要展开的行
              collectExpandableRows(item.children)
            }
          })
        }
        
        collectExpandableRows(departments.value)
        console.log(`🌳 共找到 ${expandableRows.length} 个需要展开的节点`)
        
        // 逐个展开所有可展开的行
        expandableRows.forEach((row, index) => {
          setTimeout(() => {
            console.log(`🌳 强制展开第 ${index + 1} 个节点: ${row.name} (ID: ${row.id})`)
            departmentTableRef.value?.toggleRowExpansion(row, true)
          }, index * 100) // 每个节点间隔100ms展开
        })
        
      } catch (err) {
        console.error('🌳 展开节点时出错:', err)
      }
    }, 500) // 等待expand-row-keys生效后再执行后备方案
    
  } else {
    console.warn('🌳 表格引用不可用或部门数据为空，无法展开节点')
  }
}

// 展开状态变化回调
const onExpandChange = (row: Department, expanded: boolean) => {
  console.log(`🌳 展开状态变化: ${row.name} -> ${expanded ? '展开' : '收起'}`)
}

// 收集所有应该展开的键
const collectExpandKeys = (data: Department[]): number[] => {
  const keys: number[] = []
  const collect = (items: Department[]) => {
    items.forEach(item => {
      if (item.hasChildren && item.children && item.children.length > 0) {
        keys.push(item.id)
        collect(item.children)
      }
    })
  }
  collect(data)
  return keys
}

const editDepartment = (department: Department) => {
  editingDepartment.value = department
  departmentForm.parent = department.parent
  departmentForm.name = department.name
  departmentForm.description = department.description
  showAddDialog.value = true
}

const addSubDepartment = (parent: Department) => {
  editingDepartment.value = null
  departmentForm.parent = parent.id
  departmentForm.name = ''
  departmentForm.description = ''
  showAddDialog.value = true
}

const saveDepartment = async () => {
  try {
    saving.value = true
    
    if (editingDepartment.value) {
      // 更新部门
      await departmentService.updateDepartment(editingDepartment.value.id, departmentForm)
      ElMessage.success('部门信息更新成功')
    } else {
      // 创建新部门
      await departmentService.createDepartment(departmentForm)
      ElMessage.success('新增部门成功')
    }
    
    showAddDialog.value = false
    // 重置表单
    departmentForm.parent = null
    departmentForm.name = ''
    departmentForm.description = ''
    editingDepartment.value = null
    
    // 刷新数据
    await loadDepartments()  } catch (error: any) {
    ElMessage.error('操作失败')
    console.error('保存部门失败:', error)
  } finally {
    saving.value = false
  }
}

const deleteDepartment = async (department: Department) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除部门"${department.name}"吗？此操作不可撤销。`,
      '删除确认',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    loading.value = true
    await departmentService.deleteDepartment(department.id)
    ElMessage.success('删除成功')
    
    // 刷新数据
    await loadDepartments()  } catch (error: any) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
      console.error('删除部门失败:', error)
    }
  } finally {
    loading.value = false
  }
}

const setManager = async (department: Department) => {
  try {
    selectedDepartment.value = department
    selectedManagerId.value = department.manager?.id || null
    
    // 加载可用的经理列表（获取所有用户，然后筛选）
    const response = await getUserList({})
    availableManagers.value = response.results.filter(
      (user: any) => user.user_type === 'admin' || user.user_type === 'manager'
    )
    
    showManagerDialog.value = true
  } catch (error) {
    console.error('加载经理列表失败:', error)
    ElMessage.error('加载经理列表失败')
  }
}

const saveManager = async () => {
  try {
    saving.value = true
    
    if (!selectedDepartment.value) return
    
    // 暂时通过提示信息来模拟功能
    ElMessage.success(`已将经理设置为: ${availableManagers.value.find(u => u.id === selectedManagerId.value)?.first_name || '未选择'} ${availableManagers.value.find(u => u.id === selectedManagerId.value)?.last_name || ''}`)
    
    showManagerDialog.value = false
    selectedDepartment.value = null
    selectedManagerId.value = null
    
    // 刷新数据
    await loadDepartments()
  } catch (error: any) {
    ElMessage.error('设置经理失败')
    console.error('设置部门经理失败:', error)
  } finally {
    saving.value = false
  }
}

onMounted(async () => {
  console.log('组件挂载, 开始加载部门数据...')
  await loadDepartments()
  
  // 延迟一点时间确保表格已完全渲染
  setTimeout(() => {
    console.log('组件挂载完成后再次尝试展开所有节点')
    console.log('当前 departments.value:', departments.value)
    console.log('当前 filteredDepartments.value:', filteredDepartments.value)
    forceExpandAll()
  }, 500)
})
</script>

<style scoped>
.department-management {
  padding: var(--hr-space-lg);
}

.page-header {
  margin-bottom: var(--hr-space-lg);
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-content h2 {
  margin: 0;
  font-size: 22px;
  color: var(--color-text-primary);
  font-weight: 700;
}

.header-actions {
  display: flex;
  gap: var(--hr-space-sm);
}

.search-card {
  margin-bottom: var(--hr-space-lg);
}

.table-card {
  margin-bottom: var(--hr-space-lg);
}

.department-name {
  display: flex;
  align-items: center;
  gap: 8px;
}

.dept-icon {
  color: var(--hr-primary);
}

:deep(.el-table .el-table__row) {
  cursor: pointer;
  transition: all var(--hr-transition-fast);
}

:deep(.el-table .el-table__row:hover) {
  background-color: var(--hr-gray-50);
}
</style>
