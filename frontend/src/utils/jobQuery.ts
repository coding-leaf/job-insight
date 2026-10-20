import type { LocationQuery } from 'vue-router'
import type { JobQueryParams } from '@/types/job'

export const JOB_SORT_FIELDS = [
  'id',
  'published_at',
  'salary_min_monthly',
  'salary_max_monthly',
  'salary_midpoint'
] as const

export type JobSortField = (typeof JOB_SORT_FIELDS)[number]

export const JOB_SORT_ORDERS = ['asc', 'desc'] as const

export type JobSortOrder = (typeof JOB_SORT_ORDERS)[number]

export const DEFAULT_JOB_SORT_FIELD: JobSortField = 'id'
export const DEFAULT_JOB_SORT_ORDER: JobSortOrder = 'asc'
export const DEFAULT_JOB_PAGE = 1
export const DEFAULT_JOB_PAGE_SIZE = 20
export const MAX_JOB_PAGE_SIZE = 100

export function normalizeSalary(value: number | null | undefined): number | undefined {
  return typeof value === 'number' && Number.isFinite(value) && value >= 0 ? value : undefined
}

/** The complete, normalized set of conditions applied on the job exploration page. */
export interface JobQueryState {
  keyword: string
  category: string | undefined
  province: string | undefined
  education: string | undefined
  minSalary: number | undefined
  maxSalary: number | undefined
  hasSkills: boolean | undefined
  page: number
  pageSize: number
  sortBy: JobSortField
  sortOrder: JobSortOrder
}

const SALARY_RANGE_ERROR = '最低月薪不能高于最高月薪'

function readScalar(query: LocationQuery, key: string): string | undefined {
  const value = query[key]
  // Repeated or non-scalar query values are not applied.
  if (typeof value !== 'string') return undefined
  const trimmed = value.trim()
  return trimmed === '' ? undefined : trimmed
}

function readNonNegativeInteger(value: string | undefined): number | undefined {
  if (value === undefined || !/^\d+$/.test(value)) return undefined
  const parsed = Number(value)
  return Number.isSafeInteger(parsed) ? parsed : undefined
}

function readSortField(value: string | undefined): JobSortField {
  const match = JOB_SORT_FIELDS.find((field) => field === value)
  return match ?? DEFAULT_JOB_SORT_FIELD
}

function readSortOrder(value: string | undefined): JobSortOrder {
  const match = JOB_SORT_ORDERS.find((order) => order === value)
  return match ?? DEFAULT_JOB_SORT_ORDER
}

export function parseJobQuery(query: LocationQuery): JobQueryState {
  const page = readNonNegativeInteger(readScalar(query, 'page'))
  const pageSizeRaw = readNonNegativeInteger(readScalar(query, 'page_size'))
  const pageSize =
    pageSizeRaw !== undefined && pageSizeRaw >= 1 && pageSizeRaw <= MAX_JOB_PAGE_SIZE
      ? pageSizeRaw
      : DEFAULT_JOB_PAGE_SIZE
  const hasSkillsRaw = readScalar(query, 'has_skills')

  return {
    keyword: readScalar(query, 'keyword') ?? '',
    category: readScalar(query, 'category'),
    province: readScalar(query, 'province'),
    education: readScalar(query, 'education'),
    minSalary: readNonNegativeInteger(readScalar(query, 'min_salary')),
    maxSalary: readNonNegativeInteger(readScalar(query, 'max_salary')),
    hasSkills: hasSkillsRaw === 'true' ? true : hasSkillsRaw === 'false' ? false : undefined,
    page: page !== undefined && page >= 1 ? page : DEFAULT_JOB_PAGE,
    pageSize,
    sortBy: readSortField(readScalar(query, 'sort_by')),
    sortOrder: readSortOrder(readScalar(query, 'sort_order'))
  }
}

/** Serialize the applied conditions; defaults are omitted from the URL. */
export function buildJobQuery(state: JobQueryState): Record<string, string> {
  const query: Record<string, string> = {}
  const keyword = state.keyword.trim()
  if (keyword) query.keyword = keyword
  if (state.category) query.category = state.category
  if (state.province) query.province = state.province
  if (state.education) query.education = state.education
  const min = normalizeSalary(state.minSalary)
  const max = normalizeSalary(state.maxSalary)
  if (min !== undefined) query.min_salary = String(min)
  if (max !== undefined) query.max_salary = String(max)
  if (state.hasSkills !== undefined) query.has_skills = state.hasSkills ? 'true' : 'false'
  if (state.page > DEFAULT_JOB_PAGE) query.page = String(state.page)
  if (state.pageSize !== DEFAULT_JOB_PAGE_SIZE) query.page_size = String(state.pageSize)
  if (state.sortBy !== DEFAULT_JOB_SORT_FIELD) query.sort_by = state.sortBy
  if (state.sortOrder !== DEFAULT_JOB_SORT_ORDER) query.sort_order = state.sortOrder
  return query
}

/** Returns a message when the applied salary range is contradictory, otherwise null. */
export function salaryRangeError(state: { minSalary?: number | null; maxSalary?: number | null }): string | null {
  const min = normalizeSalary(state.minSalary)
  const max = normalizeSalary(state.maxSalary)
  if (min === undefined || max === undefined) return null
  return min > max ? SALARY_RANGE_ERROR : null
}

/**
 * Build the API request parameters. An invalid salary range is never sent:
 * the visible warning blocks the request instead of querying an impossible interval.
 */
export function toJobQueryParams(state: JobQueryState): JobQueryParams {
  const params: JobQueryParams = {
    page: state.page,
    page_size: state.pageSize,
    sort_by: state.sortBy,
    sort_order: state.sortOrder
  }
  const keyword = state.keyword.trim()
  if (keyword) params.keyword = keyword
  if (state.category) params.category = state.category
  if (state.province) params.province = state.province
  if (state.education) params.education = state.education
  if (salaryRangeError(state) === null) {
    const min = normalizeSalary(state.minSalary)
    const max = normalizeSalary(state.maxSalary)
    if (min !== undefined) params.min_salary = min
    if (max !== undefined) params.max_salary = max
  }
  if (state.hasSkills !== undefined) params.has_skills = state.hasSkills
  return params
}

export function withJobPage(state: JobQueryState, page: number): JobQueryState {
  return { ...state, page }
}

/** Stable key used to trigger a single request per applied condition set. */
export function jobQueryRequestKey(state: JobQueryState): string {
  return JSON.stringify(toJobQueryParams(state))
}
