import { ref, type Ref } from 'vue'
import maplibregl from 'maplibre-gl'
import type { Checkpoint, Route, Visit } from '@/features/checkpoints'
import { createdByMarkup } from './mapPopupCreator'

type CheckpointAction = 'checkin' | 'edit' | 'delete' | 'photos' | 'qr'

type UseMapCheckpointsOptions = {
  checkpoints?: Ref<Checkpoint[]>
  routes?: Ref<Route[]>
  visits?: Ref<Visit[]>
  mapReady: Ref<boolean>
  getMap: () => maplibregl.Map | null
  getMarkerPopup: () => maplibregl.Popup | null
  setMarkerPopup: (popup: maplibregl.Popup | null) => void
  onRoutePointClick?: (id: string) => void
  onCheckpointAction?: (
    kind: 'checkpoint' | 'route',
    id: string,
    action: CheckpointAction,
    checkinId?: string,
    checkinKind?: 'checkpoint' | 'route_point',
  ) => void
}

function escapeHtml(value: string) {
  return value.replace(
    /[&<>'"]/g,
    (character) =>
      ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', "'": '&#39;', '"': '&quot;' })[character] ??
      character,
  )
}

function radiusPolygon(coordinates: [number, number], radius: number) {
  const [longitude, latitude] = coordinates
  const points = 64
  const latitudeRadius = radius / 111_320
  const longitudeRadius = radius / (111_320 * Math.max(Math.cos((latitude * Math.PI) / 180), 0.01))
  return Array.from({ length: points + 1 }, (_, index) => {
    const angle = (index / points) * Math.PI * 2
    return [
      longitude + Math.cos(angle) * longitudeRadius,
      latitude + Math.sin(angle) * latitudeRadius,
    ] as [number, number]
  })
}

export function useMapCheckpoints({
  checkpoints,
  routes,
  visits,
  mapReady,
  getMap,
  getMarkerPopup,
  setMarkerPopup,
  onRoutePointClick,
  onCheckpointAction,
}: UseMapCheckpointsOptions) {
  const checkpointDrawingMode = ref<'none' | 'checkpoint' | 'route'>('none')
  const draftCheckpoint = ref<{
    coordinates: [number, number]
    radius: number
    name: string
    description: string
    color: string
    points: number
  } | null>(null)
  const draftRoutePoints = ref<
    {
      id: string
      coordinates: [number, number]
      radius: number
      name: string
      description: string
      color: string
      points: number
    }[]
  >([])
  const activeRadius = ref<{ kind: 'checkpoint' | 'route'; id: string } | null>(null)
  let checkpointHandlersAttached = false

  function showCheckpointPopup(
    item: {
      name: string
      description?: string
      radius?: number
      radiusEntries?: {
        name: string
        radius: number
        points?: number
        isVisited?: boolean
        description?: string
        photos?: { image: string }[]
      }[]
      photos?: { image: string; is_main: boolean }[]
      points?: number
      isVisited?: boolean
      created_by_name?: string
      creator?: Checkpoint['creator']
    },
    coordinates: [number, number],
    kind: 'checkpoint' | 'route',
    id: string,
    checkinId = id,
    checkinKind: 'checkpoint' | 'route_point' = kind === 'checkpoint'
      ? 'checkpoint'
      : 'route_point',
  ) {
    const map = getMap()
    if (!map) return

    getMarkerPopup()?.remove()
    const authorMarkup = createdByMarkup(item.creator)
    const descriptionMarkup = item.description
      ? `<p style="margin:6px 0 8px;color:#475569;font-size:12px;">${escapeHtml(item.description)}</p>`
      : ''
    const radiusMarkup = item.radiusEntries?.length
      ? `<div style="margin:6px 0 0;color:#475569;font-size:12px;display:flex;flex-direction:column;gap:8px;">${item.radiusEntries
          .map(
            (entry) => `
        <div style="border-left:2px solid #e2e8f0;padding-left:8px;">
          <div><strong>${escapeHtml(entry.name)}</strong>: ${entry.radius} m${typeof entry.points === 'number' && entry.points > 0 ? ` <span style="color:#D97706;font-weight:600;font-size:11px;margin-left:4px;">+${entry.points} pts</span>` : ''}${entry.isVisited ? ' <span style="color:#10B981;font-weight:600;font-size:11px;margin-left:4px;">(Visited)</span>' : ''}</div>
          ${entry.description ? `<div style="font-size:11px;color:#64748b;margin-top:2px;">${escapeHtml(entry.description)}</div>` : ''}
          ${entry.photos?.length ? `<div style="display:flex;gap:4px;margin-top:4px;flex-wrap:wrap;">${entry.photos.map((p) => `<img src="${escapeHtml(p.image)}" style="height:32px;width:32px;object-fit:cover;border-radius:4px;" />`).join('')}</div>` : ''}
        </div>
      `,
          )
          .join('')}</div>`
      : typeof item.radius === 'number'
        ? `<p style="margin:6px 0 0;color:#475569;font-size:12px;">Radius: ${item.radius} m${typeof item.points === 'number' && item.points > 0 ? ` <span style="color:#D97706;font-weight:600;">+${item.points} pts</span>` : ''}</p>`
        : ''
    const mainPhoto = item.photos?.find((photo) => photo.is_main) ?? item.photos?.[0]
    const imageMarkup = mainPhoto
      ? `<img src="${escapeHtml(mainPhoto.image)}" style="width:100%;height:120px;object-fit:cover;border-radius:8px;margin:8px 0;" />`
      : ''
    const photosButton =
      (item.photos?.length ?? 0) > 1
        ? `<button type="button" data-checkpoint-action="photos" style="border:0;background:none;color:#2563eb;padding:0;cursor:pointer;font-size:11px;">View all</button>`
        : ''
    const checkinButtonMarkup = item.isVisited
      ? `<span style="background:#10B981;color:#fff;border-radius:6px;padding:6px 8px;font-size:11px;font-weight:600;display:inline-block;">Visited</span>`
      : `<button type="button" data-checkpoint-action="checkin" style="border:0;background:#2563eb;color:#fff;border-radius:6px;padding:6px 8px;cursor:pointer;font-size:11px;">Manual check in</button>`

    const popup = new maplibregl.Popup({
      offset: 12,
      closeButton: true,
      className: 'checkpoint-popup',
    })
      .setLngLat(coordinates)
      .setHTML(
        `<div style="min-width:190px;color:#0f172a;"><strong>${escapeHtml(item.name)}</strong>${descriptionMarkup}${radiusMarkup}${imageMarkup}${photosButton}${authorMarkup}<div style="display:flex;gap:6px;margin-top:10px;flex-wrap:wrap;">${checkinButtonMarkup}<button type="button" data-checkpoint-action="edit" style="border:0;background:#e2e8f0;color:#0f172a;border-radius:6px;padding:6px 8px;cursor:pointer;font-size:11px;">Edit</button><button type="button" data-checkpoint-action="delete" style="border:0;background:#fee2e2;color:#b91c1c;border-radius:6px;padding:6px 8px;cursor:pointer;font-size:11px;">Delete</button><button type="button" data-checkpoint-action="qr" style="border:0;background:#7c3aed;color:#fff;border-radius:6px;padding:6px 8px;cursor:pointer;font-size:11px;">QR codes</button></div></div>`,
      )
      .addTo(map)
    setMarkerPopup(popup)

    popup.on('close', () => {
      activeRadius.value = null
      updateCheckpointLayers()
    })
    popup
      .getElement()
      .querySelectorAll('[data-checkpoint-action]')
      .forEach((element) => {
        element.addEventListener('click', () => {
          const action = element.getAttribute('data-checkpoint-action') as CheckpointAction
          onCheckpointAction?.(kind, id, action, checkinId, checkinKind)
        })
      })
  }

  function checkpointRadiusEntries(route: Route, checkpoint?: Checkpoint) {
    return [
      ...(checkpoint
        ? [
            {
              name: checkpoint.name || 'Main checkpoint',
              radius: checkpoint.radius,
              points: checkpoint.points,
              isVisited: visits?.value?.some((v) => v.checkpoint === route.main_checkpoint),
              description: checkpoint.description,
              photos: checkpoint.photos,
            },
          ]
        : []),
      ...route.points.map((point) => ({
        name: point.name || `Point ${point.sequence_number}`,
        radius: point.radius,
        points: point.points,
        isVisited: visits?.value?.some((v) => v.route_point === point.id),
        description: point.description,
        photos: point.photos,
      })),
    ]
  }

  function updateCheckpointLayers() {
    const map = getMap()
    if (!map || !mapReady.value) return

    const cpData = {
      type: 'FeatureCollection' as const,
      features: (checkpoints?.value || []).map((cp) => {
        const isVisited = visits?.value?.some((v) => v.checkpoint === cp.id)
        return {
          type: 'Feature' as const,
          geometry: { type: 'Point' as const, coordinates: [cp.longitude, cp.latitude] },
          properties: {
            id: cp.id,
            name: cp.name,
            radius: cp.radius,
            routeId: cp.route?.id ?? null,
            color: isVisited ? '#10B981' : cp.color || (cp.route ? '#8B5CF6' : '#9333EA'),
            isVisited,
          },
        }
      }),
    }

    if (draftCheckpoint.value) {
      cpData.features.push({
        type: 'Feature' as const,
        geometry: { type: 'Point' as const, coordinates: draftCheckpoint.value.coordinates },
        properties: {
          id: 'draft-cp',
          name: draftCheckpoint.value.name || 'Draft',
          radius: draftCheckpoint.value.radius,
          routeId: null,
          color: draftCheckpoint.value.color,
          isVisited: false,
        },
      })
    }

    const cpSource = map.getSource('checkpoints')
    if (cpSource && 'setData' in cpSource) {
      ;(cpSource as maplibregl.GeoJSONSource).setData(cpData)
    } else if (!cpSource) {
      map.addSource('checkpoints', { type: 'geojson', data: cpData })
      map.addLayer({
        id: 'checkpoints-circle',
        type: 'circle',
        source: 'checkpoints',
        paint: {
          'circle-radius': 8,
          'circle-color': ['get', 'color'],
          'circle-stroke-width': 2,
          'circle-stroke-color': '#FFFFFF',
        },
      })
      map.addLayer({
        id: 'checkpoints-label',
        type: 'symbol',
        source: 'checkpoints',
        layout: {
          'text-field': ['get', 'name'],
          'text-font': ['Open Sans Bold', 'Arial Unicode MS Bold'],
          'text-size': 12,
          'text-offset': [0, 1.5],
          'text-anchor': 'top',
        },
        paint: { 'text-color': '#FFFFFF', 'text-halo-color': '#000000', 'text-halo-width': 2 },
      })
    }

    const cpRadiusData = {
      type: 'FeatureCollection' as const,
      features: cpData.features
        .filter(
          (feature) =>
            (activeRadius.value?.kind === 'checkpoint' &&
              activeRadius.value.id === feature.properties.id) ||
            (activeRadius.value?.kind === 'route' &&
              activeRadius.value.id === feature.properties.routeId),
        )
        .map((feature) => ({
          type: 'Feature' as const,
          geometry: {
            type: 'Polygon' as const,
            coordinates: [
              radiusPolygon(
                feature.geometry.coordinates as [number, number],
                Number(feature.properties.radius) || 0,
              ),
            ],
          },
          properties: feature.properties,
        })),
    }
    const cpRadiusSource = map.getSource('checkpoint-radius')
    if (cpRadiusSource && 'setData' in cpRadiusSource) {
      ;(cpRadiusSource as maplibregl.GeoJSONSource).setData(cpRadiusData)
    } else if (!cpRadiusSource) {
      map.addSource('checkpoint-radius', { type: 'geojson', data: cpRadiusData })
      map.addLayer({
        id: 'checkpoint-radius-fill',
        type: 'fill',
        source: 'checkpoint-radius',
        paint: { 'fill-color': ['get', 'color'], 'fill-opacity': 0.16 },
      })
      map.addLayer({
        id: 'checkpoint-radius-outline',
        type: 'line',
        source: 'checkpoint-radius',
        paint: { 'line-color': ['get', 'color'], 'line-width': 2, 'line-opacity': 0.65 },
      })
    }

    const rpData = {
      type: 'FeatureCollection' as const,
      features: (routes?.value || [])
        .flatMap((r) =>
          r.points.map((rp) => {
            const isVisited = visits?.value?.some((v) => v.route_point === rp.id)
            return {
              type: 'Feature' as const,
              geometry: { type: 'Point' as const, coordinates: [rp.longitude, rp.latitude] },
              properties: {
                id: rp.id,
                routeId: r.id,
                name: rp.name || String(rp.sequence_number),
                radius: rp.radius,
                color: isVisited ? '#10B981' : r.color || '#F43F5E',
              },
            }
          }),
        )
        .concat(
          draftRoutePoints.value.map((rp, i) => ({
            type: 'Feature' as const,
            geometry: { type: 'Point' as const, coordinates: rp.coordinates },
            properties: {
              id: rp.id,
              routeId: rp.id,
              name: rp.name || (i === 0 ? 'Main' : String(i)),
              radius: rp.radius,
              color: rp.color,
            },
          })),
        ),
    }

    const rpSource = map.getSource('route-points')
    if (rpSource && 'setData' in rpSource) {
      ;(rpSource as maplibregl.GeoJSONSource).setData(rpData)
    } else if (!rpSource) {
      map.addSource('route-points', { type: 'geojson', data: rpData })
      map.addLayer({
        id: 'route-points-circle',
        type: 'circle',
        source: 'route-points',
        paint: {
          'circle-radius': 6,
          'circle-color': ['get', 'color'],
          'circle-stroke-width': 2,
          'circle-stroke-color': '#FFFFFF',
        },
      })
      map.addLayer({
        id: 'route-points-label',
        type: 'symbol',
        source: 'route-points',
        layout: {
          'text-field': ['get', 'name'],
          'text-font': ['Open Sans Bold', 'Arial Unicode MS Bold'],
          'text-size': 10,
          'text-offset': [0, 1.2],
          'text-anchor': 'top',
        },
        paint: { 'text-color': '#FFFFFF', 'text-halo-color': '#000000', 'text-halo-width': 2 },
      })
    }

    const routeRadiusData = {
      type: 'FeatureCollection' as const,
      features: rpData.features
        .filter(
          (feature) =>
            activeRadius.value?.kind === 'route' &&
            (activeRadius.value.id === feature.properties.id ||
              activeRadius.value.id === feature.properties.routeId),
        )
        .map((feature) => ({
          type: 'Feature' as const,
          geometry: {
            type: 'Polygon' as const,
            coordinates: [
              radiusPolygon(
                feature.geometry.coordinates as [number, number],
                Number(feature.properties.radius) || 0,
              ),
            ],
          },
          properties: feature.properties,
        })),
    }
    const routeRadiusSource = map.getSource('route-point-radius')
    if (routeRadiusSource && 'setData' in routeRadiusSource) {
      ;(routeRadiusSource as maplibregl.GeoJSONSource).setData(routeRadiusData)
    } else if (!routeRadiusSource) {
      map.addSource('route-point-radius', { type: 'geojson', data: routeRadiusData })
      map.addLayer({
        id: 'route-point-radius-fill',
        type: 'fill',
        source: 'route-point-radius',
        paint: { 'fill-color': ['get', 'color'], 'fill-opacity': 0.14 },
      })
      map.addLayer({
        id: 'route-point-radius-outline',
        type: 'line',
        source: 'route-point-radius',
        paint: { 'line-color': ['get', 'color'], 'line-width': 2, 'line-opacity': 0.6 },
      })
    }

    const routeLineData = {
      type: 'FeatureCollection' as const,
      features: (routes?.value || [])
        .map((r) => {
          const cp = checkpoints?.value?.find((c) => c.id === r.main_checkpoint)
          const coords = cp ? [[cp.longitude, cp.latitude]] : []
          coords.push(...r.points.map((p) => [p.longitude, p.latitude]))
          return {
            type: 'Feature' as const,
            geometry: { type: 'LineString' as const, coordinates: coords },
            properties: { id: r.id, color: r.color },
          }
        })
        .concat(
          draftRoutePoints.value.length > 1
            ? [
                {
                  type: 'Feature' as const,
                  geometry: {
                    type: 'LineString' as const,
                    coordinates: draftRoutePoints.value.map((p) => p.coordinates),
                  },
                  properties: { id: 'draft-route-line', color: '#8B5CF6' },
                },
              ]
            : [],
        ),
    }

    const rlSource = map.getSource('route-lines')
    if (rlSource && 'setData' in rlSource) {
      ;(rlSource as maplibregl.GeoJSONSource).setData(routeLineData)
    } else if (!rlSource) {
      map.addSource('route-lines', { type: 'geojson', data: routeLineData })
      map.addLayer(
        {
          id: 'route-lines-layer',
          type: 'line',
          source: 'route-lines',
          paint: { 'line-color': ['get', 'color'], 'line-width': 3, 'line-dasharray': [2, 2] },
        },
        'route-points-circle',
      )
    }

    if (!checkpointHandlersAttached) {
      checkpointHandlersAttached = true
      const handleCpClick = (event: maplibregl.MapLayerMouseEvent) => {
        event.preventDefault()
        const cpId = event.features?.[0]?.properties?.id as string | undefined
        if (!cpId || cpId.startsWith('draft-')) return

        const checkpoint = checkpoints?.value?.find((item) => item.id === cpId)
        const route = routes?.value?.find((candidate) => candidate.main_checkpoint === cpId)
        if (route) {
          const isVisited = visits?.value?.some((v) => v.checkpoint === route.main_checkpoint)
          showCheckpointPopup(
            {
              name: route.name,
              description: route.description,
              radiusEntries: checkpointRadiusEntries(route, checkpoint),
              photos: checkpoint?.photos,
              isVisited,
              created_by_name: route.created_by_name,
              creator: route.creator,
            },
            [event.lngLat.lng, event.lngLat.lat],
            'route',
            route.id,
            route.main_checkpoint,
            'checkpoint',
          )
          activeRadius.value = { kind: 'route', id: route.id }
          updateCheckpointLayers()
          onRoutePointClick?.(route.main_checkpoint)
          return
        }

        if (checkpoint) {
          showCheckpointPopup(
            { ...checkpoint, isVisited: visits?.value?.some((v) => v.checkpoint === cpId) },
            [event.lngLat.lng, event.lngLat.lat],
            'checkpoint',
            cpId,
          )
        }
        activeRadius.value = { kind: 'checkpoint', id: cpId }
        updateCheckpointLayers()
      }

      const handleRpClick = (event: maplibregl.MapLayerMouseEvent) => {
        event.preventDefault()
        const rpId = event.features?.[0]?.properties?.id as string | undefined
        if (!rpId || rpId.startsWith('draft-')) return

        const routePoint = routes?.value
          ?.flatMap((route) => route.points)
          .find((point) => point.id === rpId)
        const route = routes?.value?.find((candidate) =>
          candidate.points.some((point) => point.id === rpId),
        )
        if (routePoint && route) {
          const checkpoint = checkpoints?.value?.find((item) => item.id === route.main_checkpoint)
          const isVisited = visits?.value?.some((v) => v.route_point === rpId)
          showCheckpointPopup(
            {
              ...routePoint,
              radiusEntries: checkpointRadiusEntries(route, checkpoint),
              photos: routePoint.photos,
              isVisited,
            },
            [event.lngLat.lng, event.lngLat.lat],
            'route',
            route.id,
            rpId,
          )
          activeRadius.value = { kind: 'route', id: route.id }
        }
        updateCheckpointLayers()
        onRoutePointClick?.(rpId)
      }

      map.on('click', 'checkpoints-circle', handleCpClick)
      map.on('click', 'checkpoints-label', handleCpClick)
      map.on('click', 'checkpoint-radius-fill', handleCpClick)
      map.on('click', 'route-points-circle', handleRpClick)
      map.on('click', 'route-points-label', handleRpClick)
      map.on('click', 'route-point-radius-fill', handleRpClick)
      map.on('click', 'route-lines-layer', (event) => {
        event.preventDefault()
        const routeId = event.features?.[0]?.properties?.id as string | undefined
        const route = routes?.value?.find((item) => item.id === routeId)
        if (!route) return
        const checkpoint = checkpoints?.value?.find((item) => item.id === route.main_checkpoint)
        const isVisited = visits?.value?.some((v) => v.checkpoint === route.main_checkpoint)
        showCheckpointPopup(
          {
            name: route.name,
            description: route.description,
            radiusEntries: checkpointRadiusEntries(route, checkpoint),
            photos: checkpoint?.photos,
            isVisited,
            created_by_name: route.created_by_name,
            creator: route.creator,
          },
          [event.lngLat.lng, event.lngLat.lat],
          'route',
          route.id,
          route.main_checkpoint,
          'checkpoint',
        )
        activeRadius.value = { kind: 'route', id: route.id }
        updateCheckpointLayers()
      })
      ;['checkpoints-circle', 'route-points-circle', 'route-lines-layer'].forEach((layer) => {
        map.on('mouseenter', layer, () => {
          map.getCanvas().style.cursor = 'pointer'
        })
        map.on('mouseleave', layer, () => {
          map.getCanvas().style.cursor = ''
        })
      })
    }
  }

  function addDraftCheckpoint(coordinates: [number, number]) {
    draftCheckpoint.value = {
      coordinates,
      radius: 50,
      name: '',
      description: '',
      color: '#9333EA',
      points: 0,
    }
    updateCheckpointLayers()
  }

  function addDraftRoutePoint(coordinates: [number, number]) {
    draftRoutePoints.value.push({
      id: `draft-${Date.now()}`,
      coordinates,
      radius: 50,
      name: '',
      description: '',
      color: '#8B5CF6',
      points: 0,
    })
    updateCheckpointLayers()
  }

  return {
    checkpointDrawingMode,
    draftCheckpoint,
    draftRoutePoints,
    updateCheckpointLayers,
    addDraftCheckpoint,
    addDraftRoutePoint,
  }
}
