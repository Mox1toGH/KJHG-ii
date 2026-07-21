export function setUserMarkerAvatar(el: HTMLElement, avatar: string | null | undefined) {
  el.replaceChildren()
  const avatarUrl = typeof avatar === 'string' ? avatar.trim() : ''

  const fallback = document.createElement('div')
  fallback.style.width = '100%'
  fallback.style.height = '100%'
  fallback.style.borderRadius = '50%'
  fallback.style.backgroundColor = '#007AFF'
  el.appendChild(fallback)

  if (avatarUrl) {
    const image = document.createElement('img')
    image.src = avatarUrl
    image.alt = 'You'
    image.style.width = '100%'
    image.style.height = '100%'
    image.style.objectFit = 'cover'
    image.style.borderRadius = '50%'
    image.onerror = () => image.remove()
    fallback.replaceWith(image)
  }
}

export function createUserMarkerElement(avatar: string | null | undefined, onClick?: () => void) {
  const el = document.createElement('div')
  el.style.width = '30px'
  el.style.height = '30px'
  el.style.borderRadius = '50%'
  el.style.border = '2px solid #FFFFFF'
  el.style.backgroundColor = '#007AFF'
  el.style.boxShadow = '0 1px 4px rgba(15, 23, 42, 0.45)'
  el.style.overflow = 'hidden'
  el.style.zIndex = '10'
  el.style.pointerEvents = onClick ? 'auto' : 'none'
  if (onClick) {
    el.addEventListener('click', (event) => {
      event.stopPropagation()
      onClick()
    })
  }
  setUserMarkerAvatar(el, avatar)
  return el
}
