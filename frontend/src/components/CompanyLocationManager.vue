<template>
  <div class="company-locations">
    <el-card class="location-card" shadow="hover">
      <template #header>
        <div class="card-header">
          <h2>
            <el-icon><LocationInformation /></el-icon>
            公司位置管理
          </h2>
          <el-text type="info">设置员工可以进行位置打卡的公司地址</el-text>
        </div>
      </template>

      <div class="location-content">
        <!-- 操作按钮 -->
        <div class="action-buttons">
          <el-button
            type="primary"
            @click="showAddDialog = true"
            :disabled="!canManage"
          >
            <el-icon><Plus /></el-icon>
            添加位置
          </el-button>
          <el-button
            type="info"
            @click="loadLocations"
            :loading="loading"
          >
            <el-icon><Refresh /></el-icon>
            刷新
          </el-button>
        </div>

        <!-- 位置列表 -->
        <div class="locations-list">
          <el-table
            :data="locations"
            v-loading="loading"
            stripe
            style="width: 100%"
          >
            <el-table-column prop="name" label="位置名称" width="150" />
            <el-table-column prop="address" label="详细地址" min-width="200" />
            <el-table-column label="坐标" width="160">
              <template #default="{ row }">
                <div class="coordinates">
                  <div>纬度: {{ row.latitude.toFixed(6) }}</div>
                  <div>经度: {{ row.longitude.toFixed(6) }}</div>
                </div>
              </template>
            </el-table-column>
            <el-table-column prop="radius" label="打卡范围" width="100">
              <template #default="{ row }">
                <el-tag type="info">{{ row.radius }}米</el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="is_active" label="状态" width="80">
              <template #default="{ row }">
                <el-tag :type="row.is_active ? 'success' : 'danger'">
                  {{ row.is_active ? '启用' : '禁用' }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="created_at" label="创建时间" width="150">
              <template #default="{ row }">
                {{ formatTime(row.created_at) }}
              </template>
            </el-table-column>
            <el-table-column label="操作" width="150" v-if="canManage">
              <template #default="{ row }">
                <el-button
                  type="primary"
                  size="small"
                  @click="editLocation(row)"
                >
                  编辑
                </el-button>
                <el-button
                  type="danger"
                  size="small"
                  @click="deleteLocation(row)"
                >
                  删除
                </el-button>
              </template>
            </el-table-column>
          </el-table>
        </div>

        <!-- 空状态 -->
        <el-empty
          v-if="!loading && locations.length === 0"
          description="暂无公司位置配置"
        >
          <el-button
            type="primary"
            @click="showAddDialog = true"
            v-if="canManage"
          >
            添加第一个位置
          </el-button>
        </el-empty>
      </div>
    </el-card>

    <!-- 添加/编辑位置对话框 -->
    <el-dialog
      v-model="showAddDialog"
      :title="editingLocation ? '编辑位置' : '添加位置'"
      width="600px"
      :close-on-click-modal="false"
    >
      <el-form
        ref="locationFormRef"
        :model="locationForm"
        :rules="locationRules"
        label-width="100px"
      >
        <el-form-item label="位置名称" prop="name">
          <el-input
            v-model="locationForm.name"
            placeholder="请输入位置名称，如：总部大厦"
          />
        </el-form-item>
        
        <el-form-item label="详细地址" prop="address">
          <el-input
            v-model="locationForm.address"
            type="textarea"
            :rows="2"
            placeholder="请输入详细地址"
          />
        </el-form-item>
        
        <el-form-item label="纬度" prop="latitude">
          <el-input-number
            v-model="locationForm.latitude"
            :precision="6"
            :step="0.000001"
            :min="-90"
            :max="90"
            placeholder="纬度"
            style="width: 100%"
          />
        </el-form-item>
        
        <el-form-item label="经度" prop="longitude">
          <el-input-number
            v-model="locationForm.longitude"
            :precision="6"
            :step="0.000001"
            :min="-180"
            :max="180"
            placeholder="经度"
            style="width: 100%"
          />
        </el-form-item>
        
        <el-form-item label="打卡范围" prop="radius">
          <el-input-number
            v-model="locationForm.radius"
            :min="10"
            :max="1000"
            :step="10"
            placeholder="打卡范围（米）"
            style="width: 100%"
          />
          <el-text type="info" size="small">
            员工在此范围内可以进行位置打卡
          </el-text>
        </el-form-item>
        
        <el-form-item label="位置描述" prop="description">
          <el-input
            v-model="locationForm.description"
            type="textarea"
            :rows="2"
            placeholder="位置描述（可选）"
          />
        </el-form-item>
        
        <el-form-item label="状态" prop="is_active">
          <el-switch
            v-model="locationForm.is_active"
            active-text="启用"
            inactive-text="禁用"
          />
        </el-form-item>
      </el-form>
      
      <template #footer>
        <el-button @click="cancelEdit">取消</el-button>
        <el-button type="primary" @click="saveLocation" :loading="saving">
          {{ editingLocation ? '保存' : '添加' }}
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, computed } from 'vue'
import { ElMessage, ElMessageBox, type FormInstance, type FormRules } from 'element-plus'
import { LocationInformation, Plus, Refresh } from '@element-plus/icons-vue'
import api from '@/utils/api'
import { useUserStore } from '@/stores/counter'

// 类型定义
interface CompanyLocation {
  id?: number
  name: string
  address: string
  latitude: number
  longitude: number
  radius: number
  description: string
  is_active: boolean
  created_at?: string
}

// 状态管理
const userStore = useUserStore()
const locations = ref<CompanyLocation[]>([])
const loading = ref(false)
const saving = ref(false)
const showAddDialog = ref(false)
const editingLocation = ref<CompanyLocation | null>(null)
const locationFormRef = ref<FormInstance>()

// 表单数据
const locationForm = reactive<CompanyLocation>({
  name: '',
  address: '',
  latitude: 0,
  longitude: 0,
  radius: 200,
  description: '',
  is_active: true
})

// 计算属性
const canManage = computed(() => {
  return userStore.user?.user_type === 'admin' || false
})

// 表单验证规则
const locationRules: FormRules = {
  name: [
    { required: true, message: '请输入位置名称', trigger: 'blur' },
    { min: 2, max: 50, message: '位置名称长度在 2 到 50 个字符', trigger: 'blur' }
  ],
  address: [
    { required: true, message: '请输入详细地址', trigger: 'blur' },
    { min: 5, max: 200, message: '地址长度在 5 到 200 个字符', trigger: 'blur' }
  ],
  latitude: [
    { required: true, message: '请输入纬度', trigger: 'blur' },
    { type: 'number', min: -90, max: 90, message: '纬度范围为 -90 到 90', trigger: 'blur' }
  ],
  longitude: [
    { required: true, message: '请输入经度', trigger: 'blur' },
    { type: 'number', min: -180, max: 180, message: '经度范围为 -180 到 180', trigger: 'blur' }
  ],
  radius: [
    { required: true, message: '请设置打卡范围', trigger: 'blur' },
    { type: 'number', min: 10, max: 1000, message: '打卡范围在 10 到 1000 米', trigger: 'blur' }
  ]
}

// 加载位置列表
const loadLocations = async () => {
  try {
    loading.value = true
    const response = await api.get('/system-config/company-locations/')
    locations.value = response.data.results || response.data
  } catch (error: any) {
    console.error('加载位置列表失败:', error)
    ElMessage.error('加载位置列表失败')
  } finally {
    loading.value = false
  }
}

// 编辑位置
const editLocation = (location: CompanyLocation) => {
  editingLocation.value = location
  Object.assign(locationForm, location)
  showAddDialog.value = true
}

// 保存位置
const saveLocation = async () => {
  if (!locationFormRef.value) return
  
  try {
    await locationFormRef.value.validate()
    saving.value = true
    
    if (editingLocation.value) {
      // 更新
      await api.put(`/system-config/company-locations/${editingLocation.value.id}/`, locationForm)
      ElMessage.success('位置更新成功')
    } else {
      // 新增
      await api.post('/system-config/company-locations/', locationForm)
      ElMessage.success('位置添加成功')
    }
    
    showAddDialog.value = false
    await loadLocations()
    
  } catch (error: any) {
    console.error('保存位置失败:', error)
    ElMessage.error(error.response?.data?.detail || '保存失败')
  } finally {
    saving.value = false
  }
}

// 删除位置
const deleteLocation = async (location: CompanyLocation) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除位置"${location.name}"吗？删除后员工将无法在此位置打卡。`,
      '确认删除',
      {
        confirmButtonText: '确定删除',
        cancelButtonText: '取消',
        type: 'error',
      }
    )
    
    await api.delete(`/system-config/company-locations/${location.id}/`)
    ElMessage.success('位置删除成功')
    await loadLocations()
    
  } catch (error: any) {
    if (error !== 'cancel') {
      console.error('删除位置失败:', error)
      ElMessage.error('删除失败')
    }
  }
}

// 取消编辑
const cancelEdit = () => {
  showAddDialog.value = false
  editingLocation.value = null
  locationFormRef.value?.resetFields()
  
  // 重置表单
  Object.assign(locationForm, {
    name: '',
    address: '',
    latitude: 0,
    longitude: 0,
    radius: 200,
    description: '',
    is_active: true
  })
}

// 格式化时间
const formatTime = (timeStr: string) => {
  return new Date(timeStr).toLocaleString('zh-CN')
}

// 页面加载时获取数据
onMounted(() => {
  loadLocations()
})
</script>

<style scoped>
.company-locations {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

.location-card {
  border-radius: 12px;
}

.card-header {
  text-align: center;
}

.card-header h2 {
  margin: 0 0 8px 0;
  color: #409EFF;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}

.location-content {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.action-buttons {
  display: flex;
  gap: 12px;
  justify-content: flex-start;
}

.locations-list {
  margin-top: 20px;
}

.coordinates {
  font-size: 12px;
  line-height: 1.4;
}

@media (max-width: 768px) {
  .company-locations {
    padding: 16px;
  }
  
  .action-buttons {
    flex-direction: column;
  }
}
</style>
