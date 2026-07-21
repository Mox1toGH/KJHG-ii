import apiClient from '@/lib/api/client'
import type {
  AddFriendPayload,
  ChangePasswordPayload,
  CsrfResponse,
  DeleteAccountPayload,
  DetailResponse,
  EmailResendPayload,
  EmailVerificationPayload,
  Friend,
  FriendStatusResponse,
  GoogleLoginPayload,
  LoginPayload,
  PasswordResetConfirmPayload,
  PasswordResetPayload,
  PublicUser,
  RegisterPayload,
  SetCurrentStatusPayload,
  UserStatus,
  UpdateProfilePayload,
  UserProfile,
} from './auth.types'

let csrfPromise: Promise<CsrfResponse | DetailResponse> | undefined

function hasCsrfCookie() {
  return typeof document !== 'undefined' && document.cookie.includes('csrftoken=')
}

function ensureCsrfCookie() {
  if (hasCsrfCookie()) {
    return Promise.resolve({ detail: 'CSRF cookie already set' })
  }

  csrfPromise ??= apiClient
    .get<CsrfResponse>('/accounts/csrf/')
    .then((r) => r.data)
    .finally(() => {
      csrfPromise = undefined
    })

  return csrfPromise
}

async function withCsrf<T>(request: () => Promise<T>) {
  await ensureCsrfCookie()
  return request()
}

export const authApi = {
  ensureCsrfCookie,

  getCurrentUser: () => apiClient.get<UserProfile>('/accounts/profile/').then((r) => r.data),

  getPublicUserProfile: (username: string) =>
    apiClient.get<PublicUser>(`/accounts/${encodeURIComponent(username)}/`).then((r) => r.data),

  register: (payload: RegisterPayload) =>
    withCsrf(() =>
      apiClient.post<DetailResponse>('/accounts/register/', payload).then((r) => r.data),
    ),

  login: (payload: LoginPayload) =>
    withCsrf(() => apiClient.post<DetailResponse>('/accounts/login/', payload).then((r) => r.data)),

  refresh: () =>
    withCsrf(() => apiClient.post<DetailResponse>('/accounts/refresh/').then((r) => r.data)),

  googleLogin: (payload: GoogleLoginPayload) =>
    withCsrf(() =>
      apiClient.post<DetailResponse>('/accounts/google/', payload).then((r) => r.data),
    ),

  logout: () =>
    withCsrf(() => apiClient.post<DetailResponse>('/accounts/logout/').then((r) => r.data)),

  verifyEmail: (payload: EmailVerificationPayload) =>
    withCsrf(() =>
      apiClient.post<DetailResponse>('/accounts/email/verify/', payload).then((r) => r.data),
    ),

  resendVerificationEmail: (payload: EmailResendPayload) =>
    withCsrf(() =>
      apiClient.post<DetailResponse>('/accounts/email/resend/', payload).then((r) => r.data),
    ),

  requestPasswordReset: (payload: PasswordResetPayload) =>
    withCsrf(() =>
      apiClient.post<DetailResponse>('/accounts/password/reset/', payload).then((r) => r.data),
    ),

  confirmPasswordReset: (payload: PasswordResetConfirmPayload) =>
    withCsrf(() =>
      apiClient
        .post<DetailResponse>('/accounts/password/reset/confirm/', payload)
        .then((r) => r.data),
    ),

  changePassword: (payload: ChangePasswordPayload) =>
    withCsrf(() =>
      apiClient.post<DetailResponse>('/accounts/password/change/', payload).then((r) => r.data),
    ),

  updateProfile: (payload: UpdateProfilePayload) => {
    const data = new FormData()
    Object.entries(payload).forEach(([key, value]) => {
      if (value instanceof File) data.append(key, value)
      else if (value !== undefined && value !== null) data.append(key, value)
    })
    return withCsrf(() =>
      apiClient.patch<UserProfile>('/accounts/profile/', data).then((r) => r.data),
    )
  },

  deleteAccount: (payload: DeleteAccountPayload) =>
    withCsrf(() => apiClient.delete('/accounts/profile/', { data: payload }).then(() => undefined)),

  getStatuses: () => apiClient.get<UserStatus[]>('/accounts/statuses/').then((r) => r.data),

  createStatus: (name: string) =>
    withCsrf(() => apiClient.post<UserStatus>('/accounts/statuses/', { name }).then((r) => r.data)),

  deleteStatus: (id: number) =>
    withCsrf(() => apiClient.delete(`/accounts/statuses/${id}/`).then(() => undefined)),

  setCurrentStatus: (payload: SetCurrentStatusPayload) =>
    withCsrf(() =>
      apiClient.post<UserProfile>('/accounts/status/current/', payload).then((r) => r.data),
    ),

  getFriends: () => apiClient.get<Friend[]>('/accounts/friends/').then((r) => r.data),

  addFriend: (payload: AddFriendPayload) =>
    withCsrf(() => apiClient.post<Friend>('/accounts/friends/', payload).then((r) => r.data)),

  removeFriend: (friendId: number) =>
    withCsrf(() => apiClient.delete(`/accounts/friends/${friendId}/`).then(() => undefined)),

  checkFriendStatus: (userId: number) =>
    apiClient.get<FriendStatusResponse>(`/accounts/friends/status/${userId}/`).then((r) => r.data),

  getFriendRequests: () => apiClient.get<Friend[]>('/accounts/friends/requests/').then((r) => r.data),

  acceptFriendRequest: (requestId: number) =>
    withCsrf(() =>
      apiClient.patch<Friend>(`/accounts/friends/requests/${requestId}/accept/`).then((r) => r.data),
    ),

  rejectFriendRequest: (requestId: number) =>
    withCsrf(() =>
      apiClient.patch<Friend>(`/accounts/friends/requests/${requestId}/reject/`).then((r) => r.data),
    ),
}
