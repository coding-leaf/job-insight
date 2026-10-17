import client from './client'
import type { ResponseModel } from '@/types/api'
import type { JobItem, JobListData, JobQueryParams } from '@/types/job'

export async function getJobs(params?: JobQueryParams): Promise<JobListData> {
  const res = await client.get<ResponseModel<JobListData>>('/jobs', { params })
  return res.data.data
}

export async function getJobDetail(id: string): Promise<JobItem> {
  const res = await client.get<ResponseModel<JobItem>>(`/jobs/${encodeURIComponent(id)}`)
  return res.data.data
}
