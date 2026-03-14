<template>
  <div class="system-config">
    <el-card class="page-header">
      <div class="header-content">
        <h2>系统配置</h2>
        <div class="header-actions">
          <el-button type="success" @click="saveAllConfigs" :loading="saving">
            <el-icon><Check /></el-icon>
            保存所有配置
          </el-button>
          <el-button @click="resetConfigs">
            <el-icon><Refresh /></el-icon>
            重置配置
          </el-button>
        </div>
      </div>
    </el-card>

    <el-row :gutter="20">
      <!-- 基础配置 -->
      <el-col :span="12">
        <el-card class="config-card" header="基础配置">
          <el-form :model="basicConfig" label-width="120px">
            <el-form-item label="系统名称">
              <el-input v-model="basicConfig.systemName" placeholder="请输入系统名称" />
            </el-form-item>
            
            <el-form-item label="公司名称">
              <el-input v-model="basicConfig.companyName" placeholder="请输入公司名称" />
            </el-form-item>
            
            <el-form-item label="系统版本">
              <el-input v-model="basicConfig.version" placeholder="请输入系统版本" readonly />
            </el-form-item>
            
            <el-form-item label="系统Logo">
              <el-upload
                class="logo-upload"
                :show-file-list="false"
                :on-success="handleLogoSuccess"
                :on-error="handleLogoError"
                :on-progress="handleLogoProgress"
                :before-upload="beforeLogoUpload"
                :headers="uploadHeaders"
                action="/api/upload/logo"
                name="file"
                :data="{ type: 'logo' }"
              >
                <img v-if="basicConfig.logoUrl" :src="basicConfig.logoUrl" class="logo-preview" />
                <el-icon v-else class="logo-upload-icon"><Plus /></el-icon>
              </el-upload>
            </el-form-item>
            
            <el-form-item label="系统描述">
              <el-input
                v-model="basicConfig.description"
                type="textarea"
                :rows="3"
                placeholder="请输入系统描述"
              />
            </el-form-item>
            
            <el-form-item label="联系电话">
              <el-input v-model="basicConfig.contactPhone" placeholder="请输入联系电话" />
            </el-form-item>
            
            <el-form-item label="系统地址">
              <el-input v-model="basicConfig.systemUrl" placeholder="请输入系统访问地址" />
            </el-form-item>
          </el-form>
        </el-card>
      </el-col>

      <!-- 考勤配置 -->
      <el-col :span="12">
        <el-card class="config-card" header="考勤配置">
          <el-form :model="attendanceConfig" label-width="120px">
            <el-form-item label="上班时间">
              <el-time-picker
                v-model="attendanceConfig.startTime"
                placeholder="选择上班时间"
                format="HH:mm"
                value-format="HH:mm"
              />
            </el-form-item>
            
            <el-form-item label="下班时间">
              <el-time-picker
                v-model="attendanceConfig.endTime"
                placeholder="选择下班时间"
                format="HH:mm"
                value-format="HH:mm"
              />
            </el-form-item>
            
            <el-form-item label="午休开始">
              <el-time-picker
                v-model="attendanceConfig.lunchStartTime"
                placeholder="选择午休开始时间"
                format="HH:mm"
                value-format="HH:mm"
              />
            </el-form-item>
            
            <el-form-item label="午休结束">
              <el-time-picker
                v-model="attendanceConfig.lunchEndTime"
                placeholder="选择午休结束时间"
                format="HH:mm"
                value-format="HH:mm"
              />
            </el-form-item>
            
            <el-form-item label="迟到阈值">
              <el-input-number
                v-model="attendanceConfig.lateThreshold"
                :min="1"
                :max="60"
                controls-position="right"
              />
              <span style="margin-left: 10px;">分钟</span>
            </el-form-item>
            
            <el-form-item label="早退阈值">
              <el-input-number
                v-model="attendanceConfig.earlyLeaveThreshold"
                :min="1"
                :max="60"
                controls-position="right"
              />
              <span style="margin-left: 10px;">分钟</span>
            </el-form-item>
            
            <el-form-item label="工作日">
              <el-checkbox-group v-model="attendanceConfig.workDays">
                <el-checkbox label="1">周一</el-checkbox>
                <el-checkbox label="2">周二</el-checkbox>
                <el-checkbox label="3">周三</el-checkbox>
                <el-checkbox label="4">周四</el-checkbox>
                <el-checkbox label="5">周五</el-checkbox>
                <el-checkbox label="6">周六</el-checkbox>
                <el-checkbox label="0">周日</el-checkbox>
              </el-checkbox-group>
            </el-form-item>
            
            <el-form-item label="启用地理位置">
              <el-switch v-model="attendanceConfig.enableLocation" />
            </el-form-item>
            
            <el-form-item label="打卡范围" v-if="attendanceConfig.enableLocation">
              <el-input-number
                v-model="attendanceConfig.locationRange"
                :min="10"
                :max="1000"
                controls-position="right"
              />
              <span style="margin-left: 10px;">米</span>
            </el-form-item>
            
            <el-form-item label="启用人脸识别">
              <el-switch v-model="attendanceConfig.enableFaceRecognition" />
            </el-form-item>
          </el-form>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" style="margin-top: 20px;">



    </el-row>

    <el-row :gutter="20" style="margin-top: 20px;">
      <!-- 通知配置 -->
      <el-col :span="12">
        <el-card class="config-card" header="通知配置">
          <el-form :model="notificationConfig" label-width="120px">
            <el-form-item label="启用邮件通知">
              <el-switch v-model="notificationConfig.enableEmail" />
            </el-form-item>
            
            <el-form-item label="启用短信通知">
              <el-switch v-model="notificationConfig.enableSMS" />
            </el-form-item>
            
            <el-form-item label="启用站内通知">
              <el-switch v-model="notificationConfig.enableInApp" />
            </el-form-item>
            
            <el-form-item label="考勤异常通知">
              <el-switch v-model="notificationConfig.attendanceAlert" />
            </el-form-item>
            
            <el-form-item label="请假审批通知">
              <el-switch v-model="notificationConfig.leaveApprovalAlert" />
            </el-form-item>
            
            <el-form-item label="薪资发放通知">
              <el-switch v-model="notificationConfig.salaryAlert" />
            </el-form-item>
            
            <el-form-item label="生日提醒">
              <el-switch v-model="notificationConfig.birthdayReminder" />
            </el-form-item>
            
            <el-form-item label="合同到期提醒">
              <el-switch v-model="notificationConfig.contractExpireReminder" />
            </el-form-item>
            
            <el-form-item label="提醒提前天数">
              <el-input-number
                v-model="notificationConfig.reminderDays"
                :min="1"
                :max="30"
                controls-position="right"
              />
              <span style="margin-left: 10px;">天</span>
            </el-form-item>
          </el-form>
        </el-card>
      </el-col>

      <!-- 系统维护 -->
      <el-col :span="12">
        <el-card class="config-card" header="系统维护">
          <el-form :model="maintenanceConfig" label-width="120px">
            <el-form-item label="系统状态">
              <el-tag :type="maintenanceConfig.isMaintenanceMode ? 'warning' : 'success'">
                {{ maintenanceConfig.isMaintenanceMode ? '维护中' : '正常运行' }}
              </el-tag>
            </el-form-item>
            
            <el-form-item label="维护模式">
              <el-switch
                v-model="maintenanceConfig.isMaintenanceMode"
                @change="handleMaintenanceModeChange"
              />
            </el-form-item>
            
            <el-form-item label="维护公告" v-if="maintenanceConfig.isMaintenanceMode">
              <el-input
                v-model="maintenanceConfig.maintenanceMessage"
                type="textarea"
                :rows="3"
                placeholder="请输入维护公告"
              />
            </el-form-item>
            
            <el-form-item label="预计恢复时间" v-if="maintenanceConfig.isMaintenanceMode">
              <el-date-picker
                v-model="maintenanceConfig.estimatedRecoveryTime"
                type="datetime"
                placeholder="选择预计恢复时间"
                format="YYYY-MM-DD HH:mm:ss"
                value-format="YYYY-MM-DD HH:mm:ss"
              />
            </el-form-item>
            
            <el-form-item label="数据保留天数">
              <el-input-number
                v-model="maintenanceConfig.dataRetentionDays"
                :min="30"
                :max="3650"
                controls-position="right"
              />
              <span style="margin-left: 10px;">天</span>
            </el-form-item>
            
            <el-form-item label="日志清理">
              <el-button type="warning" @click="cleanLogs" :loading="cleaning">
                <el-icon><Delete /></el-icon>
                清理过期日志
              </el-button>
            </el-form-item>
            
            <el-form-item label="缓存清理">
              <el-button type="warning" @click="clearCache" :loading="clearing">
                <el-icon><Refresh /></el-icon>
                清理系统缓存
              </el-button>
            </el-form-item>
            
            <el-form-item label="系统重启">
              <el-popconfirm
                title="确定要重启系统吗？这将中断所有用户的操作！"
                @confirm="restartSystem"
              >
                <template #reference>
                  <el-button type="danger" :loading="restarting">
                    <el-icon><Switch /></el-icon>
                    重启系统
                  </el-button>
                </template>
              </el-popconfirm>
            </el-form-item>
          </el-form>
        </el-card>
      </el-col>
    </el-row>

    <!-- 公司地址管理 -->
    <el-row :gutter="20" style="margin-top: 20px;">
      <el-col :span="24">
        <el-card class="config-card">
          <template #header>
            <div class="card-header">
              <span>
                <el-icon><LocationInformation /></el-icon>
                公司地址管理
              </span>
              <el-button type="primary" size="small" @click="showAddLocationDialog">
                <el-icon><Plus /></el-icon>
                添加地址
              </el-button>
            </div>
          </template>
          
          <el-table :data="companyLocations" style="width: 100%">
            <el-table-column prop="name" label="地点名称" />
            <el-table-column prop="address" label="详细地址" />
            <el-table-column prop="range" label="打卡范围">
              <template #default="scope">
                {{ scope.row.range }}米
              </template>
            </el-table-column>
            <el-table-column prop="is_default" label="默认地点">
              <template #default="scope">
                <el-tag :type="scope.row.is_default ? 'success' : 'info'">
                  {{ scope.row.is_default ? '是' : '否' }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="status" label="状态">
              <template #default="scope">
                <el-tag :type="scope.row.status === 'active' ? 'success' : 'danger'">
                  {{ scope.row.status === 'active' ? '启用' : '禁用' }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column label="操作" width="200">
              <template #default="scope">
                <el-button size="small" @click="editLocation(scope.row)">编辑</el-button>
                <el-button size="small" type="success" @click="setDefaultLocation(scope.row)" :disabled="scope.row.is_default">
                  设为默认
                </el-button>
                <el-button size="small" type="danger" @click="deleteLocation(scope.row)">删除</el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>
    </el-row>

    <!-- 添加/编辑地址对话框 -->
    <el-dialog
      v-model="locationDialogVisible"
      :title="editingLocation.id ? '编辑地址' : '添加地址'"
      width="600px"
    >
      <el-form :model="editingLocation" label-width="100px">
        <el-form-item label="地点名称" required>
          <el-input v-model="editingLocation.name" placeholder="如：总部大楼、分公司等" />
        </el-form-item>
        
        <el-form-item label="详细地址" required>
          <el-input v-model="editingLocation.address" placeholder="请输入详细地址" />
        </el-form-item>
        
        <el-form-item label="地理坐标">
          <el-row :gutter="10">
            <el-col :span="12">
              <el-input v-model="editingLocation.latitude" placeholder="纬度 (如: 39.908823)" />
            </el-col>
            <el-col :span="12">
              <el-input v-model="editingLocation.longitude" placeholder="经度 (如: 116.399010)" />
            </el-col>
          </el-row>
          <div class="form-tip">
            <el-button size="small" type="primary" @click="getCurrentLocation">获取当前位置</el-button>
            <el-button size="small" @click="showCoordinateHelp">坐标帮助</el-button>
            <el-button size="small" @click="showCommonLocations">常用城市</el-button>
            <span class="tip-text">或手动输入经纬度坐标</span>
          </div>
          <div class="coordinate-info">
            <el-text type="info" size="small">
              提示：可通过百度地图、高德地图等工具获取准确坐标
            </el-text>
          </div>
        </el-form-item>
        
        <el-form-item label="打卡范围">
          <el-input-number
            v-model="editingLocation.range"
            :min="10"
            :max="1000"
            controls-position="right"
          />
          <span style="margin-left: 10px;">米</span>
        </el-form-item>
        
        <el-form-item label="设为默认">
          <el-switch v-model="editingLocation.is_default" />
        </el-form-item>
        
        <el-form-item label="状态">
          <el-radio-group v-model="editingLocation.status">
            <el-radio label="active">启用</el-radio>
            <el-radio label="inactive">禁用</el-radio>
          </el-radio-group>
        </el-form-item>
      </el-form>
      
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="locationDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="saveLocation" :loading="locationSaving">保存</el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Check,
  Refresh,
  Plus,
  Delete,
  Switch,
  LocationInformation
} from '@element-plus/icons-vue'
import systemConfigService, { type SystemConfig, CONFIG_TYPES } from '@/services/systemConfig'
import locationService from '@/services/location'

// 响应式数据
const saving = ref(false)
const testing = ref(false)
const cleaning = ref(false)
const clearing = ref(false)
const restarting = ref(false)
const loading = ref(false)
const locationSaving = ref(false)
const locationDialogVisible = ref(false)

// 上传请求头
const uploadHeaders = ref({
  'Authorization': `Bearer ${localStorage.getItem('access_token') || ''}`
})

// 动态更新上传请求头
const updateUploadHeaders = () => {
  uploadHeaders.value = {
    'Authorization': `Bearer ${localStorage.getItem('access_token') || ''}`
  }
}

// 配置映射对象，用于存储从API获取的配置
const configMap = ref<Map<string, SystemConfig>>(new Map())

const normalizeBoolean = (value: any): boolean => {
  if (typeof value === 'boolean') return value
  if (value === null || value === undefined) return false
  const normalized = String(value).trim().toLowerCase()
  return normalized === 'true' || normalized === '1' || normalized === 'yes'
}

// 缺省需要存在的配置项（避免因数据库未初始化导致开关无效）
const requiredConfigs = [
  { key: 'enable_location', config_type: 'attendance', description: '启用地理位置', value: 'false' },
  { key: 'location_range', config_type: 'attendance', description: '打卡范围(米)', value: '200' },
  { key: 'enable_face_recognition', config_type: 'attendance', description: '启用人脸识别', value: 'false' },
]

// 基础配置
const basicConfig = reactive({
  systemName: '',
  companyName: '',
  version: '',
  logoUrl: '',
  description: '',
  contactPhone: '',
  systemUrl: ''
})

// 考勤配置
const attendanceConfig = reactive({
  startTime: '',
  endTime: '',
  lunchStartTime: '',
  lunchEndTime: '',
  lateThreshold: 15,
  earlyLeaveThreshold: 30,
  workDays: ['1', '2', '3', '4', '5'],
  enableLocation: true,
  locationRange: 200,
  enableFaceRecognition: false
})

// 通知配置
const notificationConfig = reactive({
  enableEmail: true,
  enableSMS: false,
  enableInApp: true,
  attendanceAlert: true,
  leaveApprovalAlert: true,
  salaryAlert: true,
  birthdayReminder: true,
  contractExpireReminder: true,
  reminderDays: 7
})

// 系统维护配置
const maintenanceConfig = reactive({
  isMaintenanceMode: false,
  maintenanceMessage: '',
  estimatedRecoveryTime: '',
  dataRetentionDays: 365
})

// 公司地址列表
const companyLocations = ref<Array<{
  id: number
  name: string
  address: string
  latitude: string
  longitude: string
  range: number
  is_default: boolean
  status: string
}>>([])

// 加载公司地址列表
const loadCompanyLocations = async () => {
  try {
    console.log('开始加载公司地址列表...')
    const result = await locationService.getCompanyLocations()
    console.log('API响应结果:', result)
    
    if (result.success && result.data) {
      console.log('原始数据:', result.data)
      companyLocations.value = result.data.map(location => ({
        id: location.id,
        name: location.name,
        address: location.address,
        latitude: location.latitude.toString(),
        longitude: location.longitude.toString(),
        range: location.radius,
        is_default: false, // 这个字段在后端模型中不存在，可以后续添加
        status: location.is_active ? 'active' : 'inactive'
      }))
      console.log('转换后的数据:', companyLocations.value)
      ElMessage.success(`成功加载 ${companyLocations.value.length} 个地址`)
    } else {
      console.warn('API返回数据格式异常:', result)
      ElMessage.warning('加载地址数据格式异常')
    }
  } catch (error) {
    console.error('加载公司地址失败:', error)
    ElMessage.error('加载公司地址失败')
  }
}

// 编辑中的地址
const editingLocation = reactive({
  id: null as number | null,
  name: '',
  address: '',
  latitude: '',
  longitude: '',
  range: 200,
  is_default: false,
  status: 'active'
})

// 加载配置数据
const loadConfigs = async () => {
  try {
    console.log('🔥 开始加载系统配置...')
    loading.value = true
    const configs = await systemConfigService.getAllConfigs()
    console.log('🔥 获取到的配置:', configs)
    console.log('🔥 配置数量:', configs.length)

    // 若数据库缺少关键配置项（如启用地理位置/人脸识别），先补全再重新加载
    const created = await ensureRequiredConfigs(configs)
    if (created) {
      console.log('🔥 已补全缺失的配置，重新加载一次...')
      return await loadConfigs()
    }
    
    // 将配置存储到映射对象中
    configMap.value.clear()
    configs.forEach(config => {
      configMap.value.set(config.key, config)
    })
    console.log('🔥 配置映射对象:', configMap.value)
    
    // 映射配置到前端数据结构
    mapConfigsToFrontend(configs)
    console.log('🔥 映射后的基础配置:', basicConfig)
    console.log('🔥 映射后的考勤配置:', attendanceConfig)
    
  } catch (error: any) {
    console.error('🔥 加载配置失败:', error)
    console.error('🔥 错误详情:', error.response)
    ElMessage.error('加载配置失败')
  } finally {
    loading.value = false
  }
}

// 确保关键配置存在，若缺失则创建默认值
const ensureRequiredConfigs = async (configs: SystemConfig[]): Promise<boolean> => {
  const existingKeys = new Set(configs.map(c => c.key))
  const missing = requiredConfigs.filter(cfg => !existingKeys.has(cfg.key))
  if (missing.length === 0) return false

  console.warn('检测到缺失配置项，准备创建:', missing.map(m => m.key))
  await Promise.all(missing.map(cfg => systemConfigService.createConfig(cfg)))
  return true
}

// 将API配置映射到前端数据结构
const mapConfigsToFrontend = (configs: SystemConfig[]) => {
  configs.forEach(config => {
    const value = config.json_value || config.value
    
    switch (config.key) {
      // 基础配置
      case 'system_name':
        basicConfig.systemName = value
        break
      case 'company_name':
        basicConfig.companyName = value
        break
      case 'system_version':
        basicConfig.version = value
        break
      case 'company_logo':
        basicConfig.logoUrl = value
        break
      case 'system_description':
        basicConfig.description = value
        break
      case 'contact_phone':
        basicConfig.contactPhone = value
        break
      case 'system_url':
        basicConfig.systemUrl = value
        break
      
      // 考勤配置
      case 'work_start_time':
        attendanceConfig.startTime = value
        break
      case 'work_end_time':
        attendanceConfig.endTime = value
        break
      case 'lunch_start_time':
        attendanceConfig.lunchStartTime = value
        break
      case 'lunch_end_time':
        attendanceConfig.lunchEndTime = value
        break
      case 'late_threshold':
        attendanceConfig.lateThreshold = parseInt(value) || 15
        break
      case 'early_leave_threshold':
        attendanceConfig.earlyLeaveThreshold = parseInt(value) || 30
        break
      case 'work_days':
        attendanceConfig.workDays = value ? value.split(',') : ['1', '2', '3', '4', '5']
        break
      case 'enable_location':
        attendanceConfig.enableLocation = normalizeBoolean(value)
        break
      case 'location_range':
        attendanceConfig.locationRange = parseInt(value) || 200
        break
      case 'enable_face_recognition':
        attendanceConfig.enableFaceRecognition = normalizeBoolean(value)
        break
      
      // 通知配置
      case 'notification_enabled':
      case 'inapp_notification':
        notificationConfig.enableInApp = normalizeBoolean(value)
        break
      case 'email_notification':
        notificationConfig.enableEmail = normalizeBoolean(value)
        break
      case 'sms_notification':
        notificationConfig.enableSMS = normalizeBoolean(value)
        break
      case 'attendance_alert':
        notificationConfig.attendanceAlert = normalizeBoolean(value)
        break
      case 'leave_approval_alert':
        notificationConfig.leaveApprovalAlert = normalizeBoolean(value)
        break
      case 'salary_alert':
        notificationConfig.salaryAlert = normalizeBoolean(value)
        break
      case 'birthday_reminder':
        notificationConfig.birthdayReminder = normalizeBoolean(value)
        break
      case 'contract_expire_reminder':
        notificationConfig.contractExpireReminder = normalizeBoolean(value)
        break
      case 'reminder_days':
        notificationConfig.reminderDays = parseInt(value) || 7
        break
      
      // 系统维护
      case 'maintenance_mode':
        maintenanceConfig.isMaintenanceMode = normalizeBoolean(value)
        break
      case 'maintenance_message':
        maintenanceConfig.maintenanceMessage = value
        break
      case 'estimated_recovery_time':
        maintenanceConfig.estimatedRecoveryTime = value
        break
      case 'data_retention_days':
        maintenanceConfig.dataRetentionDays = parseInt(value) || 365
        break
    }
  })
}

// 将前端数据映射回API格式
const mapFrontendToConfigs = () => {
  const updates: Array<{ id: number; [key: string]: any }> = []
  
  // 基础配置映射
  const systemNameConfig = configMap.value.get('system_name')
  if (systemNameConfig) {
    updates.push({ id: systemNameConfig.id, value: basicConfig.systemName })
  }
  
  const companyNameConfig = configMap.value.get('company_name')
  if (companyNameConfig) {
    updates.push({ id: companyNameConfig.id, value: basicConfig.companyName })
  }
  
  const systemVersionConfig = configMap.value.get('system_version')
  if (systemVersionConfig) {
    updates.push({ id: systemVersionConfig.id, value: basicConfig.version })
  }
  
  const companyLogoConfig = configMap.value.get('company_logo')
  if (companyLogoConfig) {
    updates.push({ id: companyLogoConfig.id, value: basicConfig.logoUrl })
  }
  
  const systemDescriptionConfig = configMap.value.get('system_description')
  if (systemDescriptionConfig) {
    updates.push({ id: systemDescriptionConfig.id, value: basicConfig.description })
  }
  
  const contactPhoneConfig = configMap.value.get('contact_phone')
  if (contactPhoneConfig) {
    updates.push({ id: contactPhoneConfig.id, value: basicConfig.contactPhone })
  }
  
  const systemUrlConfig = configMap.value.get('system_url')
  if (systemUrlConfig) {
    updates.push({ id: systemUrlConfig.id, value: basicConfig.systemUrl })
  }
  
  // 考勤配置映射
  const workStartConfig = configMap.value.get('work_start_time')
  if (workStartConfig) {
    updates.push({ id: workStartConfig.id, value: attendanceConfig.startTime })
  }
  
  const workEndConfig = configMap.value.get('work_end_time')
  if (workEndConfig) {
    updates.push({ id: workEndConfig.id, value: attendanceConfig.endTime })
  }
  
  const lunchStartConfig = configMap.value.get('lunch_start_time')
  if (lunchStartConfig) {
    updates.push({ id: lunchStartConfig.id, value: attendanceConfig.lunchStartTime })
  }
  
  const lunchEndConfig = configMap.value.get('lunch_end_time')
  if (lunchEndConfig) {
    updates.push({ id: lunchEndConfig.id, value: attendanceConfig.lunchEndTime })
  }
  
  const lateThresholdConfig = configMap.value.get('late_threshold')
  if (lateThresholdConfig) {
    updates.push({ id: lateThresholdConfig.id, value: attendanceConfig.lateThreshold.toString() })
  }
  
  const earlyLeaveThresholdConfig = configMap.value.get('early_leave_threshold')
  if (earlyLeaveThresholdConfig) {
    updates.push({ id: earlyLeaveThresholdConfig.id, value: attendanceConfig.earlyLeaveThreshold.toString() })
  }
  
  const workDaysConfig = configMap.value.get('work_days')
  if (workDaysConfig) {
    updates.push({ id: workDaysConfig.id, value: attendanceConfig.workDays.join(',') })
  }
  
  const enableLocationConfig = configMap.value.get('enable_location')
  if (enableLocationConfig) {
    updates.push({ id: enableLocationConfig.id, value: attendanceConfig.enableLocation.toString() })
  }
  
  const locationRangeConfig = configMap.value.get('location_range')
  if (locationRangeConfig) {
    updates.push({ id: locationRangeConfig.id, value: attendanceConfig.locationRange.toString() })
  }
  
  const enableFaceRecognitionConfig = configMap.value.get('enable_face_recognition')
  if (enableFaceRecognitionConfig) {
    updates.push({ id: enableFaceRecognitionConfig.id, value: attendanceConfig.enableFaceRecognition.toString() })
  }
  
  // 通知配置映射
  const inappNotificationConfig = configMap.value.get('inapp_notification')
  if (inappNotificationConfig) {
    updates.push({ id: inappNotificationConfig.id, value: notificationConfig.enableInApp.toString() })
  }
  
  const emailNotificationConfig = configMap.value.get('email_notification')
  if (emailNotificationConfig) {
    updates.push({ id: emailNotificationConfig.id, value: notificationConfig.enableEmail.toString() })
  }
  
  const smsNotificationConfig = configMap.value.get('sms_notification')
  if (smsNotificationConfig) {
    updates.push({ id: smsNotificationConfig.id, value: notificationConfig.enableSMS.toString() })
  }
  
  const attendanceAlertConfig = configMap.value.get('attendance_alert')
  if (attendanceAlertConfig) {
    updates.push({ id: attendanceAlertConfig.id, value: notificationConfig.attendanceAlert.toString() })
  }
  
  const leaveApprovalAlertConfig = configMap.value.get('leave_approval_alert')
  if (leaveApprovalAlertConfig) {
    updates.push({ id: leaveApprovalAlertConfig.id, value: notificationConfig.leaveApprovalAlert.toString() })
  }
  
  const salaryAlertConfig = configMap.value.get('salary_alert')
  if (salaryAlertConfig) {
    updates.push({ id: salaryAlertConfig.id, value: notificationConfig.salaryAlert.toString() })
  }
  
  const birthdayReminderConfig = configMap.value.get('birthday_reminder')
  if (birthdayReminderConfig) {
    updates.push({ id: birthdayReminderConfig.id, value: notificationConfig.birthdayReminder.toString() })
  }
  
  const contractExpireReminderConfig = configMap.value.get('contract_expire_reminder')
  if (contractExpireReminderConfig) {
    updates.push({ id: contractExpireReminderConfig.id, value: notificationConfig.contractExpireReminder.toString() })
  }
  
  const reminderDaysConfig = configMap.value.get('reminder_days')
  if (reminderDaysConfig) {
    updates.push({ id: reminderDaysConfig.id, value: notificationConfig.reminderDays.toString() })
  }
  
  // 系统维护映射
  const maintenanceModeConfig = configMap.value.get('maintenance_mode')
  if (maintenanceModeConfig) {
    updates.push({ id: maintenanceModeConfig.id, value: maintenanceConfig.isMaintenanceMode.toString() })
  }
  
  const maintenanceMessageConfig = configMap.value.get('maintenance_message')
  if (maintenanceMessageConfig) {
    updates.push({ id: maintenanceMessageConfig.id, value: maintenanceConfig.maintenanceMessage })
  }
  
  const estimatedRecoveryTimeConfig = configMap.value.get('estimated_recovery_time')
  if (estimatedRecoveryTimeConfig) {
    updates.push({ id: estimatedRecoveryTimeConfig.id, value: maintenanceConfig.estimatedRecoveryTime })
  }
  
  const dataRetentionDaysConfig = configMap.value.get('data_retention_days')
  if (dataRetentionDaysConfig) {
    updates.push({ id: dataRetentionDaysConfig.id, value: maintenanceConfig.dataRetentionDays.toString() })
  }
  
  return updates
}

// 保存所有配置
const saveAllConfigs = async () => {
  try {
    console.log('🔥 开始保存配置...')
    saving.value = true
    const updates = mapFrontendToConfigs()
    console.log('🔥 准备更新的配置:', updates)
    
    if (updates.length > 0) {
      console.log('🔥 调用批量更新API...')
      const result = await systemConfigService.batchUpdateConfigs({ configs: updates })
      console.log('🔥 API响应:', result)
      ElMessage.success(result.message || '配置保存成功')
      
      // 重新加载配置
      await loadConfigs()
    } else {
      console.log('🔥 没有需要保存的更改')
      ElMessage.warning('没有需要保存的配置更改')
    }
  } catch (error: any) {
    console.error('🔥 保存配置失败:', error)
    console.error('🔥 错误详情:', error.response)
    ElMessage.error('保存配置失败')
  } finally {
    saving.value = false
  }
}

// 重置配置
const resetConfigs = async () => {
  try {
    await ElMessageBox.confirm(
      '确定要重置所有配置到默认值吗？此操作不可撤销！',
      '重置确认',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    // 重新加载配置
    await loadConfigs()
    ElMessage.success('配置已重置')
  } catch {
    // 用户取消
  }
}

// Logo上传处理
const handleLogoSuccess = (response: any, file: any) => {
  console.log('上传响应:', response)
  console.log('文件信息:', file)
  
  if (response && response.url) {
    basicConfig.logoUrl = response.url
    ElMessage.success('Logo上传成功')
  } else if (response && response.logo_url) {
    basicConfig.logoUrl = response.logo_url
    ElMessage.success('Logo上传成功')
  } else if (response && typeof response === 'string') {
    // 如果响应是字符串，可能是URL
    basicConfig.logoUrl = response
    ElMessage.success('Logo上传成功')
  } else {
    console.error('上传响应格式异常:', response)
    ElMessage.error('Logo上传失败：服务器响应格式错误')
  }
}

// 上传失败处理
const handleLogoError = (error: any) => {
  console.error('Logo上传失败:', error)
  
  let errorMessage = 'Logo上传失败，请重试'
  
  // 尝试解析错误信息
  if (error && error.message) {
    try {
      // 检查是否是JSON格式的错误信息
      const errorData = JSON.parse(error.message)
      if (errorData.error) {
        errorMessage = `上传失败：${errorData.error}`
      }
    } catch (e) {
      // 如果不是JSON格式，直接使用错误信息
      errorMessage = `上传失败：${error.message}`
    }
  } else if (error && error.response && error.response.data) {
    // 处理axios错误响应
    if (error.response.data.error) {
      errorMessage = `上传失败：${error.response.data.error}`
    } else if (typeof error.response.data === 'string') {
      errorMessage = `上传失败：${error.response.data}`
    }
  }
  
  ElMessage.error(errorMessage)
}

// 上传进度处理
const handleLogoProgress = (event: any, file: any, fileList: any) => {
  console.log('上传进度:', event.percent + '%')
}

const beforeLogoUpload = (file: any) => {
  console.log('准备上传文件:', file)
  console.log('文件类型:', file.type)
  console.log('文件大小:', file.size)
  
  // 与后端保持一致，只支持 JPG, PNG, GIF 格式
  const isValidType = ['image/jpeg', 'image/png', 'image/gif'].includes(file.type)
  const isLt2M = file.size / 1024 / 1024 < 2

  if (!isValidType) {
    ElMessage.error('Logo只能是 JPG、PNG、GIF 格式的图片!')
    return false
  }
  if (!isLt2M) {
    ElMessage.error('Logo大小不能超过 2MB!')
    return false
  }
  
  // 确保认证头是最新的
  updateUploadHeaders()
  console.log('上传头信息:', uploadHeaders.value)
  
  return true
}



// 维护模式变更处理
const handleMaintenanceModeChange = async (value: boolean) => {
  if (value) {
    try {
      await ElMessageBox.confirm(
        '开启维护模式后，普通用户将无法访问系统，确定要开启吗？',
        '维护模式确认',
        {
          confirmButtonText: '确定',
          cancelButtonText: '取消',
          type: 'warning'
        }
      )
      
      ElMessage.warning('维护模式已开启')
    } catch {
      maintenanceConfig.isMaintenanceMode = false
    }
  } else {
    ElMessage.success('维护模式已关闭')
  }
}

// 清理日志
const cleanLogs = async () => {
  try {
    cleaning.value = true
    
    const result = await systemConfigService.performMaintenance({
      action: 'clear_logs',
      confirm: true
    })
    
    ElMessage.success(result.message || '过期日志清理完成')
  } catch (error: any) {
    console.error('日志清理失败:', error)
    ElMessage.error(error.response?.data?.error || '日志清理失败')
  } finally {
    cleaning.value = false
  }
}

// 清理缓存
const clearCache = async () => {
  try {
    clearing.value = true
    
    const result = await systemConfigService.performMaintenance({
      action: 'clear_cache',
      confirm: true
    })
    
    ElMessage.success(result.message || '系统缓存清理完成')
  } catch (error: any) {
    console.error('缓存清理失败:', error)
    ElMessage.error(error.response?.data?.error || '缓存清理失败')
  } finally {
    clearing.value = false
  }
}

// 显示添加地址对话框
const showAddLocationDialog = () => {
  // 重置编辑表单
  Object.assign(editingLocation, {
    id: null,
    name: '',
    address: '',
    latitude: '',
    longitude: '',
    range: 200,
    is_default: false,
    status: 'active'
  })
  locationDialogVisible.value = true
}

// 编辑地址
const editLocation = (location: any) => {
  Object.assign(editingLocation, { ...location })
  locationDialogVisible.value = true
}

// 获取当前位置
const getCurrentLocation = () => {
  if (!navigator.geolocation) {
    ElMessage.error('浏览器不支持地理定位功能')
    return
  }

  ElMessage.info('正在获取位置信息，请允许浏览器访问您的位置...')

  const options = {
    enableHighAccuracy: false, // 降低精度要求，避免网络请求
    timeout: 15000, // 增加超时时间
    maximumAge: 300000 // 允许使用5分钟内的缓存位置
  }

  navigator.geolocation.getCurrentPosition(
    (position) => {
      editingLocation.latitude = position.coords.latitude.toFixed(6)
      editingLocation.longitude = position.coords.longitude.toFixed(6)
      ElMessage.success(`位置获取成功！精度约 ${Math.round(position.coords.accuracy)} 米`)
    },
    (error) => {
      console.error('获取位置失败:', error)
      
      let errorMessage = '获取位置失败'
      let suggestion = ''
      
      switch (error.code) {
        case error.PERMISSION_DENIED:
          errorMessage = '用户拒绝了地理位置访问请求'
          suggestion = '请在浏览器地址栏左侧点击锁图标，允许位置访问权限。'
          break
        case error.POSITION_UNAVAILABLE:
          errorMessage = '位置信息不可用'
          suggestion = '请检查GPS是否开启，或尝试刷新页面后重试。'
          break
        case error.TIMEOUT:
          errorMessage = '获取位置超时'
          suggestion = '网络较慢或位置服务响应超时，请重试。'
          break
        default:
          errorMessage = '位置服务出现网络错误'
          suggestion = '可能是由于浏览器扩展（如广告拦截器）阻止了位置服务。请尝试禁用相关扩展或手动输入坐标。'
          break
      }
      
      // 显示详细的错误信息和解决方案
      ElMessageBox.alert(
        `<div style="text-align: left;">
          <p><strong>错误原因：</strong>${errorMessage}</p>
          <p><strong>解决方案：</strong>${suggestion}</p>
          <hr style="margin: 15px 0;">
          <p><strong>其他获取坐标的方法：</strong></p>
          <ol>
            <li><strong>使用在线地图：</strong>
              <ul>
                <li>百度地图：搜索地址 → 右键点击 → "这里是哪里"</li>
                <li>高德地图：搜索地址 → 右键选择 → "这里是哪"</li>
                <li>腾讯地图：搜索地址 → 右键选择 → "在这里"</li>
              </ul>
            </li>
            <li><strong>GPS坐标拾取工具：</strong>搜索"GPS坐标拾取"使用在线工具</li>
            <li><strong>手机GPS：</strong>使用手机地图应用获取当前位置坐标</li>
          </ol>
          <p style="color: #E6A23C; margin-top: 15px;">
            <strong>提示：</strong>如果经常遇到此问题，建议将常用地址的坐标保存备用。
          </p>
        </div>`,
        '位置获取失败',
        {
          dangerouslyUseHTMLString: true,
          confirmButtonText: '知道了',
          type: 'warning'
        }
      )
      
      ElMessage.error('位置获取失败，请手动输入坐标或参考帮助信息')
    },
    options
  )
}

// 显示坐标帮助
const showCoordinateHelp = () => {
  ElMessageBox.alert(
    `<div style="text-align: left;">
      <h4>如何获取地理坐标？</h4>
      <p><strong>方法一：在线地图工具</strong></p>
      <ul>
        <li>百度地图：搜索地址后右键点击"这里是哪里"</li>
        <li>高德地图：搜索地址后右键选择"这里是哪"</li>
        <li>腾讯地图：搜索地址后右键选择"在这里"</li>
      </ul>
      <p><strong>方法二：GPS坐标转换</strong></p>
      <ul>
        <li>使用GPS坐标拾取工具网站</li>
        <li>输入详细地址自动获取坐标</li>
      </ul>
      <p><strong>坐标格式示例：</strong></p>
      <ul>
        <li>北京天安门：纬度 39.908823，经度 116.399010</li>
        <li>上海外滩：纬度 31.235929，经度 121.481892</li>
      </ul>
      <p style="color: #E6A23C;">注意：请确保坐标准确，这将影响员工打卡范围判断。</p>
    </div>`,
    '坐标获取帮助',
    {
      dangerouslyUseHTMLString: true,
      confirmButtonText: '知道了'
    }
  )
}

// 显示常用城市坐标
const showCommonLocations = () => {
  const commonCities = [
    { name: '北京市中心（天安门）', lat: '39.908823', lng: '116.399010' },
    { name: '上海市中心（人民广场）', lat: '31.231761', lng: '121.472718' },
    { name: '广州市中心（越秀区）', lat: '23.129142', lng: '113.264434' },
    { name: '深圳市中心（福田区）', lat: '22.526887', lng: '114.059196' },
    { name: '杭州市中心（西湖区）', lat: '30.274085', lng: '120.155070' },
    { name: '南京市中心（玄武区）', lat: '32.042982', lng: '118.778074' },
    { name: '成都市中心（锦江区）', lat: '30.659462', lng: '104.065735' },
    { name: '武汉市中心（江汉区）', lat: '30.581084', lng: '114.311494' },
    { name: '西安市中心（雁塔区）', lat: '34.341568', lng: '108.940174' },
    { name: '重庆市中心（渝中区）', lat: '29.559751', lng: '106.570071' }
  ]
  
  const cityOptions = commonCities.map(city => 
    `<div style="cursor: pointer; padding: 8px; border-radius: 4px; margin: 2px 0; border: 1px solid #ddd;" onclick="selectCity('${city.lat}', '${city.lng}')">
      <strong>${city.name}</strong><br>
      <small style="color: #666;">纬度: ${city.lat}, 经度: ${city.lng}</small>
    </div>`
  ).join('')
  
  // 创建全局函数用于选择城市
  ;(window as any).selectCity = (lat: string, lng: string) => {
    editingLocation.latitude = lat
    editingLocation.longitude = lng
    ElMessage.success('坐标已填入，您可以根据实际位置进行微调')
    // 关闭消息框
    const messageBox = document.querySelector('.el-message-box')
    if (messageBox) {
      const closeBtn = messageBox.querySelector('.el-message-box__headerbtn') as HTMLElement
      if (closeBtn) closeBtn.click()
    }
  }
  
  ElMessageBox.alert(
    `<div style="text-align: left; max-height: 400px; overflow-y: auto;">
      <h4 style="margin-top: 0;">选择常用城市坐标</h4>
      <p style="color: #E6A23C; margin-bottom: 15px;">
        <strong>提示：</strong>以下为各城市中心区域坐标，请根据实际办公地址进行调整
      </p>
      ${cityOptions}
      <div style="margin-top: 15px; padding: 10px; background: #f5f7fa; border-radius: 4px;">
        <small style="color: #606266;">
          <strong>使用说明：</strong><br>
          1. 点击城市名称快速填入坐标<br>
          2. 建议使用地图工具获取精确坐标<br>
          3. 坐标精度直接影响打卡范围判断
        </small>
      </div>
    </div>`,
    '常用城市坐标',
    {
      dangerouslyUseHTMLString: true,
      confirmButtonText: '关闭'
    }
  ).finally(() => {
    // 清理全局函数
    delete (window as any).selectCity
  })
}

// 保存地址
const saveLocation = async () => {
  try {
    if (!editingLocation.name || !editingLocation.address) {
      ElMessage.error('请填写地点名称和详细地址')
      return
    }
    
    locationSaving.value = true
    
    if (editingLocation.id) {
      // 编辑现有地点
      const result = await locationService.updateCompanyLocation(editingLocation.id, {
        name: editingLocation.name,
        address: editingLocation.address,
        latitude: parseFloat(editingLocation.latitude),
        longitude: parseFloat(editingLocation.longitude),
        radius: editingLocation.range,
        description: '',
        is_active: editingLocation.status === 'active'
      })
      
      if (result.success) {
        const index = companyLocations.value.findIndex(item => item.id === editingLocation.id)
        if (index !== -1) {
          // 更新前端数据结构
          companyLocations.value[index] = {
            id: result.data.id,
            name: result.data.name,
            address: result.data.address,
            latitude: result.data.latitude.toString(),
            longitude: result.data.longitude.toString(),
            range: result.data.radius,
            is_default: editingLocation.is_default,
            status: result.data.is_active ? 'active' : 'inactive'
          }
        }
        ElMessage.success('地点更新成功')
      }
    } else {
      // 创建新地点
      const result = await locationService.createCompanyLocation({
        name: editingLocation.name,
        address: editingLocation.address,
        latitude: parseFloat(editingLocation.latitude),
        longitude: parseFloat(editingLocation.longitude),
        radius: editingLocation.range,
        description: '',
        is_active: editingLocation.status === 'active'
      })
      
      if (result.success) {
        // 添加到前端数据结构
        companyLocations.value.push({
          id: result.data.id,
          name: result.data.name,
          address: result.data.address,
          latitude: result.data.latitude.toString(),
          longitude: result.data.longitude.toString(),
          range: result.data.radius,
          is_default: false,
          status: result.data.is_active ? 'active' : 'inactive'
        })
        ElMessage.success('地点创建成功')
      }
    }
    
    locationDialogVisible.value = false
    
  } catch (error: any) {
    console.error('保存地址失败:', error)
    ElMessage.error(error.response?.data?.message || '保存地址失败，请检查网络连接')
  } finally {
    locationSaving.value = false
  }
}

// 设为默认地址
const setDefaultLocation = async (location: any) => {
  try {
    // 取消所有默认地址
    companyLocations.value.forEach(item => {
      item.is_default = false
    })
    
    // 设置当前地址为默认
    location.is_default = true
    
    ElMessage.success('默认地址设置成功')
  } catch (error) {
    console.error('设置默认地址失败:', error)
    ElMessage.error('设置默认地址失败')
  }
}

// 删除地址
const deleteLocation = async (location: any) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除地址 "${location.name}" 吗？`,
      '删除确认',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    // 调用后端API删除
    const result = await locationService.deleteCompanyLocation(location.id)
    if (result.success) {
      const index = companyLocations.value.findIndex(item => item.id === location.id)
      if (index !== -1) {
        companyLocations.value.splice(index, 1)
      }
      ElMessage.success('地址删除成功')
    }
  } catch (error: any) {
    if (error !== 'cancel') {
      console.error('删除地址失败:', error)
      ElMessage.error(error.response?.data?.message || '删除地址失败')
    }
  }
}

// 重启系统
const restartSystem = async () => {
  try {
    restarting.value = true
    
    const result = await systemConfigService.performMaintenance({
      action: 'restart_system',
      confirm: true
    })
    
    ElMessage.success(result.message || '系统重启请求已提交')
  } catch (error: any) {
    console.error('系统重启失败:', error)
    ElMessage.error(error.response?.data?.error || '系统重启失败')
  } finally {
    restarting.value = false
  }
}

// 组件挂载时加载配置
onMounted(() => {
  updateUploadHeaders()
  loadConfigs()
  loadCompanyLocations()
})
</script>

<style scoped>
.system-config {
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

.config-card {
  margin-bottom: var(--hr-space-lg);
  height: fit-content;
}

.logo-upload {
  width: 120px;
  height: 120px;
  border: 1px dashed var(--hr-gray-300);
  border-radius: var(--hr-radius-md);
  cursor: pointer;
  position: relative;
  overflow: hidden;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: border-color var(--hr-transition-fast);
}

.logo-upload:hover {
  border-color: var(--hr-primary);
}

.logo-upload-icon {
  font-size: 28px;
  color: var(--color-text-placeholder);
}

.logo-preview {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

:deep(.el-card__header) {
  background-color: var(--hr-gray-50);
  font-weight: 600;
  color: var(--color-text-primary);
}

:deep(.el-form-item__label) {
  font-weight: 500;
}

:deep(.el-checkbox-group) {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

:deep(.el-checkbox-group .el-checkbox) {
  margin-right: 0;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.form-tip {
  margin-top: 8px;
  display: flex;
  align-items: center;
  gap: var(--hr-space-sm);
}

.tip-text {
  color: var(--color-text-secondary);
  font-size: 12px;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: var(--hr-space-sm);
}

.coordinate-info {
  margin-top: 5px;
  padding: 5px 0;
}

.coordinate-info .el-text {
  font-size: 12px;
}
</style>
