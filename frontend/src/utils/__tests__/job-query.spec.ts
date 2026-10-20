import { describe, expect, it } from 'vitest'
import type { LocationQuery } from 'vue-router'
import {
  DEFAULT_JOB_PAGE,
  DEFAULT_JOB_PAGE_SIZE,
  buildJobQuery,
  parseJobQuery,
  salaryRangeError,
  toJobQueryParams,
  type JobQueryState
} from '@/utils/jobQuery'
import { displayText, toSafeExternalUrl } from '@/utils/jobDisplay'

function emptyQuery(): LocationQuery {
  return {}
}

function stateOf(overrides: Partial<JobQueryState> = {}): JobQueryState {
  return {
    ...parseJobQuery(emptyQuery()),
    ...overrides
  }
}

describe('parseJobQuery', () => {
  it('applies defaults for an empty URL', () => {
    expect(parseJobQuery(emptyQuery())).toEqual({
      keyword: '',
      category: undefined,
      province: undefined,
      education: undefined,
      minSalary: undefined,
      maxSalary: undefined,
      hasSkills: undefined,
      page: DEFAULT_JOB_PAGE,
      pageSize: DEFAULT_JOB_PAGE_SIZE,
      sortBy: 'id',
      sortOrder: 'asc'
    })
  })

  it('parses has_skills=false as false instead of a truthy string', () => {
    expect(parseJobQuery({ has_skills: 'false' }).hasSkills).toBe(false)
    expect(parseJobQuery({ has_skills: 'true' }).hasSkills).toBe(true)
    expect(parseJobQuery({ has_skills: 'yes' }).hasSkills).toBeUndefined()
  })

  it('drops illegal numbers, unknown sort fields and repeated scalars', () => {
    const parsed = parseJobQuery({
      min_salary: '-1',
      max_salary: '12k',
      page: '0',
      page_size: '500',
      sort_by: 'company',
      sort_order: 'random',
      keyword: ['a', 'b']
    })
    expect(parsed.minSalary).toBeUndefined()
    expect(parsed.maxSalary).toBeUndefined()
    expect(parsed.page).toBe(DEFAULT_JOB_PAGE)
    expect(parsed.pageSize).toBe(DEFAULT_JOB_PAGE_SIZE)
    expect(parsed.sortBy).toBe('id')
    expect(parsed.sortOrder).toBe('asc')
    expect(parsed.keyword).toBe('')
  })

  it('trims keyword and keeps a valid sort whitelist entry', () => {
    const parsed = parseJobQuery({
      keyword: '  数据开发  ',
      sort_by: 'salary_midpoint',
      sort_order: 'desc',
      page: '3',
      page_size: '50'
    })
    expect(parsed.keyword).toBe('数据开发')
    expect(parsed.sortBy).toBe('salary_midpoint')
    expect(parsed.sortOrder).toBe('desc')
    expect(parsed.page).toBe(3)
    expect(parsed.pageSize).toBe(50)
  })
})

describe('buildJobQuery round-trip', () => {
  it('omits defaults and restores the same applied state', () => {
    const state = stateOf({
      keyword: '数据分析',
      category: '数据分析与大数据',
      province: '广东省',
      education: '本科及以上',
      minSalary: 8000,
      maxSalary: 20000,
      hasSkills: false,
      page: 2,
      pageSize: 50,
      sortBy: 'salary_midpoint',
      sortOrder: 'desc'
    })
    const query = buildJobQuery(state)
    expect(query).toEqual({
      keyword: '数据分析',
      category: '数据分析与大数据',
      province: '广东省',
      education: '本科及以上',
      min_salary: '8000',
      max_salary: '20000',
      has_skills: 'false',
      page: '2',
      page_size: '50',
      sort_by: 'salary_midpoint',
      sort_order: 'desc'
    })
    expect(parseJobQuery(query)).toEqual(state)
  })

  it('produces an empty query for the default state', () => {
    expect(buildJobQuery(stateOf())).toEqual({})
  })
})

describe('salary range validation', () => {
  it('rejects max below min and never sends that interval', () => {
    const state = stateOf({ minSalary: 20000, maxSalary: 8000 })
    expect(salaryRangeError(state)).toBeTruthy()
    expect(toJobQueryParams(state)).not.toHaveProperty('min_salary')
    expect(toJobQueryParams(state)).not.toHaveProperty('max_salary')
  })

  it('accepts a single-sided or ordered range', () => {
    expect(salaryRangeError(stateOf({ minSalary: 8000 }))).toBeNull()
    expect(salaryRangeError(stateOf({ minSalary: 8000, maxSalary: 8000 }))).toBeNull()
    expect(toJobQueryParams(stateOf({ minSalary: 8000, maxSalary: 12000 }))).toMatchObject({
      min_salary: 8000,
      max_salary: 12000
    })
  })

  it('safely handles null salary values from cleared input controls', () => {
    // When el-input-number is cleared, runtime value is null
    const stateWithNullMax = { minSalary: 8000, maxSalary: null }
    expect(salaryRangeError(stateWithNullMax)).toBeNull()

    const stateWithNullMin = { minSalary: null, maxSalary: 8000 }
    expect(salaryRangeError(stateWithNullMin)).toBeNull()

    // URL builder omits null values and does not emit min_salary=null
    const built = buildJobQuery(stateOf({ minSalary: null as any, maxSalary: 8000 }))
    expect(built).toEqual({ max_salary: '8000' })
    expect(built).not.toHaveProperty('min_salary')

    // API params also normalize null to undefined
    const params = toJobQueryParams(stateOf({ minSalary: 8000, maxSalary: null as any }))
    expect(params.min_salary).toBe(8000)
    expect(params.max_salary).toBeUndefined()
  })
})

describe('toJobQueryParams', () => {
  it('always sends pagination and sort fields understood by the API', () => {
    expect(toJobQueryParams(stateOf())).toEqual({
      page: 1,
      page_size: 20,
      sort_by: 'id',
      sort_order: 'asc'
    })
  })
})

describe('job display helpers', () => {
  it('keeps missing values explicit', () => {
    expect(displayText(null)).toBe('未注明')
    expect(displayText('  ')).toBe('未注明')
    expect(displayText('本科及以上')).toBe('本科及以上')
  })

  it('only allows http and https source links', () => {
    expect(toSafeExternalUrl('https://job.ncss.cn/job/1')).toBe('https://job.ncss.cn/job/1')
    expect(toSafeExternalUrl('http://job.ncss.cn/job/1')).toBe('http://job.ncss.cn/job/1')
    expect(toSafeExternalUrl('javascript:alert(1)')).toBeNull()
    expect(toSafeExternalUrl('data:text/html,hi')).toBeNull()
    expect(toSafeExternalUrl('not a url')).toBeNull()
    expect(toSafeExternalUrl(null)).toBeNull()
  })
})
