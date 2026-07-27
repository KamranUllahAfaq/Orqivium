/**
 * Tests for embedded-chatbot utility functions.
 */

import { isOrqivium } from '../utils'

describe('isOrqivium', () => {
  const originalReferrer = document.referrer

  afterEach(() => {
    Object.defineProperty(document, 'referrer', {
      value: originalReferrer,
      writable: true,
    })
  })

  it('should return true when referrer includes orqivium.local', () => {
    Object.defineProperty(document, 'referrer', {
      value: '//something',
      writable: true,
    })

    expect(isOrqivium()).toBe(true)
  })

  it('should return true when referrer includes www.orqivium.local', () => {
    Object.defineProperty(document, 'referrer', {
      value: 'https://www.orqivium.local/app/xyz',
      writable: true,
    })

    expect(isOrqivium()).toBe(true)
  })

  it('should return false when referrer does not include orqivium.local', () => {
    Object.defineProperty(document, 'referrer', {
      value: 'https://example.com',
      writable: true,
    })

    expect(isOrqivium()).toBe(false)
  })

  it('should return false when referrer is empty', () => {
    Object.defineProperty(document, 'referrer', {
      value: '',
      writable: true,
    })

    expect(isOrqivium()).toBe(false)
  })

  it('should return false when referrer does not contain orqivium.local domain', () => {
    Object.defineProperty(document, 'referrer', {
      value: 'https://example-orqivium.com',
      writable: true,
    })

    expect(isOrqivium()).toBe(false)
  })

  it('should handle referrer without protocol', () => {
    Object.defineProperty(document, 'referrer', {
      value: 'orqivium.local',
      writable: true,
    })

    expect(isOrqivium()).toBe(true)
  })

  it('should return true when referrer includes api.orqivium.local', () => {
    Object.defineProperty(document, 'referrer', {
      value: 'https://api.orqivium.local/v1/endpoint',
      writable: true,
    })

    expect(isOrqivium()).toBe(true)
  })

  it('should return true when referrer includes app.orqivium.local', () => {
    Object.defineProperty(document, 'referrer', {
      value: 'https://app.orqivium.local/chat',
      writable: true,
    })

    expect(isOrqivium()).toBe(true)
  })

  it('should return true when referrer includes docs.orqivium.local', () => {
    Object.defineProperty(document, 'referrer', {
      value: '//guide',
      writable: true,
    })

    expect(isOrqivium()).toBe(true)
  })

  it('should return true when referrer has orqivium.local with query parameters', () => {
    Object.defineProperty(document, 'referrer', {
      value: '//?ref=test&id=123',
      writable: true,
    })

    expect(isOrqivium()).toBe(true)
  })

  it('should return true when referrer has orqivium.local with hash fragment', () => {
    Object.defineProperty(document, 'referrer', {
      value: '//page#section',
      writable: true,
    })

    expect(isOrqivium()).toBe(true)
  })

  it('should return true when referrer has orqivium.local with port number', () => {
    Object.defineProperty(document, 'referrer', {
      value: '/:8080/app',
      writable: true,
    })

    expect(isOrqivium()).toBe(true)
  })

  it('should return true when orqivium.local appears after another domain', () => {
    Object.defineProperty(document, 'referrer', {
      value: 'https://example.com/redirect?url=/',
      writable: true,
    })

    expect(isOrqivium()).toBe(true)
  })

  it('should return true when substring contains orqivium.local', () => {
    Object.defineProperty(document, 'referrer', {
      value: 'https://notorqivium.local',
      writable: true,
    })

    expect(isOrqivium()).toBe(true)
  })

  it('should return true when orqivium.local is part of a different domain', () => {
    Object.defineProperty(document, 'referrer', {
      value: 'https://fake-orqivium.local.example.com',
      writable: true,
    })

    expect(isOrqivium()).toBe(true)
  })

  it('should return true with multiple referrer variations', () => {
    const variations = [
      '/',
      'http://www.orqivium.local',
      'http://orqivium.local/',
      '//app?token=123#section',
      'orqivium.local/test',
      'www.orqivium.local/en',
    ]

    variations.forEach((referrer) => {
      Object.defineProperty(document, 'referrer', {
        value: referrer,
        writable: true,
      })
      expect(isOrqivium()).toBe(true)
    })
  })

  it('should return false with multiple non-orqivium referrer variations', () => {
    const variations = [
      'https://github.com',
      'https://google.com',
      'https://stackoverflow.com',
      'https://example.orqivium',
      'https://difyai.com',
      '',
    ]

    variations.forEach((referrer) => {
      Object.defineProperty(document, 'referrer', {
        value: referrer,
        writable: true,
      })
      expect(isOrqivium()).toBe(false)
    })
  })
})
