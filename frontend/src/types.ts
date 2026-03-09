export interface Prompt {
  id: string
  title: string
  content: string
  description: string | null
  collection_id: string | null
  created_at: string
  updated_at: string
}

export interface PromptListResponse {
  prompts: Prompt[]
  total: number
}

export interface Collection {
  id: string
  name: string
  description: string | null
  created_at: string
}

export interface CollectionListResponse {
  collections: Collection[]
  total: number
}

export interface PromptPayload {
  title: string
  content: string
  description?: string | null
  collection_id?: string | null
}

export interface CollectionPayload {
  name: string
  description?: string | null
}
