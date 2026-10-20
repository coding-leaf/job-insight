/** Persisted local user state. This is user action state, not recruitment data. */
export interface PersistedWorkspaceState {
  version: number
  savedJobIds: string[]
  /** `null` means "not set"; `[]` means the user explicitly selected no skill. */
  knownSkills: string[] | null
}

export type WorkspaceStorageStatus =
  | 'empty'
  | 'loaded'
  | 'corrupt'
  | 'unknown_version'
  | 'unavailable'

export interface WorkspaceSnapshot {
  status: WorkspaceStorageStatus
  savedJobIds: string[]
  knownSkills: string[] | null
}

export type CompareAddResult = 'added' | 'duplicate' | 'limit_reached'

/** Maximum number of side-by-side comparison columns. */
export const MAX_COMPARE_JOBS = 3
