import client from './client'
import type { ResponseModel } from '@/types/api'
import type {
  CategorySalaryStat,
  RegionSalaryStat,
  SkillsTopData,
  GlobalFilterParams
} from '@/types/job'

export async function getSalaryByCategory(
  params?: GlobalFilterParams
): Promise<CategorySalaryStat[]> {
  const res = await client.get<ResponseModel<CategorySalaryStat[]>>('/stats/salary-by-category', {
    params
  })
  return res.data.data
}

export async function getSalaryByRegion(
  params?: GlobalFilterParams
): Promise<RegionSalaryStat[]> {
  const res = await client.get<ResponseModel<RegionSalaryStat[]>>('/stats/salary-by-region', {
    params
  })
  return res.data.data
}

export async function getSkillsTop(
  params?: GlobalFilterParams & { limit?: number }
): Promise<SkillsTopData> {
  const res = await client.get<ResponseModel<SkillsTopData>>('/stats/skills-top', {
    params
  })
  return res.data.data
}
