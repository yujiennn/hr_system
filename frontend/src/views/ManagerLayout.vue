<template>  <div class="manager-layout">
    <el-container style="height: auto; min-height: 100vh;">
      <!-- 顶部导航栏 -->
      <el-header class="header">
        <div class="header-left">
          <img src="/favicon.ico" alt="Logo" class="logo" />
          <h1 class="title">智慧员工运营系统 - 部门经理</h1>
        </div>
        <div class="header-right">
          <el-dropdown @command="handleCommand">
            <span class="user-info">
              <el-avatar :size="32" :src="userStore.user?.avatar">
                <el-icon><User /></el-icon>
              </el-avatar>
              <span class="username">{{ userStore.user?.first_name || '经理' }}</span>
              <el-icon><ArrowDown /></el-icon>
            </span>            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="profile">个人资料</el-dropdown-item>
                <el-dropdown-item divided command="logout">退出登录</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </el-header>      <el-container style="height: auto; flex: 1;">
        <!-- 侧边导航栏 -->
        <el-aside width="240px" class="sidebar">
          <el-menu
            :default-active="$route.path"
            class="sidebar-menu"
            router
            unique-opened
          >
            <el-menu-item index="/manager/dashboard">
              <el-icon><Odometer /></el-icon>
              <span>工作台</span>
            </el-menu-item>
            
            <el-sub-menu index="employee-management">
              <template #title>
                <el-icon><UserFilled /></el-icon>
                <span>员工管理</span>
              </template>
              <el-menu-item index="/manager/employees">员工列表</el-menu-item>
            </el-sub-menu>

            <el-sub-menu index="attendance-management">
              <template #title>
                <el-icon><Clock /></el-icon>
                <span>考勤管理</span>
              </template>
              <el-menu-item index="/manager/attendance">考勤统计</el-menu-item>
            </el-sub-menu>

            <el-sub-menu index="leave-management">
              <template #title>
                <el-icon><Calendar /></el-icon>
                <span>请假管理</span>
              </template>
              <el-menu-item index="/manager/leave">请假审批</el-menu-item>
            </el-sub-menu>

            <el-sub-menu index="performance-management">
              <template #title>
                <el-icon><TrendCharts /></el-icon>
                <span>绩效管理</span>
              </template>
              <el-menu-item index="/manager/performance">绩效评估</el-menu-item>
            </el-sub-menu>

            <el-sub-menu index="salary-approval">
              <template #title>
                <el-icon><Money /></el-icon>
                <span>薪资审批</span>
              </template>
              <el-menu-item index="/manager/salary">薪资审批</el-menu-item>
            </el-sub-menu>
          </el-menu>
        </el-aside>

        <!-- 主要内容区域 -->
        <el-main class="main-content">
          <div class="breadcrumb">
            <el-breadcrumb separator="/">
              <el-breadcrumb-item>部门经理</el-breadcrumb-item>
              <el-breadcrumb-item>{{ getBreadcrumbTitle() }}</el-breadcrumb-item>
            </el-breadcrumb>
          </div>
          <router-view />
        </el-main>
      </el-container>
    </el-container>
  </div>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/counter'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  User,
  ArrowDown,
  Odometer,
  UserFilled,
  Clock,
  Calendar,
  TrendCharts,
  Money
} from '@element-plus/icons-vue'

const router = useRouter()
const userStore = useAuthStore()

const handleCommand = async (command: string) => {
  switch (command) {
    case 'profile':
      // 跳转到个人资料页面
      router.push('/manager/profile')
      break
    case 'logout':
      try {
        await ElMessageBox.confirm('确定要退出登录吗？', '确认', {
          type: 'warning'
        })
        await userStore.logout()
        router.push('/login')
        ElMessage.success('已退出登录')
      } catch (error: any) {
        // 用户取消操作
      }
      break
  }
}

const getBreadcrumbTitle = () => {
  const routeMap: Record<string, string> = {
    '/manager/dashboard': '工作台',
    '/manager/employees': '员工管理',
    '/manager/attendance': '考勤管理',
    '/manager/leave': '请假管理',
    '/manager/performance': '绩效管理',
    '/manager/salary': '薪资审批',
    '/manager/profile': '个人资料'
  }
  return routeMap[router.currentRoute.value.path] || '未知页面'
}
</script>

<style scoped>
.manager-layout {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.header {
  background: linear-gradient(135deg, #13c2c2 0%, #1890ff 100%);
  border-bottom: none;
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 20px;
  flex-shrink: 0;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
}

.header-left {
  display: flex;
  align-items: center;
}

.logo {
  width: 32px;
  height: 32px;
  margin-right: 12px;
  filter: brightness(0) invert(1);
}

.title {
  margin: 0;
  font-size: 20px;
  color: #fff;
  font-weight: 700;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.header-right {
  display: flex;
  align-items: center;
}

.user-info {
  display: flex;
  align-items: center;
  cursor: pointer;
  padding: 8px 16px;
  border-radius: 8px;
  transition: all 0.3s;
  background: rgba(255, 255, 255, 0.1);
}

.user-info:hover {
  background: rgba(255, 255, 255, 0.2);
  transform: translateY(-1px);
}

.username {
  margin: 0 8px;
  color: #fff;
  font-weight: 500;
}

.user-info .el-icon {
  color: #fff;
}

.sidebar {
  background: linear-gradient(180deg, #304156 0%, #263445 100%);
  border-right: none;
  box-shadow: 2px 0 8px rgba(0, 0, 0, 0.1);
}

.sidebar-menu {
  border-right: none;
  background: transparent;
}

.sidebar-menu :deep(.el-menu-item) {
  color: #bfcbd9;
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
  transition: all 0.3s ease;
  margin: 4px 8px;
  border-radius: 8px;
}

.sidebar-menu :deep(.el-menu-item:hover) {
  background: linear-gradient(135deg, #13c2c2 0%, #1890ff 100%);
  color: #fff;
  transform: translateX(4px);
}

.sidebar-menu :deep(.el-menu-item.is-active) {
  background: linear-gradient(135deg, #13c2c2 0%, #1890ff 100%) !important;
  color: #fff;
  box-shadow: 0 4px 12px rgba(19, 194, 194, 0.4);
}

.sidebar-menu :deep(.el-sub-menu__title) {
  color: #bfcbd9;
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
  transition: all 0.3s ease;
  margin: 4px 8px;
  border-radius: 8px;
}

.sidebar-menu :deep(.el-sub-menu__title:hover) {
  background: rgba(19, 194, 194, 0.2);
  color: #fff;
}

.sidebar-menu :deep(.el-sub-menu .el-menu-item) {
  background-color: rgba(30, 45, 61, 0.3);
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
  margin: 2px 8px;
}

.sidebar-menu :deep(.el-sub-menu .el-menu-item:hover) {
  background: linear-gradient(135deg, #13c2c2 0%, #1890ff 100%);
  color: #fff;
  transform: translateX(4px);
}

.main-content {
  background: #f0f2f5;
  padding: 0;
  flex: 1;
  overflow-y: auto;
  min-height: 0;
}

.breadcrumb {
  background: #fff;
  padding: 16px 24px;
  border-bottom: 1px solid #e6e6e6;
  margin-bottom: 16px;
}
</style>
