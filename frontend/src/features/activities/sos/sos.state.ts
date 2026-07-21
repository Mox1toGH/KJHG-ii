import { ref } from 'vue'

export const sosActive = ref(false)
export const sosActivityId = ref<string | undefined>()
export const currentActivityId = ref<string | undefined>()
export const sosFocusParticipantId = ref<string | undefined>()

export function updateSosState(activityId: string | undefined, active: boolean) {
  sosActivityId.value = activityId
  sosActive.value = active
}

export function setCurrentActivityId(activityId: string | undefined) {
  currentActivityId.value = activityId
}

export function requestSosParticipantFocus(participantId: string | undefined) {
  sosFocusParticipantId.value = participantId
}
