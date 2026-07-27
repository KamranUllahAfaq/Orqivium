#!/usr/bin/env -S bun

import { resolveBuildInfo } from '../scripts/lib/resolve-buildinfo.ts'

const info = resolveBuildInfo()
globalThis.__ORQCTL_VERSION__ = info.version
globalThis.__ORQCTL_COMMIT__ = info.commit
globalThis.__ORQCTL_BUILD_DATE__ = info.buildDate
globalThis.__ORQCTL_CHANNEL__ = info.channel
globalThis.__ORQCTL_MIN_ORQIVIUM__ = info.minOrqivium
globalThis.__ORQCTL_MAX_ORQIVIUM__ = info.maxOrqivium

const { commandTree } = await import('../src/commands/tree.ts')
const { run } = await import('../src/framework/run.ts')

await run(commandTree, process.argv.slice(2))
