'use client'

import { createLocalStorageState } from 'foxact/create-local-storage-state'

export const LEARN_ORQIVIUM_HIDDEN_STORAGE_KEY = 'explore-learn-orqivium-hidden'

const [_useLearnOrqiviumHidden, useLearnOrqiviumHiddenValue, useSetLearnOrqiviumHidden] =
  createLocalStorageState<boolean>(LEARN_ORQIVIUM_HIDDEN_STORAGE_KEY, false)

export { useLearnOrqiviumHiddenValue, useSetLearnOrqiviumHidden }
