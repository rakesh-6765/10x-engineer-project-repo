import { useEffect, useMemo, useState, type FormEvent } from 'react'
import type { Collection, Prompt, PromptPayload } from '../../types'
import { Button } from '../../components/Button'
import { Card } from '../../components/Card'

interface PromptFormProps {
  collections: Collection[]
  selectedPrompt: Prompt | null
  onSubmit: (payload: PromptPayload) => Promise<void>
  onCancelEdit: () => void
  isSubmitting: boolean
}

const EMPTY_FORM: PromptPayload = {
  title: '',
  content: '',
  description: '',
  collection_id: null,
}

export function PromptForm({
  collections,
  selectedPrompt,
  onSubmit,
  onCancelEdit,
  isSubmitting,
}: PromptFormProps) {
  const [formState, setFormState] = useState<PromptPayload>(EMPTY_FORM)

  useEffect(() => {
    if (selectedPrompt) {
      setFormState({
        title: selectedPrompt.title,
        content: selectedPrompt.content,
        description: selectedPrompt.description ?? '',
        collection_id: selectedPrompt.collection_id,
      })
    } else {
      setFormState(EMPTY_FORM)
    }
  }, [selectedPrompt])

  const submitLabel = useMemo(() => (selectedPrompt ? 'Update Prompt' : 'Create Prompt'), [selectedPrompt])

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    await onSubmit({
      title: formState.title.trim(),
      content: formState.content.trim(),
      description: formState.description?.trim() || null,
      collection_id: formState.collection_id || null,
    })
    if (!selectedPrompt) {
      setFormState(EMPTY_FORM)
    }
  }

  return (
    <Card className="stack">
      <h2>{selectedPrompt ? 'Edit Prompt' : 'Create Prompt'}</h2>
      <form className="stack" onSubmit={handleSubmit}>
        <label className="field">
          <span>Title</span>
          <input
            required
            maxLength={200}
            value={formState.title}
            onChange={(event) => setFormState((prev) => ({ ...prev, title: event.target.value }))}
          />
        </label>

        <label className="field">
          <span>Description</span>
          <input
            maxLength={500}
            value={formState.description ?? ''}
            onChange={(event) =>
              setFormState((prev) => ({ ...prev, description: event.target.value }))
            }
          />
        </label>

        <label className="field">
          <span>Collection</span>
          <select
            value={formState.collection_id ?? ''}
            onChange={(event) =>
              setFormState((prev) => ({
                ...prev,
                collection_id: event.target.value || null,
              }))
            }
          >
            <option value="">No collection</option>
            {collections.map((collection) => (
              <option key={collection.id} value={collection.id}>
                {collection.name}
              </option>
            ))}
          </select>
        </label>

        <label className="field">
          <span>Prompt Content</span>
          <textarea
            required
            value={formState.content}
            onChange={(event) => setFormState((prev) => ({ ...prev, content: event.target.value }))}
            rows={8}
          />
        </label>

        <div className="button-row">
          <Button type="submit" disabled={isSubmitting}>
            {isSubmitting ? 'Saving...' : submitLabel}
          </Button>
          {selectedPrompt ? (
            <Button type="button" tone="secondary" onClick={onCancelEdit}>
              Cancel
            </Button>
          ) : null}
        </div>
      </form>
    </Card>
  )
}
