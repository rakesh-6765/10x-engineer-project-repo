import { useCallback, useEffect, useMemo, useState } from 'react'
import { getCollections, createCollection, updateCollection, deleteCollection } from './api/collections'
import { createPrompt, deletePrompt, getPrompts, updatePrompt } from './api/prompts'
import { ApiError } from './api/client'
import { FeedbackBanner } from './components/FeedbackBanner'
import { LoadingOverlay } from './components/LoadingOverlay'
import { PromptForm } from './features/prompts/PromptForm'
import { PromptGrid } from './features/prompts/PromptGrid'
import { PromptFilters } from './features/prompts/PromptFilters'
import { CollectionsPanel } from './features/collections/CollectionsPanel'
import type { Collection, CollectionPayload, Prompt, PromptPayload } from './types'

interface AsyncState {
  loading: boolean
  error: string | null
  success: string | null
}

function getErrorMessage(error: unknown): string {
  if (error instanceof ApiError) {
    return error.message
  }

  if (error instanceof Error) {
    return error.message
  }

  return 'Unexpected error. Please retry.'
}

function App() {
  const [collections, setCollections] = useState<Collection[]>([])
  const [prompts, setPrompts] = useState<Prompt[]>([])
  const [selectedPrompt, setSelectedPrompt] = useState<Prompt | null>(null)
  const [activeCollectionFilter, setActiveCollectionFilter] = useState('')

  const [bootLoading, setBootLoading] = useState(true)
  const [promptState, setPromptState] = useState<AsyncState>({
    loading: false,
    error: null,
    success: null,
  })
  const [collectionState, setCollectionState] = useState<AsyncState>({
    loading: false,
    error: null,
    success: null,
  })

  const loadData = useCallback(async () => {
    setBootLoading(true)
    try {
      const [collectionResponse, promptResponse] = await Promise.all([
        getCollections(),
        getPrompts(activeCollectionFilter || undefined),
      ])
      setCollections(collectionResponse.collections)
      setPrompts(promptResponse.prompts)
    } finally {
      setBootLoading(false)
    }
  }, [activeCollectionFilter])

  useEffect(() => {
    loadData().catch((error: unknown) => {
      setPromptState((prev) => ({ ...prev, error: getErrorMessage(error) }))
    })
  }, [loadData])

  const collectionNameMap = useMemo(
    () => new Map(collections.map((collection) => [collection.id, collection.name])),
    [collections],
  )

  async function handlePromptSubmit(payload: PromptPayload) {
    setPromptState({ loading: true, error: null, success: null })
    try {
      if (selectedPrompt) {
        await updatePrompt(selectedPrompt.id, payload)
        setPromptState({ loading: false, error: null, success: 'Prompt updated.' })
      } else {
        await createPrompt(payload)
        setPromptState({ loading: false, error: null, success: 'Prompt created.' })
      }
      setSelectedPrompt(null)
      await loadData()
    } catch (error: unknown) {
      setPromptState({ loading: false, error: getErrorMessage(error), success: null })
    }
  }

  async function handlePromptDelete(prompt: Prompt) {
    setPromptState({ loading: true, error: null, success: null })
    try {
      await deletePrompt(prompt.id)
      if (selectedPrompt?.id === prompt.id) {
        setSelectedPrompt(null)
      }
      setPromptState({ loading: false, error: null, success: 'Prompt deleted.' })
      await loadData()
    } catch (error: unknown) {
      setPromptState({ loading: false, error: getErrorMessage(error), success: null })
    }
  }

  async function handleCreateCollection(payload: CollectionPayload) {
    setCollectionState({ loading: true, error: null, success: null })
    try {
      await createCollection(payload)
      setCollectionState({ loading: false, error: null, success: 'Collection created.' })
      await loadData()
    } catch (error: unknown) {
      setCollectionState({ loading: false, error: getErrorMessage(error), success: null })
    }
  }

  async function handleUpdateCollection(collectionId: string, payload: CollectionPayload) {
    setCollectionState({ loading: true, error: null, success: null })
    try {
      await updateCollection(collectionId, payload)
      setCollectionState({ loading: false, error: null, success: 'Collection updated.' })
      await loadData()
    } catch (error: unknown) {
      setCollectionState({ loading: false, error: getErrorMessage(error), success: null })
    }
  }

  async function handleDeleteCollection(collectionId: string) {
    setCollectionState({ loading: true, error: null, success: null })
    try {
      await deleteCollection(collectionId)
      setCollectionState({ loading: false, error: null, success: 'Collection deleted.' })
      if (activeCollectionFilter === collectionId) {
        setActiveCollectionFilter('')
      }
      await loadData()
    } catch (error: unknown) {
      setCollectionState({ loading: false, error: getErrorMessage(error), success: null })
    }
  }

  return (
    <div className="app-shell">
      <header className="hero">
        <p className="eyebrow">PromptLab Workspace</p>
        <h1>Build, Curate, and Ship Better AI Prompts</h1>
        <p>
          Manage prompt assets and collections in one place, with full backend integration and
          durable CRUD workflows.
        </p>
      </header>

      {promptState.error ? <FeedbackBanner tone="error" message={promptState.error} /> : null}
      {collectionState.error ? <FeedbackBanner tone="error" message={collectionState.error} /> : null}
      {promptState.success ? <FeedbackBanner tone="success" message={promptState.success} /> : null}
      {collectionState.success ? <FeedbackBanner tone="success" message={collectionState.success} /> : null}

      <main className="layout">
        <section className="main-column stack">
          <PromptForm
            collections={collections}
            selectedPrompt={selectedPrompt}
            onSubmit={handlePromptSubmit}
            onCancelEdit={() => setSelectedPrompt(null)}
            isSubmitting={promptState.loading}
          />

          <div className="toolbar">
            <h2>Prompt Library ({prompts.length})</h2>
            <PromptFilters
              collections={collections}
              activeCollectionId={activeCollectionFilter}
              onCollectionChange={setActiveCollectionFilter}
            />
          </div>

          <PromptGrid
            prompts={prompts}
            collections={collections}
            onEdit={setSelectedPrompt}
            onDelete={handlePromptDelete}
          />
        </section>

        <aside className="side-column">
          <CollectionsPanel
            collections={collections}
            prompts={prompts}
            onCreateCollection={handleCreateCollection}
            onUpdateCollection={handleUpdateCollection}
            onDeleteCollection={handleDeleteCollection}
            isSubmitting={collectionState.loading}
          />

          <section className="card stack">
            <h2>Collection Snapshot</h2>
            {collections.length === 0 ? (
              <p className="muted">No collections available.</p>
            ) : (
              <ul className="summary-list">
                {collections.map((collection) => (
                  <li key={collection.id}>
                    <span>{collection.name}</span>
                    <span>{prompts.filter((p) => p.collection_id === collection.id).length} prompts</span>
                  </li>
                ))}
              </ul>
            )}
            <small className="muted">
              Unassigned prompts: {prompts.filter((prompt) => !prompt.collection_id).length}
            </small>
            {selectedPrompt?.collection_id ? (
              <small className="muted">
                Editing in: {collectionNameMap.get(selectedPrompt.collection_id) ?? 'Unknown collection'}
              </small>
            ) : null}
          </section>
        </aside>
      </main>

      {bootLoading ? <LoadingOverlay label="Loading prompts and collections..." /> : null}
    </div>
  )
}

export default App
