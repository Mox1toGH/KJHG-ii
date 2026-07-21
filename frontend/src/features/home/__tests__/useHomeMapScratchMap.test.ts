import { describe, expect, it, vi } from 'vitest'
import { ref } from 'vue'
import type { ScratchDiscovery } from '@/features/exploration/core/scratchMap.types'
import {
  scratchMapFeatureCollection,
  safeDiscoveryFeature,
} from '@/features/exploration/core/scratchMapGeoJson'

describe('useHomeMap Scratch Map rendering synchronization', () => {
  it('handles incremental updates correctly', () => {
    const discoveries: ScratchDiscovery[] = [
      {
        id: '1',
        user_id: 42,
        h3_index: '8a1f1d48b287fff',
        discovered_at: '2026-07-18T10:00:00Z',
      },
    ]

    const collection = scratchMapFeatureCollection(discoveries)
    expect(collection.features).toHaveLength(1)

    // Add new discovery
    discoveries.push({
      id: '2',
      user_id: 42,
      h3_index: '8a1f1d48b28ffff',
      discovered_at: '2026-07-18T10:01:00Z',
    })

    const updatedCollection = scratchMapFeatureCollection(discoveries)
    expect(updatedCollection.features).toHaveLength(2)
  })

  it('handles corrupted cells without breaking rendering', () => {
    const discoveries: ScratchDiscovery[] = [
      {
        id: '1',
        user_id: 42,
        h3_index: '8a1f1d48b287fff',
        discovered_at: '2026-07-18T10:00:00Z',
      },
      {
        id: '2',
        user_id: 42,
        h3_index: 'invalid-cell',
        discovered_at: '2026-07-18T10:01:00Z',
      },
      {
        id: '3',
        user_id: 42,
        h3_index: '8a1f1d48b28ffff',
        discovered_at: '2026-07-18T10:02:00Z',
      },
    ]

    const collection = scratchMapFeatureCollection(discoveries)
    // Should only render valid cells
    expect(collection.features).toHaveLength(2)
  })

  it('maintains rendering order deterministically', () => {
    const discoveries: ScratchDiscovery[] = [
      {
        id: '3',
        user_id: 42,
        h3_index: '8a1f1d48b28ffff',
        discovered_at: '2026-07-18T10:02:00Z',
      },
      {
        id: '1',
        user_id: 42,
        h3_index: '8a1f1d48b287fff',
        discovered_at: '2026-07-18T10:00:00Z',
      },
      {
        id: '2',
        user_id: 42,
        h3_index: '8a1f1d48b287eff',
        discovered_at: '2026-07-18T10:01:00Z',
      },
    ]

    const collection1 = scratchMapFeatureCollection(discoveries)
    const collection2 = scratchMapFeatureCollection(discoveries)

    // Order should be consistent
    expect(collection1.features.map(f => f.id)).toEqual(
      collection2.features.map(f => f.id)
    )
  })

  it('handles empty discovery list', () => {
    const discoveries: ScratchDiscovery[] = []
    const collection = scratchMapFeatureCollection(discoveries)

    expect(collection.features).toHaveLength(0)
    expect(collection.type).toBe('FeatureCollection')
  })

  it('handles large number of discoveries without performance issues', () => {
    const discoveries: ScratchDiscovery[] = Array.from({ length: 100 }, (_, i) => ({
      id: `discovery-${i}`,
      user_id: 42,
      h3_index: '8a1f1d48b287fff', // Use valid H3 index for all
      discovered_at: '2026-07-18T10:00:00Z',
    }))

    const start = performance.now()
    const collection = scratchMapFeatureCollection(discoveries)
    const end = performance.now()

    expect(collection.features).toHaveLength(100)
    expect(end - start).toBeLessThan(100) // Should complete in < 100ms
  })
})
