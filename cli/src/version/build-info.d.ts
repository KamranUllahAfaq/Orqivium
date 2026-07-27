// Build-time globals injected by vite-plus. Single source of truth — both
// info.ts (client identity) and compat.ts (supported orqivium range) read from
// here. Values are computed in scripts/lib/resolve-buildinfo.ts.
declare const __ORQCTL_VERSION__: string
declare const __ORQCTL_COMMIT__: string
declare const __ORQCTL_BUILD_DATE__: string
declare const __ORQCTL_CHANNEL__: string
declare const __ORQCTL_MIN_ORQIVIUM__: string
declare const __ORQCTL_MAX_ORQIVIUM__: string
