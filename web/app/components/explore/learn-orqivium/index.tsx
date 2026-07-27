'use client'

import type { App } from '@/models/explore'
import type { TryAppSelection } from '@/types/try-app'
import { cn } from '@orqivium/ui/cn'
import { useSuspenseQuery } from '@tanstack/react-query'
import * as React from 'react'
import { useEffect, useRef, useState } from 'react'
import { useTranslation } from 'react-i18next'
import { systemFeaturesQueryOptions } from '@/features/system-features/client'
import { useLearnOrqiviumAppList } from '@/service/use-explore'
import LearnOrqiviumItem from './item'
import { useLearnOrqiviumHiddenValue, useSetLearnOrqiviumHidden } from './storage'

type LearnOrqiviumProps = {
  canCreate?: boolean
  className?: string
  dismissible?: boolean
  forceVisible?: boolean
  itemLimit?: number
  loadingFallback?: React.ReactNode
  onCreate?: (app: App) => void
  onTry?: (params: TryAppSelection) => void
  showDescription?: boolean
  stepByStepTourTarget?: string
  title?: string
}

type LearnOrqiviumContentProps = LearnOrqiviumProps & {
  onHide?: () => void
}

const LearnOrqiviumContent = ({
  canCreate = false,
  className,
  itemLimit,
  loadingFallback = null,
  onHide,
  onCreate,
  onTry,
  showDescription = true,
  stepByStepTourTarget,
  title,
}: LearnOrqiviumContentProps) => {
  const { t } = useTranslation()
  const [isClosing, setIsClosing] = useState(false)
  const [collapseTransform, setCollapseTransform] = useState<string>()
  const hideTimerRef = useRef<ReturnType<typeof setTimeout> | null>(null)
  const sectionRef = useRef<HTMLElement>(null)
  const { data: learnOrqiviumItems = [], isLoading } = useLearnOrqiviumAppList()

  useEffect(() => {
    return () => {
      if (hideTimerRef.current) clearTimeout(hideTimerRef.current)
    }
  }, [])

  const handleHide = () => {
    const sectionRect = sectionRef.current?.getBoundingClientRect()
    const helpTargetRect = document
      .querySelector('[data-learn-orqivium-help-target]')
      ?.getBoundingClientRect()
    if (sectionRect && helpTargetRect) {
      const sectionCenterX = sectionRect.left + sectionRect.width / 2
      const sectionCenterY = sectionRect.top + sectionRect.height / 2
      const helpCenterX = helpTargetRect.left + helpTargetRect.width / 2
      const helpCenterY = helpTargetRect.top + helpTargetRect.height / 2

      setCollapseTransform(
        `translate3d(${helpCenterX - sectionCenterX}px, ${helpCenterY - sectionCenterY}px, 0) scale(0.08)`,
      )
    } else {
      setCollapseTransform('scale(0.08)')
    }
    setIsClosing(true)
    hideTimerRef.current = setTimeout(() => {
      onHide?.()
      setIsClosing(false)
      setCollapseTransform(undefined)
    }, 800)
  }

  const visibleItems = itemLimit ? learnOrqiviumItems.slice(0, itemLimit) : learnOrqiviumItems
  const sectionTitle = title ?? t(($) => $['learnOrqivium.title'], { ns: 'explore' })

  if (isLoading) return loadingFallback
  if (visibleItems.length === 0) return null

  return (
    <section
      ref={sectionRef}
      className={cn(
        'px-8 pb-6 transition-[opacity,transform] duration-800 ease-in-out',
        isClosing && 'pointer-events-none relative z-50 opacity-20',
        className,
      )}
      style={
        isClosing ? { transform: collapseTransform, transformOrigin: 'center center' } : undefined
      }
      aria-labelledby="learn-orqivium-title"
      data-step-by-step-tour-target={stepByStepTourTarget}
    >
      <div className="-mx-4 rounded-2xl bg-background-section p-4">
        <div className="flex items-start justify-between gap-4 pb-2.5">
          <div className="min-w-0">
            <h2
              id="learn-orqivium-title"
              className="truncate system-xl-medium text-text-primary"
              title={sectionTitle}
            >
              {sectionTitle}
            </h2>
            {showDescription && (
              <p className="mt-0.5 truncate system-xs-regular text-text-tertiary">
                {t(($) => $['learnOrqivium.description'], { ns: 'explore' })}
              </p>
            )}
          </div>
          {onHide && (
            <button
              type="button"
              className="flex size-8 shrink-0 items-center justify-center rounded-lg text-text-tertiary hover:bg-state-base-hover hover:text-text-secondary focus-visible:bg-state-base-hover focus-visible:ring-1 focus-visible:ring-components-input-border-hover focus-visible:outline-hidden"
              aria-label={t(($) => $['learnOrqivium.hide'], { ns: 'explore' })}
              onClick={handleHide}
            >
              <span className="i-ri-close-line size-4" aria-hidden="true" />
            </button>
          )}
        </div>
        <div className="grid grid-cols-[repeat(auto-fill,minmax(296px,1fr))] gap-2.5">
          {visibleItems.map((item) => (
            <LearnOrqiviumItem
              key={item.app_id}
              canCreate={canCreate}
              item={item}
              onCreate={onCreate}
              onTry={onTry}
            />
          ))}
        </div>
      </div>
    </section>
  )
}

const DismissibleLearnOrqivium = (props: LearnOrqiviumProps) => {
  const hidden = useLearnOrqiviumHiddenValue()
  const setHidden = useSetLearnOrqiviumHidden()

  if (hidden) return null

  return <LearnOrqiviumContent {...props} onHide={() => setHidden(true)} />
}

const LearnOrqivium = (props: LearnOrqiviumProps) => {
  const { data: systemFeatures } = useSuspenseQuery(systemFeaturesQueryOptions())

  if (!systemFeatures.enable_learn_app) return null

  if (props.dismissible === false || props.forceVisible) return <LearnOrqiviumContent {...props} />

  return <DismissibleLearnOrqivium {...props} />
}

export default React.memo(LearnOrqivium)
