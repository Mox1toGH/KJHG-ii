export interface PublicUser {
  id: number
  username: string
  email: string
  first_name: string
  last_name: string
  avatar: string | null
  current_status: string | null
  created_at: string
  last_seen: string | null
  hexagons_explored?: number
  checkpoints_visited?: number
}

export interface MapObjectCreator {
  id: number
  username: string
  display_name: string
  avatar: string | null
  current_status: string | null
}

export interface UserProfile extends PublicUser {
  email: string
  is_email_verified: boolean
  auth_provider: string
}

export interface RegisterPayload {
  username: string
  email: string
  first_name?: string
  last_name?: string
  password: string
}

export interface LoginPayload {
  identifier: string
  password: string
}

export interface EmailVerificationPayload {
  uid: string
  token: string
}

export interface EmailResendPayload {
  email: string
}

export interface PasswordResetPayload {
  email: string
}

export interface PasswordResetConfirmPayload {
  uid: string
  token: string
  new_password: string
}

export interface ChangePasswordPayload {
  current_password: string
  new_password: string
}

export interface UpdateProfilePayload {
  username?: string
  email?: string
  first_name?: string
  last_name?: string
  avatar?: File | null
}

export interface DeleteAccountPayload {
  password: string
}

export interface GoogleLoginPayload {
  credential: string
}

export interface DetailResponse {
  detail: string
}

export interface UserStatus {
  id: number
  name: string
  created_at: string
  updated_at: string
}

export interface SetCurrentStatusPayload {
  status_id: number | null
}

export interface Friend {
  id: number
  friend: PublicUser
  friend_id: number
  status: 'pending' | 'accepted' | 'rejected'
  created_at: string
  updated_at: string
}

export interface AddFriendPayload {
  friend_id: number
}

export interface FriendStatusResponse {
  is_friend: boolean
  status?: 'pending' | 'accepted' | 'rejected'
}
