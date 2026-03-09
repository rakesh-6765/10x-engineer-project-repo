import { useMemo, useState, type FormEvent } from 'react'
import type { Collection, CollectionPayload, Prompt } from '../../types'
import { Button } from '../../components/Button'
import { Card } from '../../components/Card'
import { EmptyState } from '../../components/EmptyState'

interface CollectionsPanelProps {
  collections: Collection[]
  prompts: Prompt[]
  onCreateCollection: (payload: CollectionPayload) => Promise<void>
  onUpdateCollection: (collectionId: string, payload: CollectionPayload) => Promise<void>
  onDeleteCollection: (collectionId: string) => Promise<void>
  isSubmitting: boolean
}

export function CollectionsPanel({
  collections,
  prompts,
  onCreateCollection,
  onUpdateCollection,
  onDeleteCollection,
  isSubmitting,
}: CollectionsPanelProps) {
  const [name, setName] = useState('')
  const [description, setDescription] = useState('')
  const [editingCollectionId, setEditingCollectionId] = useState<string | null>(null)

  const promptCountByCollection = useMemo(() => {
    const map: Record<string, number> = {}
    for (const prompt of prompts) {
      if (prompt.collection_id) {
        map[prompt.collection_id] = (map[prompt.collection_id] ?? 0) + 1
      }
    }
    return map
  }, [prompts])

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()

    const payload: CollectionPayload = {
      name: name.trim(),
      description: description.trim() || null,
    }

    if (editingCollectionId) {
      await onUpdateCollection(editingCollectionId, payload)
    } else {
      await onCreateCollection(payload)
    }

    setEditingCollectionId(null)
    setName('')
    setDescription('')
  }

  return (
    <Card className="stack">
      <h2>Collections</h2>
      <form className="stack" onSubmit={handleSubmit}>
        <label className="field">
          <span>Name</span>
          <input required maxLength={100} value={name} onChange={(e) => setName(e.target.value)} />
        </label>
        <label className="field">
          <span>Description</span>
          <input
            maxLength={500}
            value={description}
            onChange={(e) => setDescription(e.target.value)}
          />
        </label>
        <div className="button-row">
          <Button type="submit" disabled={isSubmitting}>
            {isSubmitting
              ? 'Saving...'
              : editingCollectionId
                ? 'Update Collection'
                : 'Create Collection'}
          </Button>
          {editingCollectionId ? (
            <Button
              type="button"
              tone="secondary"
              onClick={() => {
                setEditingCollectionId(null)
                setName('')
                setDescription('')
              }}
            >
              Cancel
            </Button>
          ) : null}
        </div>
      </form>

      {collections.length === 0 ? (
        <EmptyState
          title="No collections yet"
          body="Create a collection to organize your prompt library."
        />
      ) : (
        <ul className="collection-list">
          {collections.map((collection) => (
            <li key={collection.id}>
              <div>
                <p className="collection-name">{collection.name}</p>
                <p className="muted">{collection.description || 'No description.'}</p>
                <small>{promptCountByCollection[collection.id] ?? 0} prompts</small>
              </div>
              <div className="button-row">
                <Button
                  type="button"
                  tone="secondary"
                  onClick={() => {
                    setEditingCollectionId(collection.id)
                    setName(collection.name)
                    setDescription(collection.description ?? '')
                  }}
                >
                  Edit
                </Button>
                <Button
                  type="button"
                  tone="danger"
                  onClick={async () => {
                    if (window.confirm('Delete this collection? Prompts will be detached.')) {
                      await onDeleteCollection(collection.id)
                      if (editingCollectionId === collection.id) {
                        setEditingCollectionId(null)
                        setName('')
                        setDescription('')
                      }
                    }
                  }}
                >
                  Delete
                </Button>
              </div>
            </li>
          ))}
        </ul>
      )}
    </Card>
  )
}
