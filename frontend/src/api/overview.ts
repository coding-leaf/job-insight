import client from './client'
import type { ResponseModel } from '@/types/api'
import type { OverviewData, GlobalFilterParams } from '@/types/job'

export async function getOverview(params?: GlobalFilterParams): Promise<OverviewData> {
  const res = await client.get<ResponseModel<OverviewData>>('/overview', { params })
  return res.data.data
}
