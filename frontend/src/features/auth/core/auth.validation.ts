import * as v from 'valibot'

export const loginSchema = v.object({
  identifier: v.pipe(v.string(), v.trim(), v.minLength(1, 'Identifier is required.')),
  password: v.pipe(v.string(), v.minLength(8, 'Password must be at least 8 characters.')),
})

export const signupSchema = v.object({
  firstName: v.pipe(v.string(), v.trim(), v.minLength(1, 'First name is required.')),
  lastName: v.pipe(v.string(), v.trim(), v.minLength(1, 'Last name is required.')),
  username: v.pipe(v.string(), v.trim(), v.minLength(3, 'Username must be at least 3 characters.')),
  email: v.pipe(v.string(), v.trim(), v.email('Please enter a valid email address.')),
  password: v.pipe(v.string(), v.minLength(8, 'Password must be at least 8 characters.')),
  confirmPassword: v.pipe(v.string(), v.minLength(1, 'Please confirm your password.')),
})

export function validateLoginForm(values: { identifier: string; password: string }) {
  const result = v.safeParse(loginSchema, values)

  if (result.success) {
    return { success: true, errors: {} }
  }

  const errors = Object.fromEntries(
    (result.issues ?? []).map((issue) => [issue.path?.[0]?.key ?? 'form', issue.message]),
  )

  return { success: false, errors }
}

export function validateSignupForm(values: {
  firstName: string
  lastName: string
  username: string
  email: string
  password: string
  confirmPassword: string
}) {
  const result = v.safeParse(signupSchema, values)

  if (result.success) {
    return {
      success: values.password === values.confirmPassword,
      errors:
        values.password === values.confirmPassword
          ? {}
          : { confirmPassword: 'Passwords must match.' },
    }
  }

  const errors = Object.fromEntries(
    (result.issues ?? []).map((issue) => [issue.path?.[0]?.key ?? 'form', issue.message]),
  )

  if (values.password !== values.confirmPassword) {
    errors.confirmPassword = 'Passwords must match.'
  }

  return { success: false, errors }
}
