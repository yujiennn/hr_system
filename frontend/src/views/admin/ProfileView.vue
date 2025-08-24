<template>
  <div class="profile-settings">
    <el-card class="page-header">
      <div class="header-content">
        <h2>个人资料</h2>
      </div>
    </el-card>

    <el-row :gutter="20">
      <!-- 头像和基本信息 -->
      <el-col :span="8">
        <el-card>
          <div class="profile-header">            <div class="avatar-section">              <el-avatar :size="120" :src="avatarUrl">
                <el-icon><User /></el-icon>
              </el-avatar>
              <div class="avatar-actions">
                <el-button 
                  size="small" 
                  @click="handleAvatarClick" 
                  :loading="saving"
                  :disabled="saving"
                >
                  {{ saving ? '上传中...' : '更换头像' }}
                </el-button>
                <input
                  ref="avatarInputRef"
                  type="file"
                  accept="image/*"
                  @change="handleAvatarChange"
                  style="display: none"
                />
              </div>
            </div>
            <div class="basic-info">
              <h3>{{ profileForm.first_name }} {{ profileForm.last_name }}</h3>
              <p class="job-info">{{ profileForm.position }} - {{ profileForm.department_name }}</p>
              <p class="role-info">
                <el-tag :type="profileForm.user_type === 'admin' ? 'danger' : profileForm.user_type === 'manager' ? 'warning' : 'success'">
                  {{ profileForm.user_type === 'admin' ? '系统管理员' : profileForm.user_type === 'manager' ? '部门经理' : '普通员工' }}
                </el-tag>
              </p>
            </div>
          </div>
        </el-card>
      </el-col>

      <!-- 个人信息表单 -->
      <el-col :span="16">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>个人信息</span>
              <el-button type="primary" @click="editMode = !editMode">
                {{ editMode ? '取消编辑' : '编辑资料' }}
              </el-button>
            </div>
          </template>
          
          <el-form
            :model="profileForm"
            :rules="formRules"
            ref="formRef"
            label-width="120px"
            :disabled="!editMode"
          >
            <el-row :gutter="20">
              <el-col :span="12">
                <el-form-item label="用户名" prop="username">
                  <el-input v-model="profileForm.username" readonly />
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="邮箱" prop="email">
                  <el-input v-model="profileForm.email" />
                </el-form-item>
              </el-col>
            </el-row>
            
            <el-row :gutter="20">
              <el-col :span="12">
                <el-form-item label="姓" prop="first_name">
                  <el-input v-model="profileForm.first_name" />
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="名" prop="last_name">
                  <el-input v-model="profileForm.last_name" />
                </el-form-item>
              </el-col>
            </el-row>
            
            <el-row :gutter="20">
              <el-col :span="12">
                <el-form-item label="手机号" prop="phone">
                  <el-input v-model="profileForm.phone" />
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="职位" prop="position">
                  <el-input v-model="profileForm.position" />
                </el-form-item>
              </el-col>
            </el-row>
            
            <el-row :gutter="20">
              <el-col :span="12">
                <el-form-item label="入职日期" prop="hire_date">
                  <el-date-picker
                    v-model="profileForm.hire_date"
                    type="date"
                    placeholder="选择入职日期"
                    format="YYYY-MM-DD"
                    value-format="YYYY-MM-DD"
                    style="width: 100%"
                  />
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="部门" prop="department_name">
                  <el-input v-model="profileForm.department_name" readonly />
                </el-form-item>
              </el-col>
            </el-row>
            
            <el-form-item v-if="editMode">
              <el-button type="primary" @click="saveProfile" :loading="saving">保存修改</el-button>
              <el-button @click="resetForm">重置</el-button>
            </el-form-item>
          </el-form>
        </el-card>
      </el-col>
    </el-row>

    <!-- 修改密码 -->
    <el-card style="margin-top: 20px;">
      <template #header>
        <span>安全设置</span>
      </template>
      
      <el-row :gutter="20">
        <el-col :span="12">
          <el-button type="warning" @click="showPasswordDialog = true">
            <el-icon><Lock /></el-icon>
            修改密码
          </el-button>
        </el-col>
      </el-row>
    </el-card>

    <!-- 修改密码对话框 -->
    <el-dialog v-model="showPasswordDialog" title="修改密码" width="500px">
      <el-form
        :model="passwordForm"
        :rules="passwordRules"
        ref="passwordFormRef"
        label-width="100px"
      >
        <el-form-item label="当前密码" prop="oldPassword">
          <el-input
            v-model="passwordForm.oldPassword"
            type="password"
            show-password
            placeholder="请输入当前密码"
          />
        </el-form-item>
        
        <el-form-item label="新密码" prop="newPassword">
          <el-input
            v-model="passwordForm.newPassword"
            type="password"
            show-password
            placeholder="请输入新密码"
          />
        </el-form-item>
        
        <el-form-item label="确认密码" prop="confirmPassword">
          <el-input
            v-model="passwordForm.confirmPassword"
            type="password"
            show-password
            placeholder="请再次输入新密码"
          />
        </el-form-item>
      </el-form>
      
      <template #footer>
        <el-button @click="showPasswordDialog = false">取消</el-button>
        <el-button type="primary" @click="changePassword" :loading="saving">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, computed } from 'vue'
import { ElMessage } from 'element-plus'
import { User, Lock } from '@element-plus/icons-vue'
import { useAuthStore } from '@/stores/counter'
import { updateProfile, changeUserPassword, uploadAvatar } from '@/services/user'

const authStore = useAuthStore()

// 响应式数据
const editMode = ref(false)
const saving = ref(false)
const showPasswordDialog = ref(false)
const formRef = ref()
const passwordFormRef = ref()
const avatarInputRef = ref()

// 个人资料表单
const profileForm = reactive({
  username: '',
  email: '',
  first_name: '',
  last_name: '',
  phone: '',
  position: '',
  hire_date: '',
  department_name: '',
  user_type: 'employee',
  avatar: ''
})

// 密码修改表单
const passwordForm = reactive({
  oldPassword: '',
  newPassword: '',
  confirmPassword: ''
})

// 表单验证规则
const formRules = {
  email: [
    { required: true, message: '请输入邮箱', trigger: 'blur' },
    { type: 'email', message: '请输入正确的邮箱格式', trigger: 'blur' }
  ],
  first_name: [
    { required: true, message: '请输入姓', trigger: 'blur' }
  ],
  last_name: [
    { required: true, message: '请输入名', trigger: 'blur' }
  ],
  phone: [
    { pattern: /^1[3-9]\d{9}$/, message: '请输入正确的手机号', trigger: 'blur' }
  ]
}

const passwordRules = {
  oldPassword: [
    { required: true, message: '请输入当前密码', trigger: 'blur' }
  ],
  newPassword: [
    { required: true, message: '请输入新密码', trigger: 'blur' },
    { min: 6, message: '密码长度至少6位', trigger: 'blur' }
  ],
  confirmPassword: [
    { required: true, message: '请确认新密码', trigger: 'blur' },
    {
      validator: (rule: any, value: string, callback: Function) => {
        if (value !== passwordForm.newPassword) {
          callback(new Error('两次输入的密码不一致'))
        } else {
          callback()
        }
      },
      trigger: 'blur'
    }
  ]
}

// 计算头像完整URL
const avatarUrl = computed(() => {
  if (!profileForm.avatar) return ''
  if (profileForm.avatar.startsWith('http')) {
    return profileForm.avatar
  }
  return `http://localhost:8001${profileForm.avatar}`
})

// 加载个人资料
const loadProfile = async () => {
  try {
    // 如果用户信息未加载，先尝试获取
    if (!authStore.user && authStore.isAuthenticated) {
      await authStore.fetchUserInfo()
    }
    
    const userInfo = authStore.user
    if (userInfo) {
      Object.assign(profileForm, {
        username: userInfo.username,
        email: userInfo.email,
        first_name: userInfo.first_name || '',
        last_name: userInfo.last_name || '',
        phone: userInfo.phone || '',
        position: userInfo.position || '',
        hire_date: userInfo.hire_date || '',
        department_name: userInfo.department_name || '',
        user_type: userInfo.user_type,
        avatar: userInfo.avatar || ''
      })
    }
  } catch (error) {
    console.error('加载个人资料失败:', error)
    ElMessage.error('加载个人资料失败')
  }
}

// 保存个人资料
const saveProfile = async () => {
  if (!formRef.value) return
  
  try {
    await formRef.value.validate()
    saving.value = true
    
    await updateProfile({
      email: profileForm.email,
      first_name: profileForm.first_name,
      last_name: profileForm.last_name,
      phone: profileForm.phone,
      position: profileForm.position,
      hire_date: profileForm.hire_date
    })
    
    ElMessage.success('个人资料更新成功')
    editMode.value = false
    
    // 更新store中的用户信息
    await authStore.fetchUserInfo()
  } catch (error) {
    console.error('保存个人资料失败:', error)
    ElMessage.error('保存个人资料失败')
  } finally {
    saving.value = false
  }
}

// 重置表单
const resetForm = () => {
  loadProfile()
}

// 修改密码
const changePassword = async () => {
  if (!passwordFormRef.value) return
  
  try {
    await passwordFormRef.value.validate()
    saving.value = true
    
    await changeUserPassword({
      old_password: passwordForm.oldPassword,
      new_password: passwordForm.newPassword
    })
    
    ElMessage.success('密码修改成功，请重新登录')
    showPasswordDialog.value = false
    
    // 重置密码表单
    Object.assign(passwordForm, {
      oldPassword: '',
      newPassword: '',
      confirmPassword: ''
    })
    
    // 延迟后跳转到登录页
    setTimeout(() => {
      authStore.logout()
    }, 2000)
  } catch (error) {
    console.error('修改密码失败:', error)
    ElMessage.error('修改密码失败')
  } finally {
    saving.value = false
  }
}

// 头像上传
const handleAvatarClick = () => {
  avatarInputRef.value?.click()
}

const handleAvatarChange = async (event: Event) => {
  console.log('handleAvatarChange 被调用')
  const target = event.target as HTMLInputElement
  const file = target.files?.[0]
  
  console.log('选择的文件:', file)
  
  if (file) {
    console.log('文件信息:', {
      name: file.name,
      size: file.size,
      type: file.type
    })
    
    // 验证文件类型
    if (!file.type.startsWith('image/')) {
      console.log('文件类型验证失败:', file.type)
      ElMessage.error('请选择图片文件')
      return
    }
    
    // 验证文件大小 (5MB)
    if (file.size > 5 * 1024 * 1024) {
      console.log('文件大小验证失败:', file.size)
      ElMessage.error('图片大小不能超过5MB')
      return
    }
    
    try {
      saving.value = true
      console.log('开始上传头像...')
      ElMessage.info('正在上传头像...')
      
      const updatedUser = await uploadAvatar(file)
      console.log('头像上传成功，返回数据:', updatedUser)
      
      profileForm.avatar = updatedUser.avatar || ''
      console.log('更新profileForm.avatar:', profileForm.avatar)
      
      // 更新store中的用户信息
      await authStore.fetchUserInfo()
      console.log('authStore用户信息已更新')
      
      ElMessage.success('头像上传成功')
      
      // 清空input value，这样同一个文件可以再次选择
      target.value = ''
    } catch (error: any) {
      console.error('头像上传失败:', error)
      console.error('错误详情:', error.response?.data)
      ElMessage.error('头像上传失败: ' + (error.response?.data?.message || error.message))
    } finally {
      saving.value = false
      console.log('头像上传流程结束')
    }
  } else {
    console.log('没有选择文件')
  }
}

onMounted(() => {
  loadProfile()
})
</script>

<style scoped>
.profile-settings {
  padding: 20px;
}

.page-header .header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.profile-header {
  text-align: center;
}

.avatar-section {
  margin-bottom: 20px;
}

.avatar-actions {
  margin-top: 10px;
}

.basic-info h3 {
  margin: 10px 0 5px;
  color: #303133;
}

.job-info, .role-info {
  margin: 5px 0;
  color: #606266;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>
