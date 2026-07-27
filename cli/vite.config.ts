import { fileURLToPath } from 'node:url'
import { defineConfig } from 'vite-plus'
import { resolveBuildInfo } from './scripts/lib/resolve-buildinfo.js'

const buildInfo = resolveBuildInfo()

export default defineConfig({
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url)),
      '@test': fileURLToPath(new URL('./test', import.meta.url)),
    },
  },
  pack: {
    entry: ['src/index.ts', 'src/commands/**/*.ts', 'src/framework/**/*.ts'],
    format: ['esm'],
    fixedExtension: false,
    dts: true,
    clean: true,
    sourcemap: true,
    treeshake: false,
    outDir: 'dist',
    target: 'node22',
    define: {
      __ORQCTL_VERSION__: JSON.stringify(buildInfo.version),
      __ORQCTL_COMMIT__: JSON.stringify(buildInfo.commit),
      __ORQCTL_BUILD_DATE__: JSON.stringify(buildInfo.buildDate),
      __ORQCTL_CHANNEL__: JSON.stringify(buildInfo.channel),
      __ORQCTL_MIN_ORQIVIUM__: JSON.stringify(buildInfo.minOrqivium),
      __ORQCTL_MAX_ORQIVIUM__: JSON.stringify(buildInfo.maxOrqivium),
    },
  },
  test: {
    environment: 'node',
    setupFiles: ['./test/setup.ts'],
    include: ['test/**/*.test.ts', 'src/**/*.test.ts', 'scripts/**/*.test.ts'],
    exclude: ['**/node_modules/**', '**/dist/**'],
    coverage: {
      provider: 'v8',
      reporter: ['text', 'text-summary', 'json'],
      include: ['src/**/*.ts'],
      exclude: ['src/**/*.test.ts', 'src/types/**'],
    },
  },
})
