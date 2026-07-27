import {
  newKnowledgeAddSourcePath,
  normalizeWebsiteSourceUrl,
  parseNewKnowledgeSourceDraft,
  singleSearchParam,
} from '../routes'

describe('New RAG routes', () => {
  it('keeps source details out of the add-source URL', () => {
    expect(newKnowledgeAddSourcePath('space-1', 'websiteCrawl', 'opaque-draft-key')).toBe(
      '/datasets/new/space-1/sources/new?type=websiteCrawl&draft=opaque-draft-key',
    )
  })

  it('rejects repeated search parameters instead of selecting an ambiguous value', () => {
    expect(singleSearchParam(['websiteCrawl', 'onlineDrive'])).toBeUndefined()
    expect(singleSearchParam('websiteCrawl')).toBe('websiteCrawl')
  })

  it('rejects credentials embedded in website URLs', () => {
    expect(normalizeWebsiteSourceUrl('https://user:secret@docs.orqivium.local')).toBeUndefined()
    expect(normalizeWebsiteSourceUrl('//docs#intro')?.toString()).toBe(
      '//docs',
    )
  })

  it('rejects malformed session drafts', () => {
    expect(parseNewKnowledgeSourceDraft('{')).toBeUndefined()
    expect(
      parseNewKnowledgeSourceDraft(
        JSON.stringify({
          includeSubpages: true,
          maxPages: 201,
          provider: 'Firecrawl',
          rootUrl: '/',
          sourceName: 'Orqivium docs',
          sourceType: 'websiteCrawl',
          syncPolicy: 'provider',
        }),
      ),
    ).toBeUndefined()
  })

  it('migrates a valid website draft saved before source discriminators were added', () => {
    expect(
      parseNewKnowledgeSourceDraft(
        JSON.stringify({
          includeSubpages: false,
          maxPages: 25,
          provider: 'Firecrawl',
          rootUrl: '/',
          sourceName: 'Orqivium docs',
        }),
      ),
    ).toEqual({
      includeSubpages: false,
      maxPages: 25,
      provider: 'Firecrawl',
      rootUrl: '/',
      sourceName: 'Orqivium docs',
      sourceType: 'websiteCrawl',
      syncPolicy: 'provider',
    })
  })
})
