import apiClient from '@/lib/api/client'

export const sosApi = {
  state: (activityId: string) =>
    apiClient.get<{ active: boolean; activated_at: string | null }>(
      `/tracking/activities/${activityId}/sos/`,
    ).then(({ data }) => data),
  setActive: (activityId: string, active: boolean) =>
    apiClient.post<{ active: boolean; activated_at: string | null }>(
      `/tracking/activities/${activityId}/sos/`,
      { active },
    ).then(({ data }) => data),
}
