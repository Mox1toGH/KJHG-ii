import { computed, ref } from 'vue'
import { defineStore } from 'pinia'
import { checkpointQrApi } from './qr.api'
import type { CheckpointQrCode, CreateCheckpointQrPayload, ScanCheckpointQrPayload } from './qr.types'

export const useCheckpointQrStore = defineStore('checkpointQr', () => {
  const checkpointId = ref<string | null>(null)
  const codes = ref<CheckpointQrCode[]>([])
  const isLoading = ref(false)
  const error = ref<string | null>(null)
  const isMutating = ref(false)

  const hasCodes = computed(() => codes.value.length > 0)

  async function load(id: string) {
    checkpointId.value = id
    isLoading.value = true
    error.value = null
    try {
      codes.value = await checkpointQrApi.list(id)
    } catch (cause) {
      error.value = getErrorMessage(cause, 'Could not load QR codes.')
    } finally {
      isLoading.value = false
    }
  }

  async function create(payload: CreateCheckpointQrPayload) {
    if (!checkpointId.value) return
    isMutating.value = true
    error.value = null
    try {
      await checkpointQrApi.create(checkpointId.value, payload)
      await load(checkpointId.value)
    } catch (cause) {
      error.value = getErrorMessage(cause, 'Could not create the QR code.')
      throw cause
    } finally {
      isMutating.value = false
    }
  }

  async function remove(code: CheckpointQrCode) {
    isMutating.value = true
    error.value = null
    try {
      await checkpointQrApi.delete(code.id)
      codes.value = codes.value.filter((item) => item.id !== code.id)
    } catch (cause) {
      error.value = getErrorMessage(cause, 'Could not delete the QR code.')
      throw cause
    } finally {
      isMutating.value = false
    }
  }

  async function scan(payload: ScanCheckpointQrPayload) {
    return checkpointQrApi.scan(payload)
  }

  function clear() {
    checkpointId.value = null
    codes.value = []
    error.value = null
  }

  return { checkpointId, codes, hasCodes, isLoading, isMutating, error, load, create, remove, scan, clear }
})

function getErrorMessage(cause: unknown, fallback: string) {
  const response = (cause as { response?: { data?: { detail?: string } } })?.response
  return response?.data?.detail || fallback
}
