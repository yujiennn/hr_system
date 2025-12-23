<template>  <div class="employee-layout">
    <!-- 头部导航 -->
    <el-header class="header">
      <div class="header-content">
        <h2>智慧员工运营系统</h2>
        <div class="user-info">
          <el-avatar :src="userStore.user?.avatar" class="avatar">
            {{ userStore.user?.first_name || userStore.user?.username }}
          </el-avatar>
          <span class="username">{{ userStore.user?.first_name || userStore.user?.username }}</span>
          <el-dropdown @command="handleCommand">
            <el-button type="text">
              <el-icon><ArrowDown /></el-icon>
            </el-button>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="profile">个人资料</el-dropdown-item>
                <el-dropdown-item command="logout">退出登录</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </div>
    </el-header>    <el-container style="height: auto; flex: 1;">
      <!-- 侧边菜单 -->
      <el-aside width="250px" class="sidebar">
        <el-menu
          :default-active="activeMenu"
          class="sidebar-menu"
          router
        >
          <el-menu-item index="/employee">
            <el-icon><House /></el-icon>
            <span>首页</span>
          </el-menu-item>
          
          <el-menu-item index="/employee/attendance">
            <el-icon><Clock /></el-icon>
            <span>考勤打卡</span>
          </el-menu-item>
          
          <el-menu-item index="/employee/leave">
            <el-icon><Calendar /></el-icon>
            <span>请假申请</span>
          </el-menu-item>
          
          <el-menu-item index="/employee/salary">
            <el-icon><Money /></el-icon>
            <span>薪资查询</span>
          </el-menu-item>
          
          <el-menu-item index="/employee/performance">
            <el-icon><TrendCharts /></el-icon>
            <span>绩效查询</span>
          </el-menu-item>
          
          <el-menu-item index="/employee/profile">
            <el-icon><User /></el-icon>
            <span>个人资料</span>
          </el-menu-item>

          <el-menu-item index="/employee/face-registration">
            <el-icon><Camera /></el-icon>
            <span>人脸录入</span>
          </el-menu-item>
        </el-menu>
      </el-aside>

      <!-- 主内容区域 -->
      <el-main class="main-content">
        <router-view />
      </el-main>
    </el-container>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { 
  ArrowDown, House, Clock, Calendar, Money, 
  TrendCharts, User, Camera 
} from '@element-plus/icons-vue'
import { useUserStore } from '@/stores/counter'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()

const activeMenu = computed(() => route.path)

onMounted(() => {
  // 初始化用户信息
  userStore.initAuth()
})

// 处理下拉菜单命令
const handleCommand = async (command: string) => {
  switch (command) {
    case 'profile':
      router.push('/employee/profile')
      break
    case 'logout':
      try {
        await ElMessageBox.confirm('确定要退出登录吗？', '提示', {
          confirmButtonText: '确定',
          cancelButtonText: '取消',
          type: 'warning'
        })
        await userStore.logout()
        ElMessage.success('已退出登录')
        router.push('/login')
      } catch (error: any) {
        // 用户取消操作
      }
      break
  }
}
</script>

<style scoped>
.employee-layout {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.header {
  background: linear-gradient(135deg, #fa8c16 0%, #ff7a45 100%);
  color: white;
  display: flex;
  align-items: center;
  padding: 0 20px;
  flex-shrink: 0;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
}

.header-content h2 {
  margin: 0;
  font-size: 20px;
  font-weight: 700;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.user-info {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 8px 16px;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s;
  background: rgba(255, 255, 255, 0.1);
}

.user-info:hover {
  background: rgba(255, 255, 255, 0.2);
  transform: translateY(-1px);
}

.avatar {
  width: 32px;
  height: 32px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
}

.username {
  font-size: 14px;
  font-weight: 500;
}

.sidebar {
  background: linear-gradient(180deg, #f5f7fa 0%, #e8eaed 100%);
  border-right: 1px solid #d9dce0;
}

.sidebar-menu {
  border: none;
  height: 100%;
  background: transparent;
}

.sidebar-menu :deep(.el-menu-item) {
  margin: 4px 8px;
  border-radius: 8px;
  transition: all 0.3s ease;
  font-weight: 500;
}

.sidebar-menu :deep(.el-menu-item:hover) {
  background: linear-gradient(135deg, #fa8c16 0%, #ff7a45 100%);
  color: #fff;
  transform: translateX(4px);
}

.sidebar-menu :deep(.el-menu-item.is-active) {
  background: linear-gradient(135deg, #fa8c16 0%, #ff7a45 100%);
  color: #fff;
  box-shadow: 0 4px 12px rgba(250, 140, 22, 0.4);
}

.main-content {
  background: #f5f7fa;
  padding: 20px;
  flex: 1;
  overflow-y: auto;
  min-height: 0;
}
</style>
