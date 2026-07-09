import axios from 'axios'

const client = axios.create({
  baseURL: '/api',
})

// 请求拦截：附加 access token
client.interceptors.request.use((config) => {
  const token = localStorage.getItem('access')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// 响应拦截：access 过期时用 refresh 自动续期一次
let refreshing = null

client.interceptors.response.use(
  (response) => response,
  async (error) => {
    const original = error.config
    const refresh = localStorage.getItem('refresh')
    if (
      error.response &&
      error.response.status === 401 &&
      refresh &&
      !original._retry
    ) {
      original._retry = true
      try {
        if (!refreshing) {
          refreshing = axios
            .post('/api/auth/refresh/', { refresh })
            .then((res) => {
              localStorage.setItem('access', res.data.access)
              return res.data.access
            })
            .finally(() => {
              refreshing = null
            })
        }
        const newAccess = await refreshing
        original.headers.Authorization = `Bearer ${newAccess}`
        return client(original)
      } catch (e) {
        localStorage.removeItem('access')
        localStorage.removeItem('refresh')
        window.location.href = '/login'
      }
    }
    return Promise.reject(error)
  },
)

export default client
