import { App, createApp } from 'vue'
import ProgressBar from '@/components/ProgressBar.vue'

let progressBarInstance: any = null
let progressBarApp: App | null = null

export const useProgressBar = () => {
  if (!progressBarInstance) {
    const container = document.createElement('div')
    document.body.appendChild(container)
    
    progressBarApp = createApp(ProgressBar)
    progressBarInstance = progressBarApp.mount(container)
  }

  return {
    start: () => progressBarInstance?.start(),
    finish: () => progressBarInstance?.finish(),
    fail: () => progressBarInstance?.fail()
  }
}

export default useProgressBar
