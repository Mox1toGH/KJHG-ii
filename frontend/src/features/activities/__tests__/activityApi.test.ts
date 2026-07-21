import { beforeEach, describe, expect, it, vi } from 'vitest'
import type { ActivityRolePayload } from '../core/activity.types'

const apiClientMock = vi.hoisted(() => ({
  delete: vi.fn(),
  get: vi.fn(),
  patch: vi.fn(),
  post: vi.fn(),
}))

vi.mock('@/lib/api/client', () => ({
  default: apiClientMock,
}))

describe('activityApi', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('updates the default role with a nullable role id', async () => {
    const activity = { id: 'activity-1', default_role_id: null }
    apiClientMock.patch.mockResolvedValueOnce({ data: activity })

    const { activityApi } = await import('../core/activity.api')
    await expect(activityApi.update('activity-1', { default_role_id: null })).resolves.toEqual(
      activity,
    )

    expect(apiClientMock.patch).toHaveBeenCalledWith('/activities/activity-1/', {
      default_role_id: null,
    })
  })

  it('creates an activity role with permission scopes intact', async () => {
    const payload: ActivityRolePayload = {
      name: 'Coordinator',
      description: 'Can coordinate the route',
      color: '#3B82F6',
      permissions: [
        { code: 'checkpoints.create' },
        {
          code: 'participants.map.view',
          scope: { visibility: 'roles', role_ids: ['role-1', 'role-2'] },
        },
      ],
    }
    const role = { id: 'role-3', ...payload, permission_grants: [] }
    apiClientMock.post.mockResolvedValueOnce({ data: role })

    const { activityApi } = await import('../core/activity.api')
    await expect(activityApi.createRole('activity-1', payload)).resolves.toEqual(role)

    expect(apiClientMock.post).toHaveBeenCalledWith('/activities/activity-1/roles/', payload)
  })

  it('assigns and clears participant roles through the participant endpoint', async () => {
    const participant = { id: 'participant-1', role: null }
    apiClientMock.patch
      .mockResolvedValueOnce({ data: { ...participant, role: { id: 'role-1' } } })
      .mockResolvedValueOnce({ data: participant })

    const { activityApi } = await import('../core/activity.api')
    await activityApi.assignRole('activity-1', 'participant-1', 'role-1')
    await activityApi.assignRole('activity-1', 'participant-1', null)

    expect(apiClientMock.patch).toHaveBeenNthCalledWith(
      1,
      '/activities/activity-1/participants/participant-1/',
      { role_id: 'role-1' },
    )
    expect(apiClientMock.patch).toHaveBeenNthCalledWith(
      2,
      '/activities/activity-1/participants/participant-1/',
      { role_id: null },
    )
  })

  it('loads incoming and outgoing join requests with the requested direction', async () => {
    apiClientMock.get
      .mockResolvedValueOnce({ data: [{ id: 'join-1' }] })
      .mockResolvedValueOnce({ data: [{ id: 'join-2' }] })

    const { activityApi } = await import('../core/activity.api')
    await expect(activityApi.listJoinRequests('incoming')).resolves.toEqual([{ id: 'join-1' }])
    await expect(activityApi.listJoinRequests('outgoing')).resolves.toEqual([{ id: 'join-2' }])

    expect(apiClientMock.get).toHaveBeenNthCalledWith(
      1,
      '/activities/join-requests/?direction=incoming',
    )
    expect(apiClientMock.get).toHaveBeenNthCalledWith(
      2,
      '/activities/join-requests/?direction=outgoing',
    )
  })
})
