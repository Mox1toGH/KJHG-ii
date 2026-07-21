import { beforeEach, describe, expect, it, vi } from 'vitest'

const apiClientMock = vi.hoisted(() => ({
  get: vi.fn(),
  post: vi.fn(),
}))

vi.mock('@/lib/api/client', () => ({
  default: apiClientMock,
}))

describe('scratchMapApi', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('posts user coordinates to discover a scratch-map cell', async () => {
    const response = {
      discovery: {
        id: 'discovery-1',
        user_id: 42,
        h3_index: '8a1f1d48b287fff',
        discovered_at: '2026-07-18T10:00:00Z',
      },
      created: true,
    }
    apiClientMock.post.mockResolvedValueOnce({ data: response })

    const { scratchMapApi } = await import('../core/scratchMap.api')
    await expect(scratchMapApi.discover(50.45, 30.52)).resolves.toEqual(response)

    expect(apiClientMock.post).toHaveBeenCalledWith('/homemap/discover/', {
      latitude: 50.45,
      longitude: 30.52,
    })
  })

  it('loads every discovery page until the API has no next page', async () => {
    const firstDiscovery = {
      id: 'discovery-1',
      user_id: 42,
      h3_index: '8a1f1d48b287fff',
      discovered_at: '2026-07-18T10:00:00Z',
    }
    const secondDiscovery = {
      id: 'discovery-2',
      user_id: 42,
      h3_index: '8a1f1d48b28ffff',
      discovered_at: '2026-07-18T10:01:00Z',
    }
    apiClientMock.get
      .mockResolvedValueOnce({ data: { next: 'next-page', results: [firstDiscovery] } })
      .mockResolvedValueOnce({ data: { next: null, results: [secondDiscovery] } })

    const { scratchMapApi } = await import('../core/scratchMap.api')
    await expect(scratchMapApi.listDiscoveries()).resolves.toEqual([
      firstDiscovery,
      secondDiscovery,
    ])

    expect(apiClientMock.get).toHaveBeenNthCalledWith(1, '/homemap/discovered/', {
      params: { limit: 5000, offset: 0 },
    })
    expect(apiClientMock.get).toHaveBeenNthCalledWith(2, '/homemap/discovered/', {
      params: { limit: 5000, offset: 1 },
    })
  })

  it('loads scratch-map statistics', async () => {
    const statistics = { discovered_cells: 12, discovered_area_sq_m: 3456 }
    apiClientMock.get.mockResolvedValueOnce({ data: statistics })

    const { scratchMapApi } = await import('../core/scratchMap.api')
    await expect(scratchMapApi.statistics()).resolves.toEqual(statistics)

    expect(apiClientMock.get).toHaveBeenCalledWith('/homemap/statistics/')
  })
})
