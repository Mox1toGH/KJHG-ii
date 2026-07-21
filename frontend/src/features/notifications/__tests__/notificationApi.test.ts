import { beforeEach, describe, expect, it, vi } from 'vitest'

const apiClientMock = vi.hoisted(() => ({
  delete: vi.fn(),
  get: vi.fn(),
  post: vi.fn(),
  put: vi.fn(),
}))

vi.mock('@/lib/api/client', () => ({
  default: apiClientMock,
}))

describe('notificationApi', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('loads notification preferences from the preferences endpoint', async () => {
    const preferences = { email_enabled: true, in_app_enabled: true }
    apiClientMock.get.mockResolvedValueOnce({ data: preferences })

    const { notificationApi } = await import('../core/notification.api')
    await expect(notificationApi.getPreferences()).resolves.toEqual(preferences)

    expect(apiClientMock.get).toHaveBeenCalledWith('/notifications/preferences/')
  })

  it('updates notification preferences with a partial payload', async () => {
    const payload = { email_enabled: false }
    const updated = { email_enabled: false, in_app_enabled: true }
    apiClientMock.put.mockResolvedValueOnce({ data: updated })

    const { notificationApi } = await import('../core/notification.api')
    await expect(notificationApi.updatePreferences(payload)).resolves.toEqual(updated)

    expect(apiClientMock.put).toHaveBeenCalledWith('/notifications/preferences/', payload)
  })

  it('marks all notifications as read without returning response data', async () => {
    apiClientMock.post.mockResolvedValueOnce({ data: { ignored: true } })

    const { notificationApi } = await import('../core/notification.api')
    await expect(notificationApi.markAllRead()).resolves.toBeUndefined()

    expect(apiClientMock.post).toHaveBeenCalledWith('/notifications/read-all/')
  })
})
