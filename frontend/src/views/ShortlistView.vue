<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import { Star, Refresh, Search, Delete, WarningFilled, View } from '@element-plus/icons-vue'
import { useWorkspaceStore } from '@/stores/workspace'
import { useJobDetails } from '@/composables/useJobDetails'
import JobActions from '@/components/JobActions.vue'
import JobDetailDrawer from '@/components/JobDetailDrawer.vue'
import { displayText, toSafeExternalUrl } from '@/utils/jobDisplay'

const PAGE_SIZE = 10

const router = useRouter()
const workspace = useWorkspaceStore()
const { records, load, retry } = useJobDetails()

const page = ref(1)
const drawerVisible = ref(false)
const selectedJobId = ref<string | null>(null)

const totalCount = computed(() => workspace.savedJobIds.length)
const totalPages = computed(() => Math.max(1, Math.ceil(totalCount.value / PAGE_SIZE)))
const pageIds = computed(() =>
  workspace.savedJobIds.slice((page.value - 1) * PAGE_SIZE, page.value * PAGE_SIZE)
)

const failedIds = computed(() =>
  pageIds.value.filter((id) => records.value[id]?.status === 'error')
)

watch(
  totalPages,
  (lastPage) => {
    if (page.value > lastPage) page.value = lastPage
  },
  { immediate: true }
)

// Only the current page is requested; each record keeps its own load state.
watch(
  () => pageIds.value.join(','),
  (joined) => {
    void load(joined ? joined.split(',') : [])
  },
  { immediate: true }
)

function retryFailed() {
  void retry(failedIds.value)
}

function removeSaved(id: string) {
  workspace.removeSaved(id)
}

function openDetail(id: string) {
  selectedJobId.value = id
  drawerVisible.value = true
}

function goToJobs() {
  void router.push({ path: '/jobs' })
}
</script>

<template>
  <div class="shortlist-view">
    <div class="page-head">
      <div class="head-left">
        <h1 class="page-title">
          <el-icon><Star /></el-icon>
          <span>候选清单</span>
          <el-tag size="small" type="primary" effect="plain">{{ totalCount }} 个岗位</el-tag>
        </h1>
        <p class="page-desc">
          候选清单保存在本浏览器。刷新后可恢复，清除站点数据或更换设备/浏览器会丢失；它不是账号同步的收藏。
        </p>
      </div>
      <el-button type="primary" :icon="Search" @click="goToJobs">继续选岗</el-button>
    </div>

    <el-alert
      v-if="!workspace.canPersist && totalCount > 0"
      title="浏览器不允许本地保存，本次候选仅在当前会话有效，刷新后可能丢失。"
      type="warning"
      :closable="false"
      show-icon
    />

    <el-empty
      v-if="totalCount === 0"
      description="还没有收藏任何岗位。先在岗位探索中选择感兴趣的岗位。"
    >
      <el-button type="primary" :icon="Search" @click="goToJobs">开始选岗</el-button>
    </el-empty>

    <template v-else>
      <div v-if="failedIds.length > 0" class="batch-error">
        <el-alert
          :title="`本页有 ${failedIds.length} 个岗位加载失败，收藏状态已保留`"
          type="error"
          :closable="false"
          show-icon
        >
          <el-button size="small" :icon="Refresh" @click="retryFailed">重试失败项</el-button>
        </el-alert>
      </div>

      <div class="shortlist-list">
        <el-card
          v-for="id in pageIds"
          :key="id"
          shadow="never"
          class="shortlist-card"
          :body-style="{ padding: '16px 20px' }"
        >
          <!-- Loading -->
          <el-skeleton v-if="!records[id] || records[id].status === 'loading'" :rows="2" animated />

          <!-- Not found: the record may be gone from the current dataset, but the
               local selection is kept until the user removes it. -->
          <div v-else-if="records[id].status === 'not_found'" class="item-state">
            <el-icon class="state-icon state-warning"><WarningFilled /></el-icon>
            <div class="state-body">
              <span class="state-title">当前数据中未找到该岗位记录</span>
              <span class="state-desc">
                岗位 ID：{{ id }}。这不代表岗位已下架，也不会自动取消收藏，你可以保留或手动移除。
              </span>
            </div>
            <el-button size="small" :icon="Delete" @click="removeSaved(id)">从清单移除</el-button>
          </div>

          <!-- Network or service failure: retry, never treat as removed. -->
          <div v-else-if="records[id].status === 'error'" class="item-state">
            <el-icon class="state-icon state-error"><WarningFilled /></el-icon>
            <div class="state-body">
              <span class="state-title">{{ records[id].errorMessage }}</span>
              <span class="state-desc">岗位 ID：{{ id }}。网络或服务异常不代表岗位失效，收藏已保留。</span>
            </div>
            <el-button size="small" :icon="Refresh" @click="retry([id])">重试</el-button>
          </div>

          <!-- Loaded -->
          <template v-else-if="records[id].job">
            <div class="item-main">
              <div class="item-title-row">
                <span class="item-title">{{ records[id].job?.title }}</span>
                <el-tag v-if="records[id].job?.job_category" size="small" type="primary" effect="light">
                  {{ records[id].job?.job_category }}
                </el-tag>
                <el-tag v-else size="small" type="info" effect="plain">未分类</el-tag>
              </div>

              <div class="item-meta">
                <span class="meta-company">{{ records[id].job?.company }}</span>
                <span class="meta-sep">·</span>
                <span>{{ displayText(records[id].job?.work_location) }}</span>
                <span class="meta-sep">·</span>
                <span>{{ displayText(records[id].job?.education_requirement) }}</span>
                <span class="meta-sep">·</span>
                <span>{{ displayText(records[id].job?.experience_requirement) }}</span>
              </div>

              <div class="item-detail-row">
                <span class="meta-salary">{{ records[id].job?.salary_display || '薪资未注明' }}</span>
                <span
                  v-if="records[id].job?.salary_eligible_for_midpoint && records[id].job?.salary_midpoint !== null"
                  class="meta-midpoint"
                >
                  区间中点 ¥{{ records[id].job?.salary_midpoint?.toLocaleString() }}
                </span>
                <span v-else class="meta-muted">区间不完整，未计算中点</span>
                <span class="meta-muted">发布：{{ displayText(records[id].job?.published_at) }}</span>
                <el-link
                  v-if="toSafeExternalUrl(records[id].job?.source_url)"
                  :href="toSafeExternalUrl(records[id].job?.source_url) ?? undefined"
                  target="_blank"
                  rel="noopener noreferrer"
                  type="primary"
                  :underline="false"
                  class="meta-link"
                >
                  原始来源
                </el-link>
              </div>

              <div v-if="records[id].job && records[id].job!.skills.length > 0" class="item-skills">
                <el-tag
                  v-for="skill in records[id].job?.skills"
                  :key="skill.skill_name"
                  size="small"
                  type="info"
                  effect="plain"
                >
                  {{ skill.skill_name }}
                </el-tag>
              </div>
              <div v-else class="meta-muted skill-empty">未标注技能标签</div>
            </div>

            <div class="item-actions">
              <el-button size="small" :icon="View" @click="openDetail(id)">详情</el-button>
              <JobActions :job-id="id" />
              <el-button size="small" text :icon="Delete" @click="removeSaved(id)">移出清单</el-button>
            </div>
          </template>
        </el-card>
      </div>

      <div v-if="totalPages > 1" class="pagination-container">
        <el-pagination
          v-model:current-page="page"
          :page-size="PAGE_SIZE"
          :total="totalCount"
          layout="total, prev, pager, next"
          background
        />
      </div>
    </template>

    <JobDetailDrawer v-model:visible="drawerVisible" :job-id="selectedJobId" />
  </div>
</template>

<style scoped>
.shortlist-view {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.page-head {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 16px;
  flex-wrap: wrap;
}

.page-title {
  display: flex;
  align-items: center;
  gap: 8px;
  margin: 0 0 6px;
  font-size: 22px;
  font-weight: 700;
  color: #1f2d3d;
}

.page-desc {
  margin: 0;
  font-size: 13px;
  color: #909399;
  line-height: 1.6;
  max-width: 760px;
}

.shortlist-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.shortlist-card {
  border-radius: 8px;
  border: 1px solid #e4e7ed;
  background: #ffffff;
}

.item-main {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.item-title-row {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
}

.item-title {
  font-size: 16px;
  font-weight: 600;
  color: #1f2d3d;
}

.item-meta,
.item-detail-row {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
  font-size: 13px;
  color: #606266;
}

.meta-company {
  font-weight: 600;
}

.meta-sep {
  color: #dcdfe6;
}

.meta-salary {
  font-weight: 700;
  color: #ff6a00;
}

.meta-midpoint {
  color: #0284c7;
  font-size: 12px;
}

.meta-muted {
  color: #909399;
  font-size: 12px;
}

.meta-link {
  font-size: 12px;
}

.item-skills {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.skill-empty {
  margin: 0;
}

.item-actions {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: 8px;
  flex-wrap: wrap;
  margin-top: 12px;
  padding-top: 12px;
  border-top: 1px dashed #ebeef5;
}

.item-state {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
}

.state-icon {
  font-size: 20px;
}

.state-warning {
  color: #e6a23c;
}

.state-error {
  color: #f56c6c;
}

.state-body {
  display: flex;
  flex-direction: column;
  gap: 4px;
  flex: 1;
  min-width: 200px;
}

.state-title {
  font-size: 14px;
  font-weight: 600;
  color: #303133;
}

.state-desc {
  font-size: 12px;
  color: #909399;
  line-height: 1.5;
}

.pagination-container {
  display: flex;
  justify-content: flex-end;
}

@media (max-width: 640px) {
  .item-actions {
    justify-content: flex-start;
  }

  .pagination-container {
    justify-content: center;
  }
}
</style>
