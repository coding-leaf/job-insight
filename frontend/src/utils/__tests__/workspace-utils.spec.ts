import { beforeEach, describe, expect, it } from 'vitest'
import { setActivePinia, createPinia } from 'pinia'
import { checkSkills } from '@/utils/skillCheck'
import {
  WORKSPACE_STORAGE_KEY,
  parseWorkspacePayload,
  readWorkspaceStorage,
  serializeWorkspace
} from '@/utils/workspace'
import { useWorkspaceStore } from '@/stores/workspace'

class MemoryStorage implements Storage {
  private items = new Map<string, string>()
  failOnWrite = false

  get length(): number {
    return this.items.size
  }

  clear(): void {
    this.items.clear()
  }

  getItem(key: string): string | null {
    return this.items.has(key) ? (this.items.get(key) as string) : null
  }

  key(index: number): string | null {
    return Array.from(this.items.keys())[index] ?? null
  }

  removeItem(key: string): void {
    this.items.delete(key)
  }

  setItem(key: string, value: string): void {
    if (this.failOnWrite) throw new Error('QuotaExceededError')
    this.items.set(key, value)
  }
}

function installStorage(storage: Storage | null) {
  Object.defineProperty(globalThis, 'localStorage', {
    value: storage,
    configurable: true,
    writable: true
  })
}

function freshStore() {
  setActivePinia(createPinia())
  return useWorkspaceStore()
}

describe('parseWorkspacePayload', () => {
  it('returns empty state when the entry does not exist', () => {
    expect(parseWorkspacePayload(null)).toEqual({
      status: 'empty',
      savedJobIds: [],
      knownSkills: null
    })
  })

  it('restores saved ids in stored order and keeps knownSkills null', () => {
    const raw = serializeWorkspace({ savedJobIds: ['b', 'a', 'b'], knownSkills: null })
    expect(parseWorkspacePayload(raw)).toEqual({
      status: 'loaded',
      savedJobIds: ['b', 'a'],
      knownSkills: null
    })
  })

  it('keeps an explicitly empty skill selection distinct from null', () => {
    const raw = serializeWorkspace({ savedJobIds: [], knownSkills: [] })
    const parsed = parseWorkspacePayload(raw)
    expect(parsed.status).toBe('loaded')
    expect(parsed.knownSkills).toEqual([])
    expect(parseWorkspacePayload(serializeWorkspace({ savedJobIds: [], knownSkills: null })).knownSkills).toBeNull()
  })

  it('falls back to empty state for broken JSON without clearing other keys', () => {
    expect(parseWorkspacePayload('{not json').status).toBe('corrupt')
  })

  it('falls back to empty state for known-version shape errors', () => {
    expect(parseWorkspacePayload(JSON.stringify({ version: 1, savedJobIds: 'a', knownSkills: null })).status).toBe(
      'corrupt'
    )
    expect(
      parseWorkspacePayload(JSON.stringify({ version: 1, savedJobIds: [1], knownSkills: null })).status
    ).toBe('corrupt')
    expect(
      parseWorkspacePayload(JSON.stringify({ version: 1, savedJobIds: [], knownSkills: 'Python' })).status
    ).toBe('corrupt')
    expect(parseWorkspacePayload(JSON.stringify([])).status).toBe('corrupt')
  })

  it('ignores entries written by an unknown version', () => {
    const parsed = parseWorkspacePayload(
      JSON.stringify({ version: 2, savedJobIds: ['a'], knownSkills: ['Python'] })
    )
    expect(parsed).toEqual({ status: 'unknown_version', savedJobIds: [], knownSkills: null })
  })
})

describe('workspace storage access', () => {
  it('reports unavailable when the browser provides no storage', () => {
    installStorage(null)
    expect(readWorkspaceStorage().status).toBe('unavailable')
  })

  it('reports unavailable when reading throws', () => {
    const broken = new MemoryStorage()
    broken.getItem = () => {
      throw new Error('SecurityError')
    }
    installStorage(broken)
    expect(readWorkspaceStorage().status).toBe('unavailable')
  })

  it('never clears unrelated storage keys', () => {
    const storage = new MemoryStorage()
    storage.setItem('other-app:key', 'keep-me')
    storage.setItem(WORKSPACE_STORAGE_KEY, '{broken')
    installStorage(storage)

    expect(readWorkspaceStorage().status).toBe('corrupt')
    expect(storage.getItem('other-app:key')).toBe('keep-me')
    expect(storage.getItem(WORKSPACE_STORAGE_KEY)).toBe('{broken')
  })
})

describe('workspace store', () => {
  let storage: MemoryStorage

  beforeEach(() => {
    storage = new MemoryStorage()
    installStorage(storage)
  })

  it('saves, deduplicates, and restores candidate ids', () => {
    const store = freshStore()
    expect(store.toggleSaved('job-a')).toBe(true)
    expect(store.toggleSaved('job-b')).toBe(true)
    expect(store.toggleSaved('job-a')).toBe(false)
    expect(store.savedJobIds).toEqual(['job-b'])
    expect(store.toggleSaved('job-a')).toBe(true)
    expect(store.savedJobIds).toEqual(['job-a', 'job-b'])
    expect(store.isSaved('job-a')).toBe(true)

    const restored = freshStore()
    expect(restored.savedJobIds).toEqual(['job-a', 'job-b'])
  })

  it('cancels a candidate and persists the removal', () => {
    const store = freshStore()
    store.toggleSaved('job-a')
    store.toggleSaved('job-b')
    store.toggleSaved('job-b')
    expect(store.savedJobIds).toEqual(['job-a'])
    expect(JSON.parse(storage.getItem(WORKSPACE_STORAGE_KEY) as string).savedJobIds).toEqual(['job-a'])
  })

  it('restores saved ids from existing storage on creation', () => {
    storage.setItem(
      WORKSPACE_STORAGE_KEY,
      JSON.stringify({ version: 1, savedJobIds: ['job-z'], knownSkills: ['Python'] })
    )
    const store = freshStore()
    expect(store.savedJobIds).toEqual(['job-z'])
    expect(store.knownSkills).toEqual(['Python'])
    expect(store.canPersist).toBe(true)
  })

  it('keeps null and empty knownSkills distinct and persists both', () => {
    const store = freshStore()
    store.setKnownSkills(['Python', 'Python', ' SQL '])
    expect(store.knownSkills).toEqual(['Python', 'SQL'])
    store.setKnownSkills([])
    expect(store.knownSkills).toEqual([])
    expect(JSON.parse(storage.getItem(WORKSPACE_STORAGE_KEY) as string).knownSkills).toEqual([])
    store.setKnownSkills(null)
    expect(store.knownSkills).toBeNull()
    expect(JSON.parse(storage.getItem(WORKSPACE_STORAGE_KEY) as string).knownSkills).toBeNull()
  })

  it('limits comparison to three unique jobs and rejects the fourth', () => {
    const store = freshStore()
    expect(store.addToCompare('job-1')).toBe('added')
    expect(store.addToCompare('job-1')).toBe('duplicate')
    expect(store.addToCompare('job-2')).toBe('added')
    expect(store.addToCompare('job-3')).toBe('added')
    expect(store.addToCompare('job-4')).toBe('limit_reached')
    expect(store.compareJobIds).toEqual(['job-1', 'job-2', 'job-3'])
  })

  it('keeps comparison independent from the candidate shortlist', () => {
    const store = freshStore()
    store.toggleSaved('job-1')
    store.toggleSaved('job-2')
    store.addToCompare('job-1')
    store.addToCompare('job-2')

    store.removeSaved('job-1')
    expect(store.savedJobIds).toEqual(['job-2'])
    expect(store.compareJobIds).toEqual(['job-1', 'job-2'])

    store.removeFromCompare('job-1')
    expect(store.compareJobIds).toEqual(['job-2'])
    expect(store.savedJobIds).toEqual(['job-2'])

    store.clearCompare()
    expect(store.compareJobIds).toEqual([])
    expect(store.savedJobIds).toEqual(['job-2'])
  })

  it('does not persist comparison ids to local storage', () => {
    const store = freshStore()
    store.addToCompare('job-1')
    expect(storage.getItem(WORKSPACE_STORAGE_KEY)).toBeNull()
    expect(JSON.parse(serializeWorkspace({ savedJobIds: [], knownSkills: null }))).not.toHaveProperty(
      'compareJobIds'
    )
  })

  it('keeps in-memory edits when writing fails and warns the user', () => {
    storage.failOnWrite = true
    const store = freshStore()
    expect(store.toggleSaved('job-a')).toBe(true)
    expect(store.savedJobIds).toEqual(['job-a'])
    expect(store.canPersist).toBe(false)
    expect(store.persistenceNotice).toContain('刷新后可能丢失')
  })

  it('falls back to session mode when storage is blocked', () => {
    installStorage(null)
    const store = freshStore()
    expect(store.canPersist).toBe(false)
    expect(store.storageStatus).toBe('unavailable')
    expect(store.toggleSaved('job-a')).toBe(true)
    expect(store.savedJobIds).toEqual(['job-a'])
  })

  it('warns once about an unreadable entry without wiping it', () => {
    storage.setItem(WORKSPACE_STORAGE_KEY, '{broken')
    const store = freshStore()
    expect(store.storageStatus).toBe('corrupt')
    expect(store.persistenceNotice).toBeTruthy()
    expect(store.savedJobIds).toEqual([])
    store.dismissPersistenceNotice()
    expect(store.persistenceNotice).toBeNull()
  })

  it('rebuilds a corrupt entry after an explicit user change', () => {
    storage.setItem(WORKSPACE_STORAGE_KEY, '{broken')
    const store = freshStore()
    store.toggleSaved('job-a')
    expect(JSON.parse(storage.getItem(WORKSPACE_STORAGE_KEY) as string)).toEqual({
      version: 1,
      savedJobIds: ['job-a'],
      knownSkills: null
    })
  })

  it('does not overwrite an entry written by an unknown version', () => {
    const raw = JSON.stringify({ version: 2, savedJobIds: ['legacy'], knownSkills: ['Python'] })
    storage.setItem(WORKSPACE_STORAGE_KEY, raw)
    const store = freshStore()
    expect(store.storageStatus).toBe('unknown_version')
    expect(store.canPersist).toBe(false)
    expect(store.savedJobIds).toEqual([])

    store.toggleSaved('job-a')
    expect(store.savedJobIds).toEqual(['job-a'])
    expect(storage.getItem(WORKSPACE_STORAGE_KEY)).toBe(raw)
  })
})

describe('checkSkills', () => {
  it('reports not_set when the user has not chosen any skill', () => {
    expect(checkSkills(null, [{ skill_name: 'Python' }])).toEqual({
      status: 'not_set',
      matched: [],
      pending: []
    })
  })

  it('reports no_job_skills when the record has no tags, even with a selection', () => {
    expect(checkSkills(['Python'], [])).toEqual({
      status: 'no_job_skills',
      matched: [],
      pending: []
    })
  })

  it('splits job tags into checked and to-review sets without scoring', () => {
    const result = checkSkills(['Python', 'SQL'], [
      { skill_name: 'Python' },
      { skill_name: 'Spark' },
      { skill_name: 'SQL' }
    ])
    expect(result).toEqual({
      status: 'ready',
      matched: ['Python', 'SQL'],
      pending: ['Spark']
    })
    expect(result).not.toHaveProperty('score')
    expect(result).not.toHaveProperty('percentage')
  })

  it('treats an explicitly empty selection as no checked tags', () => {
    expect(checkSkills([], [{ skill_name: 'Python' }])).toEqual({
      status: 'ready',
      matched: [],
      pending: ['Python']
    })
  })

  it('counts duplicated job tags once', () => {
    expect(checkSkills([], [{ skill_name: 'Python' }, { skill_name: 'Python' }])).toEqual({
      status: 'ready',
      matched: [],
      pending: ['Python']
    })
  })
})
