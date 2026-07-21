import { onUnmounted, ref } from 'vue'
import type { IScannerControls } from '@zxing/browser'

export function useQrScanner(onToken: (token: string) => void) {
  const video = ref<HTMLVideoElement | null>(null)
  const isStarting = ref(false)
  const isActive = ref(false)
  const error = ref<string | null>(null)
  let stream: MediaStream | null = null
  let controls: IScannerControls | null = null

  async function start() {
    if (isActive.value || isStarting.value) return
    isStarting.value = true
    error.value = null

    try {
      if (!navigator.mediaDevices?.getUserMedia) {
        throw new Error('Camera access is not supported by this browser.')
      }
      if (!video.value) throw new Error('Camera preview is not ready.')

      // Request permission explicitly before starting the decoder. This also
      // works in browsers that do not implement the native BarcodeDetector API.
      stream = await navigator.mediaDevices.getUserMedia({
        video: { facingMode: { ideal: 'environment' } },
        audio: false,
      })
      video.value.srcObject = stream
      await video.value.play()
      isActive.value = true

      const { BrowserQRCodeReader } = await import('@zxing/browser')
      const reader = new BrowserQRCodeReader()
      controls = await reader.decodeFromStream(stream, video.value, (result) => {
        const token = result?.getText()
        if (token) onToken(token)
      })

      if (!isActive.value) controls.stop()
    } catch (cause) {
      error.value = getCameraError(cause)
      stop()
    } finally {
      isStarting.value = false
    }
  }

  function stop() {
    isActive.value = false
    controls?.stop()
    controls = null
    stream?.getTracks().forEach((track) => track.stop())
    stream = null
    if (video.value) video.value.srcObject = null
  }

  onUnmounted(stop)
  return { video, isStarting, isActive, error, start, stop }
}

function getCameraError(cause: unknown) {
  if (cause instanceof DOMException && cause.name === 'NotAllowedError') {
    return 'Camera access was denied. Allow camera access in your browser settings and try again.'
  }
  if (cause instanceof DOMException && cause.name === 'NotFoundError') {
    return 'No camera was found on this device.'
  }
  return cause instanceof Error ? cause.message : 'Could not open the camera.'
}
