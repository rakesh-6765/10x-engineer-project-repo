interface EmptyStateProps {
  title: string
  body: string
}

export function EmptyState({ title, body }: EmptyStateProps) {
  return (
    <div className="empty-state" role="status" aria-live="polite">
      <h3>{title}</h3>
      <p>{body}</p>
    </div>
  )
}
