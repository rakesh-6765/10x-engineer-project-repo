interface FeedbackBannerProps {
  tone: 'error' | 'success'
  message: string
}

export function FeedbackBanner({ tone, message }: FeedbackBannerProps) {
  return <p className={`feedback feedback-${tone}`}>{message}</p>
}
