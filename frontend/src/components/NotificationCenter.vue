<template>
  <el-badge :value="unreadCount" :hidden="unreadCount === 0" class="notification-badge">
    <el-button :icon="Bell" circle @click="toggleDrawer" />
  </el-badge>

  <el-drawer
    v-model="drawerVisible"
    title="消息中心"
    direction="rtl"
    size="400px"
    :before-close="handleClose"
  >
    <div class="notification-header">
      <el-tabs v-model="activeTab">
        <el-tab-pane label="全部" name="all">
          <el-badge :value="unreadCount" class="tab-badge" />
        </el-tab-pane>
        <el-tab-pane label="未读" name="unread">
          <el-badge :value="unreadCount" class="tab-badge" />
        </el-tab-pane>
        <el-tab-pane label="已读" name="read" />
      </el-tabs>
      
      <div class="notification-actions">
        <el-button text @click="markAllAsRead">全部标记为已读</el-button>
        <el-button text @click="clearAll">清空</el-button>
      </div>
    </div>

    <div class="notification-list">
      <el-empty v-if="filteredNotifications.length === 0" description="暂无消息" />
      
      <div
        v-for="notification in filteredNotifications"
        :key="notification.id"
        class="notification-item"
        :class="{ 'is-unread': !notification.read }"
        @click="handleNotificationClick(notification)"
      >
        <div class="notification-icon" :class="`type-${notification.type}`">
          <el-icon v-if="notification.type === 'success'"><SuccessFilled /></el-icon>
          <el-icon v-else-if="notification.type === 'warning'"><WarningFilled /></el-icon>
          <el-icon v-else-if="notification.type === 'error'"><CircleCloseFilled /></el-icon>
          <el-icon v-else><InfoFilled /></el-icon>
        </div>
        
        <div class="notification-content">
          <div class="notification-title">{{ notification.title }}</div>
          <div class="notification-message">{{ notification.message }}</div>
          <div class="notification-time">{{ formatTime(notification.time) }}</div>
        </div>
        
        <div class="notification-actions-btn">
          <el-button
            v-if="!notification.read"
            text
            size="small"
            @click.stop="markAsRead(notification.id)"
          >
            标记已读
          </el-button>
          <el-button
            text
            size="small"
            type="danger"
            @click.stop="deleteNotification(notification.id)"
          >
            删除
          </el-button>
        </div>
      </div>
    </div>
  </el-drawer>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { Bell, SuccessFilled, WarningFilled, CircleCloseFilled, InfoFilled } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'

interface Notification {
  id: number
  type: 'success' | 'warning' | 'error' | 'info'
  title: string
  message: string
  time: Date
  read: boolean
  link?: string
}

const drawerVisible = ref(false)
const activeTab = ref('all')

const notifications = ref<Notification[]>([
  {
    id: 1,
    type: 'info',
    title: '系统通知',
    message: '欢迎使用智慧员工运营系统',
    time: new Date(),
    read: false
  }
])

const unreadCount = computed(() => {
  return notifications.value.filter(n => !n.read).length
})

const filteredNotifications = computed(() => {
  if (activeTab.value === 'unread') {
    return notifications.value.filter(n => !n.read)
  } else if (activeTab.value === 'read') {
    return notifications.value.filter(n => n.read)
  }
  return notifications.value
})

const toggleDrawer = () => {
  drawerVisible.value = !drawerVisible.value
}

const handleClose = (done: () => void) => {
  done()
}

const handleNotificationClick = (notification: Notification) => {
  if (!notification.read) {
    markAsRead(notification.id)
  }
  
  if (notification.link) {
    // 跳转到相关页面
    window.location.href = notification.link
  }
}

const markAsRead = (id: number) => {
  const notification = notifications.value.find(n => n.id === id)
  if (notification) {
    notification.read = true
  }
}

const markAllAsRead = () => {
  notifications.value.forEach(n => {
    n.read = true
  })
  ElMessage.success('已全部标记为已读')
}

const deleteNotification = (id: number) => {
  const index = notifications.value.findIndex(n => n.id === id)
  if (index > -1) {
    notifications.value.splice(index, 1)
    ElMessage.success('已删除')
  }
}

const clearAll = () => {
  notifications.value = []
  ElMessage.success('已清空所有消息')
}

const formatTime = (time: Date) => {
  const now = new Date()
  const diff = now.getTime() - time.getTime()
  const minutes = Math.floor(diff / 60000)
  const hours = Math.floor(diff / 3600000)
  const days = Math.floor(diff / 86400000)

  if (minutes < 1) return '刚刚'
  if (minutes < 60) return `${minutes}分钟前`
  if (hours < 24) return `${hours}小时前`
  if (days < 7) return `${days}天前`
  return time.toLocaleDateString('zh-CN')
}

// 添加新通知的方法
const addNotification = (notification: Omit<Notification, 'id' | 'time' | 'read'>) => {
  notifications.value.unshift({
    ...notification,
    id: Date.now(),
    time: new Date(),
    read: false
  })
}

defineExpose({
  addNotification
})
</script>

<style scoped>
.notification-badge {
  margin-right: 20px;
}

.notification-header {
  margin-bottom: 20px;
}

.notification-actions {
  display: flex;
  justify-content: flex-end;
  margin-top: 10px;
  gap: 10px;
}

.notification-list {
  max-height: calc(100vh - 200px);
  overflow-y: auto;
}

.notification-item {
  display: flex;
  padding: 16px;
  border-bottom: 1px solid #f0f0f0;
  cursor: pointer;
  transition: all 0.3s;
  background: #fff;
}

.notification-item:hover {
  background: #f5f7fa;
}

.notification-item.is-unread {
  background: #f0f9ff;
}

.notification-icon {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 12px;
  font-size: 20px;
  flex-shrink: 0;
}

.notification-icon.type-success {
  background: #f0f9ff;
  color: #67c23a;
}

.notification-icon.type-warning {
  background: #fef7e6;
  color: #e6a23c;
}

.notification-icon.type-error {
  background: #fef0f0;
  color: #f56c6c;
}

.notification-icon.type-info {
  background: #f0f9ff;
  color: #409eff;
}

.notification-content {
  flex: 1;
  min-width: 0;
}

.notification-title {
  font-size: 14px;
  font-weight: 600;
  color: #303133;
  margin-bottom: 4px;
}

.notification-message {
  font-size: 13px;
  color: #606266;
  margin-bottom: 4px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.notification-time {
  font-size: 12px;
  color: #909399;
}

.notification-actions-btn {
  display: flex;
  flex-direction: column;
  gap: 4px;
  margin-left: 12px;
}

.tab-badge {
  margin-left: 4px;
}
</style>
