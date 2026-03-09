import { request } from './client'
import type {
  Collection,
  CollectionListResponse,
  CollectionPayload,
} from '../types'

export async function getCollections(): Promise<CollectionListResponse> {
  return request<CollectionListResponse>('/collections')
}

export async function createCollection(payload: CollectionPayload): Promise<Collection> {
  return request<Collection>('/collections', {
    method: 'POST',
    body: JSON.stringify(payload),
  })
}

export async function updateCollection(
  collectionId: string,
  payload: CollectionPayload,
): Promise<Collection> {
  return request<Collection>(`/collections/${collectionId}`, {
    method: 'PUT',
    body: JSON.stringify(payload),
  })
}

export async function deleteCollection(collectionId: string): Promise<void> {
  return request<void>(`/collections/${collectionId}`, {
    method: 'DELETE',
  })
}
