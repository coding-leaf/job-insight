import type { PersistedWorkspaceState, WorkspaceSnapshot } from '@/types/workspace'

export const WORKSPACE_STORAGE_KEY = 'jobinsight:workspace:v1'
export const WORKSPACE_VERSION = 1

/** Deduplicate non-empty identifiers while preserving input order. */
export function uniqueIds(values: readonly string[]): string[] {
  const result: string[] = []
  for (const value of values) {
    if (typeof value !== 'string') continue
    const trimmed = value.trim()
    if (!trimmed || result.includes(trimmed)) continue
    result.push(trimmed)
  }
  return result
}

function invalidSnapshot(status: 'corrupt' | 'unknown_version' | 'unavailable'): WorkspaceSnapshot {
  return { status, savedJobIds: [], knownSkills: null }
}

/**
 * Read a non-empty string array from untrusted JSON.
 * Returns `null` when the shape is not a string[] of non-empty values.
 */
function readStringList(value: unknown): string[] | null {
  if (!Array.isArray(value)) return null
  const result: string[] = []
  for (const item of value) {
    if (typeof item !== 'string') return null
    const trimmed = item.trim()
    if (!trimmed) return null
    if (!result.includes(trimmed)) result.push(trimmed)
  }
  return result
}

export function parseWorkspacePayload(raw: string | null): WorkspaceSnapshot {
  if (raw === null || raw.trim() === '') {
    return { status: 'empty', savedJobIds: [], knownSkills: null }
  }

  let parsed: unknown
  try {
    parsed = JSON.parse(raw)
  } catch {
    return invalidSnapshot('corrupt')
  }

  if (typeof parsed !== 'object' || parsed === null || Array.isArray(parsed)) {
    return invalidSnapshot('corrupt')
  }

  const record = parsed as Record<string, unknown>
  const version = record.version
  if (typeof version !== 'number' || !Number.isInteger(version)) {
    return invalidSnapshot('unknown_version')
  }
  if (version !== WORKSPACE_VERSION) {
    return invalidSnapshot('unknown_version')
  }

  const savedJobIds = readStringList(record.savedJobIds)
  if (savedJobIds === null) {
    return invalidSnapshot('corrupt')
  }

  const knownSkillsRaw = record.knownSkills
  let knownSkills: string[] | null = null
  if (knownSkillsRaw !== null) {
    knownSkills = readStringList(knownSkillsRaw)
    if (knownSkills === null) {
      return invalidSnapshot('corrupt')
    }
  }

  return { status: 'loaded', savedJobIds, knownSkills }
}

export function serializeWorkspace(state: {
  savedJobIds: readonly string[]
  knownSkills: string[] | null
}): string {
  const payload: PersistedWorkspaceState = {
    version: WORKSPACE_VERSION,
    savedJobIds: uniqueIds(state.savedJobIds),
    knownSkills: state.knownSkills === null ? null : uniqueIds(state.knownSkills)
  }
  return JSON.stringify(payload)
}

function getLocalStorage(): Storage | null {
  try {
    if (typeof globalThis.localStorage === 'undefined') return null
    return globalThis.localStorage
  } catch {
    // Accessing localStorage can throw when storage is blocked by the browser.
    return null
  }
}

/**
 * Read the workspace entry. Never throws and never clears other storage keys.
 */
export function readWorkspaceStorage(): WorkspaceSnapshot {
  const storage = getLocalStorage()
  if (!storage) return invalidSnapshot('unavailable')
  try {
    return parseWorkspacePayload(storage.getItem(WORKSPACE_STORAGE_KEY))
  } catch {
    return invalidSnapshot('unavailable')
  }
}

/** Returns false when the browser rejects persistence (disabled, quota, private mode). */
export function writeWorkspaceStorage(state: {
  savedJobIds: readonly string[]
  knownSkills: string[] | null
}): boolean {
  const storage = getLocalStorage()
  if (!storage) return false
  try {
    storage.setItem(WORKSPACE_STORAGE_KEY, serializeWorkspace(state))
    return true
  } catch {
    return false
  }
}
