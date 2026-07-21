// ─── Core ────────────────────────────────────────────────────────────────────
export type {
  Activity,
  ActivityStatus,
  ActivityMessage,
  ActivityPermissionCode,
  RolePermissionGrant,
  ActivityRole,
  ActivityParticipant,
  ActivityRolePermissionPayload,
  ActivityRolePayload,
  CreateActivityPayload,
  JoinRequest,
} from './core/activity.types'

export { activityApi } from './core/activity.api'

export {
  activityKeys,
  useActivities,
  useCreateActivity,
  useDeleteActivity,
  useUpdateActivity,
  useJoinActivity,
  useLeaveActivity,
  useActivityRoles,
  useActivityParticipants,
  useCreateActivityRole,
  useUpdateActivityRole,
  useDeleteActivityRole,
  useAssignActivityRole,
  useRemoveActivityParticipant,
  useJoinRequests,
  useApproveJoinRequest,
  useRejectJoinRequest,
} from './core/activity.queries'

// ─── Composables ──────────────────────────────────────────────────────────────
export { useHiddenParticipants } from './composables/useHiddenParticipants'

// ─── Tracking ─────────────────────────────────────────────────────────────────
export type {
  ParticipantLocation,
  LocationUpdatedMessage,
  SosUpdatedMessage,
} from './tracking/tracking.types'

export { trackingApi } from './tracking/tracking.api'
export { useActivityTracking } from './tracking/useActivityTracking'

// ─── SOS ─────────────────────────────────────────────────────────────────────
export { sosApi } from './sos/sos.api'
export {
  sosActive,
  sosActivityId,
  currentActivityId,
  sosFocusParticipantId,
  updateSosState,
  setCurrentActivityId,
  requestSosParticipantFocus,
} from './sos/sos.state'
