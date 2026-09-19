const API_BASE_URL = (import.meta as any).env?.VITE_API_BASE_URL || '/api/v1'

export async function fetchApi<T>(endpoint: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE_URL}${endpoint}`, {
    headers: {
      'Content-Type': 'application/json',
      ...options?.headers,
    },
    ...options,
  })

  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}))
    throw new Error(errorData.detail || `API request failed with status ${res.status}`)
  }

  return res.json()
}

export const api = {
  syncProfile: (handle: string) =>
    fetchApi<{ handle: string; status: string; sync_job_id: string }>(`/cf/profile/${handle}`, {
      method: 'POST',
    }),

  getSyncStatus: (jobId: string) =>
    fetchApi<{ handle: string; status: string; sync_job_id: string; error_message?: string }>(
      `/cf/sync-status/${jobId}`
    ),

  getOverview: (handle: string) =>
    fetchApi<{
      handle: string
      current_rating: number
      max_rating: number
      rank: string
      max_rank: string
      avatar: string
      volatility: number
      contests_attended: number
      total_solved: number
      total_submissions: number
      overall_accuracy: number
    }>(`/analytics/overview/${handle}`),

  getContests: (handle: string) =>
    fetchApi<{
      handle: string
      total_contests: number
      best_rank: number
      max_positive_delta: number
      max_negative_delta: number
      contests: Array<{
        contest_id: number
        name: string
        rank: number
        old_rating: number
        new_rating: number
        rating_change: number
      }>
    }>(`/analytics/contests/${handle}`),

  getTopics: (handle: string) =>
    fetchApi<{
      handle: string
      difficulty_distribution: Record<number, number>
      tags: Array<{
        tag: string
        solved_count: number
        attempted_count: number
        max_rating_solved: number
        accuracy: number
      }>
    }>(`/analytics/topics/${handle}`),

  getSkillGap: (handle: string) =>
    fetchApi<{
      handle: string
      overall_rating: number
      weaknesses_count: number
      balanced_count: number
      strengths_count: number
      gaps: Array<{
        tag: string
        user_rating: number
        tag_effective_rating: number
        gap_delta: number
        classification: string
      }>
    }>(`/skill-gap/matrix/${handle}`),

  getRecommendations: (handle: string) =>
    fetchApi<{
      handle: string
      total_recommendations: number
      recommendations: Array<{
        problem_id: string
        contest_id: number
        index: string
        name: string
        rating: number
        recommendation_type: string
        reason: string
        tags: string[]
      }>
    }>(`/recommendations/daily/${handle}`),

  getAICoachReview: (handle: string) =>
    fetchApi<{
      handle: string
      current_rating: number
      summary: string
      tactical_advice: string[]
      strengths_assessment: string[]
      weaknesses_assessment: string[]
      action_plan: Array<{
        step: number
        focus_area: string
        action: string
        target_problem_rating: number
      }>
    }>(`/ai-coach/review/${handle}`, { method: 'POST' }),
}
