export const authKeys = {
  all: ['auth'] as const,
  user: () => [...authKeys.all, 'user'] as const,
  publicUser: () => [...authKeys.all, 'public-user'] as const,
  statuses: () => [...authKeys.all, 'statuses'] as const,
  friends: () => [...authKeys.all, 'friends'] as const,
  friendStatus: (userId: number) => [...authKeys.all, 'friend-status', userId] as const,
  friendRequests: () => [...authKeys.all, 'friend-requests'] as const,
}
