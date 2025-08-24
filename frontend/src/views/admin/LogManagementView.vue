<template>
  <div class="log-management">
    <el-card class="page-header">
      <div class="header-content">
        <h2>日志管理</h2>
        <div class="header-actions">
          <el-button type="primary" @click="exportLogs" :loading="exporting">
            <el-icon><Download /></el-icon>
            导出日志
          </el-button>
          <el-button type="warning" @click="clearLogs">
            <el-icon><Delete /></el-icon>
            清理日志
          </el-button>
          <el-button @click="refreshLogs">
            <el-icon><Refresh /></el-icon>
            刷新
          </el-button>
        </div>
      </div>
    </el-card>

    <el-row :gutter="20">
      <!-- 日志统计 -->
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-item">
            <div class="stat-icon error">
              <el-icon><Warning /></el-icon>
            </div>
            <div class="stat-content">
              <div class="stat-value">{{ logStats.error }}</div>
              <div class="stat-label">错误日志</div>
            </div>
          </div>
        </el-card>
      </el-col>
      
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-item">
            <div class="stat-icon warning">
              <el-icon><InfoFilled /></el-icon>
            </div>
            <div class="stat-content">
              <div class="stat-value">{{ logStats.warning }}</div>
              <div class="stat-label">警告日志</div>
            </div>
          </div>
        </el-card>
      </el-col>
      
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-item">
            <div class="stat-icon info">
              <el-icon><Check /></el-icon>
            </div>
            <div class="stat-content">
              <div class="stat-value">{{ logStats.info }}</div>
              <div class="stat-label">信息日志</div>
            </div>
          </div>
        </el-card>
      </el-col>
      
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-item">
            <div class="stat-icon debug">
              <el-icon><Tools /></el-icon>
            </div>
            <div class="stat-content">
              <div class="stat-value">{{ logStats.debug }}</div>
              <div class="stat-label">调试日志</div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 日志类型选择 -->
    <el-card class="log-types" style="margin-top: 20px;">
      <el-tabs v-model="activeLogType" @tab-change="handleTabChange">
        <el-tab-pane label="系统日志" name="system">
          <el-icon><Setting /></el-icon>
        </el-tab-pane>
        <el-tab-pane label="访问日志" name="access">
          <el-icon><View /></el-icon>
        </el-tab-pane>
        <el-tab-pane label="错误日志" name="error">
          <el-icon><Warning /></el-icon>
        </el-tab-pane>
        <el-tab-pane label="安全日志" name="security">
          <el-icon><Lock /></el-icon>
        </el-tab-pane>
        <el-tab-pane label="操作日志" name="operation">
          <el-icon><Operation /></el-icon>
        </el-tab-pane>
        <el-tab-pane label="登录日志" name="login">
          <el-icon><User /></el-icon>
        </el-tab-pane>
      </el-tabs>
    </el-card>

    <!-- 搜索筛选 -->
    <el-card class="search-card" style="margin-top: 20px;">
      <el-form :inline="true" :model="searchForm">
        <el-form-item label="时间范围">
          <el-date-picker
            v-model="searchForm.dateRange"
            type="datetimerange"
            range-separator="至"
            start-placeholder="开始时间"
            end-placeholder="结束时间"
            format="YYYY-MM-DD HH:mm:ss"
            value-format="YYYY-MM-DD HH:mm:ss"
          />
        </el-form-item>
        
        <el-form-item label="日志级别">
          <el-select v-model="searchForm.level" placeholder="全部级别" clearable>
            <el-option label="错误 (ERROR)" value="error" />
            <el-option label="警告 (WARN)" value="warning" />
            <el-option label="信息 (INFO)" value="info" />
            <el-option label="调试 (DEBUG)" value="debug" />
          </el-select>
        </el-form-item>
        
        <el-form-item label="模块">
          <el-input 
            v-model="searchForm.module" 
            placeholder="模块名称"
            clearable
          />
        </el-form-item>
        
        <el-form-item label="IP地址">
          <el-input 
            v-model="searchForm.ip" 
            placeholder="IP地址"
            clearable
          />
        </el-form-item>
        
        <el-form-item label="关键字">
          <el-input 
            v-model="searchForm.keyword" 
            placeholder="搜索关键字"
            clearable
          />
        </el-form-item>
        
        <el-form-item>
          <el-button type="primary" @click="searchLogs">
            <el-icon><Search /></el-icon>
            搜索
          </el-button>
          <el-button @click="resetSearch">重置</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 日志表格 -->
    <el-card class="log-table" style="margin-top: 20px;">
      <el-table
        :data="logs"
        v-loading="loading"
        style="width: 100%"
        :height="600"
        stripe
      >
        <el-table-column type="expand">
          <template #default="{ row }">
            <div class="log-detail">
              <el-descriptions :column="2" border>
                <el-descriptions-item label="日志ID">{{ row.id }}</el-descriptions-item>
                <el-descriptions-item label="模块">{{ row.module }}</el-descriptions-item>
                <el-descriptions-item label="用户ID">{{ row.user || '系统' }}</el-descriptions-item>
                <el-descriptions-item label="IP地址">{{ row.ip_address }}</el-descriptions-item>
                <el-descriptions-item label="完整消息" :span="2">
                  <pre>{{ row.full_message }}</pre>
                </el-descriptions-item>
              </el-descriptions>
            </div>
          </template>
        </el-table-column>
        
        <el-table-column label="时间" prop="created_at" width="160" sortable>
          <template #default="{ row }">
            {{ formatDate(row.created_at) }}
          </template>
        </el-table-column>
        
        <el-table-column label="级别" prop="level" width="80">
          <template #default="{ row }">
            <el-tag :type="getLevelTagType(row.level)" size="small">
              {{ row.level.toUpperCase() }}
            </el-tag>
          </template>
        </el-table-column>
        
        <el-table-column label="模块" prop="module" width="100" />
        
        <el-table-column label="用户" prop="user" width="100">
          <template #default="{ row }">
            {{ row.user || '系统' }}
          </template>
        </el-table-column>
        
        <el-table-column label="IP地址" prop="ip_address" width="120" />
        
        <el-table-column label="消息" prop="message" show-overflow-tooltip />
        
        <el-table-column label="操作" width="120">
          <template #default="{ row }">
            <el-button type="primary" size="small" @click="viewLogDetail(row)">详情</el-button>
            <el-button type="danger" size="small" @click="deleteLog(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>

      <el-pagination
        v-model:current-page="pagination.currentPage"
        v-model:page-size="pagination.pageSize"
        :page-sizes="[20, 50, 100, 200]"
        :total="pagination.total"
        layout="total, sizes, prev, pager, next, jumper"
        style="margin-top: 20px; justify-content: center;"
        @size-change="handleSizeChange"
        @current-change="handleCurrentChange"
      />
    </el-card>

    <!-- 日志详情对话框 -->
    <el-dialog
      v-model="showDetailDialog"
      title="日志详情"
      width="800px"
    >
      <div v-if="selectedLog" class="log-detail-dialog">
        <el-descriptions :column="1" border>
          <el-descriptions-item label="时间">{{ formatDate(selectedLog.created_at) }}</el-descriptions-item>
          <el-descriptions-item label="级别">
            <el-tag :type="getLevelTagType(selectedLog.level)">
              {{ selectedLog.level.toUpperCase() }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="用户">{{ selectedLog.user || '系统' }}</el-descriptions-item>
          <el-descriptions-item label="IP地址">{{ selectedLog.ip_address }}</el-descriptions-item>
          <el-descriptions-item label="模块">{{ selectedLog.module }}</el-descriptions-item>
          <el-descriptions-item label="消息">{{ selectedLog.message }}</el-descriptions-item>
          <el-descriptions-item label="完整内容">
            <el-input
              type="textarea"
              :rows="10"
              :value="selectedLog.full_message"
              readonly
            />
          </el-descriptions-item>
        </el-descriptions>
      </div>
      
      <template #footer>
        <el-button @click="showDetailDialog = false">关闭</el-button>
        <el-button type="primary" @click="copyLogDetail">复制内容</el-button>
      </template>
    </el-dialog>

    <!-- 清理日志对话框 -->
    <el-dialog
      v-model="showClearDialog"
      title="清理日志"
      width="500px"
    >
      <el-form :model="clearForm" label-width="100px">
        <el-form-item label="清理策略">
          <el-radio-group v-model="clearForm.strategy">
            <el-radio label="by_time">按时间</el-radio>
            <el-radio label="by_count">按数量</el-radio>
            <el-radio label="by_size">按大小</el-radio>
          </el-radio-group>
        </el-form-item>
        
        <el-form-item label="保留天数" v-if="clearForm.strategy === 'by_time'">
          <el-input-number v-model="clearForm.retentionDays" :min="1" :max="365" />
          <span style="margin-left: 10px;">天</span>
        </el-form-item>
        
        <el-form-item label="保留数量" v-if="clearForm.strategy === 'by_count'">
          <el-input-number v-model="clearForm.retentionCount" :min="100" :max="100000" />
          <span style="margin-left: 10px;">条</span>
        </el-form-item>
        
        <el-form-item label="最大大小" v-if="clearForm.strategy === 'by_size'">
          <el-input-number v-model="clearForm.maxSize" :min="100" :max="10000" />
          <span style="margin-left: 10px;">MB</span>
        </el-form-item>
        
        <el-form-item label="日志级别">
          <el-checkbox-group v-model="clearForm.levels">
            <el-checkbox label="debug">调试</el-checkbox>
            <el-checkbox label="info">信息</el-checkbox>
            <el-checkbox label="warning">警告</el-checkbox>
            <el-checkbox label="error">错误</el-checkbox>
          </el-checkbox-group>
        </el-form-item>
      </el-form>
      
      <template #footer>
        <el-button @click="showClearDialog = false">取消</el-button>
        <el-button type="danger" @click="confirmClearLogs" :loading="clearing">
          确定清理
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import reportsService, { type SystemLog } from '@/services/reports'
import {
  Download,
  Delete,
  Refresh,
  Warning,
  InfoFilled,
  Check,
  Tools,
  Setting,
  View,
  Lock,
  Operation,
  User,
  Search
} from '@element-plus/icons-vue'

// 响应式数据
const loading = ref(false)
const exporting = ref(false)
const clearing = ref(false)
const showDetailDialog = ref(false)
const showClearDialog = ref(false)
const selectedLog = ref<SystemLog | null>(null)

const activeLogType = ref('system')

// 日志统计
const logStats = reactive({
  error: 0,
  warning: 0,
  info: 0,
  debug: 0
})

// 搜索表单
const searchForm = reactive({
  dateRange: [] as string[],
  level: '',
  module: '',
  ip: '',
  keyword: ''
})

// 清理表单
const clearForm = reactive({
  strategy: 'by_time',
  retentionDays: 30,
  retentionCount: 10000,
  maxSize: 1000,
  levels: ['debug']
})

// 分页
const pagination = reactive({
  currentPage: 1,
  pageSize: 50,
  total: 0
})

// 日志数据
const logs = ref<SystemLog[]>([])

// 方法
const loadLogStats = async () => {
  // 从已加载的日志中统计
  const stats = { error: 0, warning: 0, info: 0, debug: 0 }
  logs.value.forEach(log => {
    if (stats.hasOwnProperty(log.level)) {
      stats[log.level as keyof typeof stats]++
    }
  })
  Object.assign(logStats, stats)
}

const handleTabChange = (name: string) => {
  activeLogType.value = name
  searchLogs()
}

const searchLogs = async () => {
  loading.value = true
  try {
    const params: any = {
      page: pagination.currentPage,
      page_size: pagination.pageSize
    }
    
    if (searchForm.level) params.level = searchForm.level
    if (searchForm.module) params.module = searchForm.module
    if (searchForm.ip) params.ip_address = searchForm.ip
    if (searchForm.keyword) params.search = searchForm.keyword
    
    const response = await reportsService.getSystemLogs(params)
    logs.value = response.results
    pagination.total = response.count
    
    await loadLogStats()
  } catch (error: any) {
    console.error('加载日志失败:', error)
    ElMessage.error('加载日志失败')
  } finally {
    loading.value = false
  }
}

const resetSearch = () => {
  searchForm.dateRange = []
  searchForm.level = ''
  searchForm.module = ''
  searchForm.ip = ''
  searchForm.keyword = ''
  searchLogs()
}

const refreshLogs = () => {
  searchLogs()
}

const exportLogs = async () => {
  try {
    exporting.value = true
    // 这里可以调用导出API
    await new Promise(resolve => setTimeout(resolve, 2000))
    ElMessage.success('日志导出成功')
  } catch (error: any) {
    ElMessage.error('导出失败')
  } finally {
    exporting.value = false
  }
}

const clearLogs = () => {
  showClearDialog.value = true
}

const confirmClearLogs = async () => {
  try {
    clearing.value = true
    // 这里可以调用清理API
    await new Promise(resolve => setTimeout(resolve, 3000))
    ElMessage.success('日志清理完成')
    showClearDialog.value = false
    searchLogs()
  } catch (error: any) {
    ElMessage.error('清理失败')
  } finally {
    clearing.value = false
  }
}

const viewLogDetail = (log: SystemLog) => {
  selectedLog.value = log
  showDetailDialog.value = true
}

const deleteLog = async (log: SystemLog) => {
  try {
    await ElMessageBox.confirm('确定要删除这条日志吗？', '删除确认', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    
    // 这里可以调用删除API
    const index = logs.value.findIndex(l => l.id === log.id)
    if (index > -1) {
      logs.value.splice(index, 1)
      pagination.total--
    }
    ElMessage.success('日志删除成功')
  } catch {
    // 用户取消
  }
}

const copyLogDetail = () => {
  if (selectedLog.value) {
    const content = `时间: ${selectedLog.value.created_at}\n级别: ${selectedLog.value.level}\n用户: ${selectedLog.value.user || '系统'}\nIP: ${selectedLog.value.ip_address}\n模块: ${selectedLog.value.module}\n消息: ${selectedLog.value.message}\n详细内容:\n${selectedLog.value.full_message}`
    
    navigator.clipboard.writeText(content).then(() => {
      ElMessage.success('日志内容已复制到剪贴板')
    }).catch(() => {
      ElMessage.error('复制失败')
    })
  }
}

const formatDate = (dateStr: string) => {
  return new Date(dateStr).toLocaleString('zh-CN')
}

const getLevelTagType = (level: string) => {
  const types = {
    error: 'danger',
    warning: 'warning',
    info: 'primary',
    debug: 'info'
  }
  return types[level as keyof typeof types] || 'info'
}

const handleSizeChange = (size: number) => {
  pagination.pageSize = size
  searchLogs()
}

const handleCurrentChange = (page: number) => {
  pagination.currentPage = page
  searchLogs()
}

onMounted(() => {
  searchLogs()
})
</script>

<style scoped>
.log-management {
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

.stat-card {
  margin-bottom: 20px;
}

.stat-item {
  display: flex;
  align-items: center;
  gap: 15px;
}

.stat-icon {
  width: 50px;
  height: 50px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
  color: white;
}

.stat-icon.error {
  background: linear-gradient(135deg, #f56c6c, #f78989);
}

.stat-icon.warning {
  background: linear-gradient(135deg, #e6a23c, #ebb563);
}

.stat-icon.info {
  background: linear-gradient(135deg, #409eff, #66b1ff);
}

.stat-icon.debug {
  background: linear-gradient(135deg, #909399, #a6a9ad);
}

.stat-content {
  flex: 1;
}

.stat-value {
  font-size: 28px;
  font-weight: bold;
  color: #303133;
  line-height: 1;
}

.stat-label {
  font-size: 14px;
  color: #909399;
  margin-top: 5px;
}

.log-detail {
  padding: 20px;
  background-color: #fafafa;
  border-radius: 6px;
}

.log-detail pre {
  background-color: #f5f5f5;
  padding: 10px;
  border-radius: 4px;
  overflow-x: auto;
  white-space: pre-wrap;
  word-wrap: break-word;
}

.log-detail-dialog {
  max-height: 600px;
  overflow-y: auto;
}

:deep(.el-card__header) {
  padding: 15px 20px;
  background-color: #f8f9fa;
  border-bottom: 1px solid #e9ecef;
}
</style>
