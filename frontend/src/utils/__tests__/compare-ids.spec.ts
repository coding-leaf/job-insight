import { describe, expect, it } from 'vitest'
import { parseCompareIds } from '@/utils/compareIds'

describe('parseCompareIds', () => {
  it('returns no ids when the URL has no ids parameter', () => {
    expect(parseCompareIds({})).toEqual([])
    expect(parseCompareIds({ ids: null })).toEqual([])
  })

  it('accepts a single id and a repeated parameter in order', () => {
    expect(parseCompareIds({ ids: 'job-a' })).toEqual(['job-a'])
    expect(parseCompareIds({ ids: ['job-b', 'job-a'] })).toEqual(['job-b', 'job-a'])
  })

  it('drops duplicates and empty values', () => {
    expect(parseCompareIds({ ids: ['job-a', 'job-a', '', 'job-b'] })).toEqual(['job-a', 'job-b'])
  })

  it('keeps at most three ids so the comparison stays side-by-side readable', () => {
    expect(parseCompareIds({ ids: ['1', '2', '3', '4'] })).toEqual(['1', '2', '3'])
  })
})
