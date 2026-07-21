import { computed, ref, watch, type Ref } from 'vue'

const STORAGE_KEY = 'mdvl_hidden_participants'

interface HiddenParticipantsStorage {
  [activityId: string]: string[]
}

function getHiddenParticipantsFromStorage(): HiddenParticipantsStorage {
  try {
    const data = localStorage.getItem(STORAGE_KEY)
    return data ? JSON.parse(data) : {}
  } catch (error) {
    console.error('[useHiddenParticipants] Failed to read from localStorage:', error)
    return {}
  }
}

function setHiddenParticipantsToStorage(data: HiddenParticipantsStorage) {
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(data))
  } catch (error) {
    console.error('[useHiddenParticipants] Failed to write to localStorage:', error)
  }
}

export function useHiddenParticipants(activityId: Ref<string | undefined>, currentUserId?: Ref<number | undefined>) {
  const hiddenParticipantIds = ref<string[]>([])

  // Load hidden participants for current activity
  function loadHiddenParticipants() {
    if (!activityId.value) {
      hiddenParticipantIds.value = []
      return
    }
    const storage = getHiddenParticipantsFromStorage()
    hiddenParticipantIds.value = storage[activityId.value] || []
  }

  // Save hidden participants for current activity
  function saveHiddenParticipants() {
    if (!activityId.value) return
    const storage = getHiddenParticipantsFromStorage()
    if (hiddenParticipantIds.value.length === 0) {
      delete storage[activityId.value]
    } else {
      storage[activityId.value] = hiddenParticipantIds.value
    }
    setHiddenParticipantsToStorage(storage)
  }

  // Hide a participant (cannot hide current user)
  function hideParticipant(participantId: string) {
    if (!hiddenParticipantIds.value.includes(participantId)) {
      hiddenParticipantIds.value.push(participantId)
      saveHiddenParticipants()
    }
  }

  // Show a participant (remove from hidden list)
  function showParticipant(participantId: string) {
    hiddenParticipantIds.value = hiddenParticipantIds.value.filter((id) => id !== participantId)
    saveHiddenParticipants()
  }

  // Check if a participant is hidden (current user is never hidden)
  const isParticipantHidden = computed(
    () => (participantId: string) => {
      // Current user is never considered hidden
      if (currentUserId?.value && participantId === String(currentUserId.value)) {
        return false
      }
      return hiddenParticipantIds.value.includes(participantId)
    },
  )

  // Get count of hidden participants
  const hiddenCount = computed(() => hiddenParticipantIds.value.length)

  // Clear all hidden participants for current activity
  function clearHiddenParticipants() {
    hiddenParticipantIds.value = []
    saveHiddenParticipants()
  }

  // Load hidden participants when activity ID changes
  watch(
    activityId,
    () => {
      loadHiddenParticipants()
    },
    { immediate: true },
  )

  return {
    hiddenParticipantIds,
    isParticipantHidden,
    hiddenCount,
    hideParticipant,
    showParticipant,
    clearHiddenParticipants,
  }
}
