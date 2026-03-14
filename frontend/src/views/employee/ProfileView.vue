<template>
  <div class="profile">
    <el-row :gutter="20">
      <el-col :span="8">
        <!-- 头像和基本信息 -->
        <el-card>
          <div class="profile-header">
            <div class="avatar-section">              <el-avatar :size="120" :src="avatarUrl" @click="handleAvatarClick">
                <el-icon><User /></el-icon>
              </el-avatar>
              <input
                ref="avatarInputRef"
                type="file"
                accept="image/*"
                @change="handleAvatarChange"
                style="display: none"
              />              <div class="avatar-actions">
                <el-button 
                  size="small" 
                  @click="handleAvatarClick"
                  :loading="saving"
                  :disabled="saving"
                >
                  {{ saving ? '上传中...' : '更换头像' }}
                </el-button>
              </div>
            </div>
            <div class="basic-info">
              <h3>{{ profileForm.first_name }} {{ profileForm.last_name }}</h3>
              <p class="job-info">{{ profileForm.position }} - {{ profileForm.department_name }}</p>
              <p class="employee-info">工号：{{ profileForm.employee_id }}</p>
            </div>
          </div>
        </el-card>

        <!-- 统计信息 -->
        <el-card style="margin-top: 20px;">
          <template #header>
            <span>统计信息</span>
          </template>
          <div class="stats-info">
            <div class="stat-item">
              <span class="label">入职时间：</span>
              <span class="value">{{ profileForm.hire_date }}</span>
            </div>
            <div class="stat-item">
              <span class="label">工作年限：</span>
              <span class="value">{{ workYears }} 年</span>
            </div>
            <div class="stat-item">
              <span class="label">累计考勤：</span>
              <span class="value">{{ stats.totalAttendance }} 天</span>
            </div>
            <div class="stat-item">
              <span class="label">请假次数：</span>
              <span class="value">{{ stats.totalLeaves }} 次</span>
            </div>
          </div>
        </el-card>
      </el-col>

      <el-col :span="16">
        <!-- 个人信息编辑 -->
        <el-card>
          <template #header>
            <div class="card-header">
              <span>个人信息</span>
              <el-button v-if="!isEditing" type="primary" @click="startEdit">编辑</el-button>
              <div v-else>
                <el-button type="success" @click="saveProfile" :loading="saving">保存</el-button>
                <el-button @click="cancelEdit">取消</el-button>
              </div>
            </div>
          </template>

          <el-form
            ref="profileFormRef"
            :model="profileForm"
            :rules="profileRules"
            label-width="120px"
            :disabled="!isEditing"
          >
            <el-row :gutter="20">
              <el-col :span="12">
                <el-form-item label="姓名" prop="first_name">
                  <el-input v-model="profileForm.first_name" />
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="姓氏" prop="last_name">
                  <el-input v-model="profileForm.last_name" />
                </el-form-item>
              </el-col>
            </el-row>

            <el-row :gutter="20">
              <el-col :span="12">
                <el-form-item label="性别">
                  <el-select v-model="profileForm.gender" placeholder="请选择性别">
                    <el-option label="男" value="M" />
                    <el-option label="女" value="F" />
                  </el-select>
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="出生日期">
                  <el-date-picker
                    v-model="profileForm.birth_date"
                    type="date"
                    placeholder="选择出生日期"
                    format="YYYY-MM-DD"
                    value-format="YYYY-MM-DD"
                  />
                </el-form-item>
              </el-col>
            </el-row>

            <el-row :gutter="20">
              <el-col :span="12">
                <el-form-item label="手机号码" prop="phone">
                  <el-input v-model="profileForm.phone" />
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="邮箱" prop="email">
                  <el-input v-model="profileForm.email" />
                </el-form-item>
              </el-col>
            </el-row>

            <el-form-item label="身份证号" prop="id_card">
              <el-input v-model="profileForm.id_card" />
            </el-form-item>

            <el-form-item label="现住地址">
              <el-input v-model="profileForm.address" type="textarea" :rows="2" />
            </el-form-item>

            <el-form-item label="紧急联系人">
              <el-input v-model="profileForm.emergency_contact" />
            </el-form-item>

            <el-form-item label="紧急联系电话">
              <el-input v-model="profileForm.emergency_phone" />
            </el-form-item>

            <el-form-item label="教育背景">
              <el-select v-model="profileForm.education" placeholder="请选择学历">
                <el-option label="高中及以下" value="high_school" />
                <el-option label="专科" value="college" />
                <el-option label="本科" value="bachelor" />
                <el-option label="硕士" value="master" />
                <el-option label="博士" value="doctor" />
              </el-select>
            </el-form-item>

            <el-form-item label="专业">
              <el-input v-model="profileForm.major" />
            </el-form-item>

            <el-form-item label="毕业院校">
              <el-input v-model="profileForm.university" />
            </el-form-item>

            <el-form-item label="工作经验">
              <el-input v-model="profileForm.work_experience" type="textarea" :rows="3" />
            </el-form-item>

            <el-form-item label="专业技能">
              <el-input v-model="profileForm.skills" type="textarea" :rows="3" />
            </el-form-item>

            <el-form-item label="个人简介">
              <el-input v-model="profileForm.bio" type="textarea" :rows="3" />
            </el-form-item>
          </el-form>
        </el-card>

        <!-- 修改密码 -->
        <el-card style="margin-top: 20px;">
          <template #header>
            <span>修改密码</span>
          </template>
          <el-form
            ref="passwordFormRef"
            :model="passwordForm"
            :rules="passwordRules"
            label-width="120px"
          >
            <el-form-item label="当前密码" prop="current_password">
              <el-input
                v-model="passwordForm.current_password"
                type="password"
                show-password
                placeholder="请输入当前密码"
              />
            </el-form-item>
            <el-form-item label="新密码" prop="new_password">
              <el-input
                v-model="passwordForm.new_password"
                type="password"
                show-password
                placeholder="请输入新密码"
              />
            </el-form-item>
            <el-form-item label="确认密码" prop="confirm_password">
              <el-input
                v-model="passwordForm.confirm_password"
                type="password"
                show-password
                placeholder="请再次输入新密码"
              />
            </el-form-item>
            <el-form-item>
              <el-button type="primary" @click="changePassword" :loading="changingPassword">
                修改密码
              </el-button>
              <el-button @click="resetPasswordForm">重置</el-button>
            </el-form-item>
          </el-form>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { User } from '@element-plus/icons-vue'
import { useAuthStore } from '@/stores/counter'
import authService from '@/services/auth'
import { uploadAvatar } from '@/services/user'
import type { FormInstance, FormRules } from 'element-plus'

const authStore = useAuthStore()
const profileFormRef = ref<FormInstance>()
const passwordFormRef = ref<FormInstance>()
const avatarInputRef = ref<HTMLInputElement>()
const isEditing = ref(false)
const saving = ref(false)
const changingPassword = ref(false)

const profileForm = reactive({
  employee_id: '',
  first_name: '',
  last_name: '',
  gender: '',
  birth_date: '',
  phone: '',
  email: '',
  id_card: '',
  address: '',
  emergency_contact: '',
  emergency_phone: '',
  education: '',
  major: '',
  university: '',
  work_experience: '',
  skills: '',
  bio: '',
  hire_date: '',
  position: '',
  department_name: '',
  avatar: ''
})

const passwordForm = reactive({
  current_password: '',
  new_password: '',
  confirm_password: ''
})

const stats = reactive({
  totalAttendance: 0,
  totalLeaves: 0
})

const originalProfileForm = reactive({})

// 计算头像完整URL
const avatarUrl = computed(() => {
  if (!profileForm.avatar) return ''
  if (profileForm.avatar.startsWith('http')) {
    return profileForm.avatar
  }
  if (profileForm.avatar.startsWith('data:')) {
    return profileForm.avatar  // base64数据
  }
  return `http://localhost:8001${profileForm.avatar}`
})

// 计算工作年限
const workYears = computed(() => {
  if (!profileForm.hire_date) return 0
  const hireDate = new Date(profileForm.hire_date)
  const now = new Date()
  return Math.floor((now.getTime() - hireDate.getTime()) / (1000 * 60 * 60 * 24 * 365))
})

const profileRules: FormRules = {
  first_name: [
    { required: true, message: '请输入姓名', trigger: 'blur' }
  ],
  last_name: [
    { required: true, message: '请输入姓氏', trigger: 'blur' }
  ],
  phone: [
    { required: true, message: '请输入手机号码', trigger: 'blur' },
    { pattern: /^1[3-9]\d{9}$/, message: '请输入正确的手机号码', trigger: 'blur' }
  ],
  email: [
    { required: true, message: '请输入邮箱', trigger: 'blur' },
    { type: 'email', message: '请输入正确的邮箱地址', trigger: 'blur' }
  ],
  id_card: [
    { pattern: /^[1-9]\d{5}(18|19|20)\d{2}((0[1-9])|(1[0-2]))(([0-2][1-9])|10|20|30|31)\d{3}[0-9Xx]$/, message: '请输入正确的身份证号', trigger: 'blur' }
  ]
}

const validateConfirmPassword = (rule: any, value: string, callback: any) => {
  if (value !== passwordForm.new_password) {
    callback(new Error('两次输入的密码不一致'))
  } else {
    callback()
  }
}

const passwordRules: FormRules = {
  current_password: [
    { required: true, message: '请输入当前密码', trigger: 'blur' }
  ],
  new_password: [
    { required: true, message: '请输入新密码', trigger: 'blur' },
    { min: 6, message: '密码长度至少6位', trigger: 'blur' }
  ],
  confirm_password: [
    { required: true, message: '请确认新密码', trigger: 'blur' },
    { validator: validateConfirmPassword, trigger: 'blur' }
  ]
}

// 开始编辑
const startEdit = () => {
  isEditing.value = true
  Object.assign(originalProfileForm, profileForm)
}

// 取消编辑
const cancelEdit = () => {
  isEditing.value = false
  Object.assign(profileForm, originalProfileForm)
}

// 保存个人信息
const saveProfile = async () => {
  if (!profileFormRef.value) return
  
  await profileFormRef.value.validate(async (valid) => {
    if (valid) {
      saving.value = true
      try {
        // 调用API保存个人信息 - 只发送有值的字段
        const updateData: any = {}
        
        // 基本信息字段
        if (profileForm.first_name) updateData.first_name = profileForm.first_name
        if (profileForm.last_name) updateData.last_name = profileForm.last_name
        if (profileForm.gender) updateData.gender = profileForm.gender
        if (profileForm.birth_date) updateData.birth_date = profileForm.birth_date
        if (profileForm.phone) updateData.phone = profileForm.phone
        if (profileForm.email) updateData.email = profileForm.email
        if (profileForm.id_card) updateData.id_card = profileForm.id_card
        if (profileForm.address) updateData.address = profileForm.address
        if (profileForm.emergency_contact) updateData.emergency_contact = profileForm.emergency_contact
        if (profileForm.emergency_phone) updateData.emergency_phone = profileForm.emergency_phone
        if (profileForm.education) updateData.education = profileForm.education
        if (profileForm.major) updateData.major = profileForm.major
        if (profileForm.university) updateData.university = profileForm.university
        if (profileForm.work_experience) updateData.work_experience = profileForm.work_experience
        if (profileForm.skills) updateData.skills = profileForm.skills
        if (profileForm.bio) updateData.bio = profileForm.bio
        if (profileForm.position) updateData.position = profileForm.position
        
        console.log('准备发送的更新数据:', updateData)
        console.log('当前表单数据:', profileForm)
        
        // 验证数据格式
        if (Object.keys(updateData).length === 0) {
          ElMessage.warning('没有需要更新的数据')
          return
        }
        
        await authService.updateProfile(updateData)
        
        // 更新用户store中的信息
        await authStore.fetchUserInfo()
        
        ElMessage.success('个人信息保存成功！')
        isEditing.value = false
      } catch (error: any) {
        console.error('保存个人信息失败:', error)
        
        // 处理详细的验证错误
        if (error.response?.data) {
          const errorData = error.response.data
          let errorMessage = '保存失败：'
          
          // 处理字段验证错误
          if (typeof errorData === 'object') {
            const errorMessages = []
            for (const [field, messages] of Object.entries(errorData)) {
              if (Array.isArray(messages)) {
                const fieldName = getFieldDisplayName(field)
                errorMessages.push(`${fieldName}: ${messages.join(', ')}`)
              }
            }
            if (errorMessages.length > 0) {
              errorMessage = errorMessages.join('\n')
            } else {
              errorMessage = errorData.message || errorData.detail || '保存失败，请重试'
            }
          } else {
            errorMessage = errorData
          }
          
          ElMessage.error(errorMessage)
        } else {
          ElMessage.error('保存失败，请重试')
        }
      } finally {
        saving.value = false
      }
    }
  })
}

// 获取字段显示名称
const getFieldDisplayName = (fieldName: string): string => {
  const fieldNames: { [key: string]: string } = {
    'first_name': '姓名',
    'last_name': '姓氏', 
    'phone': '手机号码',
    'email': '邮箱地址',
    'id_card': '身份证号',
    'gender': '性别',
    'birth_date': '出生日期',
    'address': '地址',
    'emergency_contact': '紧急联系人',
    'emergency_phone': '紧急联系电话',
    'education': '教育背景',
    'major': '专业',
    'university': '毕业院校',
    'work_experience': '工作经验',
    'skills': '专业技能',
    'bio': '个人简介',
    'position': '职位'
  }
  return fieldNames[fieldName] || fieldName
}

// 修改密码
const changePassword = async () => {
  if (!passwordFormRef.value) return
  
  await passwordFormRef.value.validate(async (valid) => {
    if (valid) {
      changingPassword.value = true
      try {
        // 调用API修改密码
        const changePasswordData = {
          old_password: passwordForm.current_password,
          new_password: passwordForm.new_password,
          confirm_password: passwordForm.confirm_password
        }
        
        await authService.changePassword(changePasswordData)
        
        ElMessage.success('密码修改成功！')
        resetPasswordForm()
      } catch (error: any) {
        console.error('修改密码失败:', error)
        const errorMessage = error.response?.data?.error || 
                           error.response?.data?.message ||
                           error.response?.data?.old_password?.[0] ||
                           '密码修改失败，请检查当前密码是否正确'
        ElMessage.error(errorMessage)
      } finally {
        changingPassword.value = false
      }
    }
  })
}

// 重置密码表单
const resetPasswordForm = () => {
  if (passwordFormRef.value) {
    passwordFormRef.value.resetFields()
  }
}

// 处理头像点击
const handleAvatarClick = () => {
  if (avatarInputRef.value) {
    avatarInputRef.value.click()
  }
}

// 处理头像变更
const handleAvatarChange = async (event: Event) => {
  const target = event.target as HTMLInputElement
  const file = target.files?.[0]
  
  if (file) {
    // 检查文件类型
    if (!file.type.startsWith('image/')) {
      ElMessage.error('请选择图片文件')
      return
    }
    
    // 检查文件大小 (5MB)
    if (file.size > 5 * 1024 * 1024) {
      ElMessage.error('图片大小不能超过5MB')
      return
    }
    
    try {
      saving.value = true
      ElMessage.info('正在上传头像...')
      
      const updatedUser = await uploadAvatar(file)
      profileForm.avatar = updatedUser.avatar || ''
      
      // 更新store中的用户信息
      await authStore.fetchUserInfo()
      
      ElMessage.success('头像上传成功')
      
      // 清空input value，这样同一个文件可以再次选择
      target.value = ''
    } catch (error: any) {
      console.error('头像上传失败:', error)
      ElMessage.error('头像上传失败: ' + (error.response?.data?.message || error.message))
    } finally {
      saving.value = false
    }
  }
}

// 加载个人信息
const loadProfile = async () => {
  try {
    // 从API加载个人信息
    const userInfo = await authService.getCurrentUser()
    
    // 更新表单数据
    Object.assign(profileForm, {
      employee_id: userInfo.employee_id || '',
      first_name: userInfo.first_name || '',
      last_name: userInfo.last_name || '',
      gender: userInfo.gender || '',
      birth_date: userInfo.birth_date || '',
      phone: userInfo.phone || '',
      email: userInfo.email || '',
      id_card: userInfo.id_card || '',
      address: userInfo.address || '',
      emergency_contact: userInfo.emergency_contact || '',
      emergency_phone: userInfo.emergency_phone || '',
      education: userInfo.education || '',
      major: userInfo.major || '',
      university: userInfo.university || '',
      work_experience: userInfo.work_experience || '',
      skills: userInfo.skills || '',
      bio: userInfo.bio || '',
      hire_date: userInfo.hire_date || '',
      position: userInfo.position || '',
      department_name: userInfo.department_name || '',
      avatar: userInfo.avatar || ''
    })
    
    // 更新stats - 暂时保持模拟数据，后续可以添加相关API
    stats.totalAttendance = 500
    stats.totalLeaves = 8
  } catch (error: any) {
    console.error('加载个人信息失败:', error)
    ElMessage.error('加载个人信息失败，请刷新页面重试')
  }
}

onMounted(() => {
  loadProfile()
})
</script>

<style scoped>
.profile {
  padding: var(--hr-space-lg);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.profile-header {
  text-align: center;
  padding: var(--hr-space-lg) 0;
}

.avatar-section {
  margin-bottom: var(--hr-space-lg);
}

.avatar-actions {
  margin-top: var(--hr-space-sm);
}

.basic-info h3 {
  margin: 0 0 10px 0;
  color: var(--color-text-primary);
  font-size: 22px;
  font-weight: 700;
}

.job-info {
  color: var(--hr-primary);
  font-size: 15px;
  margin: 0 0 5px 0;
  font-weight: 500;
}

.employee-info {
  color: var(--color-text-secondary);
  font-size: 14px;
  margin: 0;
}

.stats-info {
  padding: var(--hr-space-sm) 0;
}

.stat-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 14px;
  padding: 8px 12px;
  border-radius: var(--hr-radius-sm);
  transition: background var(--hr-transition-fast);
}

.stat-item:hover {
  background: var(--hr-gray-50);
}

.stat-item:last-child {
  margin-bottom: 0;
}

.stat-item .label {
  color: var(--color-text-secondary);
  font-size: 13px;
}

.stat-item .value {
  color: var(--color-text-primary);
  font-weight: 600;
}

.el-form {
  max-width: 100%;
}

.el-form-item {
  margin-bottom: 22px;
}
</style>
