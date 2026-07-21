export type ActivityStatus = 'DRAFT' | 'ACTIVE' | 'FINISHED' | 'CANCELLED'

export interface Activity {
  id: string
  title: string
  description: string
  created_by: number
  default_role_id: string | null
  started_at: string | null
  ended_at: string | null
  status: ActivityStatus
  participant_count: number
  created_at: string
  updated_at: string
}

export interface CreateActivityPayload {
  title: string
  description?: string
  status?: ActivityStatus
}

export interface ActivityMessage { detail: string }

export type ActivityPermissionCode = 'checkpoints.create' | 'locations.create' | 'routes.create' | 'checkpoints.qrcodes.manage' | 'checkpoints.photos.upload' | 'meeting_points.set' | 'participants.map.view'

export interface RolePermissionGrant {
  code: ActivityPermissionCode
  name: string
  scope: { visibility?: 'everyone' | 'roles'; role_ids?: string[] }
}

export interface ActivityRole {
  id: string
  name: string
  description: string
  color: string
  created_at: string
  permission_grants: RolePermissionGrant[]
}

export interface ActivityParticipant {
  id: string
  user: number
  user_profile: {
    id: number
    username: string
    first_name: string
    last_name: string
    avatar: string | null
    current_status: string | null
  }
  role: ActivityRole | null
  joined_at: string
}

export interface ActivityRolePermissionPayload {
  code: ActivityPermissionCode
  scope?: { visibility?: 'everyone' | 'roles'; role_ids?: string[] }
}

export interface ActivityRolePayload {
  name: string
  description?: string
  color?: string
  permissions: ActivityRolePermissionPayload[]
}

export interface JoinRequest {
  id: string
  activity: string
  activity_title: string
  user: number
  user_profile: {
    id: number
    username: string
    first_name: string
    last_name: string
    avatar: string | null
    current_status: string | null
  }
  status: 'PENDING' | 'ACCEPTED' | 'REJECTED'
  created_at: string
  updated_at: string
}
