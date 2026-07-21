<script setup lang="ts">
import { computed, onBeforeUnmount, ref, watch } from 'vue'
import { useCheckpointQrStore } from '../qr/qr.store'
import type { CheckpointQrCode } from '../qr/qr.types'
import { checkpointQrApi } from '../qr/qr.api'
import CheckpointQrScanner from './CheckpointQrScanner.vue'
import type { UserLocation } from '@/composables/useUserLocation'

const props = defineProps<{
  checkpointId: string
  checkpointName: string
  canManage: boolean
  location: UserLocation | null
}>()
const emit = defineEmits<{ progressChanged: [] }>()
const store = useCheckpointQrStore()
const isCreateOpen = ref(false)
const isScannerOpen = ref(false)
const name = ref('')
const points = ref(0)
const localError = ref<string | null>(null)
const downloadingId = ref<string | null>(null)

const codes = computed(() => store.codes)

watch(
  [() => props.checkpointId, () => props.canManage],
  ([id, canManage]) => {
    if (canManage) void store.load(id)
    else store.clear()
  },
  { immediate: true },
)
onBeforeUnmount(() => store.clear())

async function create() {
  localError.value = null
  try {
    await store.create({ name: name.value.trim() || undefined, points: points.value })
    name.value = ''
    points.value = 0
    isCreateOpen.value = false
  } catch {
    localError.value = store.error
  }
}

async function remove(code: CheckpointQrCode) {
  try {
    await store.remove(code)
  } catch {
    localError.value = store.error
  }
}

async function downloadImage(code: CheckpointQrCode) {
  downloadingId.value = code.id
  try {
    await checkpointQrApi.downloadImage(code.id, code.name)
  } catch {
    localError.value = 'Could not download the PNG.'
  } finally {
    downloadingId.value = null
  }
}

async function downloadPdf() {
  downloadingId.value = 'pdf'
  try {
    await checkpointQrApi.downloadPdf(props.checkpointId, props.checkpointName)
  } catch {
    localError.value = 'Could not download the PDF.'
  } finally {
    downloadingId.value = null
  }
}

function handleScanSuccess() {
  isScannerOpen.value = false
  emit('progressChanged')
  void store.load(props.checkpointId)
}
</script>

<template>
  <section class="mt-4 space-y-3 rounded-2xl border border-purple-400/20 bg-purple-500/5 p-4">
    <div class="flex items-center justify-between gap-3">
      <div>
        <h3 class="text-sm font-semibold text-white">QR Codes</h3>
        <p class="text-xs text-slate-400">Find and scan the hidden codes at this checkpoint.</p>
      </div>
      <button type="button" class="rounded-lg bg-purple-600 px-3 py-2 text-xs font-semibold text-white hover:bg-purple-500" @click="isScannerOpen = !isScannerOpen">
        {{ isScannerOpen ? 'Close scanner' : 'Scan QR code' }}
      </button>
    </div>

    <CheckpointQrScanner v-if="isScannerOpen" :location="location" @success="handleScanSuccess" />

    <div v-if="canManage" class="flex flex-wrap gap-2">
      <button type="button" class="rounded-lg bg-white/10 px-3 py-2 text-xs font-semibold text-white hover:bg-white/15" @click="isCreateOpen = true">Create QR Code</button>
      <button type="button" class="rounded-lg bg-white/10 px-3 py-2 text-xs font-semibold text-white hover:bg-white/15 disabled:opacity-50" :disabled="downloadingId === 'pdf' || !codes.length" @click="downloadPdf">{{ downloadingId === 'pdf' ? 'Preparing PDF…' : 'Download PDF' }}</button>
    </div>

    <form v-if="canManage && isCreateOpen" class="space-y-2 rounded-xl border border-white/10 bg-black/20 p-3" @submit.prevent="create">
      <label class="block text-xs font-medium text-slate-300" for="qr-name">Name (optional)</label>
      <input id="qr-name" v-model="name" type="text" maxlength="200" placeholder="QR 1" class="w-full rounded-lg border border-white/10 bg-black/30 px-3 py-2 text-sm text-white outline-none focus:border-purple-400" />
      <label class="block text-xs font-medium text-slate-300" for="qr-points">Points</label>
      <input id="qr-points" v-model.number="points" type="number" min="0" placeholder="0" class="w-full rounded-lg border border-white/10 bg-black/30 px-3 py-2 text-sm text-white outline-none focus:border-purple-400" />
      <div class="flex gap-2">
        <button type="submit" class="rounded-lg bg-purple-600 px-3 py-2 text-xs font-semibold text-white disabled:opacity-50" :disabled="store.isMutating">{{ store.isMutating ? 'Creating…' : 'Create' }}</button>
        <button type="button" class="rounded-lg bg-white/10 px-3 py-2 text-xs text-white" @click="isCreateOpen = false">Cancel</button>
      </div>
    </form>

    <p v-if="canManage && (localError || store.error)" class="rounded-lg bg-rose-500/10 px-3 py-2 text-xs text-rose-200">{{ localError || store.error }}</p>
    <p v-if="canManage && store.isLoading" class="text-xs text-slate-400">Loading QR codes…</p>
    <p v-else-if="canManage && !codes.length" class="text-xs text-slate-400">No QR codes have been created yet.</p>
    <div v-else-if="canManage" class="space-y-2">
      <article v-for="code in codes" :key="code.id" class="flex items-center gap-3 rounded-xl border border-white/10 bg-black/20 p-3">
        <img :src="code.image" :alt="code.name" class="h-14 w-14 rounded bg-white p-1" />
        <div class="min-w-0 flex-1">
          <p class="truncate text-sm font-semibold text-white">{{ code.name }}</p>
          <p class="text-xs text-slate-400">Scans: {{ code.scan_count }}</p>
          <p v-if="code.points > 0" class="text-xs text-purple-400">Points: {{ code.points }}</p>
        </div>
        <div v-if="canManage" class="flex shrink-0 gap-1">
          <button type="button" class="rounded-lg bg-white/10 px-2 py-1.5 text-xs text-white hover:bg-white/15 disabled:opacity-50" :disabled="downloadingId === code.id" @click="downloadImage(code)">{{ downloadingId === code.id ? '…' : 'PNG' }}</button>
          <button type="button" class="rounded-lg bg-rose-500/10 px-2 py-1.5 text-xs text-rose-200 hover:bg-rose-500/20 disabled:opacity-50" :disabled="store.isMutating" @click="remove(code)">Delete</button>
        </div>
      </article>
    </div>
  </section>
</template>
