<script setup lang="ts">
import { computed, ref } from 'vue'
import { UserRound, UserMinus, UserPlus, Check, X, Search } from '@lucide/vue'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'

import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { useCurrentUser, useFriends, useRemoveFriend, useFriendRequests, useAcceptFriendRequest, useRejectFriendRequest, useAddFriend, usePublicUserProfile } from '@/features/auth'

const { t } = useI18n()
const router = useRouter()
const userQuery = useCurrentUser()
const friendsQuery = useFriends()
const friendRequestsQuery = useFriendRequests()
const removeFriendMutation = useRemoveFriend()
const acceptFriendRequestMutation = useAcceptFriendRequest()
const rejectFriendRequestMutation = useRejectFriendRequest()
const addFriendMutation = useAddFriend()

const usernameInput = ref('')
const searchError = ref('')

const displayName = (user: { first_name: string; last_name: string; username: string }) => {
  return [user.first_name, user.last_name].filter(Boolean).join(' ') || user.username
}

const handleRemoveFriend = (friendId: number) => {
  if (confirm('Are you sure you want to remove this friend?')) {
    removeFriendMutation.mutate(friendId)
  }
}

const handleAcceptRequest = (requestId: number) => {
  acceptFriendRequestMutation.mutate(requestId)
}

const handleRejectRequest = (requestId: number) => {
  if (confirm('Are you sure you want to reject this friend request?')) {
    rejectFriendRequestMutation.mutate(requestId)
  }
}

const goToPublicProfile = (username: string) => {
  router.push(`/profile/${username}`)
}

const handleAddFriendByUsername = async () => {
  searchError.value = ''
  const username = usernameInput.value.trim()
  if (!username) {
    searchError.value = 'Please enter a username'
    return
  }

  try {
    // First, get the user by username to find their ID
    const userResponse = await fetch(`/api/accounts/${username}/`)
    if (!userResponse.ok) {
      searchError.value = 'User not found'
      return
    }
    const userData = await userResponse.json()

    // Check if already friends
    if (friendsQuery.data.value?.some(f => f.friend_id === userData.id)) {
      searchError.value = 'This user is already your friend'
      return
    }

    // Add friend
    addFriendMutation.mutate({ friend_id: userData.id }, {
      onSuccess: () => {
        usernameInput.value = ''
      },
      onError: (error) => {
        searchError.value = error.message || 'Failed to add friend'
      }
    })
  } catch (error) {
    searchError.value = 'User not found'
  }
}
</script>

<template>
  <main class="mx-auto max-w-3xl px-4 py-8 sm:px-6 lg:py-12">
    <header class="mb-8">
      <p class="mb-2 text-xs font-semibold uppercase tracking-[0.25em] text-muted-foreground">
        MDVL / Friends
      </p>
      <h1 class="text-3xl font-bold tracking-tight sm:text-4xl">Friends</h1>
      <p class="mt-2 text-muted-foreground">Manage your friends list</p>
    </header>

    <!-- Add Friend by Username -->
    <Card class="mb-6">
      <CardHeader>
        <CardTitle class="flex items-center gap-2">
          <UserPlus class="size-5" />
          Add Friend by Username
        </CardTitle>
        <CardDescription>Enter a username to send a friend request</CardDescription>
      </CardHeader>
      <CardContent>
        <div class="flex gap-2">
          <Input
            v-model="usernameInput"
            placeholder="Enter username"
            @keyup.enter="handleAddFriendByUsername"
          />
          <Button
            type="button"
            :disabled="addFriendMutation.isPending.value || !usernameInput.trim()"
            @click="handleAddFriendByUsername"
          >
            <Search class="mr-2 size-4" />
            Add
          </Button>
        </div>
        <p v-if="searchError" class="mt-2 text-sm text-destructive">{{ searchError }}</p>
      </CardContent>
    </Card>

    <!-- Friend Requests Section -->
    <Card v-if="friendRequestsQuery.data.value && friendRequestsQuery.data.value.length > 0" class="mb-6">
      <CardHeader>
        <CardTitle class="flex items-center gap-2">
          <UserPlus class="size-5" />
          Friend Requests
          <span class="rounded-full bg-primary px-2 py-0.5 text-xs text-primary-foreground">
            {{ friendRequestsQuery.data.value.length }}
          </span>
        </CardTitle>
        <CardDescription>People who want to be your friend</CardDescription>
      </CardHeader>
      <CardContent class="space-y-3">
        <div
          v-for="request in friendRequestsQuery.data.value"
          :key="request.id"
          class="flex items-center gap-3 rounded-lg border border-border p-3"
        >
          <div
            class="size-10 shrink-0 overflow-hidden rounded-lg bg-primary text-primary-foreground"
          >
            <img
              v-if="request.friend.avatar"
              :src="request.friend.avatar"
              :alt="`${request.friend.username}'s avatar`"
              class="size-full object-cover"
            />
            <UserRound v-else class="m-2 size-6" aria-hidden="true" />
          </div>
          <div class="min-w-0 flex-1">
            <p class="truncate font-medium">{{ displayName(request.friend) }}</p>
            <p class="truncate text-sm text-muted-foreground">@{{ request.friend.username }}</p>
          </div>
          <div class="flex items-center gap-2">
            <Button
              type="button"
              size="icon"
              :disabled="acceptFriendRequestMutation.isPending.value"
              :aria-label="`Accept ${request.friend.username}'s friend request`"
              @click="handleAcceptRequest(request.id)"
            >
              <Check class="size-4" />
            </Button>
            <Button
              type="button"
              variant="outline"
              size="icon"
              :disabled="rejectFriendRequestMutation.isPending.value"
              :aria-label="`Reject ${request.friend.username}'s friend request`"
              @click="handleRejectRequest(request.id)"
            >
              <X class="size-4" />
            </Button>
          </div>
        </div>
      </CardContent>
    </Card>

    <!-- Friends List Section -->
    <div
      v-if="friendsQuery.isPending.value"
      class="rounded-xl border border-dashed border-border p-12 text-center text-muted-foreground"
    >
      Loading friends…
    </div>

    <div
      v-else-if="friendsQuery.error.value"
      class="rounded-xl border border-destructive/40 p-8 text-center text-destructive"
    >
      Failed to load friends.
    </div>

    <template v-else-if="friendsQuery.data.value">
      <Card v-if="friendsQuery.data.value.length === 0" class="mb-5">
        <CardContent class="flex flex-col items-center justify-center p-12 text-center">
          <UserRound class="mb-4 size-12 text-muted-foreground" />
          <h3 class="text-lg font-semibold">No friends yet</h3>
          <p class="mt-2 text-sm text-muted-foreground">
            Visit public profiles to add friends.
          </p>
        </CardContent>
      </Card>

      <div v-else class="space-y-3">
        <Card
          v-for="friend in friendsQuery.data.value"
          :key="friend.id"
          class="cursor-pointer transition-colors hover:bg-accent/50"
          @click="goToPublicProfile(friend.friend.username)"
        >
          <CardContent class="flex items-center gap-4 p-4">
            <div
              class="size-12 shrink-0 overflow-hidden rounded-xl bg-primary text-primary-foreground"
            >
              <img
                v-if="friend.friend.avatar"
                :src="friend.friend.avatar"
                :alt="`${friend.friend.username}'s avatar`"
                class="size-full object-cover"
              />
              <UserRound v-else class="m-3 size-6" aria-hidden="true" />
            </div>
            <div class="min-w-0 flex-1">
              <h3 class="truncate font-semibold">{{ displayName(friend.friend) }}</h3>
              <p class="truncate text-sm text-muted-foreground">@{{ friend.friend.username }}</p>
            </div>
            <div class="flex items-center gap-2" @click.stop>
              <Button
                type="button"
                variant="ghost"
                size="icon"
                :disabled="removeFriendMutation.isPending.value"
                :aria-label="`Remove ${friend.friend.username} from friends`"
                @click="handleRemoveFriend(friend.friend_id)"
              >
                <UserMinus class="size-4 text-destructive" />
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>
    </template>
  </main>
</template>
