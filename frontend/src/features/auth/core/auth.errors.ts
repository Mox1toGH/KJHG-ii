import { isAxiosError } from 'axios'

export function getAuthErrorMessage(error: Error | null) {
  if (!error) {
    return ''
  }

  if (isAxiosError(error)) {
    const data = error.response?.data

    if (Array.isArray(data)) {
      return data.join(' ')
    }

    if (typeof data === 'string') {
      return data
    }

    if (data && typeof data === 'object') {
      const messages = Object.entries(data).flatMap(([field, value]) => {
        if (typeof value === 'string') {
          return `${formatField(field)}: ${value}`
        }

        if (Array.isArray(value)) {
          return `${formatField(field)}: ${value.join(' ')}`
        }

        return []
      })

      if (messages.length > 0) {
        return messages.join(' ')
      }
    }
  }

  return error.message
}

function formatField(field: string) {
  if (field === 'non_field_errors') {
    return 'Error'
  }

  return field.replace(/_/g, ' ')
}
