'use client'

import type { ButtonProps } from '@orqivium/ui/button'
import { Button } from '@orqivium/ui/button'
import { cn } from '@orqivium/ui/cn'
import { useTranslation } from 'react-i18next'
import { useAgentOrchestrateReadOnly } from '../read-only-context'

type ConfigureSectionAddButtonProps = Omit<
  ButtonProps,
  'aria-label' | 'children' | 'size' | 'variant'
> & {
  ariaLabel: string
}

export function ConfigureSectionAddButton({
  ariaLabel,
  className,
  ...props
}: ConfigureSectionAddButtonProps) {
  const { t } = useTranslation('common')
  const readOnly = useAgentOrchestrateReadOnly()

  if (readOnly) return null

  return (
    <Button
      {...props}
      aria-label={ariaLabel}
      variant="ghost"
      size="small"
      className={cn('shrink-0 gap-1 px-2', className)}
    >
      <span aria-hidden className="i-ri-add-line size-3.5" />
      <span>{t(($) => $['operation.add'])}</span>
    </Button>
  )
}
