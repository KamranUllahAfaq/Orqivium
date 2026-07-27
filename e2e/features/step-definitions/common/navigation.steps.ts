import type { OrqiviumWorld } from '../../support/world'
import { Then, When } from '@cucumber/cucumber'
import { expect } from '@playwright/test'
import { waitForAppsConsole } from '../../../support/apps'
import { waitForConsoleHome } from '../../../support/home'

When('I open the default console entry', async function (this: OrqiviumWorld) {
  await this.getPage().goto('/')
})

When('I open the apps console', async function (this: OrqiviumWorld) {
  await this.getPage().goto('/apps')
})

When('I refresh the current page', async function (this: OrqiviumWorld) {
  await this.getPage().reload()
})

Then('I should stay on the apps console', async function (this: OrqiviumWorld) {
  await waitForAppsConsole(this.getPage())
})

Then('I should be on the console home', async function (this: OrqiviumWorld) {
  await waitForConsoleHome(this.getPage())
})

Then('I should be redirected to the signin page', async function (this: OrqiviumWorld) {
  await expect(this.getPage()).toHaveURL(/\/signin(?:\?.*)?$/)
})

Then('I should see the {string} button', async function (this: OrqiviumWorld, label: string) {
  await expect(this.getPage().getByRole('button', { name: label })).toBeVisible()
})

Then('I should not see the {string} button', async function (this: OrqiviumWorld, label: string) {
  await expect(this.getPage().getByRole('button', { name: label })).not.toBeVisible()
})

Then('I should see the {string} text', async function (this: OrqiviumWorld, text: string) {
  await expect(this.getPage().getByText(text)).toBeVisible({ timeout: 30_000 })
})
