import { isRef, toValue, type MaybeRefOrGetter, type Ref } from 'vue'

export type RefPayload<T> = T extends readonly (infer Item)[]
  ? MaybeRefOrGetter<readonly RefPayload<Item>[]>
  : T extends object
    ? MaybeRefOrGetter<{ [Key in keyof T]: RefPayload<T[Key]> }>
    : MaybeRefOrGetter<T>

export function unwrapRefPayload<T>(payload: RefPayload<T>): T {
  const value = toValue(payload) as T | Ref<unknown>

  if (isRef(value)) {
    return unwrapRefPayload(value.value as RefPayload<T>)
  }

  if (Array.isArray(value)) {
    return value.map((item) => unwrapRefPayload(item as RefPayload<unknown>)) as T
  }

  // Binary values must remain intact. Recursing into a File turns it into an
  // empty object, which makes multipart uploads fail server-side.
  if (
    (typeof Blob !== 'undefined' && value instanceof Blob) ||
    (typeof FormData !== 'undefined' && value instanceof FormData)
  ) {
    return value
  }

  if (value && typeof value === 'object') {
    return Object.fromEntries(
      Object.entries(value).map(([key, item]) => [
        key,
        unwrapRefPayload(item as RefPayload<unknown>),
      ]),
    ) as T
  }

  return value as T
}
