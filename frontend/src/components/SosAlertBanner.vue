<script setup lang="ts">
import { computed, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import type { UserLocation } from '@/composables/useUserLocation'
import type { ParticipantLocation } from '@/features/activities'
import { useCurrentUser } from '@/features/auth'
import {
  useActivityTracking,
  currentActivityId,
  requestSosParticipantFocus,
  sosActive,
  sosActivityId,
} from '@/features/activities'

const { t } = useI18n()

const router = useRouter()
const currentUserQuery = useCurrentUser()
const currentUserId = computed(() => currentUserQuery.data.value?.id)
const userPosition = ref<UserLocation | null>(null)
const { participants } = useActivityTracking(currentActivityId, currentUserId, userPosition)
const activeAlerts = computed(() =>
  Object.values(participants.value).filter((participant) => {
    if (!participant.sos_active) return false
    const isCurrentUser =
      currentUserId.value !== undefined && participant.user.id === String(currentUserId.value)
    const wasCancelledLocally =
      isCurrentUser && sosActivityId.value === currentActivityId.value && !sosActive.value
    return !wasCancelledLocally
  }),
)
const activeAlert = computed<ParticipantLocation | undefined>(() => activeAlerts.value[0])
const hasAlert = computed(() => activeAlerts.value.length > 0 || sosActive.value)
const alertName = computed(
  () => activeAlert.value?.user.display_name || activeAlert.value?.user.username || t('common.participant'),
)
const alertParticipantId = computed(() => activeAlert.value?.participant_id)

function openActivity() {
  const activityId = currentActivityId.value ?? sosActivityId.value
  if (activityId) {
    requestSosParticipantFocus(alertParticipantId.value)
    void router.push({
      name: 'activity-map',
      params: { activityId },
    })
  }
}
</script>

<template>
  <button
    v-if="hasAlert"
    type="button"
    class="fixed left-3 right-3 top-3 z-[1000] flex cursor-pointer items-center justify-between gap-3 rounded-xl border border-red-300/50 bg-red-700/95 px-4 py-3 text-left text-white shadow-xl backdrop-blur pointer-events-auto sm:left-6 sm:right-6"
    role="alert"
    :aria-label="t('common.openMap')"
    @click="openActivity"
  >
    <span
      ><strong>🚨 {{ t('common.sosActivated') }}</strong
      ><span class="ml-2 text-sm text-red-100"
        >{{ t('common.activatedBy') }}: {{ sosActive && !activeAlert ? t('common.you') : alertName }}</span
      ></span
    >
    <span
      v-if="currentActivityId || sosActivityId"
      class="shrink-0 text-xs font-semibold uppercase tracking-wider"
    >
      {{ t('common.openMap') }}
    </span>
  </button>
</template>
