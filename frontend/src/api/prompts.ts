import { request } from './client'
import type { Prompt, PromptListResponse, PromptPayload } from '../types'

export async function getPrompts(collectionId?: string): Promise<PromptListResponse> {
  const query = collectionId ? `?collection_id=${encodeURIComponent(collectionId)}` : ''
  return request<PromptListResponse>(`/prompts${query}`)
}

export async function createPrompt(payload: PromptPayload): Promise<Prompt> {
  return request<Prompt>('/prompts', {
    method: 'POST',
    body: JSON.stringify(payload),
  })
}

export async function updatePrompt(promptId: string, payload: PromptPayload): Promise<Prompt> {
  return request<Prompt>(`/prompts/${promptId}`, {
    method: 'PUT',
    body: JSON.stringify(payload),
  })
}

export async function deletePrompt(promptId: string): Promise<void> {
  return request<void>(`/prompts/${promptId}`, {
    method: 'DELETE',
  })
}
