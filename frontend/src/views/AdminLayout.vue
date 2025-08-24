<template>  <div class="admin-layout">
    <el-container style="height: auto; min-height: 100vh;">
      <!-- 顶部导航栏 -->
      <el-header class="header">
        <div class="header-left">
          <img src="/favicon.ico" alt="Logo" class="logo" />
          <h1 class="title">智慧员工运营系统 - 系统管理员</h1>
        </div>
        <div class="header-right">
          <el-dropdown @command="handleCommand">
            <span class="user-info">
              <el-avatar :size="32" :src="userStore.user?.avatar">
                <el-icon><User /></el-icon>
              </el-avatar>
              <span class="username">{{ userStore.user?.first_name || '管理员' }}</span>
              <el-icon><ArrowDown /></el-icon>
            </span>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="profile">个人资料</el-dropdown-item>
                <el-dropdown-item command="settings">系统设置</el-dropdown-item>
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
            <el-menu-item index="/admin/dashboard">
              <el-icon><Odometer /></el-icon>
              <span>系统概览</span>
            </el-menu-item>
            
            <el-sub-menu index="user-management">
              <template #title>
                <el-icon><UserFilled /></el-icon>
                <span>用户管理</span>
              </template>
              <el-menu-item index="/admin/users">用户列表</el-menu-item>
            </el-sub-menu>            <el-sub-menu index="department-management">
              <template #title>
                <el-icon><OfficeBuilding /></el-icon>
                <span>部门管理</span>
              </template>
              <el-menu-item index="/admin/departments">部门管理</el-menu-item>
            </el-sub-menu>

            <el-sub-menu index="performance-management">
              <template #title>
                <el-icon><Trophy /></el-icon>
                <span>绩效管理</span>
              </template>
              <el-menu-item index="/admin/performance">绩效管理</el-menu-item>
            </el-sub-menu>

            <el-sub-menu index="system-management">
              <template #title>
                <el-icon><Setting /></el-icon>
                <span>系统管理</span>
              </template>
              <el-menu-item index="/admin/system">系统配置</el-menu-item>
            </el-sub-menu>
          </el-menu>
        </el-aside>

        <!-- 主要内容区域 -->
        <el-main class="main-content">
          <div class="breadcrumb">
            <el-breadcrumb separator="/">
              <el-breadcrumb-item>系统管理员</el-breadcrumb-item>
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
import { onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/counter'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  User,
  ArrowDown,
  Odometer,
  UserFilled,
  OfficeBuilding,
  Setting,
  Trophy
} from '@element-plus/icons-vue'

const router = useRouter()
const userStore = useAuthStore()

// 确保用户信息已加载
onMounted(async () => {
  if (!userStore.user && userStore.isAuthenticated) {
    await userStore.fetchUserInfo()
  }
})

const handleCommand = async (command: string) => {
  switch (command) {
    case 'profile':
      router.push('/admin/profile')
      break
    case 'settings':
      router.push('/admin/system')
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
    '/admin/dashboard': '系统概览',
    '/admin/users': '用户管理',
    '/admin/departments': '部门管理',
    '/admin/performance': '绩效管理',
    '/admin/system': '系统管理'
  }
  return routeMap[router.currentRoute.value.path] || '未知页面'
}
</script>

<style scoped>
.admin-layout {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.header {
  background: #fff;
  border-bottom: 1px solid #e6e6e6;
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 20px;
  flex-shrink: 0;
}

.header-left {
  display: flex;
  align-items: center;
}

.logo {
  width: 32px;
  height: 32px;
  margin-right: 12px;
}

.title {
  margin: 0;
  font-size: 20px;
  color: #303133;
  font-weight: 600;
}

.header-right {
  display: flex;
  align-items: center;
}

.user-info {
  display: flex;
  align-items: center;
  cursor: pointer;
  padding: 8px 12px;
  border-radius: 6px;
  transition: background-color 0.3s;
}

.user-info:hover {
  background-color: #f5f7fa;
}

.username {
  margin: 0 8px;
  color: #303133;
}

.sidebar {
  background: #001529;
  border-right: none;
}

.sidebar-menu {
  border-right: none;
  background: #001529;
}

.sidebar-menu :deep(.el-menu-item) {
  color: rgba(255, 255, 255, 0.65);
  border-bottom: 1px solid #002140;
}

.sidebar-menu :deep(.el-menu-item:hover) {
  background-color: #1890ff;
  color: #fff;
}

.sidebar-menu :deep(.el-menu-item.is-active) {
  background-color: #1890ff !important;
  color: #fff;
}

.sidebar-menu :deep(.el-sub-menu__title) {
  color: rgba(255, 255, 255, 0.65);
  border-bottom: 1px solid #002140;
}

.sidebar-menu :deep(.el-sub-menu__title:hover) {
  background-color: #1890ff;
  color: #fff;
}

.sidebar-menu :deep(.el-sub-menu .el-menu-item) {
  background-color: #000c17;
  border-bottom: 1px solid #002140;
}

.sidebar-menu :deep(.el-sub-menu .el-menu-item:hover) {
  background-color: #1890ff;
  color: #fff;
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
