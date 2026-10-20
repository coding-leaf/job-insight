import type { LocationQuery } from 'vue-router'
import { MAX_COMPARE_JOBS } from '@/types/workspace'
import { uniqueIds } from '@/utils/workspace'

/**
 * Read comparison ids from `/compare?ids=a&ids=b`: repeated or single values are
 * accepted, empties dropped, duplicates removed and the first three kept in order.
 */
export function parseCompareIds(query: LocationQuery): string[] {
  const raw = query.ids
  const list = (Array.isArray(raw) ? raw : typeof raw === 'string' ? [raw] : []).filter(
    (value): value is string => typeof value === 'string'
  )
  return uniqueIds(list).slice(0, MAX_COMPARE_JOBS)
}
