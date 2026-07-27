import {
  asyncRunSafe,
  canFindTool,
  correctModelProvider,
  correctToolProvider,
  fetchWithRetry,
  getPurifyHref,
} from './index'

describe('asyncRunSafe', () => {
  it('returns resolved values and rejected errors as tuples', async () => {
    await expect(asyncRunSafe(Promise.resolve('ok'))).resolves.toEqual([null, 'ok'])

    const error = new Error('failed')
    await expect(asyncRunSafe(Promise.reject(error))).resolves.toEqual([error])
  })

  it('normalizes an empty rejection reason', async () => {
    // oxlint-disable-next-line prefer-promise-reject-errors
    const [error] = await asyncRunSafe(Promise.reject())
    expect(error).toEqual(new Error('unknown error'))
  })
})

describe('getPurifyHref', () => {
  it('escapes unsafe HTML while preserving an empty input', () => {
    expect(getPurifyHref('<script>alert("xss")</script>&')).toBe(
      '&lt;script&gt;alert(&quot;xss&quot;)&lt;/script&gt;&amp;',
    )
    expect(getPurifyHref('')).toBe('')
  })
})

describe('fetchWithRetry', () => {
  it('returns the resolved value or the final rejection', async () => {
    await expect(fetchWithRetry(Promise.resolve('ok'))).resolves.toEqual([null, 'ok'])

    const error = new Error('failed')
    await expect(fetchWithRetry(Promise.reject(error), 1)).resolves.toEqual([error])
  })
})

describe('provider normalization', () => {
  it('normalizes legacy model providers without changing qualified providers', () => {
    expect(correctModelProvider('google')).toBe('orqivium/gemini/google')
    expect(correctModelProvider('openai')).toBe('orqivium/openai/openai')
    expect(correctModelProvider('company/model')).toBe('company/model')
  })

  it('normalizes legacy tool providers without changing catalog providers', () => {
    expect(correctToolProvider('jina')).toBe('orqivium/jina_tool/jina')
    expect(correctToolProvider('standard')).toBe('orqivium/standard/standard')
    expect(correctToolProvider('catalog-provider', true)).toBe('catalog-provider')
  })

  it('matches legacy tool IDs against supported provider formats', () => {
    expect(canFindTool('tool-id', 'tool-id')).toBe(true)
    expect(canFindTool('orqivium/tool-id/tool-id', 'tool-id')).toBe(true)
    expect(canFindTool('orqivium/tool-id_tool/tool-id', 'tool-id')).toBe(true)
    expect(canFindTool('provider-a', 'tool-b')).toBe(false)
  })
})
