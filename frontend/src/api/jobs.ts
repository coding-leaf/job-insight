import client from './client'
import type { ResponseModel } from '@/types/api'
import type { JobItem, JobListData, JobQueryParams } from '@/types/job'

export async function getJobs(params?: JobQueryParams): Promise<JobListData> {
  const res = await client.get<ResponseModel<JobListData>>('/jobs', { params })
  return res.data.data
}

export interface JobDetailRequestOptions {
  /** Batch loaders render per-item failures, so the global toast is suppressed. */
  silentError?: boolean
}

export async function getJobDetail(
  id: string,
  options?: JobDetailRequestOptions
): Promise<JobItem> {
  const res = await client.get<ResponseModel<JobItem>>(`/jobs/${encodeURIComponent(id)}`, {
    silentError: options?.silentError === true
  })
  return res.data.data
}
