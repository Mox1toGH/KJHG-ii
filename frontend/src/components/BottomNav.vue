<script setup lang="ts">
import { ChevronDown, CircleUserRound, Home, ListChecks, PanelBottomOpen, Siren } from '@lucide/vue'
import { computed, nextTick, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import { RouterLink, useRoute, useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { sosApi, activityApi, setCurrentActivityId, updateSosState } from '@/features/activities'

const { t } = useI18n()
const route = useRoute()
const router = useRouter()
const routeActivityId = computed(() =>
  typeof route.params.activityId === 'string' ? route.params.activityId : undefined,
)
const selectedActivityId = ref<string | undefined>(
  typeof window !== 'undefined'
    ? (window.localStorage.getItem('mdvl-current-activity-id') ?? undefined)
    : undefined,
)
const activityId = computed(() => routeActivityId.value ?? selectedActivityId.value)
const sosActive = ref(false)
const sosUpdating = ref(false)
const storageKey = 'mdvl-bottom-nav-state'
const storedState = typeof window !== 'undefined' ? window.localStorage.getItem(storageKey) : null
const navState = ref<'open' | 'hidden'>(storedState === 'hidden' ? 'hidden' : 'open')

const items = [
  { label: t('common.home'), to: '/', icon: Home },
  { label: t('activities.activities'), to: '/activities', icon: ListChecks },
  { label: t('profile.myProfile'), to: '/profile', icon: CircleUserRound },
]

const isHidden = computed(() => navState.value === 'hidden')

function isActive(to: string) {
  if (to === '/') return route.path === '/'
  if (to === '/profile' && route.name === 'public-profile') return false
  return route.path === to || route.path.startsWith(`${to}/`)
}

function setNavState(value: 'open' | 'hidden') {
  navState.value = value
}

async function toggleSos() {
  if (sosUpdating.value) return
  if (!activityId.value) {
    await router.push('/activities')
    return
  }
  sosUpdating.value = true
  try {
    const result = await sosApi.setActive(activityId.value, !sosActive.value)
    sosActive.value = result.active
    updateSosState(activityId.value, result.active)
  } finally {
    sosUpdating.value = false
  }
}

watch(navState, (value) => {
  if (typeof window !== 'undefined') {
    window.localStorage.setItem(storageKey, value)
  }
})

watch(
  activityId,
  (value) => {
    setCurrentActivityId(value)
    sosActive.value = false
    updateSosState(value, false)
    if (value)
      void sosApi
        .state(value)
        .then((result) => {
          sosActive.value = result.active
          updateSosState(value, result.active)
        })
        .catch(() => undefined)
  },
  { immediate: true },
)

watch(routeActivityId, (value) => {
  if (value) selectedActivityId.value = value
})

watch(selectedActivityId, (value) => {
  if (typeof window !== 'undefined' && value)
    window.localStorage.setItem('mdvl-current-activity-id', value)
})

onMounted(() => {
  if (routeActivityId.value || selectedActivityId.value) return

  void activityApi
    .list()
    .then((activities) => {
      selectedActivityId.value = activities[0]?.id
    })
    .catch(() => undefined)
})

// --- horizontal scroll fade indicators ---
const navScrollEl = ref<HTMLElement | null>(null)
const canScrollLeft = ref(false)
const canScrollRight = ref(false)

function updateScrollFade() {
  const node = navScrollEl.value
  if (!node) return
  const { scrollLeft, scrollWidth, clientWidth } = node
  canScrollLeft.value = scrollLeft > 1
  canScrollRight.value = scrollLeft + clientWidth < scrollWidth - 1
}

let resizeObserver: ResizeObserver | null = null

function attachScrollListeners(node: HTMLElement) {
  node.addEventListener('scroll', updateScrollFade, { passive: true })
  resizeObserver = new ResizeObserver(updateScrollFade)
  resizeObserver.observe(node)
  updateScrollFade()
}

function detachScrollListeners(node: HTMLElement) {
  node.removeEventListener('scroll', updateScrollFade)
  resizeObserver?.disconnect()
  resizeObserver = null
}

watch(isHidden, async (hidden) => {
  if (!hidden) {
    await nextTick()
    if (navScrollEl.value) attachScrollListeners(navScrollEl.value)
  } else if (navScrollEl.value) {
    detachScrollListeners(navScrollEl.value)
  }
})

onMounted(async () => {
  if (!isHidden.value) {
    await nextTick()
    if (navScrollEl.value) attachScrollListeners(navScrollEl.value)
  }
})

onBeforeUnmount(() => {
  if (navScrollEl.value) detachScrollListeners(navScrollEl.value)
})
</script>

<template>
  <div
    class="fixed bottom-3 left-1/2 z-50 -translate-x-1/2 sm:bottom-4"
    :class="isHidden ? 'w-max' : 'w-[calc(100%-0.75rem)] sm:w-[calc(100%-1.5rem)] sm:max-w-xl'"
  >
    <transition name="bottom-nav" mode="out-in" appear>
      <template v-if="isHidden">
        <button
          type="button"
          key="open-btn"
          class="mx-auto flex h-12 w-12 items-center justify-center rounded-full border border-border/70 bg-background/95 text-foreground shadow-md shadow-black/10 backdrop-blur transition hover:bg-accent focus:outline-none focus:ring-2 focus:ring-ring"
          aria-label="Open bottom navigation"
          title="Open navigation"
          @click="setNavState('open')"
        >
          <PanelBottomOpen class="h-5 w-5" aria-hidden="true" />
        </button>
      </template>

      <template v-else>
        <div key="nav" class="relative overflow-hidden rounded-full">
          <nav
            ref="navScrollEl"
            class="overflow-x-auto rounded-full border border-foreground/10 bg-background/95 px-1.5 py-1.5 shadow-md shadow-black/10 ring-1 ring-background/80 backdrop-blur [-ms-overflow-style:none] scrollbar-none [&::-webkit-scrollbar]:hidden sm:px-2 sm:py-2"
            aria-label="Bottom navigation"
          >
            <div class="mx-auto flex w-max items-center gap-1">
              <template v-for="(item, index) in items" :key="item.to">
                <span
                  v-if="index > 0"
                  class="h-5 w-px shrink-0 bg-foreground/10"
                  aria-hidden="true"
                />

                <RouterLink
                  :to="item.to"
                  class="flex h-11 shrink-0 items-center justify-center overflow-hidden rounded-full text-[13px] font-medium transition-[width,background-color,color,box-shadow] duration-300 ease-out"
                  :class="
                    isActive(item.to)
                      ? 'w-28 gap-1.5 bg-primary px-3 text-primary-foreground shadow-sm sm:w-32'
                      : 'w-11 px-0 text-muted-foreground hover:bg-accent hover:text-foreground'
                  "
                  :aria-label="item.label"
                >
                  <component :is="item.icon" class="h-4 w-4 shrink-0" aria-hidden="true" />
                  <span
                    class="truncate transition-[max-width,opacity] duration-300 ease-out"
                    :class="isActive(item.to) ? 'max-w-20 opacity-100' : 'max-w-0 opacity-0'"
                    aria-hidden="true"
                  >
                    {{ item.label }}
                  </span>
                </RouterLink>
              </template>

              <span class="mx-0.5 h-6 w-px shrink-0 bg-foreground/15" aria-hidden="true" />

              <button
                type="button"
                class="flex h-11 shrink-0 items-center justify-center gap-1.5 rounded-full px-3 text-[13px] font-bold text-white transition focus:outline-none focus:ring-2 focus:ring-red-300 disabled:opacity-60"
                :class="
                  sosActive ? 'bg-slate-700 hover:bg-slate-600' : 'bg-red-600 hover:bg-red-500'
                "
                :disabled="sosUpdating"
                :aria-label="
                  activityId
                    ? sosActive
                      ? 'Cancel SOS'
                      : 'Activate SOS'
                    : 'Choose an activity to activate SOS'
                "
                :title="activityId ? undefined : 'Choose an activity to activate SOS'"
                @click="toggleSos"
              >
                <Siren class="h-4 w-4" aria-hidden="true" />
                <span>{{ sosActive ? t('common.cancelSOS') : t('common.sos') }}</span>
              </button>

              <button
                type="button"
                class="flex h-11 w-11 shrink-0 items-center justify-center rounded-full text-muted-foreground transition-colors hover:bg-accent hover:text-foreground focus:outline-none focus:ring-2 focus:ring-ring"
                aria-label="Hide bottom navigation"
                title="Hide navigation"
                @click="setNavState('hidden')"
              >
                <ChevronDown class="h-4 w-4" aria-hidden="true" />
              </button>
            </div>
          </nav>

          <!-- left scroll fade -->
          <div
            class="pointer-events-none absolute inset-y-0 left-0 z-10 w-6 bg-linear-to-r from-white/25 to-transparent backdrop-blur-[2px] transition-opacity duration-200"
            :class="canScrollLeft ? 'opacity-100' : 'opacity-0'"
            aria-hidden="true"
          />

          <!-- right scroll fade -->
          <div
            class="pointer-events-none absolute inset-y-0 right-0 z-10 w-6 bg-linear-to-l from-white/25 to-transparent backdrop-blur-[2px] transition-opacity duration-200"
            :class="canScrollRight ? 'opacity-100' : 'opacity-0'"
            aria-hidden="true"
          />
        </div>
      </template>
    </transition>
  </div>
</template>

<style scoped>
/* Fast, snappy bottom-nav animation */
.bottom-nav-enter-from,
.bottom-nav-leave-to {
  transform: translateY(10px) scale(0.98);
  opacity: 0;
}

.bottom-nav-enter-active {
  transition:
    transform 160ms cubic-bezier(0.2, 0.9, 0.2, 1),
    opacity 160ms cubic-bezier(0.2, 0.9, 0.2, 1);
  will-change: transform, opacity;
  transform-origin: center bottom;
}

.bottom-nav-leave-active {
  transition:
    transform 120ms cubic-bezier(0.4, 0, 0.2, 1),
    opacity 120ms cubic-bezier(0.4, 0, 0.2, 1);
  will-change: transform, opacity;
}

.bottom-nav-enter-to,
.bottom-nav-leave-from {
  transform: translateY(0) scale(1);
  opacity: 1;
}

/* Slight pop for the open button when it appears */
.bottom-nav-enter-from {
  filter: blur(0);
}
</style>
