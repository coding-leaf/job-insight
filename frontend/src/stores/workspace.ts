import { ref } from 'vue'
import { defineStore } from 'pinia'
import { MAX_COMPARE_JOBS, type CompareAddResult, type WorkspaceStorageStatus } from '@/types/workspace'
import { readWorkspaceStorage, uniqueIds, writeWorkspaceStorage } from '@/utils/workspace'

const READ_NOTICES: Partial<Record<WorkspaceStorageStatus, string>> = {
  corrupt:
    '本地保存的候选清单无法解析，本次按空清单运行；浏览器中的其他站点数据未被清除。',
  unknown_version:
    '本地保存的候选清单版本暂不支持，本次使用会话状态，刷新后可能丢失。',
  unavailable:
    '浏览器不允许本地保存，候选清单与个人技能仅在本次会话有效，刷新后可能丢失。'
}

const WRITE_FAILURE_NOTICE = '候选清单未能写入本地存储，本次操作仍然有效，但刷新后可能丢失。'

export const useWorkspaceStore = defineStore('workspace', () => {
  const snapshot = readWorkspaceStorage()

  const savedJobIds = ref<string[]>(snapshot.savedJobIds)
  const knownSkills = ref<string[] | null>(snapshot.knownSkills)
  // Comparison selection stays in memory only; it is restored from the /compare URL.
  const compareJobIds = ref<string[]>([])
  const canPersist = ref(
    snapshot.status !== 'unavailable' && snapshot.status !== 'unknown_version'
  )
  const storageStatus = ref<WorkspaceStorageStatus>(snapshot.status)
  const persistenceNotice = ref<string | null>(READ_NOTICES[snapshot.status] ?? null)

  function persist() {
    if (!canPersist.value) return
    const ok = writeWorkspaceStorage({
      savedJobIds: savedJobIds.value,
      knownSkills: knownSkills.value
    })
    if (!ok) {
      canPersist.value = false
      persistenceNotice.value = WRITE_FAILURE_NOTICE
    }
  }

  function isSaved(jobId: string): boolean {
    return savedJobIds.value.includes(jobId.trim())
  }

  /** Returns true when the job is saved after the toggle. */
  function toggleSaved(jobId: string): boolean {
    const normalized = jobId.trim()
    if (!normalized) return false
    const index = savedJobIds.value.indexOf(normalized)
    if (index >= 0) {
      savedJobIds.value.splice(index, 1)
      persist()
      return false
    }
    savedJobIds.value.unshift(normalized)
    persist()
    return true
  }

  function removeSaved(jobId: string) {
    const normalized = jobId.trim()
    const index = savedJobIds.value.indexOf(normalized)
    if (index < 0) return
    savedJobIds.value.splice(index, 1)
    persist()
  }

  function setKnownSkills(skills: string[] | null) {
    knownSkills.value = skills === null ? null : uniqueIds(skills)
    persist()
  }

  function isComparing(jobId: string): boolean {
    return compareJobIds.value.includes(jobId.trim())
  }

  function addToCompare(jobId: string): CompareAddResult {
    const normalized = jobId.trim()
    if (!normalized || compareJobIds.value.includes(normalized)) return 'duplicate'
    if (compareJobIds.value.length >= MAX_COMPARE_JOBS) return 'limit_reached'
    compareJobIds.value.push(normalized)
    return 'added'
  }

  function removeFromCompare(jobId: string) {
    const normalized = jobId.trim()
    const index = compareJobIds.value.indexOf(normalized)
    if (index < 0) return
    compareJobIds.value.splice(index, 1)
  }

  function clearCompare() {
    compareJobIds.value = []
  }

  /** Replace the in-memory selection with an already-normalized id list from the URL. */
  function setCompareIds(ids: readonly string[]) {
    compareJobIds.value = uniqueIds(ids).slice(0, MAX_COMPARE_JOBS)
  }

  function dismissPersistenceNotice() {
    persistenceNotice.value = null
  }

  return {
    savedJobIds,
    knownSkills,
    compareJobIds,
    canPersist,
    storageStatus,
    persistenceNotice,
    isSaved,
    toggleSaved,
    removeSaved,
    setKnownSkills,
    isComparing,
    addToCompare,
    removeFromCompare,
    clearCompare,
    setCompareIds,
    dismissPersistenceNotice
  }
})
