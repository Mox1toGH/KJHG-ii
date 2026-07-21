import { latLngToCell } from 'h3-js'
import { afterEach, beforeEach, describe, expect, it } from 'vitest'
import {
  clearCorruptedCells,
  discoveryFeature,
  getCorruptedCellCount,
  getCorruptedCells,
  safeDiscoveryFeature,
  scratchMapFeatureCollection,
} from '../core/scratchMapGeoJson'
import { mergeScratchDiscoveries } from '../composables/useScratchMapSync'

const discovery = {
  id: 'discovery-1',
  user_id: 42,
  h3_index: latLngToCell(50.45, 30.52, 10),
  discovered_at: '2026-07-18T10:00:00Z',
}

describe('Scratch Map GeoJSON conversion', () => {
  beforeEach(() => {
    clearCorruptedCells()
  })

  afterEach(() => {
    clearCorruptedCells()
  })

  it('converts an H3 cell into a closed GeoJSON polygon', () => {
    const feature = discoveryFeature(discovery)
    const coordinates = feature.geometry.coordinates[0]

    expect(coordinates).toBeDefined()
    if (!coordinates) return

    expect(feature.id).toBe(discovery.h3_index)
    expect(coordinates.length).toBe(7)
    expect(coordinates[0]).toEqual(coordinates[coordinates.length - 1])
  })

  it('ignores invalid H3 cells without throwing', () => {
    expect(safeDiscoveryFeature({ ...discovery, h3_index: 'invalid' })).toBeNull()
  })

  it('tracks corrupted H3 cells', () => {
    const invalidDiscovery = { ...discovery, h3_index: 'invalid' }
    safeDiscoveryFeature(invalidDiscovery)

    expect(getCorruptedCellCount()).toBe(1)
    expect(getCorruptedCells()).toContain('invalid')
  })

  it('clears corrupted cells', () => {
    const invalidDiscovery = { ...discovery, h3_index: 'invalid' }
    safeDiscoveryFeature(invalidDiscovery)

    expect(getCorruptedCellCount()).toBe(1)

    clearCorruptedCells()
    expect(getCorruptedCellCount()).toBe(0)
  })

  it('handles multiple corrupted cells', () => {
    safeDiscoveryFeature({ ...discovery, h3_index: 'invalid1' })
    safeDiscoveryFeature({ ...discovery, h3_index: 'invalid2' })
    safeDiscoveryFeature({ ...discovery, h3_index: 'invalid3' })

    expect(getCorruptedCellCount()).toBe(3)
    expect(getCorruptedCells()).toEqual(['invalid1', 'invalid2', 'invalid3'])
  })

  it('deduplicates discoveries by H3 index before rendering', () => {
    const unique = mergeScratchDiscoveries([discovery], [discovery])
    const collection = scratchMapFeatureCollection(unique)

    expect(unique).toHaveLength(1)
    expect(collection.features).toHaveLength(1)
  })

  it('excludes corrupted cells from feature collection', () => {
    const discoveries = [
      discovery,
      { ...discovery, h3_index: 'invalid' },
      { ...discovery, h3_index: latLngToCell(50.46, 30.53, 10) },
    ]

    const collection = scratchMapFeatureCollection(discoveries)

    expect(collection.features).toHaveLength(2) // Only valid cells
    expect(getCorruptedCellCount()).toBe(1)
  })
})
