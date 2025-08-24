<template>
  <div class="goal-approval">
    <el-card class="header-card">
      <div class="header-content">
        <h2>绩效目标审批</h2>
        <p>审批下属员工提交的绩效目标</p>
      </div>
    </el-card>

    <!-- 筛选区域 -->
    <el-card class="filter-card">
      <el-form :model="filterForm" :inline="true">
        <el-form-item label="审批状态">
          <el-select v-model="filterForm.status" placeholder="全部状态" clearable>
            <el-option label="待审批" value="submitted" />
            <el-option label="已通过" value="approved" />
            <el-option label="已拒绝" value="rejected" />
          </el-select>
        </el-form-item>
        <el-form-item label="绩效周期">
          <el-select v-model="filterForm.period" placeholder="选择周期" clearable>
            <el-option 
              v-for="period in periods" 
              :key="period.id" 
              :label="period.name" 
              :value="period.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="员工">
          <el-input
            v-model="filterForm.employee"
            placeholder="输入员工姓名"
            clearable
            style="width: 200px"
          />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="loadGoals">查询</el-button>
          <el-button @click="resetFilter">重置</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 统计概览 -->
    <el-row :gutter="20" class="stats-row">
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-icon pending">
              <el-icon size="32" color="#E6A23C"><Clock /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ stats.pending }}</div>
              <div class="stat-label">待审批</div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-icon approved">
              <el-icon size="32" color="#67C23A"><CircleCheck /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ stats.approved }}</div>
              <div class="stat-label">已通过</div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-icon rejected">
              <el-icon size="32" color="#F56C6C"><CircleClose /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ stats.rejected }}</div>
              <div class="stat-label">已拒绝</div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-icon total">
              <el-icon size="32" color="#409EFF"><DataBoard /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ stats.total }}</div>
              <div class="stat-label">总计</div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 目标列表 -->
    <el-card class="table-card">
      <el-table :data="goals" v-loading="loading" stripe>
        <el-table-column prop="user_name" label="员工" width="120" />
        <el-table-column prop="period_name" label="绩效周期" width="140" />
        <el-table-column prop="template_name" label="模板" width="120" />
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusTagType(row.status)">
              {{ getStatusLabel(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="提交时间" width="140">
          <template #default="{ row }">
            {{ formatDate(row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column prop="approver_name" label="审批人" width="120" />
        <el-table-column prop="approved_at" label="审批时间" width="140">
          <template #default="{ row }">
            {{ row.approved_at ? formatDate(row.approved_at) : '-' }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button size="small" @click="viewGoal(row)">查看</el-button>
            <el-button 
              v-if="row.status === 'submitted'" 
              size="small" 
              type="success" 
              @click="showApprovalDialog(row)"
            >
              审批
            </el-button>
            <el-button 
              v-if="row.status === 'approved' || row.status === 'rejected'" 
              size="small" 
              type="info"
              @click="viewApprovalHistory(row)"
            >
              审批记录
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <div class="pagination-wrapper">
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

    <!-- 审批对话框 -->
    <el-dialog 
      v-model="approvalDialogVisible" 
      title="绩效目标审批" 
      width="500px"
      :before-close="handleApprovalClose"
    >
      <div v-if="currentGoal" class="goal-info">
        <h4>{{ currentGoal.user_name }} - 绩效目标</h4>
        <p><strong>绩效周期：</strong>{{ currentGoal.period_name }}</p>
        <p><strong>模板：</strong>{{ currentGoal.template_name }}</p>
        <p><strong>提交时间：</strong>{{ formatDate(currentGoal.created_at) }}</p>
        
        <div v-if="currentGoal.details && currentGoal.details.length > 0" class="goal-details">
          <h5>目标详情：</h5>
          <el-table :data="currentGoal.details" size="small">
            <el-table-column prop="indicator_name" label="指标" />
            <el-table-column prop="target_value" label="目标值" width="100" />
            <el-table-column prop="weight" label="权重" width="80">
              <template #default="{ row }">
                {{ row.weight }}%
              </template>
            </el-table-column>
            <el-table-column prop="max_score" label="满分" width="80" />
          </el-table>
        </div>
      </div>

      <el-form :model="approvalForm" :rules="approvalRules" ref="approvalFormRef" label-width="80px">
        <el-form-item label="审批结果" prop="status">
          <el-radio-group v-model="approvalForm.status">
            <el-radio value="approved">通过</el-radio>
            <el-radio value="rejected">拒绝</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="审批意见" prop="note">
          <el-input 
            v-model="approvalForm.note" 
            type="textarea" 
            placeholder="请输入审批意见..." 
            rows="4"
          />
        </el-form-item>
      </el-form>
      
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="approvalDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="submitApproval" :loading="approvalSubmitting">确定</el-button>
        </div>
      </template>
    </el-dialog>

    <!-- 目标详情对话框 -->
    <el-dialog 
      v-model="viewDialogVisible" 
      title="绩效目标详情" 
      width="600px"
    >
      <div v-if="viewingGoal" class="goal-view">
        <div class="goal-header">
          <h3>{{ viewingGoal.user_name }} - 绩效目标</h3>
          <el-tag :type="getStatusTagType(viewingGoal.status)">
            {{ getStatusLabel(viewingGoal.status) }}
          </el-tag>
        </div>
        
        <el-descriptions :column="2" border>
          <el-descriptions-item label="员工">{{ viewingGoal.user_name }}</el-descriptions-item>
          <el-descriptions-item label="绩效周期">{{ viewingGoal.period_name }}</el-descriptions-item>
          <el-descriptions-item label="模板">{{ viewingGoal.template_name }}</el-descriptions-item>
          <el-descriptions-item label="状态">
            <el-tag :type="getStatusTagType(viewingGoal.status)">
              {{ getStatusLabel(viewingGoal.status) }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="提交时间">{{ formatDate(viewingGoal.created_at) }}</el-descriptions-item>
          <el-descriptions-item label="审批人">{{ viewingGoal.approver_name || '-' }}</el-descriptions-item>
          <el-descriptions-item label="审批时间">{{ viewingGoal.approved_at ? formatDate(viewingGoal.approved_at) : '-' }}</el-descriptions-item>
          <el-descriptions-item label="审批意见" span="2">{{ viewingGoal.approval_note || '-' }}</el-descriptions-item>
        </el-descriptions>

        <div v-if="viewingGoal.details && viewingGoal.details.length > 0" class="goal-details-view">
          <h4>目标详情</h4>
          <el-table :data="viewingGoal.details">
            <el-table-column prop="indicator_name" label="指标" />
            <el-table-column prop="target_value" label="目标值" width="120" />
            <el-table-column prop="weight" label="权重" width="100">
              <template #default="{ row }">
                {{ row.weight }}%
              </template>
            </el-table-column>
            <el-table-column prop="max_score" label="满分" width="100" />
            <el-table-column prop="description" label="描述" show-overflow-tooltip />
          </el-table>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Clock,
  CircleCheck,
  CircleClose,
  DataBoard
} from '@element-plus/icons-vue'
import api from '@/utils/api'

// 数据定义
const loading = ref(false)
const goals = ref<any[]>([])
const periods = ref<any[]>([])

// 筛选条件
const filterForm = reactive({
  status: '',
  period: '',
  employee: ''
})

// 分页
const currentPage = ref(1)
const pageSize = ref(20)
const total = ref(0)

// 统计数据
const stats = computed(() => {
  const pending = goals.value.filter(g => g.status === 'submitted').length
  const approved = goals.value.filter(g => g.status === 'approved').length
  const rejected = goals.value.filter(g => g.status === 'rejected').length
  const totalCount = goals.value.length
  
  return {
    pending,
    approved,
    rejected,
    total: totalCount
  }
})

// 审批对话框
const approvalDialogVisible = ref(false)
const approvalSubmitting = ref(false)
const approvalFormRef = ref()
const currentGoal = ref<any>(null)

const approvalForm = reactive({
  status: 'approved',
  note: ''
})

const approvalRules = {
  status: [{ required: true, message: '请选择审批结果', trigger: 'change' }]
}

// 查看对话框
const viewDialogVisible = ref(false)
const viewingGoal = ref<any>(null)

// 生命周期
onMounted(() => {
  loadPeriods()
  loadGoals()
})

// 方法
const loadPeriods = async () => {
  try {
    const response = await api.get('/performance/periods/')
    periods.value = response.data.results || response.data || []
  } catch (error) {
    console.error('加载绩效周期失败:', error)
  }
}

const loadGoals = async () => {
  loading.value = true
  try {
    const params: any = {
      page: currentPage.value,
      page_size: pageSize.value
    }
    
    if (filterForm.status) {
      params.status = filterForm.status
    }
    if (filterForm.period) {
      params.period = filterForm.period
    }
    if (filterForm.employee) {
      params.search = filterForm.employee
    }
    
    const response = await api.get('/performance/goals/', { params })
    const data = response.data
    
    goals.value = data.results || data || []
    total.value = data.count || goals.value.length
  } catch (error) {
    console.error('加载绩效目标失败:', error)
    ElMessage.error('加载数据失败')
  } finally {
    loading.value = false
  }
}

const resetFilter = () => {
  filterForm.status = ''
  filterForm.period = ''
  filterForm.employee = ''
  currentPage.value = 1
  loadGoals()
}

const handleSizeChange = (size: number) => {
  pageSize.value = size
  currentPage.value = 1
  loadGoals()
}

const handleCurrentChange = (page: number) => {
  currentPage.value = page
  loadGoals()
}

// 审批相关方法
const showApprovalDialog = (goal: any) => {
  currentGoal.value = goal
  approvalForm.status = 'approved'
  approvalForm.note = ''
  approvalDialogVisible.value = true
}

const handleApprovalClose = (done: Function) => {
  if (approvalSubmitting.value) {
    ElMessage.warning('正在提交，请稍候...')
    return
  }
  done()
}

const submitApproval = async () => {
  if (!currentGoal.value) return
  
  try {
    const valid = await approvalFormRef.value?.validate()
    if (!valid) return
  } catch {
    return
  }
  
  approvalSubmitting.value = true
  try {
    const formData = {
      status: approvalForm.status,
      note: approvalForm.note || ''
    }
    
    await api.post(`/performance/goals/${currentGoal.value.id}/approve/`, formData)
    ElMessage.success('审批操作成功')
    
    approvalDialogVisible.value = false
    loadGoals()
  } catch (error: any) {
    console.error('审批失败:', error)
    
    let errorMsg = '审批失败'
    if (error.response?.data?.error) {
      errorMsg = error.response.data.error
    }
    
    ElMessage.error(errorMsg)
  } finally {
    approvalSubmitting.value = false
  }
}

// 查看相关方法
const viewGoal = (goal: any) => {
  viewingGoal.value = goal
  viewDialogVisible.value = true
}

const viewApprovalHistory = (goal: any) => {
  const statusText = getStatusLabel(goal.status)
  const approver = goal.approver_name || '系统'
  const approvalTime = goal.approved_at ? formatDate(goal.approved_at) : '未知'
  const note = goal.approval_note || '无'
  
  ElMessageBox.alert(
    `<div style="text-align: left;">
      <h4>审批记录</h4>
      <p><strong>审批结果：</strong>${statusText}</p>
      <p><strong>审批人：</strong>${approver}</p>
      <p><strong>审批时间：</strong>${approvalTime}</p>
      <p><strong>审批意见：</strong>${note}</p>
    </div>`,
    '审批历史',
    {
      dangerouslyUseHTMLString: true,
      confirmButtonText: '关闭'
    }
  )
}

// 辅助方法
const getStatusTagType = (status: string) => {
  const typeMap: { [key: string]: string } = {
    'draft': '',
    'submitted': 'warning',
    'approved': 'success',
    'rejected': 'danger'
  }
  return typeMap[status] || ''
}

const getStatusLabel = (status: string) => {
  const labelMap: { [key: string]: string } = {
    'draft': '草稿',
    'submitted': '待审批',
    'approved': '已通过',
    'rejected': '已拒绝'
  }
  return labelMap[status] || status
}

const formatDate = (dateString: string) => {
  if (!dateString) return '-'
  try {
    return new Date(dateString).toLocaleString('zh-CN')
  } catch {
    return dateString
  }
}
</script>

<style scoped>
.goal-approval {
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

.filter-card {
  margin-bottom: 20px;
}

.stats-row {
  margin-bottom: 20px;
}

.stat-card {
  height: 100px;
}

.stat-content {
  display: flex;
  align-items: center;
  height: 100%;
}

.stat-icon {
  margin-right: 16px;
}

.stat-icon.pending {
  color: #E6A23C;
}

.stat-icon.approved {
  color: #67C23A;
}

.stat-icon.rejected {
  color: #F56C6C;
}

.stat-icon.total {
  color: #409EFF;
}

.stat-info {
  flex: 1;
}

.stat-value {
  font-size: 28px;
  font-weight: bold;
  line-height: 1;
  margin-bottom: 4px;
}

.stat-label {
  font-size: 14px;
  color: #909399;
}

.table-card {
  margin-bottom: 20px;
}

.pagination-wrapper {
  margin-top: 16px;
  text-align: right;
}

.goal-info {
  margin-bottom: 20px;
}

.goal-info h4 {
  margin: 0 0 12px 0;
  color: #303133;
}

.goal-info p {
  margin: 8px 0;
  color: #606266;
}

.goal-details {
  margin-top: 16px;
}

.goal-details h5 {
  margin: 0 0 12px 0;
  color: #303133;
}

.goal-view {
  max-height: 600px;
  overflow-y: auto;
}

.goal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.goal-header h3 {
  margin: 0;
  color: #303133;
}

.goal-details-view {
  margin-top: 20px;
}

.goal-details-view h4 {
  margin: 0 0 12px 0;
  color: #303133;
}
</style>
