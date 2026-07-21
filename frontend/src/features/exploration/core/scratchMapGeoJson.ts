import { cellToBoundary, isValidCell } from 'h3-js'
import type { ScratchDiscovery } from './scratchMap.types'

const corruptedCells = new Set<string>()

export type ScratchMapFeature = {
  type: 'Feature'
  id: string
  geometry: {
    type: 'Polygon'
    coordinates: [number, number][][]
  }
  properties: { h3_index: string; discovered_at: string }
}

export type ScratchMapFeatureCollection = {
  type: 'FeatureCollection'
  features: ScratchMapFeature[]
}

export function discoveryFeature(discovery: ScratchDiscovery): ScratchMapFeature {
  if (!isValidCell(discovery.h3_index)) {
    throw new Error(`Invalid H3 index ${discovery.h3_index}`)
  }
  const boundary = cellToBoundary(discovery.h3_index, true) as [number, number][]
  const first = boundary[0]
  if (!first || boundary.length < 3) {
    throw new Error(`Invalid H3 boundary for ${discovery.h3_index}`)
  }
  const last = boundary[boundary.length - 1]
  const closedBoundary =
    last?.[0] === first[0] && last?.[1] === first[1] ? boundary : [...boundary, first]

  return {
    type: 'Feature',
    id: discovery.h3_index,
    geometry: { type: 'Polygon', coordinates: [closedBoundary] },
    properties: {
      h3_index: discovery.h3_index,
      discovered_at: discovery.discovered_at,
    },
  }
}

export function safeDiscoveryFeature(discovery: ScratchDiscovery): ScratchMapFeature | null {
  try {
    return discoveryFeature(discovery)
  } catch (error) {
    console.error('[scratch-map] invalid H3 cell', discovery.h3_index, error)
    corruptedCells.add(discovery.h3_index)
    return null
  }
}

export function getCorruptedCellCount(): number {
  return corruptedCells.size
}

export function getCorruptedCells(): string[] {
  return Array.from(corruptedCells)
}

export function clearCorruptedCells(): void {
  corruptedCells.clear()
}

export function scratchMapFeatureCollection(
  discoveries: readonly ScratchDiscovery[],
): ScratchMapFeatureCollection {
  return {
    type: 'FeatureCollection',
    features: discoveries.flatMap((discovery) => {
      const feature = safeDiscoveryFeature(discovery)
      return feature ? [feature] : []
    }),
  }
}
