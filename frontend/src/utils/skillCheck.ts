export type SkillCheckStatus = 'not_set' | 'no_job_skills' | 'ready'

export interface SkillCheckResult {
  status: SkillCheckStatus
  /** Job tags the user already selected (T ∩ U). */
  matched: string[]
  /** Job tags the user has not selected yet (T − U), i.e. tags to review. */
  pending: string[]
}

/**
 * Derive the tag intersection/difference between the user's declared tags and the
 * tags present on a job record. This never produces a score, match percentage or
 * hiring probability: the tag list is partial and does not describe proficiency.
 */
export function checkSkills(
  knownSkills: string[] | null,
  jobSkills: Array<{ skill_name: string }>
): SkillCheckResult {
  if (knownSkills === null) {
    return { status: 'not_set', matched: [], pending: [] }
  }

  const jobNames: string[] = []
  for (const skill of jobSkills) {
    const name = typeof skill?.skill_name === 'string' ? skill.skill_name.trim() : ''
    if (!name || jobNames.includes(name)) continue
    jobNames.push(name)
  }

  if (jobNames.length === 0) {
    return { status: 'no_job_skills', matched: [], pending: [] }
  }

  const known = new Set(knownSkills.map((name) => name.trim()))
  return {
    status: 'ready',
    matched: jobNames.filter((name) => known.has(name)),
    pending: jobNames.filter((name) => !known.has(name))
  }
}
