interface LoadingOverlayProps {
  label: string
}

export function LoadingOverlay({ label }: LoadingOverlayProps) {
  return (
    <div className="loading-overlay" role="status" aria-live="polite" aria-label={label}>
      <div className="spinner" />
      <span>{label}</span>
    </div>
  )
}
