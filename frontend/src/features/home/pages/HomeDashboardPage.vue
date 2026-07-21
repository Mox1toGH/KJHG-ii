<script setup lang="ts">
import { computed } from 'vue'
import { ArrowRight, Map, Plus, Users } from '@lucide/vue'
import { RouterLink } from 'vue-router'
import 'maplibre-gl/dist/maplibre-gl.css'
import { useActivities } from '@/features/activities/core/activity.queries'
import { Button } from '@/components/ui/button'
import LocationMapPreview from '../components/LocationMapPreview.vue'

const activitiesQuery = useActivities()
const activities = computed(() => activitiesQuery.data.value ?? [])

const errorMessage = (error: unknown) =>
  error instanceof Error ? error.message : 'Unable to load activities.'
</script>

<template>
  <main class="mx-auto min-h-screen w-full max-w-6xl px-4 pb-28 pt-8 sm:px-6 sm:pt-12">
    <header class="mb-8 flex items-end justify-between gap-4">
      <div>
        <p class="mb-2 text-xs font-semibold uppercase tracking-[0.25em] text-muted-foreground">
          MDVL / HOME
        </p>
        <h1 class="text-3xl font-bold tracking-tight sm:text-4xl">My activities</h1>
        <p class="mt-2 max-w-xl text-muted-foreground">
          Jump back into a room or see where you are.
        </p>
      </div>
      <Button as-child variant="outline" class="shrink-0">
        <RouterLink to="/activities"><Plus class="mr-2 size-4" />Manage</RouterLink>
      </Button>
    </header>

    <section aria-labelledby="activities-heading" class="mb-10">
      <div class="mb-4 flex items-center justify-between">
        <h2 id="activities-heading" class="text-xl font-semibold">Activities</h2>
        <span class="text-sm text-muted-foreground">{{ activities.length }}</span>
      </div>
      <div
        v-if="activitiesQuery.isPending.value"
        class="rounded-2xl border border-dashed p-10 text-center text-muted-foreground"
      >
        Loading activities...
      </div>
      <div
        v-else-if="activitiesQuery.error.value"
        class="rounded-2xl border border-destructive/40 p-8 text-center text-destructive"
      >
        {{ errorMessage(activitiesQuery.error.value) }}
      </div>
      <div v-else-if="!activities.length" class="rounded-2xl border border-dashed p-10 text-center">
        <Users class="mx-auto mb-3 size-9 text-muted-foreground" />
        <h3 class="font-semibold">No activities yet</h3>
        <p class="mx-auto mt-1 max-w-sm text-sm text-muted-foreground">
          Create a new room or join one using its ID to get started.
        </p>
        <Button as-child class="mt-5"
          ><RouterLink to="/activities"
            >Create or join an activity <ArrowRight class="ml-2 size-4" /></RouterLink
        ></Button>
      </div>
      <div v-else class="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        <RouterLink
          v-for="activity in activities"
          :key="activity.id"
          :to="{ name: 'activity-map', params: { activityId: activity.id } }"
          class="group rounded-2xl border bg-card p-5 shadow-sm transition hover:-translate-y-0.5 hover:border-primary/40 hover:shadow-md focus:outline-none focus:ring-2 focus:ring-ring"
        >
          <div class="flex items-start justify-between gap-3">
            <h3 class="min-w-0 truncate font-semibold">{{ activity.title }}</h3>
          </div>
          <p class="mt-3 min-h-10 line-clamp-2 text-sm text-muted-foreground">
            {{ activity.description || 'No description provided.' }}
          </p>
          <div class="mt-5 flex items-center justify-between text-sm text-muted-foreground">
            <span class="inline-flex items-center gap-2"
              ><Users class="size-4" />{{ activity.participant_count }}
              {{ activity.participant_count === 1 ? 'participant' : 'participants' }}</span
            >
            <ArrowRight
              class="size-4 transition-transform group-hover:translate-x-1"
              aria-hidden="true"
            />
          </div>
        </RouterLink>
      </div>
    </section>

    <section aria-labelledby="map-preview-heading">
      <div class="mb-4 flex items-center justify-between">
        <div>
          <h2 id="map-preview-heading" class="text-xl font-semibold">Map preview</h2>
          <p class="mt-1 text-sm text-muted-foreground">Your current location at a glance.</p>
        </div>
        <Map class="size-5 text-muted-foreground" aria-hidden="true" />
      </div>
      <LocationMapPreview />
    </section>
  </main>
</template>
