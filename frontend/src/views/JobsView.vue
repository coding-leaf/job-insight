<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import {
  Search,
  Refresh,
  View,
  Files
} from '@element-plus/icons-vue'
import { useFilterStore } from '@/stores/filter'
import { getJobs } from '@/api/jobs'
import JobDetailDrawer from '@/components/JobDetailDrawer.vue'
import type { JobItem, JobQueryParams } from '@/types/job'

const route = useRoute()
const router = useRouter()
const filterStore = useFilterStore()

const loading = ref(false)
const jobs = ref<JobItem[]>([])
const total = ref(0)
const page = ref(1)
const pageSize = ref(20)

// Search controls
const keyword = ref('')
const minSalary = ref<number | undefined>(undefined)
const maxSalary = ref<number | undefined>(undefined)
const hasSkills = ref<boolean | undefined>(undefined)
const sortBy = ref<string>('id')
const sortOrder = ref<'asc' | 'desc'>('asc')

// Drawer state
const drawerVisible = ref(false)
const selectedJobId = ref<string | null>(null)

async function loadData() {
  loading.value = true
  try {
    const params: JobQueryParams = {
      ...filterStore.activeParams,
      page: page.value,
      page_size: pageSize.value,
      sort_by: sortBy.value,
      sort_order: sortOrder.value
    }

    if (keyword.value.trim()) params.keyword = keyword.value.trim()
    if (minSalary.value != null) params.min_salary = minSalary.value
    if (maxSalary.value != null) params.max_salary = maxSalary.value
    if (hasSkills.value != null) params.has_skills = hasSkills.value

    const res = await getJobs(params)
    jobs.value = res.items
    total.value = res.total
  } catch (err) {
    console.error('Failed to load jobs list', err)
  } finally {
    loading.value = false
  }
}

function handleSearch() {
  page.value = 1
  const query = { ...route.query }
  delete query.page
  router.replace({ query })
  loadData()
}

function handleResetQuery() {
  keyword.value = ''
  minSalary.value = undefined
  maxSalary.value = undefined
  hasSkills.value = undefined
  sortBy.value = 'id'
  sortOrder.value = 'asc'
  page.value = 1
  const query = { ...route.query }
  delete query.page
  router.replace({ query })
  loadData()
}

function handlePageChange(newPage: number) {
  page.value = newPage
  const query = { ...route.query }
  if (newPage > 1) {
    query.page = String(newPage)
  } else {
    delete query.page
  }
  router.replace({ query })
  loadData()
}

function handlePageSizeChange(newSize: number) {
  pageSize.value = newSize
  page.value = 1
  const query = { ...route.query }
  delete query.page
  router.replace({ query })
  loadData()
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

// Watch global slicer filter changes -> reset page to 1 and reload
watch(
  () => filterStore.activeParams,
  () => {
    page.value = 1
    loadData()
  },
  { deep: true }
)

onMounted(() => {
  // Sync page from route if present
  if (route.query.page && typeof route.query.page === 'string') {
    const p = parseInt(route.query.page, 10)
    if (!isNaN(p) && p > 0) page.value = p
  }
  loadData()
})
</script>

<template>
  <div class="jobs-view">
    <!-- Local Query Toolbar -->
    <el-card shadow="never" class="filter-card">
      <div class="search-form">
        <!-- Keyword -->
        <div class="form-item">
          <span class="item-label">岗位搜索</span>
          <el-input
            v-model="keyword"
            placeholder="搜索岗位名、企业、描述或技能"
            clearable
            :prefix-icon="Search"
            style="width: 260px"
            @keyup.enter="handleSearch"
          />
        </div>

        <!-- Salary Min / Max -->
        <div class="form-item">
          <span class="item-label">月薪区间 (元)</span>
          <div class="salary-range-inputs">
            <el-input-number
              v-model="minSalary"
              :min="0"
              :step="1000"
              placeholder="最低月薪"
              :controls="false"
              style="width: 100px"
            />
            <span class="range-sep">-</span>
            <el-input-number
              v-model="maxSalary"
              :min="0"
              :step="1000"
              placeholder="最高月薪"
              :controls="false"
              style="width: 100px"
            />
          </div>
        </div>

        <!-- Skills Filter -->
        <div class="form-item">
          <span class="item-label">技能打标</span>
          <el-select
            v-model="hasSkills"
            placeholder="全部岗位"
            clearable
            style="width: 130px"
          >
            <el-option label="全部" :value="undefined" />
            <el-option label="仅含技能标签" :value="true" />
            <el-option label="无技能标签" :value="false" />
          </el-select>
        </div>

        <!-- Sort by -->
        <div class="form-item">
          <span class="item-label">排序方式</span>
          <el-select v-model="sortBy" style="width: 130px" @change="handleSearch">
            <el-option label="默认 ID" value="id" />
            <el-option label="发布时间" value="published_at" />
            <el-option label="中点月薪" value="salary_midpoint" />
            <el-option label="最低月薪" value="salary_min_monthly" />
            <el-option label="最高月薪" value="salary_max_monthly" />
          </el-select>
          <el-select v-model="sortOrder" style="width: 90px; margin-left: 6px;" @change="handleSearch">
            <el-option label="升序" value="asc" />
            <el-option label="降序" value="desc" />
          </el-select>
        </div>

        <!-- Buttons -->
        <div class="form-actions">
          <el-button type="primary" :icon="Search" @click="handleSearch">
            查询
          </el-button>
          <el-button :icon="Refresh" @click="handleResetQuery">
            重置
          </el-button>
        </div>
      </div>
    </el-card>

    <!-- Table Card -->
    <el-card shadow="never" class="table-card">
      <template #header>
        <div class="table-header">
          <div class="table-title">
            <el-icon><Files /></el-icon>
            <span>在招岗位检索透视结果</span>
            <el-tag size="small" type="primary" effect="plain" class="ml-2">
              共命中 {{ total.toLocaleString() }} 组岗位
            </el-tag>
          </div>
          <div class="table-subtip">
            点击任意行可调起右侧全景抽屉查看原始 19 列与技能 Provenance 证据链
          </div>
        </div>
      </template>

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
        <!-- ID & Merge Badge -->
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
                {{ row.source_ids.length }}合1
              </el-tag>
            </div>
          </template>
        </el-table-column>

        <!-- Title & Category -->
        <el-table-column prop="title" label="职位名称 / 类别" min-width="180">
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
            </div>
          </template>
        </el-table-column>

        <!-- Company -->
        <el-table-column prop="company" label="招聘企业" min-width="160">
          <template #default="{ row }">
            <div class="company-cell">
              <span class="company-name" :title="row.company">{{ row.company }}</span>
              <div class="company-sub">
                <span v-if="row.company_size">{{ row.company_size }}</span>
                <span v-if="row.company_type"> · {{ row.company_type }}</span>
              </div>
            </div>
          </template>
        </el-table-column>

        <!-- Location -->
        <el-table-column label="工作地点" width="130">
          <template #default="{ row }">
            <div class="location-cell">
              <span>{{ row.province || '未注明省份' }}</span>
              <span v-if="row.city" class="text-city">{{ row.city }}</span>
            </div>
          </template>
        </el-table-column>

        <!-- Salary -->
        <el-table-column label="薪资标准" min-width="150" align="right">
          <template #default="{ row }">
            <div class="salary-cell">
              <span class="salary-text">{{ row.salary_display || '面议' }}</span>
              <span v-if="row.salary_eligible_for_midpoint && row.salary_midpoint" class="salary-mid">
                核算中点: ¥{{ row.salary_midpoint.toLocaleString() }}
              </span>
              <span v-else class="salary-excluded">
                未纳核算
              </span>
            </div>
          </template>
        </el-table-column>

        <!-- Education & Exp -->
        <el-table-column label="学历 / 经验" width="140">
          <template #default="{ row }">
            <div class="req-cell">
              <span>{{ row.education_requirement || '学历不限' }}</span>
              <span class="text-sub">{{ row.experience_requirement || '经验不限' }}</span>
            </div>
          </template>
        </el-table-column>

        <!-- Skills Tags Preview -->
        <el-table-column label="打标技能" min-width="180">
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
              <span v-else class="text-muted">无标签</span>
            </div>
          </template>
        </el-table-column>

        <!-- Actions -->
        <el-table-column label="操作" width="100" align="center" fixed="right">
          <template #default="{ row }">
            <el-button
              type="primary"
              link
              size="small"
              :icon="View"
              @click.stop="openDetail(row, $event)"
            >
              详情档案
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- Pagination -->
      <div class="pagination-container">
        <el-pagination
          v-model:current-page="page"
          v-model:page-size="pageSize"
          :page-sizes="[10, 20, 50, 100]"
          :total="total"
          layout="total, sizes, prev, pager, next, jumper"
          background
          @current-change="handlePageChange"
          @size-change="handlePageSizeChange"
        />
      </div>
    </el-card>

    <!-- Deep Component Job Detail Drawer -->
    <JobDetailDrawer
      v-model:visible="drawerVisible"
      :job-id="selectedJobId"
    />
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

.salary-range-inputs {
  display: flex;
  align-items: center;
  gap: 4px;
}

.range-sep {
  color: #909399;
}

.form-actions {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-left: auto;
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

.ml-2 {
  margin-left: 8px;
}

.dense-table :deep(tr) {
  cursor: pointer;
}

.pagination-container {
  margin-top: 16px;
  display: flex;
  justify-content: flex-end;
}
</style>
