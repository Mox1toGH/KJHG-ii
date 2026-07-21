import apiClient from '@/lib/api/client'
import type {
  CheckpointQrCode,
  CheckpointQrScan,
  CreateCheckpointQrPayload,
  ScanCheckpointQrPayload,
} from './qr.types'

let csrfPromise: Promise<unknown> | undefined

function withCsrf<T>(request: () => Promise<T>) {
  csrfPromise ??= apiClient.get('/accounts/csrf/').finally(() => {
    csrfPromise = undefined
  })
  return csrfPromise.then(request)
}

async function download(url: string, fallbackName: string) {
  const response = await apiClient.get<Blob>(url, { responseType: 'blob' })
  const contentDisposition = response.headers['content-disposition'] as string | undefined
  const match = contentDisposition?.match(/filename="?([^";]+)"?/i)
  const filename = match?.[1] ?? fallbackName
  const objectUrl = URL.createObjectURL(response.data)
  const anchor = document.createElement('a')
  anchor.href = objectUrl
  anchor.download = filename
  document.body.appendChild(anchor)
  anchor.click()
  anchor.remove()
  URL.revokeObjectURL(objectUrl)
}

export const checkpointQrApi = {
  list: (checkpointId: string) =>
    apiClient
      .get<CheckpointQrCode[]>(`/checkpoints/checkpoints/${checkpointId}/qrcodes/`)
      .then((response) => response.data),

  create: (checkpointId: string, payload: CreateCheckpointQrPayload) =>
    withCsrf(() =>
      apiClient
        .post<CheckpointQrCode>(`/checkpoints/checkpoints/${checkpointId}/qrcodes/`, payload)
        .then((response) => response.data),
    ),

  delete: (qrCodeId: string) =>
    withCsrf(() => apiClient.delete(`/checkpoints/qrcodes/${qrCodeId}/`).then(() => undefined)),

  downloadImage: (qrCodeId: string, name: string) =>
    download(`/checkpoints/qrcodes/${qrCodeId}/image/`, `${name}.png`),

  downloadPdf: (checkpointId: string, name: string) =>
    download(`/checkpoints/checkpoints/${checkpointId}/qrcodes/pdf/`, `${name}-qrcodes.pdf`),

  scan: (payload: ScanCheckpointQrPayload) =>
    withCsrf(() =>
      apiClient.post<CheckpointQrScan>('/checkpoints/qrcodes/scan/', payload).then((response) => response.data),
    ),
}
