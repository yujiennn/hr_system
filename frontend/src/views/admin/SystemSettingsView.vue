<template>
  <div class="system-settings">
    <el-card class="page-header">
      <div class="header-content">
        <h2>系统设置</h2>
        <div class="header-actions">
          <el-button type="primary" @click="saveAllSettings" :loading="saving">
            <el-icon><Check /></el-icon>
            保存所有设置
          </el-button>
        </div>
      </div>
    </el-card>

    <el-row :gutter="20">
      <!-- 基础设置 -->
      <el-col :span="12">
        <el-card>
          <template #header>
            <span>基础设置</span>
          </template>
          
          <el-form :model="basicSettings" label-width="120px">
            <el-form-item label="系统名称">
              <el-input v-model="basicSettings.systemName" placeholder="请输入系统名称" />
            </el-form-item>
            
            <el-form-item label="公司名称">
              <el-input v-model="basicSettings.companyName" placeholder="请输入公司名称" />
            </el-form-item>
            
            <el-form-item label="系统版本">
              <el-input v-model="basicSettings.version" readonly />
            </el-form-item>
            
            <el-form-item label="系统描述">
              <el-input
                v-model="basicSettings.description"
                type="textarea"
                :rows="3"
                placeholder="请输入系统描述"
              />
            </el-form-item>
          </el-form>
        </el-card>
      </el-col>

      <!-- 考勤设置 -->
      <el-col :span="12">
        <el-card>
          <template #header>
            <span>考勤设置</span>
          </template>
          
          <el-form :model="attendanceSettings" label-width="120px">
            <el-form-item label="启用地理位置">
              <el-switch v-model="attendanceSettings.enableLocation" />
            </el-form-item>
            
            <el-form-item label="打卡范围" v-if="attendanceSettings.enableLocation">
              <el-input-number
                v-model="attendanceSettings.locationRange"
                :min="10"
                :max="1000"
                controls-position="right"
                style="width: 100%"
              />
              <span class="form-text">米</span>
            </el-form-item>
            
            <el-form-item label="启用人脸识别">
              <el-switch v-model="attendanceSettings.enableFaceRecognition" />
            </el-form-item>
            
            <el-form-item label="迟到阈值">
              <el-input-number
                v-model="attendanceSettings.lateThreshold"
                :min="1"
                :max="60"
                controls-position="right"
                style="width: 100%"
              />
              <span class="form-text">分钟</span>
            </el-form-item>
          </el-form>
        </el-card>
      </el-col>
    </el-row>

    <!-- 公司地址管理 -->
    <el-card style="margin-top: 20px;">
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

    <!-- 安全设置 -->
    <el-card style="margin-top: 20px;">
      <template #header>
        <span>安全设置</span>
      </template>
      
      <el-form :model="securitySettings" label-width="120px">
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="密码过期天数">
              <el-input-number
                v-model="securitySettings.passwordExpireDays"
                :min="0"
                :max="365"
                controls-position="right"
                style="width: 100%"
              />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="登录超时时间">
              <el-input-number
                v-model="securitySettings.sessionTimeout"
                :min="30"
                :max="1440"
                controls-position="right"
                style="width: 100%"
              />
              <span class="form-text">分钟</span>
            </el-form-item>
          </el-col>
        </el-row>
        
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="允许多设备登录">
              <el-switch v-model="securitySettings.allowMultipleLogin" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="启用验证码">
              <el-switch v-model="securitySettings.enableCaptcha" />
            </el-form-item>
          </el-col>
        </el-row>
      </el-form>
    </el-card>

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
              <el-input v-model="editingLocation.latitude" placeholder="纬度" />
            </el-col>
            <el-col :span="12">
              <el-input v-model="editingLocation.longitude" placeholder="经度" />
            </el-col>
          </el-row>
          <div class="form-tip">
            <el-button size="small" type="primary" @click="getCurrentLocation">获取当前位置</el-button>
            <span class="tip-text">或手动输入经纬度坐标</span>
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
import { Check, LocationInformation, Plus } from '@element-plus/icons-vue'

// 响应式数据
const saving = ref(false)
const locationSaving = ref(false)
const locationDialogVisible = ref(false)

// 基础设置
const basicSettings = reactive({
  systemName: 'HR管理系统',
  companyName: '示例公司',
  version: '1.0.0',
  description: '一个现代化的人力资源管理系统，提供员工管理、考勤管理、绩效评估等功能。'
})

// 考勤设置
const attendanceSettings = reactive({
  enableLocation: true,
  locationRange: 200,
  enableFaceRecognition: false,
  lateThreshold: 15
})

// 安全设置
const securitySettings = reactive({
  passwordExpireDays: 90,
  sessionTimeout: 120,
  allowMultipleLogin: true,
  enableCaptcha: false
})

// 公司地址列表
const companyLocations = ref([
  {
    id: 1,
    name: '总部大楼',
    address: '北京市朝阳区建国门外大街1号',
    latitude: '39.908823',
    longitude: '116.399010',
    range: 200,
    is_default: true,
    status: 'active'
  },
  {
    id: 2,
    name: '研发中心',
    address: '北京市海淀区中关村大街27号',
    latitude: '39.991840',
    longitude: '116.314020',
    range: 150,
    is_default: false,
    status: 'active'
  }
])

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

// 保存所有设置
const saveAllSettings = async () => {
  try {
    saving.value = true
    
    // 模拟保存设置
    await new Promise(resolve => setTimeout(resolve, 1000))
    
    ElMessage.success('系统设置保存成功')
  } catch (error) {
    console.error('保存设置失败:', error)
    ElMessage.error('保存设置失败')
  } finally {
    saving.value = false
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
  if (navigator.geolocation) {
    navigator.geolocation.getCurrentPosition(
      (position) => {
        editingLocation.latitude = position.coords.latitude.toString()
        editingLocation.longitude = position.coords.longitude.toString()
        ElMessage.success('位置获取成功')
      },
      (error) => {
        console.error('获取位置失败:', error)
        ElMessage.error('获取位置失败，请手动输入坐标')
      }
    )
  } else {
    ElMessage.error('浏览器不支持地理定位')
  }
}

// 保存地址
const saveLocation = async () => {
  try {
    if (!editingLocation.name || !editingLocation.address) {
      ElMessage.error('请填写地点名称和详细地址')
      return
    }
    
    locationSaving.value = true
    
    // 模拟保存
    await new Promise(resolve => setTimeout(resolve, 1000))
    
    if (editingLocation.id) {
      // 编辑
      const index = companyLocations.value.findIndex(item => item.id === editingLocation.id)
      if (index !== -1) {
        companyLocations.value[index] = { 
          ...editingLocation,
          id: editingLocation.id as number 
        }
      }
    } else {
      // 新增
      const newLocation = {
        ...editingLocation,
        id: Date.now() // 临时ID
      }
      companyLocations.value.push(newLocation)
    }
    
    // 如果设为默认，取消其他默认地址
    if (editingLocation.is_default) {
      companyLocations.value.forEach(item => {
        if (item.id !== editingLocation.id) {
          item.is_default = false
        }
      })
    }
    
    ElMessage.success('地址保存成功')
    locationDialogVisible.value = false
  } catch (error) {
    console.error('保存地址失败:', error)
    ElMessage.error('保存地址失败')
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
    
    const index = companyLocations.value.findIndex(item => item.id === location.id)
    if (index !== -1) {
      companyLocations.value.splice(index, 1)
      ElMessage.success('地址删除成功')
    }
  } catch {
    // 用户取消删除
  }
}

// 加载设置
const loadSettings = async () => {
  try {
    // 模拟加载设置
    console.log('加载系统设置...')
  } catch (error) {
    console.error('加载设置失败:', error)
    ElMessage.error('加载设置失败')
  }
}

onMounted(() => {
  loadSettings()
})
</script>

<style scoped>
.system-settings {
  padding: var(--hr-space-lg);
}

.page-header .header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.page-header .header-content h2 {
  margin: 0;
  font-size: 22px;
  color: var(--color-text-primary);
  font-weight: 700;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.form-text {
  color: var(--color-text-secondary);
  font-size: 12px;
  margin-left: 10px;
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

:deep(.el-card__header) {
  background-color: var(--hr-gray-50);
  font-weight: 600;
  color: var(--color-text-primary);
}

:deep(.el-form-item__label) {
  font-weight: 500;
}

:deep(.el-table) {
  margin-top: 10px;
}

:deep(.el-dialog__header) {
  background-color: var(--hr-gray-50);
  padding: 20px 20px 10px;
}

:deep(.el-dialog__title) {
  font-weight: 600;
  color: var(--color-text-primary);
}
</style>
