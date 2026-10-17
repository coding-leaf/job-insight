import axios, { type AxiosInstance, type AxiosResponse } from 'axios'
import { ElMessage } from 'element-plus'
import type { ResponseModel } from '@/types/api'

const client: AxiosInstance = axios.create({
  baseURL: '/api/v1',
  timeout: 15000,
  headers: {
    'Content-Type': 'application/json'
  }
})

client.interceptors.response.use(
  (response: AxiosResponse<ResponseModel<unknown>>) => {
    const res = response.data
    // Backend returns ResponseModel with code 200 on success
    if (res.code !== 200) {
      const msg = res.message || '请求处理失败'
      ElMessage.error(msg)
      return Promise.reject(new Error(msg))
    }
    return response
  },
  (error: unknown) => {
    let message = '网络请求异常，请稍后重试'
    if (axios.isAxiosError(error)) {
      message = error.response?.data?.message || error.message || message
    } else if (error instanceof Error) {
      message = error.message
    }
    ElMessage.error(message)
    return Promise.reject(error)
  }
)

export default client
