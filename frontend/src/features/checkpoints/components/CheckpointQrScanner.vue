<script setup lang="ts">
import { computed, ref } from 'vue'
import { useCheckpointQrStore } from '../qr/qr.store'
import { useQrScanner } from '../composables/useQrScanner'
import type { UserLocation } from '@/composables/useUserLocation'

const props = defineProps<{
  location: UserLocation | null
}>()

const emit = defineEmits<{ success: [] }>()
const qrStore = useCheckpointQrStore()
const isSubmitting = ref(false)
const message = ref<string | null>(null)
const messageTone = ref<'success' | 'error'>('success')
const scanner = useQrScanner(async (token) => {
  if (isSubmitting.value) return
  scanner.stop()
  isSubmitting.value = true
  message.value = null
  try {
    if (!props.location) throw new Error('Your current location is not available yet.')
    await qrStore.scan({
      token,
      latitude: props.location.latitude,
      longitude: props.location.longitude,
    })
    messageTone.value = 'success'
    message.value = 'QR code scanned successfully.'
    emit('success')
  } catch (cause) {
    messageTone.value = 'error'
    message.value = getScanError(cause)
  } finally {
    isSubmitting.value = false
  }
})
// Template refs are resolved against top-level setup bindings.
const video = scanner.video
const isScannerActive = computed(() => scanner.isActive.value)
const isScannerStarting = computed(() => scanner.isStarting.value)

function getScanError(cause: unknown) {
  const response = (cause as { response?: { status?: number; data?: { detail?: string } } })?.response
  if (response?.status === 409) return 'You have already scanned this QR code.'
  if (response?.data?.detail?.toLowerCase().includes('outside')) {
    return 'You must be inside the checkpoint area to scan this QR code.'
  }
  return response?.data?.detail || (cause instanceof Error ? cause.message : 'Could not scan this QR code.')
}
</script>

<template>
  <div class="space-y-3">
    <div class="relative overflow-hidden rounded-xl border border-white/10 bg-black">
      <video ref="video" class="aspect-video w-full object-cover" muted playsinline />
      <div v-if="!isScannerActive && !isScannerStarting" class="absolute inset-0 flex items-center justify-center p-6 text-center text-xs text-slate-400">
        Open the camera and point it at a QR code.
      </div>
      <div v-if="isScannerActive" class="pointer-events-none absolute inset-8 rounded-2xl border-2 border-purple-400/80 shadow-[0_0_0_999px_rgb(0_0_0/30%)]" />
    </div>
    <p v-if="scanner.error" class="rounded-lg bg-rose-500/10 px-3 py-2 text-xs text-rose-200">{{ scanner.error }}</p>
    <p v-if="message" class="rounded-lg px-3 py-2 text-xs" :class="messageTone === 'success' ? 'bg-emerald-500/10 text-emerald-200' : 'bg-rose-500/10 text-rose-200'">{{ message }}</p>
    <button
      v-if="!isScannerActive"
      type="button"
      class="w-full rounded-xl bg-purple-600 px-4 py-2.5 text-sm font-semibold text-white hover:bg-purple-500 disabled:opacity-50"
      :disabled="isScannerStarting || isSubmitting"
      @click="scanner.start"
    >
      {{ isScannerStarting ? 'Opening camera…' : 'Open scanner' }}
    </button>
    <button v-else type="button" class="w-full rounded-xl bg-slate-700 px-4 py-2.5 text-sm font-semibold text-white hover:bg-slate-600" @click="scanner.stop">
      Stop scanner
    </button>
    <p v-if="isSubmitting" class="text-center text-xs text-slate-400">Checking your location…</p>
  </div>
</template>
