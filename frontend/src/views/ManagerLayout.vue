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
  background: linear-gradient(135deg, #06b6d4 0%, #3b82f6 100%);
  border-bottom: none;
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 24px;
  flex-shrink: 0;
  box-shadow: 0 2px 12px rgba(6, 182, 212, 0.25);
  height: 56px;
}

.header-left {
  display: flex;
  align-items: center;
}

.logo {
  width: 30px;
  height: 30px;
  margin-right: 12px;
  filter: brightness(0) invert(1);
}

.title {
  margin: 0;
  font-size: 17px;
  color: #fff;
  font-weight: 700;
  letter-spacing: 0.3px;
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
  background: rgba(255, 255, 255, 0.18);
}

.username {
  margin: 0 8px;
  color: #fff;
  font-weight: 500;
  font-size: 14px;
}

.user-info .el-icon {
  color: rgba(255, 255, 255, 0.85);
}

.sidebar {
  background: #fff;
  border-right: 1px solid var(--hr-gray-100);
  box-shadow: 1px 0 4px rgba(0, 0, 0, 0.03);
}

.sidebar-menu {
  border-right: none;
  background: transparent;
  padding: 8px 0;
}

.sidebar-menu :deep(.el-menu-item) {
  color: var(--hr-gray-600);
  transition: all 0.25s ease;
  margin: 2px 8px;
  border-radius: 8px;
  height: 44px;
  line-height: 44px;
  font-size: 14px;
  font-weight: 500;
}

.sidebar-menu :deep(.el-menu-item:hover) {
  background: #ecfeff;
  color: #0891b2;
}

.sidebar-menu :deep(.el-menu-item.is-active) {
  background: linear-gradient(135deg, #06b6d4 0%, #3b82f6 100%) !important;
  color: #fff !important;
  box-shadow: 0 3px 10px rgba(6, 182, 212, 0.3);
  font-weight: 600;
}

.sidebar-menu :deep(.el-sub-menu__title) {
  color: var(--hr-gray-600);
  transition: all 0.25s ease;
  margin: 2px 8px;
  border-radius: 8px;
  height: 44px;
  line-height: 44px;
  font-size: 14px;
  font-weight: 500;
}

.sidebar-menu :deep(.el-sub-menu__title:hover) {
  background: #ecfeff;
  color: #0891b2;
}

.sidebar-menu :deep(.el-sub-menu .el-menu-item) {
  margin: 2px 8px 2px 16px;
  font-size: 13px;
  height: 40px;
  line-height: 40px;
}

.sidebar-menu :deep(.el-sub-menu .el-menu-item:hover) {
  background: #ecfeff;
  color: #0891b2;
}

.main-content {
  background: var(--color-background-page);
  padding: 0;
  flex: 1;
  overflow-y: auto;
  min-height: 0;
}

.breadcrumb {
  background: #fff;
  padding: 14px 24px;
  border-bottom: 1px solid var(--hr-gray-100);
  margin-bottom: 0;
}
</style>
