import type { GoogleLoginPayload } from '@/features/auth'

export interface GoogleCredentialResponse {
  credential?: string
}

type GoogleCredentialCallback = (response: GoogleCredentialResponse) => void

declare global {
  interface Window {
    google?: {
      accounts: {
        id: {
          initialize: (config: {
            client_id: string
            callback: GoogleCredentialCallback
            auto_select?: boolean
            cancel_on_tap_outside?: boolean
          }) => void
          renderButton: (
            container: HTMLElement,
            options: {
              theme?: 'outline' | 'filled_blue' | 'filled_black'
              size?: 'large' | 'medium' | 'small'
              text?: 'signin_with' | 'signup_with' | 'continue_with' | 'signin'
              shape?: 'rectangular' | 'pill' | 'circle' | 'square'
              logo_alignment?: 'left' | 'center'
              width?: number
            },
          ) => void
        }
      }
    }
  }
}

let googleSdkPromise: Promise<void> | null = null
let googleInitialized = false

export function buildGoogleLoginPayload(
  response: GoogleCredentialResponse | null | undefined,
): GoogleLoginPayload | null {
  if (!response?.credential) {
    return null
  }

  return {
    credential: response.credential,
  }
}

export function initializeGoogleAuth(
  onCredential: (payload: GoogleLoginPayload) => void,
  clientId = import.meta.env.VITE_GOOGLE_CLIENT_ID ?? '',
): Promise<void> {
  if (typeof window === 'undefined') {
    return Promise.reject(new Error('Google auth can only run in the browser.'))
  }

  if (!clientId) {
    return Promise.reject(new Error('VITE_GOOGLE_CLIENT_ID is not configured.'))
  }

  if (window.google?.accounts?.id && googleInitialized) {
    return Promise.resolve()
  }

  if (googleSdkPromise) {
    return googleSdkPromise
  }

  googleSdkPromise = new Promise((resolve, reject) => {
    const existingScript = document.getElementById('google-gsi-script')

    if (existingScript && window.google?.accounts?.id) {
      googleInitialized = true
      resolve()
      return
    }

    const script = document.createElement('script')
    script.id = 'google-gsi-script'
    script.src = 'https://accounts.google.com/gsi/client'
    script.async = true
    script.defer = true

    script.onload = () => {
      if (!window.google?.accounts?.id) {
        reject(new Error('Google Identity Services failed to load.'))
        return
      }

      window.google.accounts.id.initialize({
        client_id: clientId,
        callback: (response) => {
          const payload = buildGoogleLoginPayload(response)

          if (payload) {
            onCredential(payload)
          }
        },
        auto_select: false,
        cancel_on_tap_outside: true,
      })

      googleInitialized = true
      resolve()
    }

    script.onerror = () => {
      reject(new Error('Failed to load Google Identity Services.'))
    }

    document.head.appendChild(script)
  })

  return googleSdkPromise
}

export async function renderGoogleButton({
  container,
  clientId,
  callback,
  width = 340,
}: {
  container: HTMLElement
  clientId: string
  callback: (payload: GoogleLoginPayload) => void
  width?: number
}): Promise<void> {
  await initializeGoogleAuth(callback, clientId)

  if (!window.google?.accounts?.id) {
    throw new Error('Google Identity Services is unavailable.')
  }

  window.google.accounts.id.renderButton(container, {
    theme: 'outline',
    size: 'large',
    text: 'signin_with',
    shape: 'rectangular',
    logo_alignment: 'left',
    width,
  })
}
