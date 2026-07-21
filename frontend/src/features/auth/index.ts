// Core types
export type {
  PublicUser,
  UserProfile,
  RegisterPayload,
  LoginPayload,
  EmailVerificationPayload,
  EmailResendPayload,
  PasswordResetPayload,
  PasswordResetConfirmPayload,
  ChangePasswordPayload,
  UpdateProfilePayload,
  DeleteAccountPayload,
  GoogleLoginPayload,
  DetailResponse,
  UserStatus,
  SetCurrentStatusPayload,
  Friend,
  AddFriendPayload,
  FriendStatusResponse,
} from './core/auth.types'

// Core API & Keys
export { authApi } from './core/auth.api'
export { authKeys } from './core/auth.keys'

// Core queries
export { useCurrentUser, usePublicUserProfile, useUserStatuses, useFriends, useFriendStatus, useFriendRequests } from './core/auth.queries'

// Core mutations
export {
  useRegister,
  useLogin,
  useGoogleLogin,
  useRefreshSession,
  useLogout,
  useVerifyEmail,
  useResendVerificationEmail,
  useRequestPasswordReset,
  useConfirmPasswordReset,
  useChangePassword,
  useUpdateProfile,
  useDeleteAccount,
  useCreateStatus,
  useDeleteStatus,
  useSetCurrentStatus,
  useAddFriend,
  useRemoveFriend,
  useAcceptFriendRequest,
  useRejectFriendRequest,
} from './core/auth.mutations'

// Core errors & validation
export { getAuthErrorMessage } from './core/auth.errors'
export {
  loginSchema,
  signupSchema,
  validateLoginForm,
  validateSignupForm,
} from './core/auth.validation'

// Routes
export { authRoutes } from './routes'
