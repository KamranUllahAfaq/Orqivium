import type { DocPathMap } from './i18n'
import type { DocPathWithoutLang } from '@/types/doc-paths'
import { renderHook } from '@testing-library/react'
import { useTranslation } from '#i18n'
import { getDocLanguage } from '@/i18n-config/language'
import { defaultDocBaseUrl, useDocLink } from './i18n'

const mockDeploymentEdition = vi.hoisted(() => ({
  value: 'CLOUD' as 'COMMUNITY' | 'ENTERPRISE' | 'CLOUD',
}))

// Mock dependencies
vi.mock('#i18n', () => ({
  useTranslation: vi.fn(() => ({
    i18n: { language: 'en-US' },
  })),
}))

vi.mock('jotai', async (importOriginal) => ({
  ...(await importOriginal<typeof import('jotai')>()),
  useAtomValue: () => mockDeploymentEdition.value,
}))

vi.mock('@/i18n-config/language', () => ({
  getDocLanguage: vi.fn((locale: string) => {
    const map: Record<string, string> = {
      'zh-Hans': 'zh',
      'ja-JP': 'ja',
      'en-US': 'en',
    }
    return map[locale] || 'en'
  }),
  getLanguage: vi.fn(),
  getPricingPageLanguage: vi.fn(),
}))

describe('useDocLink', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    mockDeploymentEdition.value = 'CLOUD'
    vi.mocked(useTranslation).mockReturnValue({
      i18n: { language: 'en-US' },
    } as ReturnType<typeof useTranslation>)
    vi.mocked(getDocLanguage).mockReturnValue('en')
  })

  describe('Base URL handling', () => {
    it('should use default base URL when no baseUrl provided', () => {
      const { result } = renderHook(() => useDocLink())
      const url = result.current()
      expect(url).toBe(`${defaultDocBaseUrl}/en/home`)
    })

    it('should use custom base URL when provided', () => {
      const customBaseUrl = 'https://custom.docs.com'
      const { result } = renderHook(() => useDocLink(customBaseUrl))
      const url = result.current()
      expect(url).toBe(`${customBaseUrl}/en/home`)
    })

    it('should remove trailing slash from base URL', () => {
      const baseUrlWithSlash = '//'
      const { result } = renderHook(() => useDocLink(baseUrlWithSlash))
      const url = result.current('/use-orqivium/getting-started/introduction')
      expect(url).toBe('//en/cloud/use-orqivium/getting-started/introduction')
    })

    it('should handle base URL without trailing slash', () => {
      const baseUrlWithoutSlash = '/'
      const { result } = renderHook(() => useDocLink(baseUrlWithoutSlash))
      const url = result.current('/use-orqivium/getting-started/introduction')
      expect(url).toBe('//en/cloud/use-orqivium/getting-started/introduction')
    })
  })

  describe('Path handling', () => {
    it('should handle path parameter', () => {
      const { result } = renderHook(() => useDocLink())
      const url = result.current('/use-orqivium/getting-started/introduction')
      expect(url).toBe(`${defaultDocBaseUrl}/en/cloud/use-orqivium/getting-started/introduction`)
    })

    it('should handle empty path', () => {
      const { result } = renderHook(() => useDocLink())
      const url = result.current()
      expect(url).toBe(`${defaultDocBaseUrl}/en/home`)
    })

    it('should handle undefined path', () => {
      const { result } = renderHook(() => useDocLink())
      const url = result.current(undefined)
      expect(url).toBe(`${defaultDocBaseUrl}/en/home`)
    })

    it('should keep common docs path without product prefix', () => {
      const { result } = renderHook(() => useDocLink())
      const url = result.current('/learn/key-concepts' as DocPathWithoutLang)
      expect(url).toBe(`${defaultDocBaseUrl}/en/learn/key-concepts`)
    })

    it('should keep explicit product docs path without adding another product prefix', () => {
      const { result } = renderHook(() => useDocLink())
      const url = result.current(
        '/cloud/use-orqivium/getting-started/introduction' as DocPathWithoutLang,
      )
      expect(url).toBe(`${defaultDocBaseUrl}/en/cloud/use-orqivium/getting-started/introduction`)
    })
  })

  describe('PathMap handling', () => {
    it('should use path from pathMap when locale matches', () => {
      vi.mocked(useTranslation).mockReturnValue({
        i18n: { language: 'zh-Hans' },
      } as ReturnType<typeof useTranslation>)
      vi.mocked(getDocLanguage).mockReturnValue('zh')

      const pathMap: DocPathMap = {
        'zh-Hans': '/use-orqivium/getting-started/introduction',
        'en-US': '/use-orqivium/workspace/tools#mcp',
      }

      const { result } = renderHook(() => useDocLink())
      const url = result.current('/use-orqivium/workspace/tools#mcp', pathMap)
      expect(url).toBe(`${defaultDocBaseUrl}/zh/cloud/use-orqivium/getting-started/introduction`)
    })

    it('should use default path when locale not in pathMap', () => {
      vi.mocked(useTranslation).mockReturnValue({
        i18n: { language: 'ja-JP' },
      } as ReturnType<typeof useTranslation>)
      vi.mocked(getDocLanguage).mockReturnValue('ja')

      const pathMap: DocPathMap = {
        'zh-Hans': '/use-orqivium/getting-started/introduction',
        'en-US': '/use-orqivium/workspace/tools#mcp',
      }

      const { result } = renderHook(() => useDocLink())
      const url = result.current('/use-orqivium/workspace/tools#mcp', pathMap)
      expect(url).toBe(`${defaultDocBaseUrl}/ja/cloud/use-orqivium/workspace/tools#mcp`)
    })

    it('should handle undefined pathMap', () => {
      const { result } = renderHook(() => useDocLink())
      const url = result.current('/use-orqivium/getting-started/introduction', undefined)
      expect(url).toBe(`${defaultDocBaseUrl}/en/cloud/use-orqivium/getting-started/introduction`)
    })
  })

  describe('Product prefix handling', () => {
    it('should add cloud product prefix for product docs available in both editions', () => {
      mockDeploymentEdition.value = 'CLOUD'

      const { result } = renderHook(() => useDocLink())
      const url = result.current('/use-orqivium/workspace/tools#mcp')
      expect(url).toBe(`${defaultDocBaseUrl}/en/cloud/use-orqivium/workspace/tools#mcp`)
    })

    it('should add self-host product prefix for product docs available in both editions outside cloud edition', () => {
      mockDeploymentEdition.value = 'COMMUNITY'

      const { result } = renderHook(() => useDocLink())
      const url = result.current('/use-orqivium/workspace/tools#mcp')
      expect(url).toBe(`${defaultDocBaseUrl}/en/self-host/use-orqivium/workspace/tools#mcp`)
    })

    it('should use the existing cloud docs path for cloud-only product docs outside cloud edition', () => {
      mockDeploymentEdition.value = 'COMMUNITY'

      const { result } = renderHook(() => useDocLink())
      const url = result.current('/use-orqivium/workspace/subscription-management#orqivium-for-education')
      expect(url).toBe(
        `${defaultDocBaseUrl}/en/cloud/use-orqivium/workspace/subscription-management#orqivium-for-education`,
      )
    })

    it('should use the self-host Start node docs path outside cloud edition', () => {
      mockDeploymentEdition.value = 'COMMUNITY'

      const { result } = renderHook(() => useDocLink())
      const url = result.current('/use-orqivium/nodes/start')
      expect(url).toBe(`${defaultDocBaseUrl}/en/self-host/use-orqivium/nodes/start`)
    })

    it('should use the existing self-host docs path for self-host-only product docs in cloud edition', () => {
      mockDeploymentEdition.value = 'CLOUD'

      const { result } = renderHook(() => useDocLink())
      const url = result.current('/deploy/overview')
      expect(url).toBe(`${defaultDocBaseUrl}/en/self-host/deploy/overview`)
    })

    it('should not add a product prefix for unknown productless paths', () => {
      mockDeploymentEdition.value = 'COMMUNITY'

      const { result } = renderHook(() => useDocLink())
      const url = result.current('/use-orqivium/unknown-page' as DocPathWithoutLang)
      expect(url).toBe(`${defaultDocBaseUrl}/en/use-orqivium/unknown-page`)
    })

    it('should open shared docs home when no path is provided outside cloud edition', () => {
      mockDeploymentEdition.value = 'COMMUNITY'

      const { result } = renderHook(() => useDocLink())
      const url = result.current()
      expect(url).toBe(`${defaultDocBaseUrl}/en/home`)
    })

    it('should keep self-host deploy paths without adding use-orqivium product prefix', () => {
      mockDeploymentEdition.value = 'CLOUD'

      const { result } = renderHook(() => useDocLink())
      const url = result.current('/self-host/deploy/overview' as DocPathWithoutLang)
      expect(url).toBe(`${defaultDocBaseUrl}/en/self-host/deploy/overview`)
    })
  })

  describe('Language prefix handling', () => {
    it('should add /en prefix for English locale', () => {
      vi.mocked(useTranslation).mockReturnValue({
        i18n: { language: 'en-US' },
      } as ReturnType<typeof useTranslation>)
      vi.mocked(getDocLanguage).mockReturnValue('en')

      const { result } = renderHook(() => useDocLink())
      const url = result.current('/use-orqivium/getting-started/introduction')
      expect(url).toContain('/en/')
    })

    it('should add /zh prefix for Chinese locale', () => {
      vi.mocked(useTranslation).mockReturnValue({
        i18n: { language: 'zh-Hans' },
      } as ReturnType<typeof useTranslation>)
      vi.mocked(getDocLanguage).mockReturnValue('zh')

      const { result } = renderHook(() => useDocLink())
      const url = result.current('/use-orqivium/getting-started/introduction')
      expect(url).toContain('/zh/')
    })

    it('should add /ja prefix for Japanese locale', () => {
      vi.mocked(useTranslation).mockReturnValue({
        i18n: { language: 'ja-JP' },
      } as ReturnType<typeof useTranslation>)
      vi.mocked(getDocLanguage).mockReturnValue('ja')

      const { result } = renderHook(() => useDocLink())
      const url = result.current('/use-orqivium/getting-started/introduction')
      expect(url).toContain('/ja/')
    })
  })

  describe('API reference path handling', () => {
    it('should add language prefix for Chinese API reference paths', () => {
      vi.mocked(useTranslation).mockReturnValue({
        i18n: { language: 'zh-Hans' },
      } as ReturnType<typeof useTranslation>)
      vi.mocked(getDocLanguage).mockReturnValue('zh')

      const { result } = renderHook(() => useDocLink())
      const url = result.current('/api-reference/annotations/create-annotation')
      expect(url).toBe(`${defaultDocBaseUrl}/zh/api-reference/annotations/create-annotation`)
    })

    it('should add language prefix for Japanese API reference paths', () => {
      vi.mocked(useTranslation).mockReturnValue({
        i18n: { language: 'ja-JP' },
      } as ReturnType<typeof useTranslation>)
      vi.mocked(getDocLanguage).mockReturnValue('ja')

      const { result } = renderHook(() => useDocLink())
      const url = result.current('/api-reference/applications/get-app-info')
      expect(url).toBe(`${defaultDocBaseUrl}/ja/api-reference/applications/get-app-info`)
    })

    it('should not translate API reference path for English locale', () => {
      vi.mocked(useTranslation).mockReturnValue({
        i18n: { language: 'en-US' },
      } as ReturnType<typeof useTranslation>)
      vi.mocked(getDocLanguage).mockReturnValue('en')

      const { result } = renderHook(() => useDocLink())
      const url = result.current('/api-reference/annotations/create-annotation')
      expect(url).toBe(`${defaultDocBaseUrl}/en/api-reference/annotations/create-annotation`)
    })

    it('should keep the API reference slug unchanged for non-English locale', () => {
      vi.mocked(useTranslation).mockReturnValue({
        i18n: { language: 'zh-Hans' },
      } as ReturnType<typeof useTranslation>)
      vi.mocked(getDocLanguage).mockReturnValue('zh')

      const { result } = renderHook(() => useDocLink())
      const url = result.current('/api-reference/annotations/create-annotation')
      expect(url).toBe(`${defaultDocBaseUrl}/zh/api-reference/annotations/create-annotation`)
    })

    it('should keep language prefix for API reference paths', () => {
      vi.mocked(useTranslation).mockReturnValue({
        i18n: { language: 'zh-Hans' },
      } as ReturnType<typeof useTranslation>)
      vi.mocked(getDocLanguage).mockReturnValue('zh')

      const { result } = renderHook(() => useDocLink())
      const url = result.current('/api-reference/annotations/create-annotation')
      expect(url).toBe(`${defaultDocBaseUrl}/zh/api-reference/annotations/create-annotation`)
    })

    it('should use the current knowledge API guide path directly', () => {
      vi.mocked(useTranslation).mockReturnValue({
        i18n: { language: 'zh-Hans' },
      } as ReturnType<typeof useTranslation>)
      vi.mocked(getDocLanguage).mockReturnValue('zh')

      const { result } = renderHook(() => useDocLink())
      const url = result.current('/api-reference/guides/knowledge')
      expect(url).toBe(`${defaultDocBaseUrl}/zh/api-reference/guides/knowledge`)
    })

    it('should not translate non-API-reference paths', () => {
      vi.mocked(useTranslation).mockReturnValue({
        i18n: { language: 'zh-Hans' },
      } as ReturnType<typeof useTranslation>)
      vi.mocked(getDocLanguage).mockReturnValue('zh')

      const { result } = renderHook(() => useDocLink())
      const url = result.current('/use-orqivium/getting-started/introduction')
      expect(url).toBe(`${defaultDocBaseUrl}/zh/cloud/use-orqivium/getting-started/introduction`)
    })
  })

  describe('Edge Cases', () => {
    it('should handle path with anchor', () => {
      const { result } = renderHook(() => useDocLink())
      const url = result.current(
        '/use-orqivium/getting-started/introduction#overview' as DocPathWithoutLang,
      )
      expect(url).toBe(
        `${defaultDocBaseUrl}/en/cloud/use-orqivium/getting-started/introduction#overview`,
      )
    })

    it('should handle multiple calls with same hook instance', () => {
      const { result } = renderHook(() => useDocLink())
      const url1 = result.current('/use-orqivium/getting-started/introduction')
      const url2 = result.current('/use-orqivium/workspace/tools#mcp')
      expect(url1).toBe(`${defaultDocBaseUrl}/en/cloud/use-orqivium/getting-started/introduction`)
      expect(url2).toBe(`${defaultDocBaseUrl}/en/cloud/use-orqivium/workspace/tools#mcp`)
    })
  })
})
