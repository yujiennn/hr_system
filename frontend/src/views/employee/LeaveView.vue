<template>
  <div class="leave">
    <el-row :gutter="20">
      <el-col :span="8">
        <el-card>
          <template #header>
            <span>申请请假</span>
          </template>
          <el-form
            ref="leaveFormRef"
            :model="leaveForm"
            :rules="leaveRules"
            label-width="100px"
            @submit.prevent="submitLeave"
          >            <el-form-item label="请假类型" prop="leave_type">
              <el-select v-model="leaveForm.leave_type" placeholder="请选择请假类型">
                <el-option 
                  v-for="type in leaveTypes" 
                  :key="type.id" 
                  :label="type.name" 
                  :value="type.id" 
                />
              </el-select>
            </el-form-item>

            <el-form-item label="开始日期" prop="start_date">
              <el-date-picker
                v-model="leaveForm.start_date"
                type="date"
                placeholder="选择开始日期"
                format="YYYY-MM-DD"
                value-format="YYYY-MM-DD"
                :disabled-date="disabledDate"
              />
            </el-form-item>

            <el-form-item label="结束日期" prop="end_date">
              <el-date-picker
                v-model="leaveForm.end_date"
                type="date"
                placeholder="选择结束日期"
                format="YYYY-MM-DD"
                value-format="YYYY-MM-DD"
                :disabled-date="disabledEndDate"
              />
            </el-form-item>

            <el-form-item label="请假天数">
              <el-input v-model="leaveDays" readonly>
                <template #suffix>天</template>
              </el-input>
            </el-form-item>

            <el-form-item label="请假原因" prop="reason">
              <el-input
                v-model="leaveForm.reason"
                type="textarea"
                :rows="4"
                placeholder="请详细描述请假原因"
                maxlength="500"
                show-word-limit
              />
            </el-form-item>

            <el-form-item label="附件">
              <el-upload
                ref="uploadRef"
                :file-list="fileList"
                :auto-upload="false"
                :on-change="handleFileChange"
                :on-remove="handleFileRemove"
                accept=".jpg,.jpeg,.png,.pdf,.doc,.docx"
                multiple
              >
                <el-button type="primary">选择文件</el-button>
                <template #tip>
                  <div class="el-upload__tip">
                    支持 jpg/png/pdf/doc/docx 格式，单个文件不超过 10MB
                  </div>
                </template>
              </el-upload>
            </el-form-item>

            <el-form-item>
              <el-button type="primary" @click="submitLeave" :loading="submitting">
                提交申请
              </el-button>
              <el-button @click="resetForm">重置</el-button>
            </el-form-item>
          </el-form>
        </el-card>

        <el-card style="margin-top: 20px;">
          <template #header>
            <span>请假额度</span>
          </template>          <div class="leave-quota">
            <div class="quota-item">
              <span class="label">年假剩余：</span>
              <span class="value">{{ leaveQuota.年假 || 0 }} 天</span>
            </div>
            <div class="quota-item">
              <span class="label">病假剩余：</span>
              <span class="value">{{ leaveQuota.病假 || 0 }} 天</span>
            </div>
            <div class="quota-item">
              <span class="label">事假剩余：</span>
              <span class="value">{{ leaveQuota.事假 || 0 }} 天</span>
            </div>
          </div>
        </el-card>
      </el-col>

      <el-col :span="16">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>请假记录</span>
              <el-select v-model="statusFilter" placeholder="状态筛选" style="width: 120px;">
                <el-option label="全部" value="" />
                <el-option label="待审批" value="pending" />
                <el-option label="已批准" value="approved" />
                <el-option label="已拒绝" value="rejected" />
              </el-select>
            </div>
          </template>

          <el-table :data="leaveRecords" v-loading="loading">            <el-table-column prop="leave_type_name" label="请假类型" width="100" />
            <el-table-column prop="start_date" label="开始日期" width="120" />
            <el-table-column prop="end_date" label="结束日期" width="120" />
            <el-table-column prop="days" label="天数" width="80" />
            <el-table-column label="状态" width="100">
              <template #default="{ row }">
                <el-tag :type="getStatusType(row.status)">
                  {{ getStatusLabel(row.status) }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="reason" label="请假原因" min-width="150" />
            <el-table-column prop="created_at" label="申请时间" width="150">
              <template #default="{ row }">
                {{ formatDateTime(row.created_at) }}
              </template>
            </el-table-column>
            <el-table-column label="操作" width="150">
              <template #default="{ row }">
                <el-button
                  v-if="row.status === 'pending'"
                  type="danger"
                  size="small"
                  @click="cancelLeave(row.id)"
                >
                  撤销
                </el-button>
                <el-button
                  type="primary"
                  size="small"
                  @click="viewLeaveDetail(row)"
                >
                  详情
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
    </el-row>

    <!-- 请假详情对话框 -->
    <el-dialog v-model="detailVisible" title="请假详情" width="60%">
      <div v-if="selectedLeave" class="leave-detail">        <el-descriptions border :column="2">
          <el-descriptions-item label="请假类型">
            {{ selectedLeave.leave_type_name }}
          </el-descriptions-item>
          <el-descriptions-item label="状态">
            <el-tag :type="getStatusType(selectedLeave.status)">
              {{ getStatusLabel(selectedLeave.status) }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="开始日期">
            {{ selectedLeave.start_date }}
          </el-descriptions-item>
          <el-descriptions-item label="结束日期">
            {{ selectedLeave.end_date }}
          </el-descriptions-item>
          <el-descriptions-item label="请假天数">
            {{ selectedLeave.days }} 天
          </el-descriptions-item>
          <el-descriptions-item label="申请时间">
            {{ formatDateTime(selectedLeave.created_at) }}
          </el-descriptions-item>
          <el-descriptions-item label="请假原因" :span="2">
            {{ selectedLeave.reason }}
          </el-descriptions-item>
          <el-descriptions-item v-if="selectedLeave.approver_name" label="审批人">
            {{ selectedLeave.approver_name }}
          </el-descriptions-item>
          <el-descriptions-item v-if="selectedLeave.approved_at" label="审批时间">
            {{ formatDateTime(selectedLeave.approved_at) }}
          </el-descriptions-item>
          <el-descriptions-item v-if="selectedLeave.approval_note" label="审批备注" :span="2">
            {{ selectedLeave.approval_note }}
          </el-descriptions-item>
        </el-descriptions>
      </div>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted, watch } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import type { FormInstance, FormRules, UploadUserFile } from 'element-plus'
import leaveService from '@/services/leave'
import type { LeaveApplication, LeaveBalance, LeaveType } from '@/services/leave'

// 类型定义
interface LeaveForm {
  leave_type: number
  start_date: string
  end_date: string
  reason: string
  attachments: any[]
}

interface LeaveQuota {
  [key: string]: number
}

const leaveFormRef = ref<FormInstance>()
const uploadRef = ref()
const submitting = ref(false)
const loading = ref(false)
const currentPage = ref(1)
const pageSize = ref(10)
const total = ref(0)
const statusFilter = ref('')
const detailVisible = ref(false)
const selectedLeave = ref<LeaveApplication | null>(null)
const fileList = ref<UploadUserFile[]>([])
const leaveTypes = ref<LeaveType[]>([])

const leaveForm = reactive<LeaveForm>({
  leave_type: 0,
  start_date: '',
  end_date: '',
  reason: '',
  attachments: []
})

const leaveQuota = reactive<LeaveQuota>({})

const leaveRecords = ref<LeaveApplication[]>([])

const leaveRules: FormRules = {
  leave_type: [
    { required: true, message: '请选择请假类型', trigger: 'change' }
  ],
  start_date: [
    { required: true, message: '请选择开始日期', trigger: 'change' }
  ],
  end_date: [
    { required: true, message: '请选择结束日期', trigger: 'change' }
  ],
  reason: [
    { required: true, message: '请填写请假原因', trigger: 'blur' },
    { min: 10, message: '请假原因至少10个字符', trigger: 'blur' }
  ]
}

// 计算请假天数
const leaveDays = computed(() => {
  if (leaveForm.start_date && leaveForm.end_date) {
    const start = new Date(leaveForm.start_date)
    const end = new Date(leaveForm.end_date)
    const diffTime = end.getTime() - start.getTime()
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24)) + 1
    return diffDays > 0 ? diffDays : 0
  }
  return 0
})

// 禁用过去的日期
const disabledDate = (time: Date) => {
  return time.getTime() < Date.now() - 8.64e7
}

// 禁用结束日期
const disabledEndDate = (time: Date) => {
  if (!leaveForm.start_date) return time.getTime() < Date.now() - 8.64e7
  return time.getTime() < new Date(leaveForm.start_date).getTime()
}

// 文件上传处理
const handleFileChange = (file: UploadUserFile) => {
  // 文件大小检查
  if (file.size && file.size > 10 * 1024 * 1024) {
    ElMessage.error('文件大小不能超过 10MB')
    return false
  }
}

const handleFileRemove = (file: UploadUserFile) => {
  const index = fileList.value.indexOf(file)
  if (index !== -1) {
    fileList.value.splice(index, 1)
  }
}

// 提交请假申请
const submitLeave = async () => {
  if (!leaveFormRef.value) return
  
  await leaveFormRef.value.validate((valid) => {
    if (valid) {
      doSubmitLeave()
    }
  })
}

const doSubmitLeave = async () => {
  submitting.value = true
  try {
    const formData = {
      leave_type: leaveForm.leave_type,
      start_date: leaveForm.start_date,
      end_date: leaveForm.end_date,
      reason: leaveForm.reason
    }
    
    await leaveService.createApplication(formData)
    ElMessage.success('请假申请提交成功！')
    resetForm()
    loadLeaveRecords()
    loadLeaveBalances()
  } catch (error: any) {
    console.error('提交请假申请失败:', error)
    ElMessage.error('提交失败，请重试')
  } finally {
    submitting.value = false
  }
}

// 重置表单
const resetForm = () => {
  if (leaveFormRef.value) {
    leaveFormRef.value.resetFields()
  }
  fileList.value = []
}

// 撤销请假
const cancelLeave = async (id: number) => {
  try {
    await ElMessageBox.confirm('确定要撤销这个请假申请吗？', '确认', {
      type: 'warning'
    })
    
    await leaveService.cancelApplication(id)
    ElMessage.success('请假申请已撤销')
    loadLeaveRecords()
  } catch (error: any) {
    if (error !== 'cancel') {
      ElMessage.error('撤销失败，请重试')
    }
  }
}

// 查看请假详情
const viewLeaveDetail = (leave: any) => {
  selectedLeave.value = leave
  detailVisible.value = true
}

// 获取状态标签
const getStatusLabel = (status: string) => {
  const statusMap: Record<string, string> = {
    pending: '待审批',
    approved: '已批准',
    rejected: '已拒绝'
  }
  return statusMap[status] || status
}

// 获取状态类型
const getStatusType = (status: string) => {
  const typeMap: Record<string, string> = {
    pending: 'warning',
    approved: 'success',
    rejected: 'danger'
  }
  return typeMap[status] || 'info'
}

// 格式化日期时间
const formatDateTime = (dateStr: string) => {
  if (!dateStr) return '-'
  return new Date(dateStr).toLocaleString('zh-CN')
}

// 分页处理
const handleSizeChange = (val: number) => {
  pageSize.value = val
  loadLeaveRecords()
}

const handleCurrentChange = (val: number) => {
  currentPage.value = val
  loadLeaveRecords()
}

// 加载请假记录
const loadLeaveRecords = async () => {
  loading.value = true
  try {
    const applications = await leaveService.getMyApplications()
    
    // 根据状态筛选
    if (statusFilter.value) {
      leaveRecords.value = applications.filter(app => app.status === statusFilter.value)
    } else {
      leaveRecords.value = applications
    }
    
    total.value = leaveRecords.value.length
  } catch (error: any) {
    console.error('加载请假记录失败:', error)
    ElMessage.error('加载请假记录失败')
  } finally {
    loading.value = false
  }
}

// 加载请假余额
const loadLeaveBalances = async () => {
  try {
    const balances = await leaveService.getLeaveBalances()
    
    // 将余额数据转换为显示格式
    leaveQuota.年假 = balances.find(b => b.leave_type_name === '年假')?.remaining_days || 0
    leaveQuota.病假 = balances.find(b => b.leave_type_name === '病假')?.remaining_days || 0
    leaveQuota.事假 = balances.find(b => b.leave_type_name === '事假')?.remaining_days || 0
  } catch (error: any) {
    console.error('加载请假余额失败:', error)
  }
}

// 加载请假类型
const loadLeaveTypes = async () => {
  try {
    leaveTypes.value = await leaveService.getLeaveTypes()
  } catch (error: any) {
    console.error('加载请假类型失败:', error)
  }
}

// 监听状态筛选
watch(statusFilter, () => {
  loadLeaveRecords()
})

onMounted(() => {
  loadLeaveTypes()
  loadLeaveRecords()
  loadLeaveBalances()
})
</script>

<style scoped>
.leave {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.leave-quota {
  padding: 10px 0;
}

.quota-item {
  display: flex;
  justify-content: space-between;
  margin-bottom: 10px;
}

.quota-item .label {
  color: #909399;
}

.quota-item .value {
  color: #303133;
  font-weight: 500;
}

.pagination {
  margin-top: 20px;
  text-align: right;
}

.leave-detail {
  padding: 20px 0;
}
</style>
