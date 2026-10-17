export interface ProvenanceItem {
  origin: string
  evidence: string
}

export interface SkillItem {
  skill_name: string
  provenance: ProvenanceItem[]
}

export interface JobItem {
  id: string
  source_ids: string[]
  source_url: string | null
  published_at: string | null
  title: string
  company: string
  company_type: string | null
  company_size: string | null
  work_location: string | null
  province: string | null
  city: string | null
  salary_display: string | null
  salary_min_monthly: number | null
  salary_max_monthly: number | null
  salary_eligible_for_midpoint: boolean
  salary_midpoint: number | null
  salary_stat_excluded: boolean
  salary_exclude_reason: string | null
  education_requirement: string | null
  education_min_code: number | null
  experience_requirement: string | null
  experience_min_years: number | null
  experience_status: string | null
  major_requirement: string | null
  description: string | null
  recruitment_headcount: number | null
  skills: SkillItem[]
  job_category: string | null
  category_source: string | null
}

export interface MetaOptionsData {
  categories: string[]
  provinces: string[]
  education_levels: string[]
}

export interface CategoryProportion {
  category: string
  count: number
  ratio: number
}

export interface OverviewData {
  total_jobs: number
  eligible_salary_jobs: number
  tagged_skills_jobs: number
  duplicate_groups: number
  overall_salary_median: number | null
  skill_coverage_ratio: number | null
  category_breakdown: CategoryProportion[]
}

export interface CategorySalaryStat {
  category: string
  sample_count: number
  eligible_count: number
  median: number | null
  p25: number | null
  p75: number | null
  is_low_sample: boolean
  rank: number | null
}

export interface RegionSalaryStat {
  province: string
  sample_count: number
  eligible_count: number
  median: number | null
  p25: number | null
  p75: number | null
  is_low_sample: boolean
  rank: number | null
}

export interface SkillStatItem {
  skill_name: string
  count: number
  ratio_annotated: number | null
  ratio_total: number | null
}

export interface SkillsTopData {
  total_jobs: number
  tagged_skills_jobs: number
  coverage_ratio: number | null
  skills: SkillStatItem[]
}

export interface JobListData {
  items: JobItem[]
  total: number
  page: number
  page_size: number
  total_pages: number
}

export interface GlobalFilterParams {
  category?: string
  province?: string
  education?: string
}

export interface JobQueryParams extends GlobalFilterParams {
  keyword?: string
  min_salary?: number
  max_salary?: number
  has_skills?: boolean
  page?: number
  page_size?: number
  sort_by?: string
  sort_order?: 'asc' | 'desc'
}
