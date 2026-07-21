import { describe, expect, it } from 'vitest'
import { accuracyFeatureCollection, createAccuracyCircleFeature } from '../utils/accuracyCircle'
import { createUserMarkerElement, setUserMarkerAvatar } from '../utils/userLocationMarker'

describe('home map utilities', () => {
  it('creates a smaller circular user avatar marker with a fallback fill', () => {
    const marker = createUserMarkerElement(null)
    const fallback = marker.firstElementChild as HTMLElement | null

    expect(marker.style.width).toBe('30px')
    expect(marker.style.height).toBe('30px')
    expect(marker.style.border).toBe('2px solid rgb(255, 255, 255)')
    expect(marker.style.pointerEvents).toBe('none')
    expect(fallback?.style.backgroundColor).toBe('rgb(0, 122, 255)')
  })

  it('renders an avatar image and keeps marker clicks off the map', () => {
    let clicked = false
    let bubbled = false
    const marker = createUserMarkerElement('/media/avatar.png', () => {
      clicked = true
    })
    const parent = document.createElement('div')
    parent.addEventListener('click', () => {
      bubbled = true
    })
    parent.appendChild(marker)
    const image = marker.querySelector('img')
    const event = new MouseEvent('click', { bubbles: true, cancelable: true })

    marker.dispatchEvent(event)

    expect(image?.getAttribute('src')).toBe('/media/avatar.png')
    expect(image?.getAttribute('alt')).toBe('You')
    expect(marker.style.pointerEvents).toBe('auto')
    expect(clicked).toBe(true)
    expect(bubbled).toBe(false)
  })

  it('can replace an existing avatar image with the fallback marker', () => {
    const marker = createUserMarkerElement('/media/avatar.png')

    setUserMarkerAvatar(marker, '   ')

    expect(marker.querySelector('img')).toBeNull()
    expect(marker.children).toHaveLength(1)
    expect((marker.firstElementChild as HTMLElement | null)?.style.borderRadius).toBe('50%')
  })

  it('builds a closed accuracy polygon only for positive finite accuracy values', () => {
    const feature = createAccuracyCircleFeature([30.52, 50.45], 25, '#007AFF')

    expect(createAccuracyCircleFeature([30.52, 50.45], null, '#007AFF')).toBeNull()
    expect(createAccuracyCircleFeature([30.52, 50.45], 0, '#007AFF')).toBeNull()
    expect(createAccuracyCircleFeature([30.52, 50.45], Number.NaN, '#007AFF')).toBeNull()
    expect(feature?.geometry.coordinates[0]).toHaveLength(97)
    expect(feature?.geometry.coordinates[0]?.at(0)).toEqual(
      feature?.geometry.coordinates[0]?.at(-1),
    )
    expect(accuracyFeatureCollection(feature ? [feature] : []).features).toHaveLength(1)
  })
})
