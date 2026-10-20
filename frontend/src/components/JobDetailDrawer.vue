<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import axios from 'axios'
import {
  Briefcase,
  Location,
  School,
  Files,
  Discount,
  Link,
  WarningFilled,
  CircleCheckFilled
} from '@element-plus/icons-vue'
import { getJobDetail } from '@/api/jobs'
import JobActions from '@/components/JobActions.vue'
import type { JobItem } from '@/types/job'
import { toSafeExternalUrl } from '@/utils/jobDisplay'

interface Props {
  visible: boolean
  jobId: string | null
}

const props = defineProps<Props>()
const emit = defineEmits<{
  (e: 'update:visible', value: boolean): void
}>()

const loading = ref(false)
const job = ref<JobItem | null>(null)
const loadError = ref<string | null>(null)
const sourceUrl = computed(() => toSafeExternalUrl(job.value?.source_url))
let requestToken = 0

watch(
  () => [props.visible, props.jobId],
  ([isVisible, id]) => {
    if (isVisible && typeof id === 'string' && id) {
      void fetchJob(id)
    } else if (!isVisible) {
      requestToken += 1
      job.value = null
      loadError.value = null
      loading.value = false
    }
  }
)

async function fetchJob(id: string) {
  const token = ++requestToken
  loading.value = true
  loadError.value = null
  // Never show the previous record while the newly selected one is loading.
  if (job.value?.id !== id) job.value = null
  try {
    const data = await getJobDetail(id, { silentError: true })
    if (token !== requestToken) return
    job.value = data
  } catch (err) {
    if (token !== requestToken) return
    job.value = null
    loadError.value =
      axios.isAxiosError(err) && err.response?.status === 404
        ? '当前数据中未找到该岗位记录'
        : '岗位详情加载失败，请稍后重试'
  } finally {
    if (token === requestToken) loading.value = false
  }
}

function handleClose() {
  emit('update:visible', false)
}
</script>

<template>
  <el-drawer
    :model-value="visible"
    title="岗位详情与来源"
    size="680px"
    destroy-on-close
    class="job-detail-drawer"
    @update:model-value="emit('update:visible', $event)"
  >
    <div v-loading="loading" class="drawer-content">
      <el-alert
        v-if="loadError"
        :title="loadError"
        type="error"
        :closable="false"
        show-icon
        class="load-error"
      >
        <el-button v-if="jobId" size="small" @click="fetchJob(jobId)">重试</el-button>
      </el-alert>

      <template v-if="job">
        <!-- Header Info -->
        <div class="job-header">
          <div class="job-title-row">
            <h2 class="job-title">{{ job.title }}</h2>
            <el-tag
              v-if="job.job_category"
              type="primary"
              effect="light"
              size="large"
              class="category-tag"
            >
              {{ job.job_category }}
            </el-tag>
            <el-tag v-else size="small" type="info" effect="plain">未分类</el-tag>
          </div>

          <div class="company-row">
            <span class="company-name">{{ job.company }}</span>
            <el-tag v-if="job.company_type" size="small" type="info">{{ job.company_type }}</el-tag>
            <el-tag v-if="job.company_size" size="small" type="info">{{ job.company_size }}</el-tag>
          </div>

          <div class="salary-highlight">
            <span class="salary-display">{{ job.salary_display || '薪资未注明' }}</span>
            <span
              v-if="job.salary_eligible_for_midpoint && job.salary_midpoint !== null"
              class="midpoint-badge"
            >
              区间中点（元/月）: <strong>{{ job.salary_midpoint.toLocaleString() }}</strong>
            </span>
            <span v-else class="midpoint-excluded">
              <el-icon><WarningFilled /></el-icon>
              {{ job.salary_exclude_reason || '区间不完整，无法计算中点' }}
            </span>
          </div>

          <div class="job-actions-row">
            <JobActions :job-id="job.id" variant="button" />
          </div>
        </div>

        <el-divider />

        <!-- Key Meta Properties -->
        <div class="section-title">
          <el-icon><Briefcase /></el-icon>
          <span>岗位基本信息</span>
        </div>

        <el-descriptions :column="2" border size="default" class="meta-descriptions">
          <el-descriptions-item label="工作地点">
            <el-icon class="desc-icon"><Location /></el-icon>
            {{ job.work_location || '未注明' }}
            <span v-if="job.province" class="sub-location">
              ({{ job.province }} · {{ job.city || '城市未注明' }})
            </span>
          </el-descriptions-item>

          <el-descriptions-item label="岗位学历要求">
            <el-icon class="desc-icon"><School /></el-icon>
            {{ job.education_requirement || '未注明' }}
            <span
              v-if="job.education_min_code !== null && job.education_min_code !== undefined"
              class="sub-val"
            >
              (代码: {{ job.education_min_code }})
            </span>
          </el-descriptions-item>

          <el-descriptions-item label="经验要求">
            {{ job.experience_requirement || '未注明' }}
            <span
              v-if="job.experience_min_years !== null && job.experience_min_years !== undefined"
              class="sub-val"
            >
              ({{ job.experience_min_years }} 年 / {{ job.experience_status || '未注明' }})
            </span>
          </el-descriptions-item>

          <el-descriptions-item label="专业要求">
            {{ job.major_requirement || '未注明' }}
          </el-descriptions-item>

          <el-descriptions-item label="招聘人数">
            {{ job.recruitment_headcount ? `${job.recruitment_headcount} 人` : '未注明' }}
          </el-descriptions-item>

          <el-descriptions-item label="发布时间">
            {{ job.published_at || '未注明' }}
          </el-descriptions-item>

          <el-descriptions-item label="分类来源">
            {{ job.category_source || '未注明' }}
          </el-descriptions-item>

          <el-descriptions-item label="月薪范围（元/月）">
            <template v-if="job.salary_min_monthly !== null && job.salary_max_monthly !== null">
              ¥{{ job.salary_min_monthly }} - ¥{{ job.salary_max_monthly }}
            </template>
            <template v-else>
              未注明有效月薪边界
            </template>
          </el-descriptions-item>
        </el-descriptions>

        <!-- Skills & Provenance -->
        <div class="section-title mt-4">
          <el-icon><Discount /></el-icon>
          <span>技能标签与来源依据</span>
          <el-tag size="small" type="success" effect="plain" class="ml-2">
            共 {{ job.skills.length }} 项标签
          </el-tag>
        </div>

        <div v-if="job.skills.length > 0" class="skills-provenance-list">
          <div v-for="skill in job.skills" :key="skill.skill_name" class="skill-card">
            <div class="skill-head">
              <el-tag type="primary" effect="dark" size="default">
                {{ skill.skill_name }}
              </el-tag>
              <span class="evidence-count">{{ skill.provenance.length }} 条依据引用</span>
            </div>
            <div class="provenance-items">
              <div
                v-for="(prov, idx) in skill.provenance"
                :key="idx"
                class="provenance-item"
              >
                <div class="prov-origin">
                  <el-icon><CircleCheckFilled /></el-icon>
                  <span>来源字段: <code>{{ prov.origin }}</code></span>
                </div>
                <div class="prov-evidence">
                  “{{ prov.evidence }}”
                </div>
              </div>
            </div>
          </div>
        </div>
        <div v-else class="empty-skills-tip">
          <el-empty
            description="当前样本暂无技能标签，无法核对"
            :image-size="60"
          />
        </div>

        <!-- Source records -->
        <div class="section-title mt-4">
          <el-icon><Files /></el-icon>
          <span>原始来源记录</span>
        </div>

        <div class="audit-card">
          <div class="audit-row">
            <span class="audit-label">岗位组代表 ID:</span>
            <code class="audit-code">{{ job.id }}</code>
          </div>
          <div class="audit-row">
            <span class="audit-label">合并来源记录数:</span>
            <el-tag :type="job.source_ids.length > 1 ? 'warning' : 'info'" size="small">
              {{ job.source_ids.length }} 条原始记录
            </el-tag>
          </div>
          <div v-if="job.source_ids.length > 1" class="audit-sources">
            <span class="audit-label">关联来源 ID:</span>
            <div class="source-id-tags">
              <el-tag
                v-for="sid in job.source_ids"
                :key="sid"
                size="small"
                type="info"
                effect="plain"
              >
                {{ sid }}
              </el-tag>
            </div>
          </div>
          <div v-if="sourceUrl" class="audit-row">
            <span class="audit-label">原始招聘链接:</span>
            <el-link
              :href="sourceUrl"
              target="_blank"
              rel="noopener noreferrer"
              type="primary"
              :underline="false"
              class="source-link"
            >
              <el-icon><Link /></el-icon>
              <span>{{ sourceUrl }}</span>
            </el-link>
          </div>
          <div v-else class="audit-row">
            <span class="audit-label">原始招聘链接:</span>
            <span class="text-muted-small">未提供可打开的来源链接</span>
          </div>
          <p class="audit-tip">
            来源链接由招聘方发布，当前状态与是否仍在招聘请以原始页面为准。
          </p>
        </div>

        <!-- Full Job Description -->
        <div class="section-title mt-4">
          <el-icon><Files /></el-icon>
          <span>岗位正文（来源原文）</span>
        </div>

        <div class="description-box">
          <pre class="desc-text">{{ job.description || '来源未提供岗位正文；其他字段与来源仍可查看' }}</pre>
        </div>
      </template>

      <template v-else-if="!loading && !loadError">
        <el-empty description="当前数据中未找到该岗位记录" />
      </template>
    </div>

    <template #footer>
      <el-button @click="handleClose">关闭</el-button>
    </template>
  </el-drawer>
</template>

<style scoped>
.drawer-content {
  padding: 4px 8px;
}

.job-header {
  background: #f8fafd;
  padding: 16px;
  border-radius: 8px;
  border: 1px solid #e9eef7;
}

.job-title-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}

.job-title {
  margin: 0;
  font-size: 20px;
  font-weight: 700;
  color: #1f2d3d;
  line-height: 1.3;
}

.company-row {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-top: 8px;
}

.company-name {
  font-size: 15px;
  font-weight: 600;
  color: #4b5563;
}

.salary-highlight {
  margin-top: 14px;
  display: flex;
  align-items: baseline;
  gap: 14px;
  flex-wrap: wrap;
}

.salary-display {
  font-size: 22px;
  font-weight: 800;
  color: #ff6a00;
  letter-spacing: -0.5px;
}

.midpoint-badge {
  font-size: 13px;
  color: #0284c7;
  background: #e0f2fe;
  padding: 3px 8px;
  border-radius: 4px;
}

.midpoint-badge strong {
  font-size: 14px;
}

.midpoint-excluded {
  font-size: 12px;
  color: #909399;
  display: flex;
  align-items: center;
  gap: 4px;
}

.section-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 15px;
  font-weight: 700;
  color: #1f2d3d;
  margin-bottom: 12px;
}

.mt-4 {
  margin-top: 24px;
}

.ml-2 {
  margin-left: 8px;
}

.meta-descriptions {
  margin-top: 8px;
}

.desc-icon {
  margin-right: 4px;
  vertical-align: middle;
}

.sub-location,
.sub-val {
  color: #909399;
  font-size: 12px;
  margin-left: 4px;
}

.skills-provenance-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.skill-card {
  background: #fbfcfe;
  border: 1px solid #e4e7ed;
  border-radius: 6px;
  padding: 12px;
}

.skill-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 8px;
}

.evidence-count {
  font-size: 12px;
  color: #909399;
}

.provenance-items {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.provenance-item {
  background: #ffffff;
  padding: 8px 12px;
  border-radius: 4px;
  border-left: 3px solid #409eff;
  font-size: 12px;
}

.prov-origin {
  display: flex;
  align-items: center;
  gap: 4px;
  color: #606266;
  font-size: 11px;
  margin-bottom: 3px;
}

.prov-origin code {
  color: #409eff;
  background: #f0f7ff;
  padding: 1px 4px;
  border-radius: 2px;
}

.prov-evidence {
  color: #303133;
  line-height: 1.4;
  font-family: monospace;
}

.audit-card {
  background: #f9fafb;
  border: 1px dashed #dcdfe6;
  border-radius: 6px;
  padding: 14px;
  display: flex;
  flex-direction: column;
  gap: 10px;
  font-size: 13px;
}

.audit-row {
  display: flex;
  align-items: center;
  gap: 8px;
}

.audit-label {
  color: #606266;
  min-width: 130px;
}

.audit-code {
  background: #eef2f7;
  padding: 2px 6px;
  border-radius: 4px;
  color: #2b3a4a;
  font-weight: 600;
  font-size: 12px;
}

.audit-sources {
  display: flex;
  gap: 8px;
  align-items: flex-start;
}

.source-id-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.source-link {
  font-size: 12px;
  word-break: break-all;
  display: flex;
  align-items: center;
  gap: 4px;
}

.description-box {
  background: #fdfdfd;
  border: 1px solid #e4e7ed;
  border-radius: 6px;
  padding: 14px;
  max-height: 280px;
  overflow-y: auto;
}

.desc-text {
  margin: 0;
  white-space: pre-wrap;
  word-break: break-word;
  font-family: inherit;
  font-size: 13px;
  line-height: 1.6;
  color: #4b5563;
}

.empty-skills-tip {
  padding: 16px 0;
}

.load-error {
  margin-bottom: 16px;
}

.job-actions-row {
  margin-top: 14px;
  padding-top: 12px;
  border-top: 1px dashed #dbe6f5;
}

.text-muted-small {
  font-size: 12px;
  color: #909399;
}

.audit-tip {
  margin: 0;
  font-size: 11px;
  color: #909399;
  line-height: 1.5;
}
</style>
