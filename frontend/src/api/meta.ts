import client from './client'
import type { ResponseModel } from '@/types/api'
import type { MetaOptionsData } from '@/types/job'

export async function getOptions(): Promise<MetaOptionsData> {
  const res = await client.get<ResponseModel<MetaOptionsData>>('/meta/options')
  return res.data.data
}
