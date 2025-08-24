<template>
  <div class="test-user-management">
    <h2>用户管理测试页面</h2>
    
    <!-- 简单的测试区域 -->
    <div style="margin: 20px 0; padding: 20px; border: 1px solid #ccc;">
      <h3>测试计数器: {{ testCounter }}</h3>
      <el-button @click="incrementCounter" type="primary">点击测试 (+1)</el-button>
      <el-button @click="resetCounter" type="warning">重置</el-button>
    </div>

    <!-- 搜索测试 -->
    <div style="margin: 20px 0; padding: 20px; border: 1px solid #ccc;">
      <h3>搜索测试</h3>
      <el-input 
        v-model="testSearchKeyword" 
        placeholder="输入搜索关键词"
        @keyup.enter="testSearch"
        style="width: 300px; margin-right: 10px;"
      />
      <el-button @click="testSearch" type="primary">搜索</el-button>
      <p>当前搜索词: {{ testSearchKeyword }}</p>
      <p>搜索次数: {{ searchCount }}</p>
    </div>

    <!-- 对话框测试 -->
    <div style="margin: 20px 0; padding: 20px; border: 1px solid #ccc;">
      <h3>对话框测试</h3>
      <el-button @click="openTestDialog" type="success">打开测试对话框</el-button>
      
      <el-dialog v-model="testDialogVisible" title="测试对话框" width="500px">
        <p>这是一个测试对话框</p>
        <el-input v-model="testDialogInput" placeholder="测试输入" />
        <template #footer>
          <el-button @click="testDialogVisible = false">取消</el-button>
          <el-button @click="saveTestDialog" type="primary">确定</el-button>
        </template>
      </el-dialog>
    </div>

    <!-- 实际用户管理功能测试 -->
    <div style="margin: 20px 0; padding: 20px; border: 1px solid #ccc;">
      <h3>实际功能测试</h3>
      <el-input 
        v-model="actualSearchForm.keyword" 
        placeholder="搜索用户名、邮箱、手机号"
        @keyup.enter="actualSearchUsers"
        style="width: 300px; margin-right: 10px;"
      />
      <el-button @click="actualSearchUsers" type="primary">实际搜索</el-button>
      <el-button @click="openAddUserDialog" type="success">新增用户</el-button>
      
      <div v-if="userList.length > 0" style="margin-top: 10px;">
        <p>用户数量: {{ userList.length }}</p>
        <div v-for="user in userList" :key="user.id" style="margin: 5px 0;">
          {{ user.username }} - {{ user.email }}
        </div>
      </div>
    </div>

    <!-- 新增用户对话框 -->
    <el-dialog v-model="showActualAddDialog" title="新增用户" width="600px">
      <el-form :model="userForm" label-width="100px">
        <el-form-item label="用户名">
          <el-input v-model="userForm.username" />
        </el-form-item>
        <el-form-item label="邮箱">
          <el-input v-model="userForm.email" />
        </el-form-item>
        <el-form-item label="密码">
          <el-input v-model="userForm.password" type="password" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showActualAddDialog = false">取消</el-button>
        <el-button @click="saveActualUser" type="primary">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { getUserList as fetchUserList } from '@/services/user'

// 基础测试状态
const testCounter = ref(0)
const testSearchKeyword = ref('')
const searchCount = ref(0)
const testDialogVisible = ref(false)
const testDialogInput = ref('')

// 实际功能状态  
const actualSearchForm = reactive({
  keyword: '',
  role: '',
  status: '',
  department: ''
})

const userList = ref<any[]>([])
const showActualAddDialog = ref(false)

const userForm = reactive({
  username: '',
  email: '',
  password: ''
})

// 基础测试函数
const incrementCounter = () => {
  testCounter.value++
  console.log('计数器增加:', testCounter.value)
  ElMessage.success(`计数器: ${testCounter.value}`)
}

const resetCounter = () => {
  testCounter.value = 0
  console.log('计数器重置')
  ElMessage.info('计数器已重置')
}

const testSearch = () => {
  searchCount.value++
  console.log('搜索测试:', testSearchKeyword.value, '次数:', searchCount.value)
  ElMessage.success(`搜索: ${testSearchKeyword.value}`)
}

const openTestDialog = () => {
  testDialogVisible.value = true
  console.log('打开测试对话框')
}

const saveTestDialog = () => {
  console.log('保存测试对话框:', testDialogInput.value)
  ElMessage.success(`保存: ${testDialogInput.value}`)
  testDialogVisible.value = false
}

// 实际功能函数
const actualSearchUsers = async () => {
  console.log('实际搜索用户:', actualSearchForm.keyword)
  try {
    const params: any = {
      page: 1,
      page_size: 10
    }
    
    if (actualSearchForm.keyword) {
      params.search = actualSearchForm.keyword
    }
    
    const response = await fetchUserList(params)
    userList.value = response.results || []
    console.log('获取到用户:', userList.value.length, '个')
    ElMessage.success(`找到 ${userList.value.length} 个用户`)
  } catch (error: any) {
    console.error('搜索用户失败:', error)
    ElMessage.error('搜索失败')
  }
}

const openAddUserDialog = () => {
  console.log('打开新增用户对话框')
  showActualAddDialog.value = true
}

const saveActualUser = () => {
  console.log('保存用户:', userForm)
  ElMessage.success('用户保存功能待实现')
  showActualAddDialog.value = false
}

// 初始化
onMounted(() => {
  console.log('测试页面已挂载')
  actualSearchUsers() // 自动加载用户列表
})
</script>

<style scoped>
.test-user-management {
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
}
</style>
