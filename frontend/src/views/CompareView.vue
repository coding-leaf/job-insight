<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Operation, Search, Refresh, Delete, Star, Link, Collection } from '@element-plus/icons-vue'
import { useWorkspaceStore } from '@/stores/workspace'
import { useJobDetails } from '@/composables/useJobDetails'
import JobActions from '@/components/JobActions.vue'
import JobDetailDrawer from '@/components/JobDetailDrawer.vue'
import SkillPicker from '@/components/SkillPicker.vue'
import { MAX_COMPARE_JOBS } from '@/types/workspace'
import type { JobItem } from '@/types/job'
import { checkSkills, type SkillCheckResult } from '@/utils/skillCheck'
import { displayText, toSafeExternalUrl } from '@/utils/jobDisplay'
import { parseCompareIds } from '@/utils/compareIds'
import { uniqueIds } from '@/utils/workspace'

const route = useRoute()
const router = useRouter()
const workspace = useWorkspaceStore()
const { records, load, retry } = useJobDetails()

const compareIds = ref<string[]>([])
const drawerVisible = ref(false)
const selectedJobId = ref<string | null>(null)
const skillSettingsOpen = ref<string[]>([])

const candidates = computed(() =>
  workspace.savedJobIds.filter((id) => !compareIds.value.includes(id))
)

function readIdsFromQuery(): string[] {
  return parseCompareIds(route.query)
}

function writeIdsToRoute(ids: string[]) {
  const current = readIdsFromQuery()
  if (current.join(',') === ids.join(',')) return
  void router.replace({ query: ids.length > 0 ? { ids } : {} })
}

/** URL ids win over the in-memory selection; without ids the selection is written to the URL. */
function syncFromRoute() {
  const fromUrl = readIdsFromQuery()
  if (fromUrl.length > 0) {
    compareIds.value = fromUrl
    workspace.setCompareIds(fromUrl)
    return
  }
  const fromStore = uniqueIds(workspace.compareJobIds).slice(0, MAX_COMPARE_JOBS)
  compareIds.value = fromStore
  if (fromStore.length > 0) writeIdsToRoute(fromStore)
}

watch(() => route.query.ids, syncFromRoute, { immediate: true })

watch(
  compareIds,
  (ids) => {
    void load(ids)
  },
  { immediate: true, deep: true }
)

// External mutations of the shared selection (tray removal, clear, action buttons)
// are mirrored into this page and its URL.
watch(
  () => workspace.compareJobIds.join(','),
  () => {
    const storeIds = uniqueIds(workspace.compareJobIds).slice(0, MAX_COMPARE_JOBS)
    if (storeIds.join(',') === compareIds.value.join(',')) return
    compareIds.value = storeIds
    writeIdsToRoute(storeIds)
  }
)

// A response may resolve an alias id to its representative group id; keep one column per group.
watch(
  records,
  (value) => {
    const canonical: string[] = []
    for (const id of compareIds.value) {
      const record = value[id]
      const jobId = record?.status === 'success' && record.job ? record.job.id : id
      if (!canonical.includes(jobId)) canonical.push(jobId)
    }
    if (canonical.length === compareIds.value.length && canonical.every((id, index) => id === compareIds.value[index])) {
      return
    }
    compareIds.value = canonical
    workspace.setCompareIds(canonical)
    writeIdsToRoute(canonical)
  },
  { deep: true }
)

const skillChecks = computed<Record<string, SkillCheckResult>>(() => {
  const result: Record<string, SkillCheckResult> = {}
  for (const id of compareIds.value) {
    result[id] = checkSkills(workspace.knownSkills, records.value[id]?.job?.skills ?? [])
  }
  return result
})

const loadedCount = computed(
  () => compareIds.value.filter((id) => records.value[id]?.status === 'success').length
)

const failedIds = computed(() =>
  compareIds.value.filter((id) => records.value[id]?.status === 'error')
)

const comparisonRows: Array<{ key: string; label: string; value: (job: JobItem) => string }> = [
  { key: 'title', label: '岗位名称', value: (job) => job.title },
  { key: 'company', label: '企业', value: (job) => job.company },
  { key: 'location', label: '工作地点', value: (job) => displayText(job.work_location) },
  {
    key: 'salary_display',
    label: '薪资原文',
    value: (job) => (job.salary_display ? job.salary_display : '未注明')
  },
  {
    key: 'salary_midpoint',
    label: '区间中点（元/月）',
    value: (job) =>
      job.salary_eligible_for_midpoint && job.salary_midpoint !== null
        ? `${job.salary_midpoint.toLocaleString()} 元/月`
        : '区间不完整，未计算中点'
  },
  { key: 'education', label: '学历要求', value: (job) => displayText(job.education_requirement) },
  { key: 'experience', label: '经验要求', value: (job) => displayText(job.experience_requirement) },
  { key: 'major', label: '专业要求', value: (job) => displayText(job.major_requirement) },
  {
    key: 'skills',
    label: '技能标签',
    value: (job) =>
      job.skills.length > 0 ? job.skills.map((skill) => skill.skill_name).join('、') : '未标注'
  },
  { key: 'published_at', label: '发布时间', value: (job) => displayText(job.published_at) }
]

function recordOf(id: string) {
  return records.value[id]
}

function jobOf(id: string): JobItem | null {
  const record = records.value[id]
  return record?.status === 'success' ? record.job : null
}

function titleOf(id: string): string {
  const job = jobOf(id)
  if (job) return job.title
  const record = recordOf(id)
  if (record?.status === 'not_found') return '当前数据中未找到'
  if (record?.status === 'error') return '加载失败'
  return '加载中…'
}

function sourceUrlOf(id: string): string | null {
  return toSafeExternalUrl(jobOf(id)?.source_url ?? null)
}

function removeColumn(id: string) {
  const next = compareIds.value.filter((current) => current !== id)
  compareIds.value = next
  workspace.setCompareIds(next)
  writeIdsToRoute(next)
}

function replaceColumn(index: number, candidateId: string) {
  if (!candidateId) return
  const next = [...compareIds.value]
  next[index] = candidateId
  const normalized = uniqueIds(next).slice(0, MAX_COMPARE_JOBS)
  compareIds.value = normalized
  workspace.setCompareIds(normalized)
  writeIdsToRoute(normalized)
}

function addCandidate(candidateId: string) {
  if (!candidateId) return
  if (compareIds.value.length >= MAX_COMPARE_JOBS) {
    ElMessage.warning(`最多同时比较 ${MAX_COMPARE_JOBS} 个岗位，请先移除一个`)
    return
  }
  if (compareIds.value.includes(candidateId)) return
  const next = [...compareIds.value, candidateId]
  compareIds.value = next
  workspace.setCompareIds(next)
  writeIdsToRoute(next)
}

function retryFailed() {
  void retry(failedIds.value)
}

function openDetail(id: string) {
  selectedJobId.value = id
  drawerVisible.value = true
}

function goToJobs() {
  void router.push({ path: '/jobs' })
}

function goToShortlist() {
  void router.push({ path: '/shortlist' })
}
</script>

<template>
  <div class="compare-view">
    <div class="page-head">
      <div class="head-left">
        <h1 class="page-title">
          <el-icon><Operation /></el-icon>
          <span>岗位对比</span>
          <el-tag size="small" type="primary" effect="plain">
            {{ compareIds.length }}/{{ MAX_COMPARE_JOBS }}
          </el-tag>
        </h1>
        <p class="page-desc">
          并排查看所选岗位的事实字段。缺失字段保持“未注明”或“未标注”，不填补为不限、0 或无需技能。
          这里不给出适配分、录用概率或“最佳岗位”结论。
        </p>
      </div>
      <div class="head-actions">
        <el-select
          v-if="candidates.length > 0 && compareIds.length < MAX_COMPARE_JOBS"
          placeholder="从候选清单添加"
          class="add-select"
          :model-value="undefined"
          @update:model-value="(value: string) => addCandidate(value)"
        >
          <el-option v-for="id in candidates" :key="id" :label="id" :value="id" />
        </el-select>
        <el-button :icon="Search" @click="goToJobs">继续选岗</el-button>
        <el-button :icon="Star" @click="goToShortlist">候选清单</el-button>
      </div>
    </div>

    <el-alert
      v-if="compareIds.length < 2"
      :title="
        compareIds.length === 0
          ? '还没有选择对比岗位，请先从岗位探索或候选清单中选择 2–3 个岗位。'
          : '再选择至少 1 个岗位才能并排比较。'
      "
      type="info"
      show-icon
      :closable="false"
    >
      <el-button size="small" @click="goToJobs">去选择岗位</el-button>
    </el-alert>

    <el-alert
      v-if="failedIds.length > 0"
      :title="`有 ${failedIds.length} 个岗位加载失败，其他岗位仍可正常对比`"
      type="error"
      show-icon
      :closable="false"
    >
      <el-button size="small" :icon="Refresh" @click="retryFailed">重试失败项</el-button>
    </el-alert>

    <!-- Skill settings drive the check section; they are never stored in the URL. -->
    <el-collapse v-model="skillSettingsOpen" class="settings-collapse">
      <el-collapse-item name="skills" title="我的技能标签设置（仅本浏览器，链接不会包含）">
        <SkillPicker />
      </el-collapse-item>
    </el-collapse>

    <template v-if="compareIds.length > 0">
      <div class="compare-scroll">
        <table class="compare-table">
          <thead>
            <tr>
              <th class="field-column">对比项</th>
              <th v-for="(id, index) in compareIds" :key="id" class="job-column">
                <div class="column-head">
                  <span class="column-title" :title="titleOf(id)">{{ titleOf(id) }}</span>
                  <span v-if="jobOf(id)" class="column-company">{{ jobOf(id)?.company }}</span>
                  <span v-else class="column-company muted">岗位 ID：{{ id }}</span>
                </div>
                <div class="column-actions">
                  <el-button
                    v-if="jobOf(id)"
                    size="small"
                    link
                    type="primary"
                    @click="openDetail(id)"
                  >
                    详情
                  </el-button>
                  <el-select
                    v-if="candidates.length > 0"
                    size="small"
                    placeholder="替换为"
                    class="replace-select"
                    :model-value="undefined"
                    @update:model-value="(value: string) => replaceColumn(index, value)"
                  >
                    <el-option v-for="cid in candidates" :key="cid" :label="cid" :value="cid" />
                  </el-select>
                  <el-button size="small" link type="danger" :icon="Delete" @click="removeColumn(id)">
                    移除
                  </el-button>
                </div>
                <div class="column-actions">
                  <JobActions :job-id="id" />
                </div>
              </th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="row in comparisonRows" :key="row.key">
              <th class="field-column">{{ row.label }}</th>
              <td v-for="id in compareIds" :key="`${row.key}-${id}`">
                <template v-if="recordOf(id)?.status === 'loading' || !recordOf(id)">
                  <el-skeleton :rows="1" animated />
                </template>
                <template v-else-if="recordOf(id)?.status === 'not_found'">
                  <span class="cell-state warning">当前数据中未找到该岗位记录</span>
                </template>
                <template v-else-if="recordOf(id)?.status === 'error'">
                  <span class="cell-state error">{{ recordOf(id)?.errorMessage }}</span>
                </template>
                <template v-else-if="jobOf(id)">
                  <span :class="{ 'cell-muted': !row.value(jobOf(id)!) }">
                    {{ row.value(jobOf(id)!) }}
                  </span>
                </template>
              </td>
            </tr>
            <tr>
              <th class="field-column">原始来源</th>
              <td v-for="id in compareIds" :key="`source-${id}`">
                <el-link
                  v-if="sourceUrlOf(id)"
                  :href="sourceUrlOf(id) ?? undefined"
                  target="_blank"
                  rel="noopener noreferrer"
                  type="primary"
                  :underline="false"
                >
                  <el-icon><Link /></el-icon>
                  打开原始招聘链接
                </el-link>
                <span v-else-if="jobOf(id)" class="cell-muted">未提供可打开的来源链接</span>
                <span v-else class="cell-muted">—</span>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- Skill tag check -->
      <section class="skill-check-section">
        <div class="section-head">
          <h2 class="section-title">技能标签核对</h2>
          <span class="section-note">
            只比较岗位已标注的标签与你勾选的标签；标签覆盖有限，不推断熟练度、必需程度或录用结果。
          </span>
        </div>

        <div class="skill-check-grid">
          <el-card
            v-for="id in compareIds"
            :key="`check-${id}`"
            shadow="never"
            class="skill-check-card"
          >
            <div class="check-head">{{ titleOf(id) }}</div>

            <template v-if="!jobOf(id)">
              <p class="check-state muted">岗位信息加载中或不可用，暂不能核对标签。</p>
            </template>
            <template v-else-if="skillChecks[id]?.status === 'not_set'">
              <p class="check-state muted">
                尚未设置“我已掌握的标签”，请在页面上方设置后再核对。
              </p>
            </template>
            <template v-else-if="skillChecks[id]?.status === 'no_job_skills'">
              <p class="check-state muted">当前样本暂无技能标签，无法核对。</p>
            </template>
            <template v-else>
              <div class="check-row">
                <span class="check-label">
                  已勾选的标签（{{ skillChecks[id]?.matched.length ?? 0 }}）
                </span>
                <div v-if="(skillChecks[id]?.matched.length ?? 0) > 0" class="check-tags">
                  <el-tag
                    v-for="name in skillChecks[id]?.matched"
                    :key="`matched-${name}`"
                    type="success"
                    size="small"
                    effect="light"
                  >
                    {{ name }}
                  </el-tag>
                </div>
                <span v-else class="check-state muted">本岗位标签中没有你已勾选的项</span>
              </div>

              <div class="check-row">
                <span class="check-label">
                  待核对的岗位标签（{{ skillChecks[id]?.pending.length ?? 0 }}）
                </span>
                <div v-if="(skillChecks[id]?.pending.length ?? 0) > 0" class="check-tags">
                  <el-tag
                    v-for="name in skillChecks[id]?.pending"
                    :key="`pending-${name}`"
                    type="info"
                    size="small"
                    effect="plain"
                  >
                    {{ name }}
                  </el-tag>
                </div>
                <span v-else class="check-state muted">岗位已标注的标签都在你的勾选范围内</span>
              </div>

              <p class="check-footnote">
                岗位共标注 {{ jobOf(id)?.skills.length ?? 0 }} 项标签，以上结果只覆盖这些既有标签。
              </p>
            </template>
          </el-card>
        </div>
      </section>

      <p class="page-footnote">
        已加载 {{ loadedCount }} / {{ compareIds.length }} 个岗位。对比地址只包含岗位标识，
        不包含你的收藏与个人技能设置。
        <el-icon><Collection /></el-icon>
      </p>
    </template>

    <JobDetailDrawer v-model:visible="drawerVisible" :job-id="selectedJobId" />
  </div>
</template>

<style scoped>
.compare-view {
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
  max-width: 820px;
}

.head-actions {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
}

.add-select {
  width: 200px;
}

.settings-collapse {
  background: #ffffff;
  border: 1px solid #e4e7ed;
  border-radius: 8px;
  padding: 0 16px;
}

.compare-scroll {
  overflow-x: auto;
  background: #ffffff;
  border: 1px solid #e4e7ed;
  border-radius: 8px;
  -webkit-overflow-scrolling: touch;
}

.compare-table {
  width: 100%;
  min-width: 720px;
  border-collapse: collapse;
  table-layout: fixed;
}

.compare-table th,
.compare-table td {
  border-bottom: 1px solid #ebeef5;
  border-right: 1px solid #f2f4f7;
  padding: 12px 14px;
  vertical-align: top;
  text-align: left;
  font-size: 13px;
  color: #303133;
  word-break: break-word;
}

.compare-table thead th {
  background: #f8fafd;
  border-bottom: 1px solid #e4e7ed;
}

.field-column {
  width: 150px;
  background: #fafbfc;
  font-weight: 600;
  color: #606266;
  font-size: 13px;
}

.job-column {
  min-width: 220px;
}

.column-head {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.column-title {
  font-size: 15px;
  font-weight: 700;
  color: #1f2d3d;
  line-height: 1.4;
}

.column-company {
  font-size: 12px;
  color: #909399;
}

.column-company.muted {
  color: #c0c4cc;
}

.column-actions {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
  margin-top: 6px;
}

.replace-select {
  width: 110px;
}

.cell-state {
  font-size: 12px;
}

.cell-state.warning {
  color: #e6a23c;
}

.cell-state.error {
  color: #f56c6c;
}

.cell-muted {
  color: #909399;
}

.skill-check-section {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.section-head {
  display: flex;
  align-items: baseline;
  gap: 12px;
  flex-wrap: wrap;
}

.section-title {
  margin: 0;
  font-size: 16px;
  font-weight: 700;
  color: #1f2d3d;
}

.section-note {
  font-size: 12px;
  color: #909399;
}

.skill-check-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
  gap: 12px;
}

.skill-check-card {
  border-radius: 8px;
  border: 1px solid #e4e7ed;
  background: #ffffff;
}

.check-head {
  font-size: 14px;
  font-weight: 600;
  color: #1f2d3d;
  margin-bottom: 10px;
}

.check-row {
  display: flex;
  flex-direction: column;
  gap: 6px;
  margin-bottom: 10px;
}

.check-label {
  font-size: 12px;
  color: #606266;
  font-weight: 600;
}

.check-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.check-state {
  margin: 0;
  font-size: 13px;
  line-height: 1.6;
}

.check-state.muted {
  color: #909399;
  font-size: 12px;
}

.check-footnote {
  margin: 0;
  font-size: 11px;
  color: #c0c4cc;
}

.page-footnote {
  display: flex;
  align-items: center;
  gap: 6px;
  margin: 0;
  font-size: 12px;
  color: #909399;
}

@media (max-width: 1024px) {
  .compare-table {
    min-width: 660px;
  }
}

@media (max-width: 640px) {
  .add-select {
    width: 160px;
  }

  .compare-table th,
  .compare-table td {
    padding: 10px 10px;
  }
}
</style>
