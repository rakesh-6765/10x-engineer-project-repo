import type { PropsWithChildren } from 'react'

interface CardProps {
  className?: string
}

export function Card({ className, children }: PropsWithChildren<CardProps>) {
  const classes = ['card', className].filter(Boolean).join(' ')
  return <section className={classes}>{children}</section>
}
