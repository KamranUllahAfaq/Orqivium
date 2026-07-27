import type { OrqiviumWorld } from '../../support/world'

export const getCurrentAgentId = (world: OrqiviumWorld) => {
  const agentId = world.createdAgentIds.at(-1)
  if (!agentId) throw new Error('No Agent v2 ID found. Create an Agent v2 test agent first.')

  return agentId
}

export const getPreseededResource = (
  world: OrqiviumWorld,
  name: string,
  kind: 'agent' | 'workflow',
) => {
  const resource = world.agentBuilder.fixtures.preseededResources[name]
  if (!resource || resource.kind !== kind) {
    throw new Error(
      `Preseeded ${kind} "${name}" is not available. Run the matching fixture setup step first.`,
    )
  }

  return resource
}

export const getAccessRegion = (world: OrqiviumWorld) =>
  world.getPage().getByRole('region', { name: 'Access Point' })

export type AccessSurfaceName = 'Web app' | 'Backend service API'

export const getAccessSurfaceCard = (world: OrqiviumWorld, surface: AccessSurfaceName) =>
  getAccessRegion(world).getByRole('article', { name: surface }).first()

export const getWebAppCard = (world: OrqiviumWorld) => getAccessSurfaceCard(world, 'Web app')

export const getServiceApiCard = (world: OrqiviumWorld) =>
  getAccessSurfaceCard(world, 'Backend service API')

export const getDialog = (world: OrqiviumWorld, name: string | RegExp) =>
  world.getPage().getByRole('dialog', { name })
