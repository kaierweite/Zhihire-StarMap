import axios from 'axios'
import type { AxiosInstance, InternalAxiosRequestConfig, AxiosResponse } from 'axios'
import { ElMessage } from 'element-plus'
import { useAuthStore } from '@/store/auth'
import router from '@/router'
import type { ApiResponse } from '@/types/api'

// 添加 silentError 支持：设为 true 时全局不弹错误消息
declare module 'axios' {
  interface InternalAxiosRequestConfig {
    _silentError?: boolean
  }
}

const service: AxiosInstance = axios.create({
  baseURL: '/api',
  timeout: 15000,
  headers: { 'Content-Type': 'application/json' },
})

// ========== 请求拦截器：自动附加 JWT token ==========
service.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    const authStore = useAuthStore()
    if (authStore.token) {
      config.headers.Authorization = `Bearer ${authStore.token}`
    }
    return config
  },
  (error) => Promise.reject(error),
)

// ========== 响应拦截器：统一错误处理 ==========
service.interceptors.response.use(
  (response: AxiosResponse<ApiResponse>) => {
    const res = response.data

    if (response.status === 204) {
      return response
    }

    if (!res) {
      ElMessage.error('响应数据为空')
      return Promise.reject(new Error('响应数据为空'))
    }

    // 静默模式：直接 reject 不弹全局提示
    if ((response.config as any)?._silentError) {
      if (res.code !== 200) {
        return Promise.reject(new Error(res.message || '请求失败'))
      }
      return response
    }

    // 后端约定：code !== 200 表示失败，弹全局提示
    if (res.code !== 200) {
      ElMessage.error(res.message || '请求失败')

      // 401 — token 过期或无效
      if (res.code === 401) {
        const authStore = useAuthStore()
        authStore.logout()
        router.push('/login')
      }

      return Promise.reject(new Error(res.message || '请求失败'))
    }

    return response
  },
  (error) => {
    if (error.response?.status === 401) {
      const authStore = useAuthStore()
      authStore.logout()
      router.push('/login')
    } else if (error.response?.status === 403) {
      ElMessage.error('没有权限访问')
    } else if (error.response?.status >= 500) {
      ElMessage.error('服务器错误，请稍后重试')
    } else if (error.code === 'ECONNABORTED') {
      ElMessage.error('请求超时')
    } else {
      ElMessage.error(error.message || '网络错误')
    }
    return Promise.reject(error)
  },
)

export default service
