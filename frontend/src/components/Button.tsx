import type { ButtonHTMLAttributes, PropsWithChildren } from 'react'

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  tone?: 'primary' | 'secondary' | 'danger'
}

export function Button({ tone = 'primary', children, className, ...props }: PropsWithChildren<ButtonProps>) {
  const classes = ['btn', `btn-${tone}`, className].filter(Boolean).join(' ')
  return (
    <button className={classes} {...props}>
      {children}
    </button>
  )
}
