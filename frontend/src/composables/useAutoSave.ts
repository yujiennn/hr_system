import { ref, watch, onUnmounted } from 'vue'
import { ElMessageBox } from 'element-plus'

interface AutoSaveOptions {
  key: string // 本地存储的键名
  delay?: number // 延迟保存时间（毫秒）
  onSave?: (data: any) => void // 保存回调
  enabled?: boolean // 是否启用自动保存
}

/**
 * 表单自动保存组合式函数
 */
export function useAutoSave<T extends Record<string, any>>(
  formData: T,
  options: AutoSaveOptions
) {
  const {
    key,
    delay = 2000,
    onSave,
    enabled = true
  } = options

  const isSaving = ref(false)
  const lastSaveTime = ref<Date | null>(null)
  let saveTimer: number | null = null

  // 保存到本地存储
  const saveToLocal = () => {
    if (!enabled) return

    try {
      const dataToSave = {
        data: formData,
        timestamp: new Date().toISOString()
      }
      localStorage.setItem(key, JSON.stringify(dataToSave))
      lastSaveTime.value = new Date()
      
      if (onSave) {
        onSave(formData)
      }
    } catch (error) {
      console.error('自动保存失败:', error)
    } finally {
      isSaving.value = false
    }
  }

  // 从本地存储恢复数据
  const restoreFromLocal = (): T | null => {
    try {
      const saved = localStorage.getItem(key)
      if (saved) {
        const parsed = JSON.parse(saved)
        return parsed.data
      }
    } catch (error) {
      console.error('恢复数据失败:', error)
    }
    return null
  }

  // 清除保存的数据
  const clearSaved = () => {
    localStorage.removeItem(key)
    lastSaveTime.value = null
  }

  // 触发保存
  const triggerSave = () => {
    if (!enabled) return

    isSaving.value = true
    
    if (saveTimer) {
      clearTimeout(saveTimer)
    }

    saveTimer = window.setTimeout(() => {
      saveToLocal()
    }, delay)
  }

  // 监听表单数据变化
  watch(
    () => formData,
    () => {
      triggerSave()
    },
    { deep: true }
  )

  // 组件卸载时清除定时器
  onUnmounted(() => {
    if (saveTimer) {
      clearTimeout(saveTimer)
    }
  })

  return {
    isSaving,
    lastSaveTime,
    restoreFromLocal,
    clearSaved,
    triggerSave
  }
}

/**
 * 检查是否有未保存的草稿
 */
export function checkDraft(key: string): boolean {
  const saved = localStorage.getItem(key)
  return !!saved
}

/**
 * 显示恢复草稿提示
 */
export async function showRestorePrompt(key: string): Promise<boolean> {
  try {
    const saved = localStorage.getItem(key)
    if (!saved) return false

    const parsed = JSON.parse(saved)
    const savedTime = new Date(parsed.timestamp)
    const timeAgo = getTimeAgo(savedTime)

    await ElMessageBox.confirm(
      `检测到 ${timeAgo} 的草稿，是否恢复？`,
      '恢复草稿',
      {
        confirmButtonText: '恢复',
        cancelButtonText: '放弃',
        type: 'info'
      }
    )

    return true
  } catch {
    return false
  }
}

function getTimeAgo(date: Date): string {
  const now = new Date()
  const diff = now.getTime() - date.getTime()
  const minutes = Math.floor(diff / 60000)
  const hours = Math.floor(diff / 3600000)
  const days = Math.floor(diff / 86400000)

  if (minutes < 1) return '刚刚'
  if (minutes < 60) return `${minutes}分钟前`
  if (hours < 24) return `${hours}小时前`
  return `${days}天前`
}

export default useAutoSave
