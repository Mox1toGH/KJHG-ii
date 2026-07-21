export interface ScratchDiscovery {
  id: string
  user_id: number
  h3_index: string
  discovered_at: string
}

export interface ScratchMapStatistics {
  total_discovered_cells: number
  today_discoveries: number
  weekly_discoveries: number
  monthly_discoveries: number
  total_explored_area_km2: number
}

export interface ScratchMapDiscoveryResponse {
  count: number
  next: string | null
  previous: string | null
  results: ScratchDiscovery[]
}

export interface ScratchMapDiscoverResponse {
  discovery: ScratchDiscovery
  created: boolean
}

export type ScratchMapSocketMessage =
  | {
      event: 'scratch_map.cell_discovered'
      payload: { discovery: ScratchDiscovery }
    }
  | {
      event: 'scratch_map.statistics_updated'
      payload: { statistics: ScratchMapStatistics }
    }
