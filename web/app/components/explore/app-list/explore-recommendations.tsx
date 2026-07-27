'use client'

import type { App } from '@/models/explore'
import type { App as WorkspaceApp } from '@/types/app'
import type { TryAppSelection } from '@/types/try-app'
import ContinueWork from '@/app/components/explore/continue-work'
import { STEP_BY_STEP_TOUR_TARGETS } from '@/app/components/step-by-step-tour/target-registry'
import dynamic from '@/next/dynamic'

const LearnOrqivium = dynamic(() => import('@/app/components/explore/learn-orqivium'), { ssr: false })

export function ExploreRecommendations({
  canCreate,
  continueWorkApps,
  forceShowLearnOrqivium,
  onCreate,
  onTry,
}: {
  canCreate: boolean
  continueWorkApps: WorkspaceApp[]
  forceShowLearnOrqivium?: boolean
  onCreate: (app: App) => void
  onTry: (params: TryAppSelection) => void
}) {
  return (
    <>
      <ContinueWork apps={continueWorkApps} />
      <LearnOrqivium
        canCreate={canCreate}
        className="pb-0"
        forceVisible={forceShowLearnOrqivium}
        onCreate={onCreate}
        onTry={onTry}
        stepByStepTourTarget={STEP_BY_STEP_TOUR_TARGETS.home}
      />
    </>
  )
}
