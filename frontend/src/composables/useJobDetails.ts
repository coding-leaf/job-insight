import { ref } from 'vue'
import axios from 'axios'
import { getJobDetail } from '@/api/jobs'
import type { JobItem } from '@/types/job'
import { uniqueIds } from '@/utils/workspace'

export type JobDetailStatus = 'loading' | 'success' | 'not_found' | 'error'

export interface JobDetailRecord {
  id: string
  status: JobDetailStatus
  job: JobItem | null
  errorMessage: string | null
}

function toRecord(
  id: string,
  status: JobDetailStatus,
  job: JobItem | null = null,
  errorMessage: string | null = null
): JobDetailRecord {
  return { id, status, job, errorMessage }
}

function describeFailure(error: unknown): { status: JobDetailStatus; message: string } {
  if (axios.isAxiosError(error)) {
    if (error.response?.status === 404) {
      return { status: 'not_found', message: '当前数据中未找到该岗位记录' }
    }
    if (error.response) {
      return { status: 'error', message: `加载失败（HTTP ${error.response.status}），可以重试` }
    }
  }
  return { status: 'error', message: '加载失败，请检查网络后重试' }
}

/**
 * Load a bounded set of job details through the single-job endpoint.
 * Each id keeps its own status so one failure never hides the other records, and a
 * newer batch invalidates late responses from an older one.
 */
export function useJobDetails() {
  const records = ref<Record<string, JobDetailRecord>>({})
  let requestToken = 0

  function setRecord(record: JobDetailRecord) {
    records.value = { ...records.value, [record.id]: record }
  }

  async function fetchInto(ids: string[], token: number) {
    await Promise.allSettled(
      ids.map(async (id) => {
        try {
          const job = await getJobDetail(id, { silentError: true })
          if (token !== requestToken) return
          setRecord(toRecord(id, 'success', job))
        } catch (error) {
          if (token !== requestToken) return
          const failure = describeFailure(error)
          setRecord(toRecord(id, failure.status, null, failure.message))
        }
      })
    )
  }

  /**
   * Ensure exactly these ids are tracked: already loaded records are kept (no
   * refetch), missing or previously failed ones are requested again, and records
   * that left the set are dropped.
   */
  async function load(ids: readonly string[]) {
    const token = ++requestToken
    const targetIds = uniqueIds(ids)
    const previous = records.value
    const next: Record<string, JobDetailRecord> = {}
    const pending: string[] = []
    for (const id of targetIds) {
      const existing = previous[id]
      if (existing && existing.status === 'success') {
        next[id] = existing
      } else {
        next[id] = toRecord(id, 'loading')
        pending.push(id)
      }
    }
    records.value = next
    await fetchInto(pending, token)
  }

  /** Retry only the failing ids, keeping already-loaded records untouched. */
  async function retry(ids: readonly string[]) {
    const token = ++requestToken
    const targets = uniqueIds(ids).filter((id) => records.value[id] !== undefined)
    for (const id of targets) {
      setRecord(toRecord(id, 'loading'))
    }
    await fetchInto(targets, token)
  }

  return {
    records,
    load,
    retry
  }
}
