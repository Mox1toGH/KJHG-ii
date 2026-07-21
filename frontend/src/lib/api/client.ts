import axios, { AxiosHeaders } from 'axios'
import { getCurrentLanguage } from '../i18n'

const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL ?? '/api',
  withCredentials: true,
})

let refreshPromise: Promise<unknown> | undefined

apiClient.interceptors.request.use((config) => {
  // Add Accept-Language header
  const headers = AxiosHeaders.from(config.headers)
  headers.set('Accept-Language', getCurrentLanguage())
  config.headers = headers

  return config
})

const AUTH_ENDPOINTS = [
  '/accounts/refresh/',
  '/accounts/login/',
  '/accounts/google/',
  '/accounts/logout/',
]

apiClient.interceptors.response.use(
  (response) => {
    return response
  },
  async (error) => {
    const config = error.config as (typeof error.config & { _retry?: boolean }) | undefined
    const url = config?.url ?? ''

    if (
      error.response?.status !== 401 ||
      !config ||
      config._retry ||
      AUTH_ENDPOINTS.some((ep) => url.includes(ep))
    ) {
      return Promise.reject(error)
    }

    config._retry = true
    refreshPromise ??= apiClient.post('/accounts/refresh/').finally(() => {
      refreshPromise = undefined
    })

    try {
      await refreshPromise
      return apiClient(config)
    } catch {
      return Promise.reject(error)
    }
  },
)

export default apiClient
