<template>
  <div class="data-backup">
    <el-card class="page-header">
      <div class="header-content">
        <h2>数据备份</h2>
        <div class="header-actions">
          <el-button type="primary" @click="createBackup" :loading="backing">
            <el-icon><Download /></el-icon>
            创建备份
          </el-button>
          <el-button type="success" @click="scheduleBackup">
            <el-icon><Timer /></el-icon>
            定时备份
          </el-button>
        </div>
      </div>
    </el-card>

    <el-row :gutter="20">
      <!-- 备份操作 -->
      <el-col :span="16">
        <el-card class="backup-operations" header="备份操作">
          <el-form :model="backupForm" label-width="120px">
            <el-form-item label="备份类型">
              <el-radio-group v-model="backupForm.type">
                <el-radio label="full">完整备份</el-radio>
                <el-radio label="incremental">增量备份</el-radio>
                <el-radio label="differential">差异备份</el-radio>
              </el-radio-group>
            </el-form-item>
            
            <el-form-item label="备份范围">
              <el-checkbox-group v-model="backupForm.scope">
                <el-checkbox label="database">数据库</el-checkbox>
                <el-checkbox label="files">文件系统</el-checkbox>
                <el-checkbox label="config">配置文件</el-checkbox>
                <el-checkbox label="logs">日志文件</el-checkbox>
              </el-checkbox-group>
            </el-form-item>
            
            <el-form-item label="压缩选项">
              <el-select v-model="backupForm.compression" placeholder="选择压缩方式">
                <el-option label="无压缩" value="none" />
                <el-option label="GZIP" value="gzip" />
                <el-option label="ZIP" value="zip" />
                <el-option label="7Z" value="7z" />
              </el-select>
            </el-form-item>
            
            <el-form-item label="备份描述">
              <el-input
                v-model="backupForm.description"
                type="textarea"
                :rows="3"
                placeholder="请输入备份描述（可选）"
              />
            </el-form-item>
            
            <el-form-item label="加密备份">
              <el-switch v-model="backupForm.encrypted" />
            </el-form-item>
            
            <el-form-item label="加密密码" v-if="backupForm.encrypted">
              <el-input
                v-model="backupForm.password"
                type="password"
                placeholder="请输入加密密码"
                show-password
              />
            </el-form-item>
            
            <el-form-item>
              <el-button 
                type="primary" 
                @click="startBackup" 
                :loading="backing"
                size="large"
              >
                <el-icon><Download /></el-icon>
                开始备份
              </el-button>
              <el-button @click="resetForm">重置</el-button>
            </el-form-item>
          </el-form>
          
          <!-- 备份进度 -->
          <div v-if="backupProgress.active" class="backup-progress">
            <el-divider>备份进度</el-divider>
            <div class="progress-info">
              <div class="progress-status">
                <el-icon class="loading-icon"><Loading /></el-icon>
                <span>{{ backupProgress.currentStep }}</span>
              </div>
              <div class="progress-details">
                <p>已处理: {{ backupProgress.processedFiles }} / {{ backupProgress.totalFiles }} 文件</p>
                <p>已完成: {{ backupProgress.completedSize }} / {{ backupProgress.totalSize }}</p>
                <p>预计剩余时间: {{ backupProgress.estimatedTime }}</p>
              </div>
            </div>
            <el-progress 
              :percentage="backupProgress.percentage" 
              :status="backupProgress.status"
              :stroke-width="8"
            />
          </div>
        </el-card>
      </el-col>

      <!-- 系统状态 -->
      <el-col :span="8">
        <el-card class="system-status" header="系统状态">
          <div class="status-item">
            <div class="status-label">数据库状态</div>
            <el-tag :type="systemStatus.database === 'healthy' ? 'success' : 'danger'">
              {{ systemStatus.database === 'healthy' ? '正常' : '异常' }}
            </el-tag>
          </div>
          
          <div class="status-item">
            <div class="status-label">磁盘使用率</div>
            <el-progress 
              :percentage="systemStatus.diskUsage" 
              :status="systemStatus.diskUsage > 80 ? 'exception' : 'success'"
              :show-text="true"
            />
          </div>
          
          <div class="status-item">
            <div class="status-label">可用空间</div>
            <span class="status-value">{{ systemStatus.freeSpace }}</span>
          </div>
          
          <div class="status-item">
            <div class="status-label">最后备份</div>
            <span class="status-value">{{ systemStatus.lastBackup }}</span>
          </div>
          
          <div class="status-item">
            <div class="status-label">总备份数</div>
            <span class="status-value">{{ systemStatus.totalBackups }}</span>
          </div>
          
          <div class="status-item">
            <div class="status-label">备份大小</div>
            <span class="status-value">{{ systemStatus.totalBackupSize }}</span>
          </div>
        </el-card>

        <!-- 快速操作 -->
        <el-card class="quick-actions" header="快速操作" style="margin-top: 20px;">
          <el-button type="primary" @click="quickFullBackup" :loading="backing" block>
            完整备份
          </el-button>
          <el-button type="success" @click="quickDatabaseBackup" :loading="backing" block>
            数据库备份
          </el-button>
          <el-button type="warning" @click="quickConfigBackup" :loading="backing" block>
            配置备份
          </el-button>
          <el-button type="info" @click="checkBackupHealth" :loading="checking" block>
            检查备份完整性
          </el-button>
        </el-card>
      </el-col>
    </el-row>

    <!-- 备份历史 -->
    <el-card class="backup-history" header="备份历史" style="margin-top: 20px;">
      <div class="history-controls">
        <el-form :inline="true" :model="historyFilter">
          <el-form-item label="时间范围">
            <el-date-picker
              v-model="historyFilter.dateRange"
              type="daterange"
              range-separator="至"
              start-placeholder="开始日期"
              end-placeholder="结束日期"
              format="YYYY-MM-DD"
              value-format="YYYY-MM-DD"
            />
          </el-form-item>
          <el-form-item label="备份类型">
            <el-select v-model="historyFilter.type" placeholder="全部类型" clearable>
              <el-option label="完整备份" value="full" />
              <el-option label="增量备份" value="incremental" />
              <el-option label="差异备份" value="differential" />
            </el-select>
          </el-form-item>
          <el-form-item label="状态">
            <el-select v-model="historyFilter.status" placeholder="全部状态" clearable>
              <el-option label="成功" value="success" />
              <el-option label="失败" value="failed" />
              <el-option label="进行中" value="running" />
            </el-select>
          </el-form-item>
          <el-form-item>
            <el-button type="primary" @click="filterHistory">搜索</el-button>
            <el-button @click="resetFilter">重置</el-button>
          </el-form-item>
        </el-form>
      </div>

      <el-table
        :data="backupHistory"
        v-loading="loadingHistory"
        style="width: 100%"
      >
        <el-table-column label="备份名称" prop="name" min-width="200">
          <template #default="{ row }">
            <div class="backup-name">
              <el-icon><FolderOpened /></el-icon>
              <span>{{ row.name }}</span>
              <el-tag v-if="row.encrypted" type="warning" size="small">加密</el-tag>
            </div>
          </template>
        </el-table-column>
        
        <el-table-column label="类型" prop="type" width="100">
          <template #default="{ row }">
            <el-tag :type="getTypeTagType(row.type)">
              {{ getTypeLabel(row.type) }}
            </el-tag>
          </template>
        </el-table-column>
        
        <el-table-column label="大小" prop="size" width="120" />
        
        <el-table-column label="状态" prop="status" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusTagType(row.status)">
              {{ getStatusLabel(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        
        <el-table-column label="创建时间" prop="createdAt" width="160">
          <template #default="{ row }">
            {{ formatDate(row.createdAt) }}
          </template>
        </el-table-column>
        
        <el-table-column label="耗时" prop="duration" width="100" />
        
        <el-table-column label="描述" prop="description" min-width="200" show-overflow-tooltip />
        
        <el-table-column label="操作" width="250" fixed="right">
          <template #default="{ row }">
            <el-button 
              type="primary" 
              size="small" 
              @click="downloadBackup(row)"
              :disabled="row.status !== 'success'"
              link
            >
              下载
            </el-button>
            <el-button 
              type="success" 
              size="small" 
              @click="restoreBackup(row)"
              :disabled="row.status !== 'success'"
              link
            >
              还原
            </el-button>
            <el-button 
              type="info" 
              size="small" 
              @click="viewBackupDetails(row)"
              link
            >
              详情
            </el-button>
            <el-popconfirm
              title="确定要删除这个备份吗？"
              @confirm="deleteBackup(row)"
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

      <el-pagination
        v-model:current-page="pagination.currentPage"
        v-model:page-size="pagination.pageSize"
        :page-sizes="[10, 20, 50, 100]"
        :total="pagination.total"
        layout="total, sizes, prev, pager, next, jumper"
        style="margin-top: 20px; justify-content: center;"
      />
    </el-card>

    <!-- 定时备份配置对话框 -->
    <el-dialog
      v-model="showScheduleDialog"
      title="定时备份配置"
      width="600px"
    >
      <el-form :model="scheduleForm" label-width="120px">
        <el-form-item label="启用定时备份">
          <el-switch v-model="scheduleForm.enabled" />
        </el-form-item>
        
        <el-form-item label="备份类型">
          <el-select v-model="scheduleForm.type" placeholder="选择备份类型">
            <el-option label="完整备份" value="full" />
            <el-option label="增量备份" value="incremental" />
          </el-select>
        </el-form-item>
        
        <el-form-item label="执行频率">
          <el-radio-group v-model="scheduleForm.frequency">
            <el-radio label="daily">每日</el-radio>
            <el-radio label="weekly">每周</el-radio>
            <el-radio label="monthly">每月</el-radio>
          </el-radio-group>
        </el-form-item>
        
        <el-form-item label="执行时间">
          <el-time-picker
            v-model="scheduleForm.time"
            placeholder="选择执行时间"
            format="HH:mm"
            value-format="HH:mm"
          />
        </el-form-item>
        
        <el-form-item label="保留份数">
          <el-input-number
            v-model="scheduleForm.retentionCount"
            :min="1"
            :max="30"
            controls-position="right"
          />
        </el-form-item>
        
        <el-form-item label="邮件通知">
          <el-switch v-model="scheduleForm.emailNotification" />
        </el-form-item>
        
        <el-form-item label="通知邮箱" v-if="scheduleForm.emailNotification">
          <el-input v-model="scheduleForm.notificationEmail" placeholder="请输入邮箱地址" />
        </el-form-item>
      </el-form>
      
      <template #footer>
        <el-button @click="showScheduleDialog = false">取消</el-button>
        <el-button type="primary" @click="saveSchedule" :loading="saving">
          保存配置
        </el-button>
      </template>
    </el-dialog>

    <!-- 备份详情对话框 -->
    <el-dialog
      v-model="showDetailsDialog"
      title="备份详情"
      width="800px"
    >
      <div v-if="selectedBackup" class="backup-details">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="备份名称">{{ selectedBackup.name }}</el-descriptions-item>
          <el-descriptions-item label="备份类型">{{ getTypeLabel(selectedBackup.type) }}</el-descriptions-item>
          <el-descriptions-item label="文件大小">{{ selectedBackup.size }}</el-descriptions-item>
          <el-descriptions-item label="状态">
            <el-tag :type="getStatusTagType(selectedBackup.status)">
              {{ getStatusLabel(selectedBackup.status) }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="创建时间">{{ formatDate(selectedBackup.createdAt) }}</el-descriptions-item>
          <el-descriptions-item label="耗时">{{ selectedBackup.duration }}</el-descriptions-item>
          <el-descriptions-item label="压缩方式">{{ selectedBackup.compression }}</el-descriptions-item>
          <el-descriptions-item label="是否加密">
            <el-tag :type="selectedBackup.encrypted ? 'warning' : 'info'">
              {{ selectedBackup.encrypted ? '是' : '否' }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="描述" :span="2">{{ selectedBackup.description || '无' }}</el-descriptions-item>
        </el-descriptions>
        
        <el-divider>备份内容</el-divider>
        <el-table :data="selectedBackup.contents" style="width: 100%">
          <el-table-column label="项目" prop="item" />
          <el-table-column label="大小" prop="size" />
          <el-table-column label="文件数" prop="fileCount" />
          <el-table-column label="状态" prop="status">
            <template #default="{ row }">
              <el-tag :type="row.status === 'success' ? 'success' : 'danger'">
                {{ row.status === 'success' ? '成功' : '失败' }}
              </el-tag>
            </template>
          </el-table-column>
        </el-table>
      </div>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Download,
  Timer,
  Loading,
  FolderOpened
} from '@element-plus/icons-vue'

interface BackupRecord {
  id: number
  name: string
  type: 'full' | 'incremental' | 'differential'
  size: string
  status: 'success' | 'failed' | 'running'
  createdAt: string
  duration: string
  description: string
  encrypted: boolean
  compression: string
  contents: Array<{
    item: string
    size: string
    fileCount: number
    status: string
  }>
}

// 响应式数据
const backing = ref(false)
const checking = ref(false)
const saving = ref(false)
const loadingHistory = ref(false)
const showScheduleDialog = ref(false)
const showDetailsDialog = ref(false)
const selectedBackup = ref<BackupRecord | null>(null)

// 备份表单
const backupForm = reactive({
  type: 'full',
  scope: ['database', 'files'],
  compression: 'gzip',
  description: '',
  encrypted: false,
  password: ''
})

// 备份进度
const backupProgress = reactive({
  active: false,
  percentage: 0,
  status: 'success' as 'success' | 'exception' | 'warning',
  currentStep: '',
  processedFiles: 0,
  totalFiles: 0,
  completedSize: '',
  totalSize: '',
  estimatedTime: ''
})

// 系统状态
const systemStatus = reactive({
  database: 'healthy',
  diskUsage: 65,
  freeSpace: '120 GB',
  lastBackup: '2024-01-15 02:00:00',
  totalBackups: 28,
  totalBackupSize: '15.6 GB'
})

// 历史记录筛选
const historyFilter = reactive({
  dateRange: [],
  type: '',
  status: ''
})

// 定时备份配置
const scheduleForm = reactive({
  enabled: true,
  type: 'incremental',
  frequency: 'daily',
  time: '02:00',
  retentionCount: 7,
  emailNotification: true,
  notificationEmail: 'admin@company.com'
})

// 分页
const pagination = reactive({
  currentPage: 1,
  pageSize: 10,
  total: 50
})

// 模拟备份历史数据
const backupHistory = ref<BackupRecord[]>([
  {
    id: 1,
    name: 'backup_2024_01_15_020000_full',
    type: 'full',
    size: '2.3 GB',
    status: 'success',
    createdAt: '2024-01-15 02:00:00',
    duration: '45分钟',
    description: '每日定时完整备份',
    encrypted: true,
    compression: 'gzip',
    contents: [
      { item: '数据库', size: '1.8 GB', fileCount: 1, status: 'success' },
      { item: '文件系统', size: '450 MB', fileCount: 2580, status: 'success' },
      { item: '配置文件', size: '50 MB', fileCount: 125, status: 'success' }
    ]
  },
  {
    id: 2,
    name: 'backup_2024_01_14_020000_incremental',
    type: 'incremental',
    size: '156 MB',
    status: 'success',
    createdAt: '2024-01-14 02:00:00',
    duration: '8分钟',
    description: '增量备份',
    encrypted: false,
    compression: 'zip',
    contents: [
      { item: '数据库', size: '120 MB', fileCount: 1, status: 'success' },
      { item: '文件系统', size: '36 MB', fileCount: 45, status: 'success' }
    ]
  },
  {
    id: 3,
    name: 'backup_2024_01_13_143000_manual',
    type: 'full',
    size: '2.1 GB',
    status: 'failed',
    createdAt: '2024-01-13 14:30:00',
    duration: '25分钟',
    description: '手动备份（版本更新前）',
    encrypted: false,
    compression: 'gzip',
    contents: [
      { item: '数据库', size: '1.6 GB', fileCount: 1, status: 'success' },
      { item: '文件系统', size: '0 MB', fileCount: 0, status: 'failed' }
    ]
  }
])

// 方法
const createBackup = () => {
  // 显示备份配置表单
}

const scheduleBackup = () => {
  showScheduleDialog.value = true
}

const startBackup = async () => {
  try {
    backing.value = true
    backupProgress.active = true
    backupProgress.percentage = 0
    backupProgress.currentStep = '准备备份环境...'
    
    // 模拟备份过程
    const steps = [
      { step: '检查系统状态...', duration: 1000 },
      { step: '锁定数据库...', duration: 500 },
      { step: '备份数据库...', duration: 3000 },
      { step: '备份文件系统...', duration: 2000 },
      { step: '压缩备份文件...', duration: 1500 },
      { step: '验证备份完整性...', duration: 1000 },
      { step: '清理临时文件...', duration: 500 }
    ]
    
    for (let i = 0; i < steps.length; i++) {
      backupProgress.currentStep = steps[i].step
      backupProgress.percentage = Math.round(((i + 1) / steps.length) * 100)
      backupProgress.processedFiles = Math.round(Math.random() * 1000)
      backupProgress.totalFiles = 1000
      backupProgress.completedSize = `${(Math.random() * 2).toFixed(1)} GB`
      backupProgress.totalSize = '2.5 GB'
      backupProgress.estimatedTime = `${7 - i}分钟`
      
      await new Promise(resolve => setTimeout(resolve, steps[i].duration))
    }
    
    backupProgress.currentStep = '备份完成'
    backupProgress.status = 'success'
    ElMessage.success('备份创建成功')
    
  } catch (error: any) {
    backupProgress.status = 'exception'
    ElMessage.error('备份失败')
  } finally {
    backing.value = false
    setTimeout(() => {
      backupProgress.active = false
    }, 2000)
  }
}

const resetForm = () => {
  backupForm.type = 'full'
  backupForm.scope = ['database', 'files']
  backupForm.compression = 'gzip'
  backupForm.description = ''
  backupForm.encrypted = false
  backupForm.password = ''
}

const quickFullBackup = async () => {
  backupForm.type = 'full'
  backupForm.scope = ['database', 'files', 'config']
  await startBackup()
}

const quickDatabaseBackup = async () => {
  backupForm.type = 'full'
  backupForm.scope = ['database']
  await startBackup()
}

const quickConfigBackup = async () => {
  backupForm.type = 'full'
  backupForm.scope = ['config']
  await startBackup()
}

const checkBackupHealth = async () => {
  try {
    checking.value = true
    await new Promise(resolve => setTimeout(resolve, 3000))
    ElMessage.success('备份完整性检查通过')
  } catch (error: any) {
    ElMessage.error('备份完整性检查失败')
  } finally {
    checking.value = false
  }
}

const filterHistory = () => {
  loadingHistory.value = true
  setTimeout(() => {
    loadingHistory.value = false
  }, 1000)
}

const resetFilter = () => {
  historyFilter.dateRange = []
  historyFilter.type = ''
  historyFilter.status = ''
  filterHistory()
}

const downloadBackup = (backup: BackupRecord) => {
  ElMessage.success(`开始下载备份: ${backup.name}`)
}

const restoreBackup = async (backup: BackupRecord) => {
  try {
    await ElMessageBox.confirm(
      `确定要从备份 "${backup.name}" 还原系统吗？此操作将覆盖当前数据！`,
      '还原确认',
      {
        confirmButtonText: '确定还原',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    ElMessage.success('开始还原系统，请耐心等待...')
  } catch {
    // 用户取消
  }
}

const viewBackupDetails = (backup: BackupRecord) => {
  selectedBackup.value = backup
  showDetailsDialog.value = true
}

const deleteBackup = async (backup: BackupRecord) => {
  try {
    await new Promise(resolve => setTimeout(resolve, 1000))
    ElMessage.success('备份删除成功')
    // 从列表中移除
    const index = backupHistory.value.findIndex(b => b.id === backup.id)
    if (index > -1) {
      backupHistory.value.splice(index, 1)
    }
  } catch (error: any) {
    ElMessage.error('删除失败')
  }
}

const saveSchedule = async () => {
  try {
    saving.value = true
    await new Promise(resolve => setTimeout(resolve, 1000))
    ElMessage.success('定时备份配置保存成功')
    showScheduleDialog.value = false
  } catch (error: any) {
    ElMessage.error('保存失败')
  } finally {
    saving.value = false
  }
}

const formatDate = (dateStr: string) => {
  return new Date(dateStr).toLocaleString('zh-CN')
}

const getTypeLabel = (type: string) => {
  const labels = {
    full: '完整',
    incremental: '增量',
    differential: '差异'
  }
  return labels[type as keyof typeof labels] || type
}

const getTypeTagType = (type: string) => {
  const types = {
    full: 'primary',
    incremental: 'success',
    differential: 'warning'
  }
  return types[type as keyof typeof types] || 'info'
}

const getStatusLabel = (status: string) => {
  const labels = {
    success: '成功',
    failed: '失败',
    running: '进行中'
  }
  return labels[status as keyof typeof labels] || status
}

const getStatusTagType = (status: string) => {
  const types = {
    success: 'success',
    failed: 'danger',
    running: 'warning'
  }
  return types[status as keyof typeof types] || 'info'
}

onMounted(() => {
  // 初始化数据
})
</script>

<style scoped>
.data-backup {
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

.header-actions {
  display: flex;
  gap: 10px;
}

.backup-operations,
.system-status,
.backup-history {
  margin-bottom: 20px;
}

.backup-progress {
  margin-top: 20px;
  padding: 20px;
  background-color: #f8f9fa;
  border-radius: 6px;
}

.progress-info {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 15px;
}

.progress-status {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 600;
  color: #409eff;
}

.loading-icon {
  animation: loading 2s infinite linear;
}

@keyframes loading {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.progress-details {
  text-align: right;
  font-size: 14px;
  color: #606266;
}

.progress-details p {
  margin: 2px 0;
}

.status-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
}

.status-label {
  font-weight: 500;
  color: #606266;
}

.status-value {
  font-weight: 600;
  color: #303133;
}

.quick-actions .el-button {
  margin-bottom: 10px;
}

.history-controls {
  margin-bottom: 20px;
}

.backup-name {
  display: flex;
  align-items: center;
  gap: 8px;
}

.backup-details {
  max-height: 600px;
  overflow-y: auto;
}

:deep(.el-card__header) {
  background-color: #f8f9fa;
  font-weight: 600;
  color: #303133;
}

:deep(.el-checkbox-group) {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

:deep(.el-checkbox-group .el-checkbox) {
  margin-right: 0;
}

:deep(.el-progress-bar__outer) {
  background-color: #e4e7ed;
}

:deep(.el-table .el-table__row:hover) {
  background-color: #f5f7fa;
}
</style>
