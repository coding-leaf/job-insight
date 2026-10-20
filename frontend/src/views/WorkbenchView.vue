<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import {
  Search,
  Star,
  Operation,
  Collection,
  Refresh,
  ArrowRight,
  DataAnalysis,
  TrendCharts,
  Cpu,
  Select
} from '@element-plus/icons-vue'
import { getOptions } from '@/api/meta'
import { useFilterStore } from '@/stores/filter'
import { useWorkspaceStore } from '@/stores/workspace'
import SkillPicker from '@/components/SkillPicker.vue'
import type { MetaOptionsData } from '@/types/job'

const router = useRouter()
const filterStore = useFilterStore()
const workspace = useWorkspaceStore()

const loadingOptions = ref(false)
const optionsError = ref<string | null>(null)
const options = ref<MetaOptionsData>({ categories: [], provinces: [], education_levels: [] })

const quick = ref({
  category: filterStore.category as string | undefined,
  province: filterStore.province as string | undefined,
  education: filterStore.education as string | undefined
})

const savedCount = computed(() => workspace.savedJobIds.length)
const compareCount = computed(() => workspace.compareJobIds.length)

const steps = [
  { title: '筛选', desc: '按类别、省份、学历要求和薪资区间缩小范围' },
  { title: '保存', desc: '收藏感兴趣的岗位，组成自己的候选清单' },
  { title: '对比', desc: '选择 2–3 个岗位并排查看事实差异' },
  { title: '核对', desc: '核对岗位已标注的技能标签，并打开原始来源' }
]

async function loadOptions() {
  loadingOptions.value = true
  optionsError.value = null
  try {
    options.value = await getOptions()
  } catch (err) {
    console.error('Failed to load meta options', err)
    optionsError.value = '可选项加载失败，无法使用快捷条件'
  } finally {
    loadingOptions.value = false
  }
}

function startExploring() {
  const query: Record<string, string> = {}
  if (quick.value.category) query.category = quick.value.category
  if (quick.value.province) query.province = quick.value.province
  if (quick.value.education) query.education = quick.value.education
  void router.push({ path: '/jobs', query })
}

function goToShortlist() {
  void router.push({ path: '/shortlist' })
}

function goToCompare() {
  void router.push({
    path: compareCount.value > 0 ? '/compare' : '/jobs',
    query: compareCount.value > 0 ? { ids: [...workspace.compareJobIds] } : {}
  })
}

function goToAnalysis(path: string) {
  void router.push({ path })
}

onMounted(() => {
  void loadOptions()
})
</script>

<template>
  <div class="workbench-view">
    <!-- Hero -->
    <section class="hero">
      <div class="hero-text">
        <h1 class="hero-title">选择适合进一步了解的岗位</h1>
        <p class="hero-desc">
          这里汇总招聘样本记录。你可以按条件筛选岗位、保存候选、比较事实差异，并核对岗位已标注的技能标签。
          样本不代表当前仍在招聘，最终请以原始来源页面为准。
        </p>
        <div class="hero-actions">
          <el-button type="primary" size="large" :icon="Search" @click="startExploring">
            开始选岗
          </el-button>
          <el-button size="large" :icon="Collection" @click="goToShortlist">
            查看候选清单
          </el-button>
        </div>
      </div>
      <div class="hero-metrics">
        <button type="button" class="metric-card" @click="goToShortlist">
          <el-icon class="metric-icon"><Star /></el-icon>
          <span class="metric-value">{{ savedCount }}</span>
          <span class="metric-label">我的候选</span>
        </button>
        <button type="button" class="metric-card" @click="goToCompare">
          <el-icon class="metric-icon"><Operation /></el-icon>
          <span class="metric-value">{{ compareCount }}</span>
          <span class="metric-label">当前对比</span>
        </button>
      </div>
    </section>

    <!-- Quick conditions -->
    <el-card shadow="never" class="quick-card">
      <div class="card-head">
        <div class="card-title">
          <el-icon><Search /></el-icon>
          <span>按条件查找岗位</span>
        </div>
        <span class="card-hint">条件会带入岗位探索页面，也可以在那里继续调整</span>
      </div>

      <el-alert
        v-if="optionsError"
        :title="optionsError"
        type="warning"
        :closable="false"
        show-icon
        class="options-alert"
      >
        <el-button size="small" :icon="Refresh" @click="loadOptions">重试</el-button>
      </el-alert>

      <div class="quick-form">
        <div class="quick-item">
          <span class="quick-label">岗位类别</span>
          <el-select
            v-model="quick.category"
            placeholder="全部类别"
            clearable
            filterable
            :loading="loadingOptions"
            class="quick-select"
          >
            <el-option v-for="item in options.categories" :key="item" :label="item" :value="item" />
          </el-select>
        </div>

        <div class="quick-item">
          <span class="quick-label">省份</span>
          <el-select
            v-model="quick.province"
            placeholder="全部省份"
            clearable
            filterable
            :loading="loadingOptions"
            class="quick-select"
          >
            <el-option v-for="item in options.provinces" :key="item" :label="item" :value="item" />
          </el-select>
        </div>

        <div class="quick-item">
          <span class="quick-label">岗位学历要求</span>
          <el-select
            v-model="quick.education"
            placeholder="全部学历要求"
            clearable
            filterable
            :loading="loadingOptions"
            class="quick-select"
          >
            <el-option
              v-for="item in options.education_levels"
              :key="item"
              :label="item"
              :value="item"
            />
          </el-select>
        </div>

        <el-button type="primary" :icon="Search" @click="startExploring">查看岗位</el-button>
      </div>
    </el-card>

    <!-- Usage guide -->
    <el-card shadow="never" class="guide-card">
      <div class="card-head">
        <div class="card-title">
          <el-icon><Select /></el-icon>
          <span>如何使用</span>
        </div>
      </div>
      <ol class="step-list">
        <li v-for="(step, index) in steps" :key="step.title" class="step-item">
          <span class="step-index">{{ index + 1 }}</span>
          <div class="step-body">
            <span class="step-title">{{ step.title }}</span>
            <span class="step-desc">{{ step.desc }}</span>
          </div>
        </li>
      </ol>
    </el-card>

    <!-- Skill settings -->
    <el-card shadow="never" class="skills-card">
      <SkillPicker />
    </el-card>

    <!-- Analysis entries -->
    <section class="analysis-section">
      <h2 class="section-title">辅助分析</h2>
      <div class="analysis-grid">
        <button type="button" class="analysis-card" @click="goToAnalysis('/overview')">
          <el-icon class="analysis-icon icon-overview"><DataAnalysis /></el-icon>
          <div class="analysis-body">
            <span class="analysis-title">样本概况</span>
            <span class="analysis-desc">当前样本的岗位数量、类别构成与薪资覆盖率</span>
          </div>
          <el-icon class="analysis-arrow"><ArrowRight /></el-icon>
        </button>

        <button type="button" class="analysis-card" @click="goToAnalysis('/salary')">
          <el-icon class="analysis-icon icon-salary"><TrendCharts /></el-icon>
          <div class="analysis-body">
            <span class="analysis-title">薪资与地域</span>
            <span class="analysis-desc">按类别与省份查看薪资分布，含低样本预警</span>
          </div>
          <el-icon class="analysis-arrow"><ArrowRight /></el-icon>
        </button>

        <button type="button" class="analysis-card" @click="goToAnalysis('/skills')">
          <el-icon class="analysis-icon icon-skills"><Cpu /></el-icon>
          <div class="analysis-body">
            <span class="analysis-title">技能标签</span>
            <span class="analysis-desc">技能标签出现频次与双分母覆盖率说明</span>
          </div>
          <el-icon class="analysis-arrow"><ArrowRight /></el-icon>
        </button>
      </div>
    </section>
  </div>
</template>

<style scoped>
.workbench-view {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.hero {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 24px;
  background: linear-gradient(135deg, #ffffff 0%, #f0f7ff 100%);
  border: 1px solid #e4e7ed;
  border-radius: 10px;
  padding: 28px 32px;
  flex-wrap: wrap;
}

.hero-text {
  flex: 1;
  min-width: 280px;
}

.hero-title {
  margin: 0 0 10px;
  font-size: 26px;
  font-weight: 700;
  color: #1f2d3d;
  letter-spacing: -0.4px;
}

.hero-desc {
  margin: 0 0 20px;
  font-size: 14px;
  line-height: 1.7;
  color: #606266;
  max-width: 720px;
}

.hero-actions {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}

.hero-metrics {
  display: flex;
  gap: 12px;
}

.metric-card {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 2px;
  width: 128px;
  padding: 18px 12px;
  background: #ffffff;
  border: 1px solid #d9ecff;
  border-radius: 10px;
  cursor: pointer;
  transition: all 0.2s ease;
  font-family: inherit;
}

.metric-card:hover {
  border-color: #409eff;
  box-shadow: 0 4px 12px rgba(64, 158, 255, 0.16);
  transform: translateY(-2px);
}

.metric-icon {
  font-size: 20px;
  color: #409eff;
}

.metric-value {
  font-size: 28px;
  font-weight: 700;
  color: #1f2d3d;
  font-variant-numeric: tabular-nums;
  line-height: 1.2;
}

.metric-label {
  font-size: 12px;
  color: #909399;
}

.quick-card,
.guide-card,
.skills-card {
  border-radius: 8px;
  border: 1px solid #e4e7ed;
  background: #ffffff;
}

.card-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  flex-wrap: wrap;
  margin-bottom: 16px;
}

.card-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 15px;
  font-weight: 600;
  color: #1f2d3d;
}

.card-hint {
  font-size: 12px;
  color: #909399;
}

.options-alert {
  margin-bottom: 12px;
}

.quick-form {
  display: flex;
  align-items: center;
  gap: 16px;
  flex-wrap: wrap;
}

.quick-item {
  display: flex;
  align-items: center;
  gap: 8px;
}

.quick-label {
  font-size: 13px;
  color: #606266;
  white-space: nowrap;
}

.quick-select {
  width: 180px;
}

.step-list {
  list-style: none;
  margin: 0;
  padding: 0;
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 16px;
}

.step-item {
  display: flex;
  align-items: flex-start;
  gap: 10px;
  background: #f8fafd;
  border: 1px solid #eef2f7;
  border-radius: 8px;
  padding: 14px;
}

.step-index {
  width: 24px;
  height: 24px;
  border-radius: 50%;
  background: #409eff;
  color: #ffffff;
  font-size: 12px;
  font-weight: 700;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.step-body {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.step-title {
  font-size: 14px;
  font-weight: 600;
  color: #1f2d3d;
}

.step-desc {
  font-size: 12px;
  color: #909399;
  line-height: 1.5;
}

.section-title {
  margin: 0 0 14px;
  font-size: 16px;
  font-weight: 700;
  color: #1f2d3d;
}

.analysis-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 16px;
}

.analysis-card {
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 18px;
  background: #ffffff;
  border: 1px solid #e4e7ed;
  border-radius: 8px;
  cursor: pointer;
  text-align: left;
  font-family: inherit;
  transition: all 0.2s ease;
}

.analysis-card:hover {
  border-color: #409eff;
  box-shadow: 0 4px 12px rgba(64, 158, 255, 0.12);
  transform: translateY(-2px);
}

.analysis-icon {
  width: 44px;
  height: 44px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;
  flex-shrink: 0;
}

.icon-overview {
  background: #e6f7ff;
  color: #1890ff;
}

.icon-salary {
  background: #fff7e6;
  color: #fa8c16;
}

.icon-skills {
  background: #f9f0ff;
  color: #722ed1;
}

.analysis-body {
  display: flex;
  flex-direction: column;
  gap: 4px;
  flex: 1;
  min-width: 0;
}

.analysis-title {
  font-size: 14px;
  font-weight: 600;
  color: #1f2d3d;
}

.analysis-desc {
  font-size: 12px;
  color: #909399;
  line-height: 1.5;
}

.analysis-arrow {
  color: #c0c4cc;
  font-size: 16px;
}

.analysis-card:hover .analysis-arrow {
  color: #409eff;
}

@media (max-width: 1100px) {
  .step-list {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }

  .analysis-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 640px) {
  .hero {
    padding: 20px;
  }

  .hero-title {
    font-size: 22px;
  }

  .hero-metrics {
    width: 100%;
  }

  .metric-card {
    flex: 1;
  }

  .step-list {
    grid-template-columns: 1fr;
  }

  .quick-select {
    width: 100%;
  }

  .quick-item {
    flex: 1 1 100%;
  }
}
</style>
