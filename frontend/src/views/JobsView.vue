<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Search, Refresh, View, Files } from '@element-plus/icons-vue'
import { getJobs } from '@/api/jobs'
import JobDetailDrawer from '@/components/JobDetailDrawer.vue'
import JobActions from '@/components/JobActions.vue'
import type { JobItem } from '@/types/job'
import {
  DEFAULT_JOB_SORT_FIELD,
  DEFAULT_JOB_SORT_ORDER,
  JOB_SORT_FIELDS,
  buildJobQuery,
  jobQueryRequestKey,
  parseJobQuery,
  salaryRangeError,
  toJobQueryParams,
  type JobQueryState,
  type JobSortField,
  type JobSortOrder
} from '@/utils/jobQuery'

const route = useRoute()
const router = useRouter()

/** The URL is the single source of truth for applied conditions. */
const applied = computed<JobQueryState>(() => parseJobQuery(route.query))

const loading = ref(false)
const jobs = ref<JobItem[]>([])
const total = ref(0)
const loadError = ref<string | null>(null)
const hasLoadedOnce = ref(false)
let requestToken = 0
// A pagination size change can emit both size and page events in one tick, before the
// route has committed; this keeps the second event from overwriting the first.
let pendingState: JobQueryState | null = null

type ChipKey = 'keyword' | 'category' | 'province' | 'education' | 'minSalary' | 'hasSkills'

const draft = ref({
  keyword: applied.value.keyword,
  minSalary: applied.value.minSalary,
  maxSalary: applied.value.maxSalary,
  hasSkills: applied.value.hasSkills
})

const rangeError = computed(() => salaryRangeError(applied.value))

const activeChips = computed(() => {
  const state = applied.value
  const chips: Array<{ key: ChipKey; label: string }> = []
  if (state.keyword) chips.push({ key: 'keyword', label: `关键词：${state.keyword}` })
  if (state.category) chips.push({ key: 'category', label: `类别：${state.category}` })
  if (state.province) chips.push({ key: 'province', label: `省份：${state.province}` })
  if (state.education) chips.push({ key: 'education', label: `岗位学历要求：${state.education}` })
  if (state.minSalary !== undefined || state.maxSalary !== undefined) {
    const label =
      state.minSalary !== undefined && state.maxSalary !== undefined
        ? `月薪：${state.minSalary} - ${state.maxSalary} 元`
        : state.minSalary !== undefined
          ? `月薪：≥ ${state.minSalary} 元`
          : `月薪：≤ ${state.maxSalary} 元`
    chips.push({ key: 'minSalary', label })
  }
  if (state.hasSkills !== undefined) {
    chips.push({ key: 'hasSkills', label: state.hasSkills ? '仅含技能标签' : '仅无技能标签' })
  }
  return chips
})

const drawerVisible = ref(false)
const selectedJobId = ref<string | null>(null)

const sortBy = computed<JobSortField>({
  get: () => applied.value.sortBy,
  set: (field) => updateSort(field, applied.value.sortOrder)
})

const sortOrder = computed<JobSortOrder>({
  get: () => applied.value.sortOrder,
  set: (order) => updateSort(applied.value.sortBy, order)
})

const sortFieldOptions = JOB_SORT_FIELDS.map((field) => ({
  value: field,
  label:
    field === 'id'
      ? '默认 ID'
      : field === 'published_at'
        ? '发布时间'
        : field === 'salary_min_monthly'
          ? '最低月薪'
          : field === 'salary_max_monthly'
            ? '最高月薪'
            : '区间中点'
}))

async function fetchJobs(state: JobQueryState) {
  const token = ++requestToken
  loading.value = true
  loadError.value = null
  try {
    const data = await getJobs(toJobQueryParams(state))
    if (token !== requestToken) return
    jobs.value = data.items
    total.value = data.total
    hasLoadedOnce.value = true
    const lastPage = Math.max(1, data.total_pages)
    if (state.page > lastPage) {
      applyState({ ...state, page: lastPage })
    }
  } catch (err) {
    if (token !== requestToken) return
    console.error('Failed to load jobs list', err)
    loadError.value = '岗位列表加载失败，当前结果可能不是最新数据'
    if (!hasLoadedOnce.value) {
      jobs.value = []
      total.value = 0
    }
  } finally {
    if (token === requestToken) loading.value = false
  }
}

function applyState(state: JobQueryState) {
  pendingState = state
  void router.replace({ query: buildJobQuery(state) })
}

/** Latest applied-or-pending conditions, so rapid control events compose instead of conflict. */
function currentState(): JobQueryState {
  return pendingState ?? applied.value
}

function applyDraft() {
  const candidate: JobQueryState = {
    ...currentState(),
    keyword: draft.value.keyword,
    minSalary: typeof draft.value.minSalary === 'number' ? draft.value.minSalary : undefined,
    maxSalary: typeof draft.value.maxSalary === 'number' ? draft.value.maxSalary : undefined,
    hasSkills: draft.value.hasSkills,
    page: 1
  }
  const error = salaryRangeError(candidate)
  if (error) {
    ElMessage.error(error)
    return
  }
  applyState(candidate)
}

function updateSort(field: JobSortField, order: JobSortOrder) {
  applyState({ ...currentState(), sortBy: field, sortOrder: order, page: 1 })
}

function resetLocalQuery() {
  applyState({
    ...currentState(),
    keyword: '',
    minSalary: undefined,
    maxSalary: undefined,
    hasSkills: undefined,
    page: 1,
    sortBy: DEFAULT_JOB_SORT_FIELD,
    sortOrder: DEFAULT_JOB_SORT_ORDER
  })
}

function clearAllConditions() {
  applyState({
    ...parseJobQuery({}),
    sortBy: DEFAULT_JOB_SORT_FIELD,
    sortOrder: DEFAULT_JOB_SORT_ORDER
  })
}

function removeChip(key: ChipKey) {
  const next: JobQueryState = { ...currentState(), page: 1 }
  switch (key) {
    case 'keyword':
      next.keyword = ''
      break
    case 'category':
      next.category = undefined
      break
    case 'province':
      next.province = undefined
      break
    case 'education':
      next.education = undefined
      break
    case 'minSalary':
      next.minSalary = undefined
      next.maxSalary = undefined
      break
    case 'hasSkills':
      next.hasSkills = undefined
      break
  }
  applyState(next)
}

function handlePageChange(page: number) {
  applyState({ ...currentState(), page })
}

function handlePageSizeChange(pageSize: number) {
  applyState({ ...currentState(), pageSize, page: 1 })
}

function handleRowClick(row: JobItem) {
  selectedJobId.value = row.id
  drawerVisible.value = true
}

function openDetail(row: JobItem, event?: Event) {
  if (event) event.stopPropagation()
  selectedJobId.value = row.id
  drawerVisible.value = true
}

// One request per applied condition set; late responses cannot overwrite a newer one.
watch(
  () => jobQueryRequestKey(applied.value),
  () => {
    void fetchJobs(applied.value)
  },
  { immediate: true }
)

// Keep the draft controls aligned with URL changes (refresh, back/forward, chip removal).
watch(
  applied,
  (state) => {
    pendingState = null
    draft.value = {
      keyword: state.keyword,
      minSalary: state.minSalary,
      maxSalary: state.maxSalary,
      hasSkills: state.hasSkills
    }
  },
  { immediate: true }
)
</script>

<template>
  <div class="jobs-view">
    <!-- Local Query Toolbar -->
    <el-card shadow="never" class="filter-card">
      <div class="search-form">
        <div class="form-item">
          <span class="item-label">关键词</span>
          <el-input
            v-model="draft.keyword"
            placeholder="岗位名称、企业、正文或技能标签"
            clearable
            :prefix-icon="Search"
            class="keyword-input"
            @keyup.enter="applyDraft"
          />
        </div>

        <div class="form-item">
          <span class="item-label">月薪区间（元）</span>
          <div class="salary-range-inputs">
            <el-input-number
              v-model="draft.minSalary"
              :min="0"
              :step="1000"
              placeholder="最低"
              :controls="false"
              class="salary-input"
            />
            <span class="range-sep">-</span>
            <el-input-number
              v-model="draft.maxSalary"
              :min="0"
              :step="1000"
              placeholder="最高"
              :controls="false"
              class="salary-input"
            />
          </div>
        </div>

        <div class="form-item">
          <span class="item-label">技能标注</span>
          <el-select v-model="draft.hasSkills" placeholder="全部" clearable class="skills-select">
            <el-option label="全部岗位" :value="undefined" />
            <el-option label="仅含技能标签" :value="true" />
            <el-option label="无技能标签" :value="false" />
          </el-select>
        </div>

        <div class="form-item">
          <span class="item-label">排序</span>
          <el-select v-model="sortBy" class="sort-select">
            <el-option
              v-for="option in sortFieldOptions"
              :key="option.value"
              :label="option.label"
              :value="option.value"
            />
          </el-select>
          <el-select v-model="sortOrder" class="order-select">
            <el-option label="升序" value="asc" />
            <el-option label="降序" value="desc" />
          </el-select>
        </div>

        <div class="form-actions">
          <el-button type="primary" :icon="Search" @click="applyDraft">查询</el-button>
          <el-button :icon="Refresh" @click="resetLocalQuery">重置条件</el-button>
        </div>
      </div>

      <el-alert
        v-if="rangeError"
        :title="`${rangeError}，当前区间条件不会提交`"
        type="warning"
        :closable="false"
        show-icon
        class="range-alert"
      />

      <div v-if="activeChips.length > 0" class="active-filters">
        <span class="chips-label">当前条件</span>
        <el-tag
          v-for="chip in activeChips"
          :key="chip.key"
          closable
          type="info"
          effect="plain"
          @close="removeChip(chip.key)"
        >
          {{ chip.label }}
        </el-tag>
        <el-button link type="primary" size="small" @click="clearAllConditions">清空全部</el-button>
      </div>
    </el-card>

    <!-- Result Table -->
    <el-card shadow="never" class="table-card">
      <template #header>
        <div class="table-header">
          <div class="table-title">
            <el-icon><Files /></el-icon>
            <span>招聘岗位检索结果</span>
            <el-tag v-if="hasLoadedOnce" size="small" type="primary" effect="plain">
              共命中 {{ total.toLocaleString() }} 条岗位记录
            </el-tag>
            <el-tag v-else size="small" type="info" effect="plain">结果未加载</el-tag>
          </div>
          <div class="table-subtip">点击行查看岗位详情、来源链接与技能标签依据</div>
        </div>
      </template>

      <el-alert
        v-if="loadError"
        :title="loadError"
        type="error"
        :closable="false"
        show-icon
        class="state-alert"
      >
        <el-button size="small" @click="fetchJobs(applied)">重试</el-button>
      </el-alert>

      <el-table
        :data="jobs"
        stripe
        border
        style="width: 100%"
        v-loading="loading"
        highlight-current-row
        class="dense-table"
        @row-click="handleRowClick"
      >
        <el-table-column prop="id" label="岗位组 ID" width="110" align="center">
          <template #default="{ row }">
            <div class="id-cell">
              <span class="job-id">{{ row.id }}</span>
              <el-tag
                v-if="row.source_ids.length > 1"
                type="warning"
                size="small"
                effect="plain"
                class="merge-tag"
              >
                {{ row.source_ids.length }} 条合并
              </el-tag>
            </div>
          </template>
        </el-table-column>

        <el-table-column prop="title" label="岗位名称 / 类别" min-width="180">
          <template #default="{ row }">
            <div class="title-cell">
              <span class="job-title" :title="row.title">{{ row.title }}</span>
              <el-tag
                v-if="row.job_category"
                size="small"
                type="primary"
                effect="light"
                class="category-tag"
              >
                {{ row.job_category }}
              </el-tag>
              <span v-else class="text-muted">未分类</span>
            </div>
          </template>
        </el-table-column>

        <el-table-column prop="company" label="招聘企业" min-width="150">
          <template #default="{ row }">
            <div class="company-cell">
              <span class="company-name" :title="row.company">{{ row.company }}</span>
              <div v-if="row.company_size || row.company_type" class="company-sub">
                <span v-if="row.company_size">{{ row.company_size }}</span>
                <span v-if="row.company_type"> · {{ row.company_type }}</span>
              </div>
            </div>
          </template>
        </el-table-column>

        <el-table-column label="工作地点" width="130">
          <template #default="{ row }">
            <div class="location-cell">
              <span>{{ row.province || '未注明省份' }}</span>
              <span v-if="row.city" class="text-city">{{ row.city }}</span>
            </div>
          </template>
        </el-table-column>

        <el-table-column label="薪资" min-width="150" align="right">
          <template #default="{ row }">
            <div class="salary-cell">
              <span class="salary-text">{{ row.salary_display || '未注明' }}</span>
              <span
                v-if="row.salary_eligible_for_midpoint && row.salary_midpoint !== null"
                class="salary-mid"
              >
                区间中点 ¥{{ row.salary_midpoint.toLocaleString() }}
              </span>
              <span v-else class="salary-excluded">未参与中点核算</span>
            </div>
          </template>
        </el-table-column>

        <el-table-column label="学历 / 经验" width="150">
          <template #default="{ row }">
            <div class="req-cell">
              <span>{{ row.education_requirement || '未注明' }}</span>
              <span class="text-sub">{{ row.experience_requirement || '未注明' }}</span>
            </div>
          </template>
        </el-table-column>

        <el-table-column label="技能标签" min-width="170">
          <template #default="{ row }">
            <div class="skills-cell">
              <template v-if="row.skills && row.skills.length > 0">
                <el-tag
                  v-for="s in row.skills.slice(0, 3)"
                  :key="s.skill_name"
                  size="small"
                  type="info"
                  effect="plain"
                  class="skill-tag"
                >
                  {{ s.skill_name }}
                </el-tag>
                <el-tag
                  v-if="row.skills.length > 3"
                  size="small"
                  type="info"
                  class="skill-more"
                >
                  +{{ row.skills.length - 3 }}
                </el-tag>
              </template>
              <span v-else class="text-muted">未标注</span>
            </div>
          </template>
        </el-table-column>

        <el-table-column label="操作" width="100" align="center">
          <template #default="{ row }">
            <el-button
              type="primary"
              link
              size="small"
              :icon="View"
              @click.stop="openDetail(row, $event)"
            >
              详情
            </el-button>
          </template>
        </el-table-column>

        <el-table-column label="收藏 / 对比" width="150" align="center" fixed="right">
          <template #default="{ row }">
            <JobActions :job-id="row.id" />
          </template>
        </el-table-column>
      </el-table>

      <el-empty
        v-if="!loading && !loadError && jobs.length === 0 && hasLoadedOnce"
        description="当前条件下没有匹配的岗位记录，可以调整或清空条件"
      >
        <el-button type="primary" @click="clearAllConditions">清空全部条件</el-button>
      </el-empty>

      <div v-if="total > 0" class="pagination-container">
        <el-pagination
          :current-page="applied.page"
          :page-size="applied.pageSize"
          :page-sizes="[10, 20, 50, 100]"
          :total="total"
          layout="total, sizes, prev, pager, next, jumper"
          background
          @current-change="handlePageChange"
          @size-change="handlePageSizeChange"
        />
      </div>
    </el-card>

    <JobDetailDrawer v-model:visible="drawerVisible" :job-id="selectedJobId" />
  </div>
</template>

<style scoped>
.jobs-view {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.filter-card,
.table-card {
  border-radius: 8px;
  border: 1px solid #e4e7ed;
  background: #ffffff;
}

.search-form {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 16px;
}

.form-item {
  display: flex;
  align-items: center;
  gap: 8px;
}

.item-label {
  font-size: 13px;
  color: #606266;
  white-space: nowrap;
}

.keyword-input {
  width: 240px;
}

.salary-range-inputs {
  display: flex;
  align-items: center;
  gap: 4px;
}

.salary-input {
  width: 96px;
}

.range-sep {
  color: #909399;
}

.skills-select {
  width: 130px;
}

.sort-select {
  width: 120px;
}

.order-select {
  width: 88px;
}

.form-actions {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-left: auto;
}

.range-alert,
.state-alert {
  margin-top: 12px;
}

.active-filters {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 8px;
  margin-top: 12px;
  padding-top: 12px;
  border-top: 1px dashed #ebeef5;
}

.chips-label {
  font-size: 12px;
  color: #909399;
}

.table-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 8px;
}

.table-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 15px;
  font-weight: 600;
  color: #1f2d3d;
}

.table-subtip {
  font-size: 12px;
  color: #909399;
}

.id-cell {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 2px;
}

.job-id {
  font-family: monospace;
  font-size: 12px;
  color: #4b5563;
}

.merge-tag {
  font-size: 10px;
  padding: 0 4px;
  height: 18px;
  line-height: 16px;
}

.title-cell {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: 4px;
}

.job-title {
  font-weight: 600;
  color: #1f2d3d;
  font-size: 13px;
  line-height: 1.4;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  max-width: 240px;
}

.company-cell {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.company-name {
  color: #303133;
  font-size: 13px;
  font-weight: 500;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  max-width: 200px;
}

.company-sub {
  font-size: 11px;
  color: #909399;
}

.location-cell,
.req-cell {
  display: flex;
  flex-direction: column;
  gap: 2px;
  font-size: 12px;
}

.text-city,
.text-sub {
  color: #909399;
  font-size: 11px;
}

.salary-cell {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 2px;
}

.salary-text {
  font-weight: 700;
  color: #ff6a00;
  font-size: 13px;
}

.salary-mid {
  font-size: 11px;
  color: #0284c7;
}

.salary-excluded {
  font-size: 11px;
  color: #909399;
}

.skills-cell {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
  align-items: center;
}

.skill-tag {
  font-size: 11px;
}

.skill-more {
  font-size: 10px;
  padding: 0 4px;
  height: 20px;
  line-height: 18px;
}

.text-muted {
  color: #c0c4cc;
  font-size: 12px;
}

.dense-table :deep(tr) {
  cursor: pointer;
}

.pagination-container {
  margin-top: 16px;
  display: flex;
  justify-content: flex-end;
}

@media (max-width: 900px) {
  .form-actions {
    margin-left: 0;
  }

  .pagination-container {
    justify-content: center;
  }
}
</style>
