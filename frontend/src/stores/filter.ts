import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { LocationQuery } from 'vue-router'
import type { GlobalFilterParams } from '@/types/job'

export const useFilterStore = defineStore('filter', () => {
  const category = ref<string | undefined>(undefined)
  const province = ref<string | undefined>(undefined)
  const education = ref<string | undefined>(undefined)

  const activeParams = computed<GlobalFilterParams>(() => {
    const params: GlobalFilterParams = {}
    if (category.value) params.category = category.value
    if (province.value) params.province = province.value
    if (education.value) params.education = education.value
    return params
  })

  const hasActiveFilters = computed<boolean>(() => {
    return Boolean(category.value || province.value || education.value)
  })

  function setCategory(val: string | undefined) {
    category.value = val || undefined
  }

  function setProvince(val: string | undefined) {
    province.value = val || undefined
  }

  function setEducation(val: string | undefined) {
    education.value = val || undefined
  }

  function resetFilters() {
    category.value = undefined
    province.value = undefined
    education.value = undefined
  }

  function syncFromQuery(query: LocationQuery) {
    const cat = query.category
    category.value = typeof cat === 'string' && cat.trim() ? cat.trim() : undefined

    const prov = query.province
    province.value = typeof prov === 'string' && prov.trim() ? prov.trim() : undefined

    const edu = query.education
    education.value = typeof edu === 'string' && edu.trim() ? edu.trim() : undefined
  }

  function toQuery(): Record<string, string> {
    const q: Record<string, string> = {}
    if (category.value) q.category = category.value
    if (province.value) q.province = province.value
    if (education.value) q.education = education.value
    return q
  }

  return {
    category,
    province,
    education,
    activeParams,
    hasActiveFilters,
    setCategory,
    setProvince,
    setEducation,
    resetFilters,
    syncFromQuery,
    toQuery
  }
})
