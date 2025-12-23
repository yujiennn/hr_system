import { createApp, h } from 'vue'
import { ElMessageBox } from 'element-plus'
import 'element-plus/es/components/message-box/style/css'

interface ConfirmOptions {
  title?: string
  message: string
  description?: string
  type?: 'warning' | 'danger' | 'info' | 'success'
  confirmButtonText?: string
  cancelButtonText?: string
  dangerouslyUseHTMLString?: boolean
}

/**
 * 显示确认对话框
 */
export const showConfirm = (options: ConfirmOptions): Promise<any> => {
  const {
    title = '确认操作',
    message,
    description,
    type = 'warning',
    confirmButtonText = '确定',
    cancelButtonText = '取消',
    dangerouslyUseHTMLString = false
  } = options

  const messageContent = description 
    ? `<div style="font-size: 16px; font-weight: 600; margin-bottom: 8px;">${message}</div><div style="font-size: 14px; color: #606266;">${description}</div>`
    : message

  // 将 danger 转换为 error，这是 Element Plus 支持的类型
  const messageType = type === 'danger' ? 'error' : type

  return ElMessageBox.confirm(
    messageContent,
    title,
    {
      confirmButtonText,
      cancelButtonText,
      type: messageType,
      dangerouslyUseHTMLString: description ? true : dangerouslyUseHTMLString,
      center: false,
      customClass: 'custom-confirm-dialog',
      confirmButtonClass: type === 'danger' ? 'el-button--danger' : '',
      showClose: false,
      closeOnClickModal: false,
      closeOnPressEscape: false
    }
  )
}

/**
 * 显示删除确认对话框
 */
export const showDeleteConfirm = (itemName: string = '该项'): Promise<any> => {
  return showConfirm({
    title: '确认删除',
    message: `确定要删除${itemName}吗？`,
    description: '此操作不可撤销，删除后数据将无法恢复。',
    type: 'danger',
    confirmButtonText: '确认删除',
    cancelButtonText: '取消'
  })
}

/**
 * 显示批量删除确认对话框
 */
export const showBatchDeleteConfirm = (count: number): Promise<any> => {
  return showConfirm({
    title: '批量删除确认',
    message: `确定要删除选中的 ${count} 项吗？`,
    description: '此操作不可撤销，删除后数据将无法恢复。',
    type: 'danger',
    confirmButtonText: '确认删除',
    cancelButtonText: '取消'
  })
}

/**
 * 显示危险操作确认对话框（需要输入确认）
 */
export const showDangerConfirm = async (
  message: string,
  description?: string
): Promise<boolean> => {
  try {
    await ElMessageBox.confirm(
      description || '此操作具有风险，请谨慎操作。',
      message,
      {
        confirmButtonText: '我已了解风险，继续操作',
        cancelButtonText: '取消',
        type: 'error',
        customClass: 'danger-confirm-dialog',
        showClose: false,
        closeOnClickModal: false,
        closeOnPressEscape: false
      }
    )
    return true
  } catch {
    return false
  }
}

export default {
  showConfirm,
  showDeleteConfirm,
  showBatchDeleteConfirm,
  showDangerConfirm
}
