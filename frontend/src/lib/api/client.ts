import axios, { AxiosHeaders } from 'axios'
import { getCurrentLanguage } from '../i18n'

const csrfCookieName = 'csrftoken'
const csrfHeaderName = 'X-CSRFToken'
const unsafeMethods = new Set(['post', 'put', 'patch', 'delete'])

let csrfToken: string | undefined

function getCookie(name: string) {
  if (typeof document === 'undefined') {
    return undefined
  }

  return document.cookie
    .split('; ')
    .find((cookie) => cookie.startsWith(`${name}=`))
    ?.split('=')
    .slice(1)
    .join('=')
}

function getCsrfToken() {
  const cookieToken = getCookie(csrfCookieName)
  return cookieToken ? decodeURIComponent(cookieToken) : csrfToken
}

const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL ?? '/api',
  withCredentials: true,
  xsrfCookieName: csrfCookieName,
  xsrfHeaderName: csrfHeaderName,
})

let refreshPromise: Promise<unknown> | undefined

apiClient.interceptors.request.use((config) => {
  const method = config.method?.toLowerCase()

  if (method && unsafeMethods.has(method)) {
    const token = getCsrfToken()

    if (token) {
      const headers = AxiosHeaders.from(config.headers)
      headers.set(csrfHeaderName, token)
      config.headers = headers
    }
  }

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
    if (response.config.url?.includes('/accounts/csrf/')) {
      const token = response.data?.csrfToken

      if (typeof token === 'string' && token.length > 0) {
        csrfToken = token
      }
    }

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
