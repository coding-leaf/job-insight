<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import {
  DataLine,
  Coin,
  CollectionTag,
  CopyDocument,
  ArrowRight,
  TrendCharts,
  Cpu,
  Search,
  InfoFilled
} from '@element-plus/icons-vue'
import { useFilterStore } from '@/stores/filter'
import { getOverview } from '@/api/overview'
import { useECharts } from '@/composables/useECharts'
import type { OverviewData } from '@/types/job'

const router = useRouter()
const filterStore = useFilterStore()

const loading = ref(false)
const overviewData = ref<OverviewData | null>(null)

const donutChartRef = ref<HTMLElement | null>(null)
const {
  setOption: setDonutOption,
  showLoading: showDonutLoading,
  hideLoading: hideDonutLoading,
  clear: clearDonut
} = useECharts(donutChartRef)

async function loadData() {
  loading.value = true
  showDonutLoading()
  try {
    const data = await getOverview(filterStore.activeParams)
    overviewData.value = data
    renderDonutChart(data)
  } catch (err) {
    console.error('Failed to load overview data', err)
  } finally {
    loading.value = false
    hideDonutLoading()
  }
}

function renderDonutChart(data: OverviewData) {
  if (!donutChartRef.value) return

  const chartData = (data.category_breakdown || []).map((item) => ({
    name: item.category,
    value: item.count,
    ratio: (item.ratio * 100).toFixed(1)
  }))

  if (chartData.length === 0) {
    clearDonut()
    return
  }

  const option = {
    title: {
      text: '技术岗位类别构成分布',
      subtext: `当前样本岗位组总量: ${data.total_jobs.toLocaleString()} 组`,
      left: 'center',
      top: 10,
      textStyle: {
        fontSize: 16,
        fontWeight: 600,
        color: '#1f2d3d'
      },
      subtextStyle: {
        fontSize: 12,
        color: '#909399'
      }
    },
    tooltip: {
      trigger: 'item',
      formatter: (params: any) => {
        return `
          <div style="font-weight: 600; margin-bottom: 4px;">${params.name}</div>
          <div>样本数量: <strong>${params.value.toLocaleString()}</strong> 组</div>
          <div>占比比例: <strong>${params.data.ratio}%</strong></div>
        `
      }
    },
    legend: {
      type: 'scroll',
      orient: 'horizontal',
      bottom: 10,
      textStyle: {
        fontSize: 12,
        color: '#606266'
      }
    },
    series: [
      {
        name: '技术类别',
        type: 'pie',
        radius: ['42%', '70%'],
        center: ['50%', '52%'],
        avoidLabelOverlap: true,
        itemStyle: {
          borderRadius: 6,
          borderColor: '#ffffff',
          borderWidth: 2
        },
        label: {
          show: true,
          formatter: '{b}: {d}%',
          fontSize: 11
        },
        emphasis: {
          label: {
            show: true,
            fontSize: 13,
            fontWeight: 'bold'
          },
          itemStyle: {
            shadowBlur: 10,
            shadowOffsetX: 0,
            shadowColor: 'rgba(0, 0, 0, 0.2)'
          }
        },
        data: chartData
      }
    ]
  }

  setDonutOption(option, true)
}

function navigateTo(path: string) {
  router.push({ path, query: filterStore.toQuery() })
}

watch(
  () => filterStore.activeParams,
  () => {
    loadData()
  },
  { deep: true }
)

onMounted(() => {
  loadData()
})
</script>

<template>
  <div class="overview-view">
    <!-- Filter Notice Banner when filters applied -->
    <div v-if="filterStore.hasActiveFilters" class="filter-notice">
      <el-alert
        title="当前处于全局切片过滤模式，大盘指标与图表已实时限制在筛选范围内"
        type="info"
        show-icon
        :closable="false"
      />
    </div>

    <!-- 4 Core Metric Cards -->
    <div class="kpi-grid">
      <!-- Total Jobs -->
      <el-card shadow="hover" class="kpi-card" :body-style="{ padding: '20px' }">
        <div class="kpi-inner">
          <div class="kpi-icon kpi-blue">
            <el-icon><DataLine /></el-icon>
          </div>
          <div class="kpi-meta">
            <span class="kpi-label">招聘岗位样本</span>
            <div class="kpi-value-row">
              <span class="kpi-value">{{ overviewData?.total_jobs?.toLocaleString() ?? '-' }}</span>
              <span class="kpi-unit">组</span>
            </div>
            <div class="kpi-footnote">
              按来源字段分组后的岗位记录
            </div>
          </div>
        </div>
      </el-card>

      <!-- Eligible Salary Jobs -->
      <el-card shadow="hover" class="kpi-card" :body-style="{ padding: '20px' }">
        <div class="kpi-inner">
          <div class="kpi-icon kpi-green">
            <el-icon><Coin /></el-icon>
          </div>
          <div class="kpi-meta">
            <span class="kpi-label">有效薪资核算样本</span>
            <div class="kpi-value-row">
              <span class="kpi-value">{{ overviewData?.eligible_salary_jobs?.toLocaleString() ?? '-' }}</span>
              <span class="kpi-unit">组</span>
            </div>
            <div class="kpi-footnote">
              占总样本 {{
                overviewData && overviewData.total_jobs > 0
                  ? ((overviewData.eligible_salary_jobs / overviewData.total_jobs) * 100).toFixed(1)
                  : 0
              }}%（排除缺失/倒置）
            </div>
          </div>
        </div>
      </el-card>

      <!-- Tagged Skills Jobs -->
      <el-card shadow="hover" class="kpi-card" :body-style="{ padding: '20px' }">
        <div class="kpi-inner">
          <div class="kpi-icon kpi-purple">
            <el-icon><CollectionTag /></el-icon>
          </div>
          <div class="kpi-meta">
            <span class="kpi-label">技能标签打标组数</span>
            <div class="kpi-value-row">
              <span class="kpi-value">{{ overviewData?.tagged_skills_jobs?.toLocaleString() ?? '-' }}</span>
              <span class="kpi-unit">组</span>
            </div>
            <div class="kpi-footnote">
              打标覆盖率 {{
                overviewData?.skill_coverage_ratio !== null && overviewData?.skill_coverage_ratio !== undefined
                  ? (overviewData.skill_coverage_ratio * 100).toFixed(1)
                  : '0.0'
              }}%
            </div>
          </div>
        </div>
      </el-card>

      <!-- Deduplicated Groups -->
      <el-card shadow="hover" class="kpi-card" :body-style="{ padding: '20px' }">
        <div class="kpi-inner">
          <div class="kpi-icon kpi-orange">
            <el-icon><CopyDocument /></el-icon>
          </div>
          <div class="kpi-meta">
            <span class="kpi-label">多源重复合并组</span>
            <div class="kpi-value-row">
              <span class="kpi-value">{{ overviewData?.duplicate_groups?.toLocaleString() ?? '-' }}</span>
              <span class="kpi-unit">组</span>
            </div>
            <div class="kpi-footnote">
              组内多条来源记录已合并，不重复计数
            </div>
          </div>
        </div>
      </el-card>
    </div>

    <!-- Middle Section: Salary Benchmark & Donut Breakdown -->
    <div class="dashboard-row">
      <!-- Benchmark Card -->
      <el-card shadow="never" class="benchmark-card">
        <template #header>
          <div class="card-header">
            <div class="header-left">
              <span class="title">样本薪资中位数</span>
              <el-tag size="small" type="success" effect="plain">大盘基准</el-tag>
            </div>
            <el-tooltip
              content="基于有效招聘月薪区间核算的中位数。"
              placement="top"
            >
              <el-icon class="help-icon"><InfoFilled /></el-icon>
            </el-tooltip>
          </div>
        </template>

        <div class="benchmark-body">
          <div class="benchmark-highlight">
            <span class="currency">¥</span>
            <span class="number">
              {{
                overviewData?.overall_salary_median !== null && overviewData?.overall_salary_median !== undefined
                  ? overviewData.overall_salary_median.toLocaleString()
                  : '暂无'
              }}
            </span>
            <span class="period">元 / 月</span>
          </div>

          <p class="benchmark-desc">
            反映当前筛选条件下公开月薪区间中点的中位数水平。
          </p>

          <div class="benchmark-details">
            <div class="detail-item">
              <span class="detail-label">有效核算样本数</span>
              <span class="detail-val">{{ overviewData?.eligible_salary_jobs?.toLocaleString() ?? 0 }} 组</span>
            </div>
            <div class="detail-item">
              <span class="detail-label">无效/未公开样本</span>
              <span class="detail-val">
                {{
                  overviewData
                    ? (overviewData.total_jobs - overviewData.eligible_salary_jobs).toLocaleString()
                    : 0
                }} 组
              </span>
            </div>
            <div class="detail-item">
              <span class="detail-label">统计覆盖率</span>
              <span class="detail-val">
                {{
                  overviewData && overviewData.total_jobs > 0
                    ? ((overviewData.eligible_salary_jobs / overviewData.total_jobs) * 100).toFixed(1)
                    : 0
                }}%
              </span>
            </div>
          </div>
        </div>
      </el-card>

      <!-- Donut Chart Card -->
      <el-card shadow="never" class="chart-card">
        <div ref="donutChartRef" class="chart-container" />
      </el-card>
    </div>

    <!-- Thematic Navigation Cards -->
    <div class="navigation-section">
      <h3 class="section-title">分析入口</h3>
      <div class="thematic-grid">
        <!-- Salary View Jump -->
        <div class="thematic-card" @click="navigateTo('/salary')">
          <div class="thematic-icon icon-salary">
            <el-icon><TrendCharts /></el-icon>
          </div>
          <div class="thematic-content">
            <h4 class="thematic-title">薪资与地域分布</h4>
            <p class="thematic-desc">
              按岗位类别与省份查看薪资分布，样本量不足 5 组时明确标记低样本预警。
            </p>
          </div>
          <div class="thematic-arrow">
            <el-icon><ArrowRight /></el-icon>
          </div>
        </div>

        <!-- Skills View Jump -->
        <div class="thematic-card" @click="navigateTo('/skills')">
          <div class="thematic-icon icon-skills">
            <el-icon><Cpu /></el-icon>
          </div>
          <div class="thematic-content">
            <h4 class="thematic-title">技能标签分析</h4>
            <p class="thematic-desc">
              技能标签出现频次与双分母覆盖率（打标基准 vs 全量基准），并说明标注覆盖范围。
            </p>
          </div>
          <div class="thematic-arrow">
            <el-icon><ArrowRight /></el-icon>
          </div>
        </div>

        <!-- Jobs View Jump -->
        <div class="thematic-card" @click="navigateTo('/jobs')">
          <div class="thematic-icon icon-jobs">
            <el-icon><Search /></el-icon>
          </div>
          <div class="thematic-content">
            <h4 class="thematic-title">岗位探索</h4>
            <p class="thematic-desc">
              按条件检索招聘样本中的岗位记录，可收藏候选、加入对比并查看来源。
            </p>
          </div>
          <div class="thematic-arrow">
            <el-icon><ArrowRight /></el-icon>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.overview-view {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.filter-notice {
  margin-bottom: -8px;
}

.kpi-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
}

@media (max-width: 1024px) {
  .kpi-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 640px) {
  .kpi-grid {
    grid-template-columns: 1fr;
  }
}

.kpi-card {
  border-radius: 8px;
  border: 1px solid #e4e7ed;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.kpi-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
}

.kpi-inner {
  display: flex;
  align-items: center;
  gap: 16px;
}

.kpi-icon {
  width: 54px;
  height: 54px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 26px;
  flex-shrink: 0;
}

.kpi-blue {
  background: #e6f7ff;
  color: #1890ff;
}

.kpi-green {
  background: #f6ffed;
  color: #52c41a;
}

.kpi-purple {
  background: #f9f0ff;
  color: #722ed1;
}

.kpi-orange {
  background: #fff7e6;
  color: #fa8c16;
}

.kpi-meta {
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.kpi-label {
  font-size: 13px;
  color: #8c8c8c;
  margin-bottom: 4px;
}

.kpi-value-row {
  display: flex;
  align-items: baseline;
  gap: 4px;
}

.kpi-value {
  font-size: 26px;
  font-weight: 700;
  color: #262626;
  line-height: 1.1;
  font-variant-numeric: tabular-nums;
}

.kpi-unit {
  font-size: 13px;
  color: #8c8c8c;
}

.kpi-footnote {
  font-size: 12px;
  color: #bfbfbf;
  margin-top: 4px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.dashboard-row {
  display: grid;
  grid-template-columns: 380px 1fr;
  gap: 20px;
}

@media (max-width: 992px) {
  .dashboard-row {
    grid-template-columns: 1fr;
  }
}

.benchmark-card,
.chart-card {
  border-radius: 8px;
  border: 1px solid #e4e7ed;
  background: #ffffff;
}

.card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 8px;
}

.title {
  font-size: 15px;
  font-weight: 600;
  color: #1f2d3d;
}

.help-icon {
  color: #909399;
  cursor: pointer;
}

.benchmark-body {
  padding: 10px 0;
}

.benchmark-highlight {
  display: flex;
  align-items: baseline;
  gap: 4px;
  margin-bottom: 12px;
}

.currency {
  font-size: 22px;
  font-weight: 700;
  color: #ff6a00;
}

.number {
  font-size: 38px;
  font-weight: 800;
  color: #ff6a00;
  line-height: 1;
  letter-spacing: -1px;
}

.period {
  font-size: 14px;
  color: #8c8c8c;
  margin-left: 6px;
}

.benchmark-desc {
  font-size: 13px;
  color: #595959;
  line-height: 1.6;
  margin-bottom: 20px;
}

.benchmark-details {
  border-top: 1px solid #f0f0f0;
  padding-top: 16px;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.detail-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 13px;
}

.detail-label {
  color: #8c8c8c;
}

.detail-val {
  font-weight: 600;
  color: #262626;
}

.chart-container {
  height: 380px;
  width: 100%;
}

.navigation-section {
  margin-top: 8px;
}

.section-title {
  font-size: 16px;
  font-weight: 700;
  color: #1f2d3d;
  margin: 0 0 16px 0;
}

.thematic-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16px;
}

@media (max-width: 900px) {
  .thematic-grid {
    grid-template-columns: 1fr;
  }
}

.thematic-card {
  background: #ffffff;
  border: 1px solid #e4e7ed;
  border-radius: 8px;
  padding: 20px;
  display: flex;
  align-items: center;
  gap: 16px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.thematic-card:hover {
  transform: translateY(-2px);
  border-color: #409eff;
  box-shadow: 0 4px 12px rgba(64, 158, 255, 0.12);
}

.thematic-icon {
  width: 48px;
  height: 48px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 22px;
  flex-shrink: 0;
}

.icon-salary {
  background: #e6f7ff;
  color: #1890ff;
}

.icon-skills {
  background: #f9f0ff;
  color: #722ed1;
}

.icon-jobs {
  background: #e6fffb;
  color: #13c2c2;
}

.thematic-content {
  flex: 1;
}

.thematic-title {
  font-size: 15px;
  font-weight: 600;
  color: #1f2d3d;
  margin: 0 0 6px 0;
}

.thematic-desc {
  font-size: 12px;
  color: #8c8c8c;
  line-height: 1.5;
  margin: 0;
}

.thematic-arrow {
  color: #bfbfbf;
  font-size: 16px;
  transition: transform 0.2s ease;
}

.thematic-card:hover .thematic-arrow {
  color: #409eff;
  transform: translateX(4px);
}
</style>
