import type { OrqiviumWorld } from '../../support/world'
import { When } from '@cucumber/cucumber'

When('I navigate to the app overview page', async function (this: OrqiviumWorld) {
  const appId = this.createdAppIds.at(-1)
  await this.getPage().goto(`/app/${appId}/overview`)
})
