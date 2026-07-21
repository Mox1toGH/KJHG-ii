import { computed, getCurrentScope, onScopeDispose, readonly, ref, watch, type Ref } from 'vue'
import type { UserLocation } from '@/composables/useUserLocation'
import { useCurrentUser } from '@/features/auth'
import { scratchMapApi } from '../core/scratchMap.api'
import type {
  ScratchDiscovery,
  ScratchMapSocketMessage,
  ScratchMapStatistics,
} from '../core/scratchMap.types'

const OFFLINE_QUEUE_KEY = 'scratch-map-offline-queue'
const MAX_RETRIES = 3
const MAX_LOAD_RETRIES = 3
const POSITION_QUEUE_MAX_SIZE = 100

interface QueuedPosition extends UserLocation {
  timestamp: number
  retryCount: number
}

function websocketUrl() {
  const configured = import.meta.env.VITE_WS_BASE_URL as string | undefined
  if (configured) return `${configured.replace(/\/$/, '')}/ws/scratch-map/`

  const apiBase =
    (import.meta.env.VITE_API_BASE_URL as string | undefined) ?? window.location.origin
  return `${apiBase.replace(/\/api\/?$/, '').replace(/^http/, 'ws')}/ws/scratch-map/`
}

function getOfflineQueue(): QueuedPosition[] {
  if (typeof window === 'undefined') return []
  try {
    return JSON.parse(localStorage.getItem(OFFLINE_QUEUE_KEY) || '[]')
  } catch {
    return []
  }
}

function setOfflineQueue(queue: QueuedPosition[]): void {
  if (typeof window === 'undefined') return
  try {
    localStorage.setItem(OFFLINE_QUEUE_KEY, JSON.stringify(queue))
  } catch (error) {
    console.error('[scratch-map] failed to save offline queue', error)
  }
}

function addToOfflineQueue(position: UserLocation): void {
  const queue = getOfflineQueue()
  queue.push({ ...position, timestamp: Date.now(), retryCount: 0 })
  if (queue.length > POSITION_QUEUE_MAX_SIZE) {
    queue.shift() // Remove oldest if queue is too large
  }
  setOfflineQueue(queue)
}

function clearOfflineQueue(): void {
  if (typeof window === 'undefined') return
  localStorage.removeItem(OFFLINE_QUEUE_KEY)
}

export function mergeScratchDiscoveries(
  current: readonly ScratchDiscovery[],
  incoming: readonly ScratchDiscovery[],
): ScratchDiscovery[] {
  const merged = new Map(current.map((item) => [item.h3_index, item]))
  incoming.forEach((item) => {
    if (!merged.has(item.h3_index)) merged.set(item.h3_index, item)
  })
  return [...merged.values()]
}

export function useScratchMapSync(enabled: Ref<boolean>, userPosition?: Ref<UserLocation | null>) {
  const discoveries = ref<ScratchDiscovery[]>([])
  const statistics = ref<ScratchMapStatistics | null>(null)
  const discoveryIndexes = new Set<string>()
  const lastDiscovery = ref<ScratchDiscovery | null>(null)
  const status = ref<'idle' | 'loading' | 'connected' | 'disconnected' | 'error'>('idle')
  const currentUserQuery = useCurrentUser()
  const currentUserId = computed(() => currentUserQuery.data.value?.id)
  
  let socket: WebSocket | null = null
  let reconnectTimer: number | undefined
  let loadRetryTimer: number | undefined
  let reconnectAttempt = 0
  let generation = 0
  let positionQueue: QueuedPosition[] = []
  let discoveryRequest: Promise<void> | null = null
  let loadRetryCount = 0
  let initialLoadComplete = false
  let pendingWebSocketMessages: string[] = []
  let isProcessingQueue = false

  function mergeDiscovery(discovery: ScratchDiscovery) {
    if (discovery.user_id !== currentUserId.value) {
      if (import.meta.env.DEV) {
        console.warn('[scratch-map] received discovery for wrong user', {
          expected: currentUserId.value,
          received: discovery.user_id,
          h3_index: discovery.h3_index,
        })
      }
      return
    }
    if (discoveryIndexes.has(discovery.h3_index)) return
    discoveryIndexes.add(discovery.h3_index)
    discoveries.value = [...discoveries.value, discovery]
    lastDiscovery.value = discovery
  }

  async function load() {
    status.value = 'loading'
    try {
      const [loadedDiscoveries, loadedStatistics] = await Promise.all([
        scratchMapApi.listDiscoveries(),
        scratchMapApi.statistics(),
      ])
      if (!enabled.value) return
      discoveries.value = mergeScratchDiscoveries(discoveries.value, loadedDiscoveries)
      discoveryIndexes.clear()
      discoveries.value.forEach((item) => discoveryIndexes.add(item.h3_index))
      statistics.value = loadedStatistics
      loadRetryCount = 0
      initialLoadComplete = true
      
      // Process any WebSocket messages that arrived during load
      while (pendingWebSocketMessages.length > 0) {
        const message = pendingWebSocketMessages.shift()
        if (message && socket?.onmessage) {
          socket.onmessage({ data: message } as MessageEvent)
        }
      }
    } catch (error) {
      console.error('[scratch-map] initial synchronization failed', error)
      if (loadRetryCount < MAX_LOAD_RETRIES) {
        loadRetryCount++
        const delay = 1000 * 2 ** loadRetryCount
        console.info(`[scratch-map] retrying initial load in ${delay}ms (attempt ${loadRetryCount}/${MAX_LOAD_RETRIES})`)
        clearLoadRetryTimer()
        loadRetryTimer = window.setTimeout(() => {
          loadRetryTimer = undefined
          if (enabled.value) load()
        }, delay)
      } else {
        status.value = 'error'
        console.error('[scratch-map] initial load failed after maximum retries')
      }
    }
  }

  function clearReconnectTimer() {
    if (reconnectTimer === undefined) return
    window.clearTimeout(reconnectTimer)
    reconnectTimer = undefined
  }

  function clearLoadRetryTimer() {
    if (loadRetryTimer === undefined) return
    window.clearTimeout(loadRetryTimer)
    loadRetryTimer = undefined
  }

  function scheduleReconnect() {
    if (!enabled.value || reconnectTimer !== undefined) return
    const delay = Math.min(30_000, 1_000 * 2 ** reconnectAttempt++)
    reconnectTimer = window.setTimeout(() => {
      reconnectTimer = undefined
      connect()
    }, delay)
  }

  function closeSocket() {
    clearReconnectTimer()
    if (!socket) return
    socket.onopen = null
    socket.onmessage = null
    socket.onerror = null
    socket.onclose = null
    socket.close()
    socket = null
  }

  function connect() {
    if (typeof window === 'undefined' || !enabled.value) return
    if (socket?.readyState === WebSocket.OPEN || socket?.readyState === WebSocket.CONNECTING) return

    socket?.close()
    socket = new WebSocket(websocketUrl())
    socket.onopen = () => {
      reconnectAttempt = 0
      status.value = 'connected'
      console.info('[scratch-map] WebSocket connected')
      // Reload data on reconnection to catch any missed updates
      if (initialLoadComplete) {
        load()
      }
    }
    socket.onmessage = (event) => {
      // Queue messages until initial load completes
      if (!initialLoadComplete) {
        pendingWebSocketMessages.push(event.data)
        return
      }
      try {
        const message = JSON.parse(event.data) as ScratchMapSocketMessage
        if (message.event === 'scratch_map.cell_discovered') {
          mergeDiscovery(message.payload.discovery)
        } else if (message.event === 'scratch_map.statistics_updated') {
          statistics.value = message.payload.statistics
        }
      } catch (error) {
        console.error('[scratch-map] invalid WebSocket message', error)
      }
    }
    socket.onerror = (error) => {
      console.error('[scratch-map] WebSocket error', error)
      status.value = 'error'
      socket?.close()
    }
    socket.onclose = () => {
      socket = null
      if (enabled.value) {
        status.value = 'disconnected'
        scheduleReconnect()
      }
    }
  }

  async function start() {
    const currentGeneration = ++generation
    closeSocket()
    clearLoadRetryTimer()
    discoveries.value = []
    discoveryIndexes.clear()
    lastDiscovery.value = null
    statistics.value = null
    loadRetryCount = 0
    initialLoadComplete = false
    pendingWebSocketMessages = []
    if (!enabled.value) {
      status.value = 'idle'
      return
    }
    connect()
    await load()
    if (currentGeneration !== generation || !enabled.value) return
    if (socket?.readyState === WebSocket.OPEN) status.value = 'connected'
    
    // Sync offline queue after initial load completes
    if (initialLoadComplete) {
      syncOfflineQueue()
    }
  }

  function stop() {
    generation += 1
    closeSocket()
    clearLoadRetryTimer()
    discoveries.value = []
    discoveryIndexes.clear()
    lastDiscovery.value = null
    statistics.value = null
    loadRetryCount = 0
    initialLoadComplete = false
    pendingWebSocketMessages = []
    positionQueue = []
    status.value = 'idle'
  }

  async function syncOfflineQueue() {
    const queue = getOfflineQueue()
    if (queue.length === 0) return
    
    console.info(`[scratch-map] syncing ${queue.length} offline discoveries`)
    
    for (let i = 0; i < queue.length; i++) {
      const item = queue[i]
      if (!item) continue
      try {
        const result = await scratchMapApi.discover(item.latitude, item.longitude)
        mergeDiscovery(result.discovery)
        // Remove successfully synced item
        queue.splice(i, 1)
        i--
      } catch (error) {
        console.error('[scratch-map] failed to sync offline discovery', error)
        // Stop on first failure, keep remaining in queue
        break
      }
    }
    
    setOfflineQueue(queue)
  }

  async function processPositionQueue() {
    if (isProcessingQueue || positionQueue.length === 0 || !enabled.value) return
    isProcessingQueue = true
    
    while (positionQueue.length > 0 && enabled.value) {
      const nextPosition = positionQueue.shift()!
      try {
        const result = await scratchMapApi.discover(nextPosition.latitude, nextPosition.longitude)
        mergeDiscovery(result.discovery)
        nextPosition.retryCount = 0 // Reset retry count on success
      } catch (error) {
        console.error('[scratch-map] location discovery failed', error)
        if (nextPosition.retryCount < MAX_RETRIES) {
          nextPosition.retryCount++
          const delay = 1000 * 2 ** nextPosition.retryCount
          console.info(`[scratch-map] retrying discovery in ${delay}ms (attempt ${nextPosition.retryCount}/${MAX_RETRIES})`)
          await new Promise(resolve => setTimeout(resolve, delay))
          // Re-queue for retry
          positionQueue.unshift(nextPosition)
        } else {
          console.error('[scratch-map] discovery failed after maximum retries, storing offline')
          addToOfflineQueue(nextPosition)
        }
      }
    }
    
    isProcessingQueue = false
  }

  function enqueueLocation(position: UserLocation | null) {
    if (!enabled.value || !position) return
    
    // Add to queue
    positionQueue.push({ ...position, timestamp: Date.now(), retryCount: 0 })
    
    // Limit queue size
    if (positionQueue.length > POSITION_QUEUE_MAX_SIZE) {
      const removed = positionQueue.shift()
      if (removed) {
        addToOfflineQueue(removed)
      }
    }
    
    // Start processing if not already running
    if (!discoveryRequest) {
      discoveryRequest = processPositionQueue().finally(() => {
        discoveryRequest = null
        if (positionQueue.length > 0 && enabled.value) {
          processPositionQueue()
        }
      })
    }
  }

  const stopEnabledWatch = watch(
    enabled,
    (isEnabled) => {
      void (isEnabled ? start() : Promise.resolve(stop()))
    },
    { immediate: true },
  )

  const stopLocationWatch = userPosition
    ? watch(userPosition, enqueueLocation, { immediate: true })
    : undefined

  const dispose = () => {
    stopEnabledWatch()
    stopLocationWatch?.()
    positionQueue = []
    stop()
  }

  if (getCurrentScope()) {
    onScopeDispose(dispose)
  }

  return {
    discoveries: readonly(discoveries),
    statistics: readonly(statistics),
    lastDiscovery: readonly(lastDiscovery),
    status: readonly(status),
  }
}
