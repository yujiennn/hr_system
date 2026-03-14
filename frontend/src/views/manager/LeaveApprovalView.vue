<template>
  <div class="leave-approval">
    <!-- 筛选区域 -->
    <el-card class="filter-card">
      <el-form :model="filterForm" :inline="true">
        <el-form-item label="申请状态">
          <el-select v-model="filterForm.status" placeholder="全部状态" clearable>
            <el-option label="待审批" value="pending" />
            <el-option label="已通过" value="approved" />
            <el-option label="已拒绝" value="rejected" />
          </el-select>
        </el-form-item>
        <el-form-item label="请假类型">
          <el-select v-model="filterForm.leaveType" placeholder="全部类型" clearable>
            <el-option label="年假" value="annual" />
            <el-option label="病假" value="sick" />
            <el-option label="事假" value="personal" />
            <el-option label="调休" value="compensatory" />
            <el-option label="产假" value="maternity" />
            <el-option label="陪产假" value="paternity" />
          </el-select>
        </el-form-item>
        <el-form-item label="申请时间">
          <el-date-picker
            v-model="filterForm.dateRange"
            type="daterange"
            range-separator="至"
            start-placeholder="开始日期"
            end-placeholder="结束日期"
          />
        </el-form-item>
        <el-form-item label="申请人">
          <el-input v-model="filterForm.applicant" placeholder="搜索申请人" clearable />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="searchLeaves">查询</el-button>
          <el-button @click="resetFilter">重置</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 统计卡片 -->
    <el-row :gutter="20" class="stats-row">
      <el-col :span="6">
        <el-card class="stats-card pending">
          <div class="stats-content">
            <div class="stats-icon">
              <el-icon size="28"><Clock /></el-icon>
            </div>
            <div class="stats-info">
              <div class="stats-value">{{ leaveStats.pending }}</div>
              <div class="stats-label">待审批</div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stats-card approved">
          <div class="stats-content">
            <div class="stats-icon">
              <el-icon size="28"><CircleCheck /></el-icon>
            </div>
            <div class="stats-info">
              <div class="stats-value">{{ leaveStats.approved }}</div>
              <div class="stats-label">已通过</div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stats-card rejected">
          <div class="stats-content">
            <div class="stats-icon">
              <el-icon size="28"><CircleClose /></el-icon>
            </div>
            <div class="stats-info">
              <div class="stats-value">{{ leaveStats.rejected }}</div>
              <div class="stats-label">已拒绝</div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stats-card total">
          <div class="stats-content">
            <div class="stats-icon">
              <el-icon size="28"><Document /></el-icon>
            </div>
            <div class="stats-info">
              <div class="stats-value">{{ leaveStats.total }}</div>
              <div class="stats-label">总申请</div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 请假申请列表 -->
    <el-card>
      <template #header>
        <div class="card-header">
          <span>请假申请列表</span>
          <div>
            <el-button type="success" @click="batchApprove" :disabled="selectedLeaves.length === 0">
              批量通过
            </el-button>
            <el-button type="danger" @click="batchReject" :disabled="selectedLeaves.length === 0">
              批量拒绝
            </el-button>
          </div>
        </div>
      </template>

      <el-table
        :data="leaveList"
        stripe
        v-loading="loading"
        @selection-change="handleSelectionChange"
      >
        <el-table-column type="selection" width="55" />
        <el-table-column prop="applicantName" label="申请人" width="100" />
        <el-table-column prop="leaveType" label="请假类型" width="100">
          <template #default="{ row }">
            <el-tag :type="getLeaveTypeColor(row.leaveType)">{{ getLeaveTypeText(row.leaveType) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="startDate" label="开始日期" width="120" />
        <el-table-column prop="endDate" label="结束日期" width="120" />
        <el-table-column prop="days" label="天数" width="80" align="center" />
        <el-table-column prop="reason" label="请假原因" show-overflow-tooltip min-width="150" />
        <el-table-column prop="applyTime" label="申请时间" width="140" />
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)">{{ getStatusText(row.status) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="urgency" label="紧急程度" width="100">
          <template #default="{ row }">
            <el-tag :type="getUrgencyType(row.urgency)" size="small">{{ row.urgency }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" size="small" @click="viewDetail(row)">详情</el-button>
            <el-button
              v-if="row.status === 'pending'"
              type="success"
              size="small"
              @click="approveLeave(row)"
            >
              通过
            </el-button>
            <el-button
              v-if="row.status === 'pending'"
              type="danger"
              size="small"
              @click="rejectLeave(row)"
            >
              拒绝
            </el-button>
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

    <!-- 详情对话框 -->
    <el-dialog v-model="showDetailDialog" title="请假申请详情" width="700px">
      <div v-if="selectedLeave" class="leave-detail">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="申请人">{{ selectedLeave.applicantName }}</el-descriptions-item>
          <el-descriptions-item label="员工工号">{{ selectedLeave.employeeId }}</el-descriptions-item>
          <el-descriptions-item label="请假类型">
            <el-tag :type="getLeaveTypeColor(selectedLeave.leaveType)">
              {{ getLeaveTypeText(selectedLeave.leaveType) }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="紧急程度">
            <el-tag :type="getUrgencyType(selectedLeave.urgency)" size="small">
              {{ selectedLeave.urgency }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="开始日期">{{ selectedLeave.startDate }}</el-descriptions-item>
          <el-descriptions-item label="结束日期">{{ selectedLeave.endDate }}</el-descriptions-item>
          <el-descriptions-item label="请假天数">{{ selectedLeave.days }} 天</el-descriptions-item>
          <el-descriptions-item label="申请时间">{{ selectedLeave.applyTime }}</el-descriptions-item>
          <el-descriptions-item label="当前状态" :span="2">
            <el-tag :type="getStatusType(selectedLeave.status)">
              {{ getStatusText(selectedLeave.status) }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="请假原因" :span="2">
            {{ selectedLeave.reason }}
          </el-descriptions-item>
          <el-descriptions-item v-if="selectedLeave.attachment" label="附件" :span="2">
            <el-link type="primary" @click="downloadAttachment(selectedLeave.attachment)">
              {{ selectedLeave.attachment }}
            </el-link>
          </el-descriptions-item>
          <el-descriptions-item v-if="selectedLeave.approverRemark" label="审批意见" :span="2">
            {{ selectedLeave.approverRemark }}
          </el-descriptions-item>
        </el-descriptions>

        <div v-if="selectedLeave.status === 'pending'" class="approval-actions">
          <el-divider>审批操作</el-divider>
          <el-form :model="approvalForm" label-width="100px">
            <el-form-item label="审批意见">
              <el-input
                v-model="approvalForm.remark"
                type="textarea"
                rows="3"
                placeholder="请输入审批意见"
              />
            </el-form-item>
            <el-form-item>
              <el-button type="success" @click="handleApproval('approve')">通过申请</el-button>
              <el-button type="danger" @click="handleApproval('reject')">拒绝申请</el-button>
            </el-form-item>
          </el-form>
        </div>
      </div>
    </el-dialog>

    <!-- 批量审批对话框 -->
    <el-dialog v-model="showBatchDialog" :title="batchAction === 'approve' ? '批量通过' : '批量拒绝'" width="500px">
      <div class="batch-content">
        <p>您确定要{{ batchAction === 'approve' ? '通过' : '拒绝' }}以下 {{ selectedLeaves.length }} 条请假申请吗？</p>
        <el-form :model="batchForm" label-width="100px">
          <el-form-item label="批量意见">
            <el-input
              v-model="batchForm.remark"
              type="textarea"
              rows="3"
              :placeholder="`请输入${batchAction === 'approve' ? '通过' : '拒绝'}意见`"
            />
          </el-form-item>
        </el-form>
      </div>
      <template #footer>
        <el-button @click="showBatchDialog = false">取消</el-button>
        <el-button :type="batchAction === 'approve' ? 'success' : 'danger'" @click="confirmBatchAction">
          确定{{ batchAction === 'approve' ? '通过' : '拒绝' }}
        </el-button>
      </template>
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
  Document
} from '@element-plus/icons-vue'
import leaveService from '@/services/leave'
import type { LeaveApplication as ApiLeaveApplication } from '@/services/leave'

// 接口定义 - 将API接口转换为页面显示接口
interface LeaveApplication {
  id: number
  applicantName: string
  employeeId: string
  leaveType: string
  startDate: string
  endDate: string
  days: number
  reason: string
  applyTime: string
  status: string
  urgency: string
  attachment?: string
  approverRemark?: string
}

// 响应式数据
const loading = ref(false)
const showDetailDialog = ref(false)
const showBatchDialog = ref(false)
const selectedLeave = ref<LeaveApplication | null>(null)
const selectedLeaves = ref<LeaveApplication[]>([])
const batchAction = ref<'approve' | 'reject'>('approve')
const currentPage = ref(1)
const pageSize = ref(20)
const total = ref(0)

// 筛选表单
const filterForm = reactive({
  status: '',
  leaveType: '',
  dateRange: [] as Date[],
  applicant: ''
})

// 统计数据
const leaveStats = ref({
  pending: 0,
  approved: 0,
  rejected: 0,
  total: 0
})

// 请假申请列表
const leaveList = ref<LeaveApplication[]>([])

// 原始API数据
const rawLeaveList = ref<ApiLeaveApplication[]>([])

// 转换API数据为页面显示格式
const convertApiToDisplayData = (apiData: ApiLeaveApplication[]): LeaveApplication[] => {
  return apiData.map(item => ({
    id: item.id,
    applicantName: item.user_name,
    employeeId: `EMP${String(item.user).padStart(3, '0')}`,
    leaveType: mapLeaveTypeFromApi(item.leave_type_name),
    startDate: item.start_date,
    endDate: item.end_date,
    days: item.days,
    reason: item.reason,
    applyTime: formatDateTime(item.created_at),
    status: item.status,
    urgency: '一般', // API没有紧急程度字段，设置默认值
    attachment: item.attachment || undefined,
    approverRemark: item.approval_note || undefined
  }))
}

// 映射请假类型从API名称到前端显示
const mapLeaveTypeFromApi = (typeName: string): string => {
  const typeMap: Record<string, string> = {
    '年假': 'annual',
    '病假': 'sick', 
    '事假': 'personal',
    '调休': 'compensatory',
    '产假': 'maternity',
    '陪产假': 'paternity'
  }
  
  for (const [key, value] of Object.entries(typeMap)) {
    if (typeName.includes(key)) {
      return value
    }
  }
  return 'personal' // 默认值
}

// 格式化日期时间
const formatDateTime = (dateString: string): string => {
  const date = new Date(dateString)
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

// 计算统计数据
const updateLeaveStats = () => {
  const stats = {
    pending: 0,
    approved: 0,
    rejected: 0,
    total: 0
  }
  
  leaveList.value.forEach(leave => {
    stats.total++
    if (leave.status === 'pending') stats.pending++
    else if (leave.status === 'approved') stats.approved++
    else if (leave.status === 'rejected') stats.rejected++
  })
  
  leaveStats.value = stats
}

// 审批表单
const approvalForm = reactive({
  remark: ''
})

// 批量表单
const batchForm = reactive({
  remark: ''
})

// 获取请假类型颜色
const getLeaveTypeColor = (type: string) => {
  const colorMap: Record<string, string> = {
    annual: '',
    sick: 'danger',
    personal: 'warning',
    compensatory: 'success',
    maternity: 'info',
    paternity: 'info'
  }
  return colorMap[type] || 'default'
}

// 获取请假类型文本
const getLeaveTypeText = (type: string) => {
  const textMap: Record<string, string> = {
    annual: '年假',
    sick: '病假',
    personal: '事假',
    compensatory: '调休',
    maternity: '产假',
    paternity: '陪产假'
  }
  return textMap[type] || type
}

// 获取状态类型
const getStatusType = (status: string) => {
  const typeMap: Record<string, string> = {
    pending: 'warning',
    approved: 'success',
    rejected: 'danger'
  }
  return typeMap[status] || 'default'
}

// 获取状态文本
const getStatusText = (status: string) => {
  const textMap: Record<string, string> = {
    pending: '待审批',
    approved: '已通过',
    rejected: '已拒绝'
  }
  return textMap[status] || status
}

// 获取紧急程度类型
const getUrgencyType = (urgency: string) => {
  const typeMap: Record<string, string> = {
    '紧急': 'danger',
    '一般': 'warning',
    '不急': 'success'
  }
  return typeMap[urgency] || 'default'
}

// 搜索请假申请
const searchLeaves = async () => {
  loading.value = true
  try {
    // 构建查询参数
    const params: any = {}
    
    // 状态筛选
    if (filterForm.status) {
      params.status = filterForm.status
    }
    
    // 申请人筛选
    if (filterForm.applicant) {
      params.user = filterForm.applicant
    }
    
    // 日期范围筛选
    if (filterForm.dateRange && filterForm.dateRange.length === 2) {
      params.start_date = filterForm.dateRange[0].toISOString().split('T')[0]
      params.end_date = filterForm.dateRange[1].toISOString().split('T')[0]
    }
    
    // 获取所有部门的请假申请（管理员权限）
    const applications = await leaveService.getAllApplications(params)
    rawLeaveList.value = applications
    
    // 请假类型筛选（前端过滤，因为API不支持按类型名称过滤）
    let filteredApplications = applications
    if (filterForm.leaveType) {
      const typeMapping: Record<string, string[]> = {
        'annual': ['年假', '年假'],
        'sick': ['病假', '病假'],
        'personal': ['事假', '事假'],
        'compensatory': ['调休', '调休'],
        'maternity': ['产假', '产假'],
        'paternity': ['陪产假', '陪产假']
      }
      
      const typeNames = typeMapping[filterForm.leaveType] || []
      filteredApplications = filteredApplications.filter(app => 
        typeNames.some(name => app.leave_type_name.includes(name))
      )
    }
    
    // 转换为显示格式
    leaveList.value = convertApiToDisplayData(filteredApplications)
    updateLeaveStats()
    total.value = leaveList.value.length
    
    ElMessage.success('查询完成')
  } catch (error: any) {
    console.error('获取请假申请失败:', error)
    ElMessage.error(error.message || '获取请假申请失败')
  } finally {
    loading.value = false
  }
}

// 重置筛选条件
const resetFilter = () => {
  Object.assign(filterForm, {
    status: '',
    leaveType: '',
    dateRange: [],
    applicant: ''
  })
  searchLeaves()
}

// 查看详情
const viewDetail = (leave: LeaveApplication) => {
  selectedLeave.value = leave
  approvalForm.remark = leave.approverRemark || ''
  showDetailDialog.value = true
}

// 通过请假申请
const approveLeave = async (leave: LeaveApplication) => {
  try {
    const { value } = await ElMessageBox.prompt('请输入审批意见', '通过申请', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      inputPlaceholder: '审批意见（可选）'
    })
    
    // 调用API进行审批
    await leaveService.approveApplication(leave.id, {
      status: 'approved',
      approval_note: value || ''
    })
    
    ElMessage.success('审批通过')
    
    // 更新本地数据
    leave.status = 'approved'
    leave.approverRemark = value || ''
    updateLeaveStats()
    
    // 重新加载数据以确保数据同步
    await searchLeaves()
  } catch (error: any) {
    if (error !== 'cancel') { // 用户没有取消操作
      console.error('审批失败:', error)
      ElMessage.error(error.message || '审批失败')
    }
  }
}

// 拒绝请假申请
const rejectLeave = async (leave: LeaveApplication) => {
  try {
    const { value } = await ElMessageBox.prompt('请输入拒绝原因', '拒绝申请', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      inputPlaceholder: '拒绝原因'
    })
    
    if (!value) {
      ElMessage.warning('请输入拒绝原因')
      return
    }
    
    // 调用API进行拒绝
    await leaveService.approveApplication(leave.id, {
      status: 'rejected',
      approval_note: value
    })
    
    ElMessage.success('已拒绝申请')
    
    // 更新本地数据
    leave.status = 'rejected'
    leave.approverRemark = value
    updateLeaveStats()
    
    // 重新加载数据以确保数据同步
    await searchLeaves()
  } catch (error: any) {
    if (error !== 'cancel') { // 用户没有取消操作
      console.error('拒绝申请失败:', error)
      ElMessage.error(error.message || '拒绝申请失败')
    }
  }
}

// 处理审批操作
const handleApproval = async (action: 'approve' | 'reject') => {
  if (!selectedLeave.value) return
  
  try {
    const status = action === 'approve' ? 'approved' : 'rejected'
    
    // 调用API进行审批
    await leaveService.approveApplication(selectedLeave.value.id, {
      status,
      approval_note: approvalForm.remark
    })
    
    // 更新本地数据
    const leave = selectedLeave.value
    leave.status = status
    leave.approverRemark = approvalForm.remark
    
    updateLeaveStats()
    
    if (action === 'approve') {
      ElMessage.success('审批通过')
    } else {
      ElMessage.success('已拒绝申请')
    }
    
    showDetailDialog.value = false
    
    // 重新加载数据以确保数据同步
    await searchLeaves()
  } catch (error: any) {
    console.error('审批操作失败:', error)
    ElMessage.error(error.message || '审批操作失败')
  }
}

// 批量通过
const batchApprove = () => {
  batchAction.value = 'approve'
  batchForm.remark = ''
  showBatchDialog.value = true
}

// 批量拒绝
const batchReject = () => {
  batchAction.value = 'reject'
  batchForm.remark = ''
  showBatchDialog.value = true
}

// 确认批量操作
const confirmBatchAction = async () => {
  const action = batchAction.value
  const count = selectedLeaves.value.length
  
  try {
    // 批量调用API
    const promises = selectedLeaves.value
      .filter(leave => leave.status === 'pending')
      .map(leave => leaveService.approveApplication(leave.id, {
        status: action === 'approve' ? 'approved' : 'rejected',
        approval_note: batchForm.remark
      }))
    
    await Promise.all(promises)
    
    // 更新本地数据
    selectedLeaves.value.forEach(leave => {
      if (leave.status === 'pending') {
        leave.status = action === 'approve' ? 'approved' : 'rejected'
        leave.approverRemark = batchForm.remark
      }
    })
    
    updateLeaveStats()
    
    if (action === 'approve') {
      ElMessage.success(`批量通过 ${count} 条申请`)
    } else {
      ElMessage.success(`批量拒绝 ${count} 条申请`)
    }
    
    selectedLeaves.value = []
    showBatchDialog.value = false
    
    // 重新加载数据以确保数据同步
    await searchLeaves()
  } catch (error: any) {
    console.error('批量操作失败:', error)
    ElMessage.error(error.message || '批量操作失败')
  }
}

// 选择变化处理
const handleSelectionChange = (selection: LeaveApplication[]) => {
  selectedLeaves.value = selection.filter(item => item.status === 'pending')
}

// 下载附件
const downloadAttachment = (filename: string) => {
  ElMessage.info(`下载附件: ${filename}`)
}

// 分页处理
const handleSizeChange = (val: number) => {
  pageSize.value = val
  searchLeaves()
}

const handleCurrentChange = (val: number) => {
  currentPage.value = val
  searchLeaves()
}

onMounted(async () => {
  await searchLeaves()
})
</script>

<style scoped>
.leave-approval {
  padding: var(--hr-space-lg);
}

.filter-card {
  margin-bottom: var(--hr-space-lg);
}

.stats-row {
  margin-bottom: var(--hr-space-lg);
}

.stats-card {
  cursor: pointer;
  transition: all var(--hr-transition-normal);
  border-radius: var(--hr-radius-md);
}

.stats-card:hover {
  transform: translateY(-3px);
  box-shadow: var(--hr-shadow-card-hover);
}

.stats-card.pending {
  border-left: 3px solid var(--hr-warning);
}

.stats-card.approved {
  border-left: 3px solid var(--hr-success);
}

.stats-card.rejected {
  border-left: 3px solid var(--hr-danger);
}

.stats-card.total {
  border-left: 3px solid var(--hr-primary);
}

.stats-content {
  display: flex;
  align-items: center;
  padding: var(--hr-space-md);
}

.stats-icon {
  width: 48px;
  height: 48px;
  border-radius: var(--hr-radius-md);
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: var(--hr-space-md);
  color: white;
}

.stats-card.pending .stats-icon {
  background: linear-gradient(135deg, var(--hr-warning), #d97706);
}

.stats-card.approved .stats-icon {
  background: linear-gradient(135deg, var(--hr-success), #16a34a);
}

.stats-card.rejected .stats-icon {
  background: linear-gradient(135deg, var(--hr-danger), #dc2626);
}

.stats-card.total .stats-icon {
  background: linear-gradient(135deg, var(--hr-primary), var(--hr-primary-dark));
}

.stats-info {
  flex: 1;
}

.stats-value {
  font-size: 24px;
  font-weight: 800;
  color: var(--color-text-primary);
  margin-bottom: 4px;
  letter-spacing: -0.5px;
}

.stats-label {
  font-size: 13px;
  color: var(--color-text-secondary);
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

.leave-detail {
  padding: var(--hr-space-sm) 0;
}

.approval-actions {
  margin-top: var(--hr-space-lg);
}

.batch-content {
  padding: var(--hr-space-lg) 0;
}

:deep(.el-table) {
  font-size: 14px;
}

:deep(.el-descriptions__body) {
  background-color: var(--hr-gray-50);
}
</style>
