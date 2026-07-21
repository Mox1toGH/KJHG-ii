import { useQueryClient } from '@tanstack/vue-query'
import type { MutationOptions } from '@tanstack/query-core'
import { useMutationWithRefs } from '@/lib/query/useMutationWithRefs'
import type { RefPayload } from '@/lib/query/refPayload'
import { authApi } from './auth.api'
import { authKeys } from './auth.keys'
import type {
  AddFriendPayload,
  ChangePasswordPayload,
  DeleteAccountPayload,
  DetailResponse,
  EmailResendPayload,
  EmailVerificationPayload,
  Friend,
  FriendStatusResponse,
  GoogleLoginPayload,
  LoginPayload,
  PasswordResetConfirmPayload,
  PasswordResetPayload,
  RegisterPayload,
  SetCurrentStatusPayload,
  UpdateProfilePayload,
  UserProfile,
  UserStatus,
} from './auth.types'

type RefMutationOptions<TData, TPayload> = Omit<
  MutationOptions<TData, Error, RefPayload<TPayload>>,
  'mutationFn'
>

export function useRegister(options?: RefMutationOptions<DetailResponse, RegisterPayload>) {
  return useMutationWithRefs(authApi.register, options)
}

export function useLogin(options?: RefMutationOptions<DetailResponse, LoginPayload>) {
  const queryClient = useQueryClient()

  return useMutationWithRefs(authApi.login, {
    ...options,
    onSuccess: (data, variables, onMutateResult, context) => {
      queryClient.invalidateQueries({ queryKey: authKeys.user() })
      options?.onSuccess?.(data, variables, onMutateResult, context)
    },
  })
}

export function useGoogleLogin(options?: RefMutationOptions<DetailResponse, GoogleLoginPayload>) {
  const queryClient = useQueryClient()

  return useMutationWithRefs(authApi.googleLogin, {
    ...options,
    onSuccess: (data, variables, onMutateResult, context) => {
      queryClient.invalidateQueries({ queryKey: authKeys.user() })
      options?.onSuccess?.(data, variables, onMutateResult, context)
    },
  })
}

export function useRefreshSession(options?: RefMutationOptions<DetailResponse, void>) {
  const queryClient = useQueryClient()

  return useMutationWithRefs(authApi.refresh, {
    ...options,
    onSuccess: (data, variables, onMutateResult, context) => {
      queryClient.invalidateQueries({ queryKey: authKeys.user() })
      options?.onSuccess?.(data, variables, onMutateResult, context)
    },
  })
}

export function useLogout(options?: RefMutationOptions<DetailResponse, void>) {
  const queryClient = useQueryClient()

  return useMutationWithRefs(authApi.logout, {
    ...options,
    onSuccess: (data, variables, onMutateResult, context) => {
      queryClient.removeQueries({ queryKey: authKeys.user() })
      options?.onSuccess?.(data, variables, onMutateResult, context)
    },
  })
}

export function useVerifyEmail(
  options?: RefMutationOptions<DetailResponse, EmailVerificationPayload>,
) {
  return useMutationWithRefs(authApi.verifyEmail, options)
}

export function useResendVerificationEmail(
  options?: RefMutationOptions<DetailResponse, EmailResendPayload>,
) {
  return useMutationWithRefs(authApi.resendVerificationEmail, options)
}

export function useRequestPasswordReset(
  options?: RefMutationOptions<DetailResponse, PasswordResetPayload>,
) {
  return useMutationWithRefs(authApi.requestPasswordReset, options)
}

export function useConfirmPasswordReset(
  options?: RefMutationOptions<DetailResponse, PasswordResetConfirmPayload>,
) {
  return useMutationWithRefs(authApi.confirmPasswordReset, options)
}

export function useChangePassword(
  options?: RefMutationOptions<DetailResponse, ChangePasswordPayload>,
) {
  return useMutationWithRefs(authApi.changePassword, options)
}

export function useUpdateProfile(options?: RefMutationOptions<UserProfile, UpdateProfilePayload>) {
  const queryClient = useQueryClient()

  return useMutationWithRefs(authApi.updateProfile, {
    ...options,
    onSuccess: (data, variables, onMutateResult, context) => {
      queryClient.setQueryData(authKeys.user(), data)
      options?.onSuccess?.(data, variables, onMutateResult, context)
    },
  })
}

export function useDeleteAccount(options?: RefMutationOptions<void, DeleteAccountPayload>) {
  const queryClient = useQueryClient()

  return useMutationWithRefs(authApi.deleteAccount, {
    ...options,
    onSuccess: (data, variables, onMutateResult, context) => {
      queryClient.removeQueries({ queryKey: authKeys.user() })
      options?.onSuccess?.(data, variables, onMutateResult, context)
    },
  })
}

export function useCreateStatus(options?: RefMutationOptions<UserStatus, string>) {
  const queryClient = useQueryClient()

  return useMutationWithRefs(authApi.createStatus, {
    ...options,
    onSuccess: (data, variables, onMutateResult, context) => {
      queryClient.invalidateQueries({ queryKey: authKeys.statuses() })
      options?.onSuccess?.(data, variables, onMutateResult, context)
    },
  })
}

export function useDeleteStatus(options?: RefMutationOptions<void, number>) {
  const queryClient = useQueryClient()

  return useMutationWithRefs(authApi.deleteStatus, {
    ...options,
    onSuccess: (data, variables, onMutateResult, context) => {
      queryClient.invalidateQueries({ queryKey: authKeys.statuses() })
      queryClient.invalidateQueries({ queryKey: authKeys.user() })
      options?.onSuccess?.(data, variables, onMutateResult, context)
    },
  })
}

export function useSetCurrentStatus(
  options?: RefMutationOptions<UserProfile, SetCurrentStatusPayload>,
) {
  const queryClient = useQueryClient()

  return useMutationWithRefs(authApi.setCurrentStatus, {
    ...options,
    onSuccess: (data, variables, onMutateResult, context) => {
      queryClient.setQueryData(authKeys.user(), data)
      options?.onSuccess?.(data, variables, onMutateResult, context)
    },
  })
}

export function useAddFriend(options?: RefMutationOptions<Friend, AddFriendPayload>) {
  const queryClient = useQueryClient()

  return useMutationWithRefs(authApi.addFriend, {
    ...options,
    onSuccess: (data, variables, onMutateResult, context) => {
      queryClient.invalidateQueries({ queryKey: authKeys.friends() })
      options?.onSuccess?.(data, variables, onMutateResult, context)
    },
  })
}

export function useRemoveFriend(options?: RefMutationOptions<void, number>) {
  const queryClient = useQueryClient()

  return useMutationWithRefs(authApi.removeFriend, {
    ...options,
    onSuccess: (data, variables, onMutateResult, context) => {
      queryClient.invalidateQueries({ queryKey: authKeys.friends() })
      options?.onSuccess?.(data, variables, onMutateResult, context)
    },
  })
}

export function useAcceptFriendRequest(options?: RefMutationOptions<Friend, number>) {
  const queryClient = useQueryClient()

  return useMutationWithRefs(authApi.acceptFriendRequest, {
    ...options,
    onSuccess: (data, variables, onMutateResult, context) => {
      queryClient.invalidateQueries({ queryKey: authKeys.friends() })
      queryClient.invalidateQueries({ queryKey: authKeys.friendRequests() })
      options?.onSuccess?.(data, variables, onMutateResult, context)
    },
  })
}

export function useRejectFriendRequest(options?: RefMutationOptions<Friend, number>) {
  const queryClient = useQueryClient()

  return useMutationWithRefs(authApi.rejectFriendRequest, {
    ...options,
    onSuccess: (data, variables, onMutateResult, context) => {
      queryClient.invalidateQueries({ queryKey: authKeys.friendRequests() })
      options?.onSuccess?.(data, variables, onMutateResult, context)
    },
  })
}
