import type { Collection, Prompt } from '../../types'
import { Button } from '../../components/Button'
import { Card } from '../../components/Card'
import { EmptyState } from '../../components/EmptyState'

interface PromptGridProps {
  prompts: Prompt[]
  collections: Collection[]
  onEdit: (prompt: Prompt) => void
  onDelete: (prompt: Prompt) => Promise<void>
}

function findCollectionName(collections: Collection[], collectionId: string | null): string {
  if (!collectionId) {
    return 'Unassigned'
  }

  return collections.find((item) => item.id === collectionId)?.name ?? 'Unknown collection'
}

export function PromptGrid({ prompts, collections, onEdit, onDelete }: PromptGridProps) {
  if (prompts.length === 0) {
    return (
      <EmptyState
        title="No prompts yet"
        body="Create your first prompt or adjust filters to see results."
      />
    )
  }

  return (
    <div className="prompt-grid">
      {prompts.map((prompt) => (
        <Card key={prompt.id} className="prompt-card">
          <div className="prompt-card-head">
            <h3>{prompt.title}</h3>
            <span className="pill">{findCollectionName(collections, prompt.collection_id)}</span>
          </div>

          <p className="muted">{prompt.description || 'No description provided.'}</p>

          <pre className="prompt-content">{prompt.content}</pre>

          <div className="meta-row">
            <small>Updated {new Date(prompt.updated_at).toLocaleString()}</small>
          </div>

          <div className="button-row">
            <Button tone="secondary" onClick={() => onEdit(prompt)}>
              Edit
            </Button>
            <Button
              tone="danger"
              onClick={async () => {
                if (window.confirm('Delete this prompt?')) {
                  await onDelete(prompt)
                }
              }}
            >
              Delete
            </Button>
          </div>
        </Card>
      ))}
    </div>
  )
}
