import axios from 'axios'
import { ElMessage, ElMessageBox } from 'element-plus'

const client = axios.create({
  baseURL: '/api',
  timeout: 600000
})

// Attach user's API key from localStorage to every request
client.interceptors.request.use(config => {
  const key = localStorage.getItem('sm_ds_key')
  if (key) {
    config.headers = config.headers || {}
    config.headers['X-Api-Key'] = key
  }
  return config
})

function isAuthError(msg) {
  const m = (msg || '').toLowerCase()
  return m.includes('authentication') || m.includes('governor') || m.includes('unauthorized') || m.includes('api key')
}

client.interceptors.response.use(
  response => {
    const data = response.data
    if (data.code === 200) return data.data
    return Promise.reject(new Error(data.message || '请求失败'))
  },
  error => {
    const msg = error.response?.data?.message || error.message || '网络错误'
    if (isAuthError(msg)) {
      ElMessageBox.alert('API Key 无效或未配置，请填写有效的 DeepSeek API Key。', '认证失败', {
        confirmButtonText: '去设置',
        type: 'warning',
      }).then(() => {
        window.dispatchEvent(new CustomEvent('open-settings'))
      }).catch(() => {})
      return Promise.reject(new Error('API Key 认证失败'))
    }
    return Promise.reject(new Error(msg))
  }
)

export default client
