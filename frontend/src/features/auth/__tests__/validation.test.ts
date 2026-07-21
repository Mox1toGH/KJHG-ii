import { describe, expect, it } from 'vitest'

import { validateLoginForm, validateSignupForm } from '../core/auth.validation'

describe('auth validation', () => {
  it('reports missing login fields', () => {
    const result = validateLoginForm({ identifier: '', password: 'short' })

    expect(result.success).toBe(false)
    expect(result.errors.identifier).toContain('required')
    expect(result.errors.password).toContain('at least 8')
  })

  it('reports weak signup details', () => {
    const result = validateSignupForm({
      username: 'ab',
      email: 'invalid',
      firstName: '',
      lastName: '',
      password: '123',
      confirmPassword: '456',
    })

    expect(result.success).toBe(false)
    expect(result.errors.username).toContain('at least 3')
    expect(result.errors.email).toContain('valid email')
    expect(result.errors.password).toContain('at least 8')
    expect(result.errors.confirmPassword).toContain('match')
  })
})
