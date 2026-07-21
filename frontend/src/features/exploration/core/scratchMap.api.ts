import apiClient from '@/lib/api/client'
import type {
  ScratchDiscovery,
  ScratchMapDiscoveryResponse,
  ScratchMapDiscoverResponse,
  ScratchMapStatistics,
} from './scratchMap.types'

const PAGE_SIZE = 5000

export const scratchMapApi = {
  discover: (latitude: number, longitude: number) =>
    apiClient
      .post<ScratchMapDiscoverResponse>('/homemap/discover/', { latitude, longitude })
      .then(({ data }) => data),

  async listDiscoveries(): Promise<ScratchDiscovery[]> {
    const discoveries: ScratchDiscovery[] = []
    let offset = 0

    while (true) {
      const { data } = await apiClient.get<ScratchMapDiscoveryResponse>('/homemap/discovered/', {
        params: { limit: PAGE_SIZE, offset },
      })
      discoveries.push(...data.results)
      if (!data.next || data.results.length === 0) break
      offset += data.results.length
    }

    return discoveries
  },

  statistics: () =>
    apiClient.get<ScratchMapStatistics>('/homemap/statistics/').then(({ data }) => data),
}
