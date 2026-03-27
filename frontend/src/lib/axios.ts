import axios from 'axios'

const API_URL = import.meta.env.VITE_API_URL || ''

// Create axios instance with default config
export const api = axios.create({
    baseURL: API_URL ? `${API_URL}/api/v1` : '/api/v1',
    timeout: 120000,  // 增加到 120 秒，適應 AI 分析需求
    headers: {
        'Content-Type': 'application/json',
    },
})

// Request interceptor - add auth token
api.interceptors.request.use(
    (config) => {
        const token = localStorage.getItem('access_token')
        if (token) {
            config.headers.Authorization = `Bearer ${token}`
        }
        return config
    },
    (error) => {
        return Promise.reject(error)
    }
)

// Response interceptor - handle errors and token refresh
api.interceptors.response.use(
    (response) => response,
    async (error) => {
        const originalRequest = error.config

        // If 401 and not already retried, try to refresh token
        if (error.response?.status === 401 && !originalRequest._retry) {
            originalRequest._retry = true

            try {
                const refreshToken = localStorage.getItem('refresh_token')
                if (refreshToken) {
                    // TODO: Implement refresh token endpoint
                    // const response = await axios.post('/api/v1/auth/refresh', { refresh_token: refreshToken })
                    // localStorage.setItem('access_token', response.data.access_token)
                    // originalRequest.headers.Authorization = `Bearer ${response.data.access_token}`
                    // return api(originalRequest)
                }
            } catch (refreshError) {
                // Refresh failed, logout user
                localStorage.removeItem('access_token')
                localStorage.removeItem('refresh_token')
                window.location.href = '/login'
                return Promise.reject(refreshError)
            }
        }

        return Promise.reject(error)
    }
)

export default api
