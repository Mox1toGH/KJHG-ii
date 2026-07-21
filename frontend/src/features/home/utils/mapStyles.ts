import type maplibregl from 'maplibre-gl'

export type BaseLayer = 'sat' | 'osm' | 'carto'

export function baseLayerStyle(name: BaseLayer): maplibregl.StyleSpecification {
  if (name === 'sat') {
    return {
      version: 8,
      sources: {
        satellite: {
          type: 'raster',
          tiles: [
            'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
          ],
          tileSize: 256,
        },
      },
      layers: [{ id: 'sat-tiles', type: 'raster', source: 'satellite' }],
    }
  }

  if (name === 'carto') {
    return {
      version: 8,
      sources: {
        carto: {
          type: 'raster',
          tiles: [
            'https://a.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}.png',
            'https://b.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}.png',
            'https://c.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}.png',
          ],
          tileSize: 256,
        },
      },
      layers: [{ id: 'carto-tiles', type: 'raster', source: 'carto' }],
    }
  }

  return {
    version: 8,
    sources: {
      osm: {
        type: 'raster',
        tiles: [
          'https://a.tile.openstreetmap.org/{z}/{x}/{y}.png',
          'https://b.tile.openstreetmap.org/{z}/{x}/{y}.png',
        ],
        tileSize: 256,
      },
    },
    layers: [{ id: 'osm-tiles', type: 'raster', source: 'osm' }],
  }
}
