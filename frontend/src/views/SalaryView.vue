<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import { Warning, TrendCharts, Location } from '@element-plus/icons-vue'
import { useFilterStore } from '@/stores/filter'
import { getSalaryByCategory, getSalaryByRegion } from '@/api/stats'
import { useECharts } from '@/composables/useECharts'
import type { CategorySalaryStat, RegionSalaryStat } from '@/types/job'

const filterStore = useFilterStore()

const loading = ref(false)
const categoryStats = ref<CategorySalaryStat[]>([])
const regionStats = ref<RegionSalaryStat[]>([])

const categoryChartRef = ref<HTMLElement | null>(null)
const regionChartRef = ref<HTMLElement | null>(null)

const {
  setOption: setCategoryOption,
  showLoading: showCategoryLoading,
  hideLoading: hideCategoryLoading,
  clear: clearCategory
} = useECharts(categoryChartRef)

const {
  setOption: setRegionOption,
  showLoading: showRegionLoading,
  hideLoading: hideRegionLoading,
  clear: clearRegion
} = useECharts(regionChartRef)

async function loadData() {
  loading.value = true
  showCategoryLoading()
  showRegionLoading()
  try {
    const [catData, regData] = await Promise.all([
      getSalaryByCategory(filterStore.activeParams),
      getSalaryByRegion(filterStore.activeParams)
    ])
    categoryStats.value = catData
    regionStats.value = regData

    renderCategoryChart(catData)
    renderRegionChart(regData)
  } catch (err) {
    console.error('Failed to load salary stats', err)
  } finally {
    loading.value = false
    hideCategoryLoading()
    hideRegionLoading()
  }
}

function renderCategoryChart(data: CategorySalaryStat[]) {
  if (!categoryChartRef.value) return

  if (!data || data.length === 0) {
    clearCategory()
    return
  }

  // Filter items with valid median or show as 0 with tooltip
  // Sort by median ascending for horizontal bar chart (so highest is at the top)
  const sorted = [...data].reverse()

  const categories = sorted.map((item) => item.category)
  const medians = sorted.map((item) => (item.median !== null ? item.median : 0))

  const option = {
    title: {
      text: '岗位类别薪资中位数排行 (元/月)',
      subtext: '样本量 N < 5 明确标记低样本预警，不参与正式位次',
      left: 10,
      top: 10,
      textStyle: { fontSize: 15, fontWeight: 600, color: '#1f2d3d' },
      subtextStyle: { fontSize: 12, color: '#909399' }
    },
    tooltip: {
      trigger: 'axis',
      axisPointer: { type: 'shadow' },
      formatter: (params: any) => {
        const item = sorted[params[0].dataIndex]
        if (!item) return ''
        return `
          <div style="font-weight: 600; margin-bottom: 6px;">${item.category}</div>
          <div>薪资中位数: <strong>${item.median !== null && item.median !== undefined ? `¥${item.median.toLocaleString()}` : '暂无有效中点'}</strong></div>
          <div>25分位数 (P25): ${item.p25 !== null && item.p25 !== undefined ? `¥${item.p25.toLocaleString()}` : '-'}</div>
          <div>75分位数 (P75): ${item.p75 !== null && item.p75 !== undefined ? `¥${item.p75.toLocaleString()}` : '-'}</div>
          <div>总样本量: ${item.sample_count} 组 | 有效核算: ${item.eligible_count} 组</div>
          ${item.is_low_sample ? '<div style="color: #e6a23c; margin-top: 4px;">⚠️ 低样本量预警 (N < 5)</div>' : ''}
          ${item.rank ? `<div style="color: #409eff;">行业位次: 第 ${item.rank} 名</div>` : ''}
        `
      }
    },
    grid: {
      top: 70,
      left: 130,
      right: 50,
      bottom: 30
    },
    xAxis: {
      type: 'value',
      name: '元/月',
      nameTextStyle: { color: '#909399', fontSize: 11 },
      splitLine: { lineStyle: { type: 'dashed', color: '#f0f0f0' } }
    },
    yAxis: {
      type: 'category',
      data: categories,
      axisLabel: {
        fontSize: 12,
        color: '#606266',
        formatter: (val: string) => {
          const raw = sorted.find((s) => s.category === val)
          if (raw?.is_low_sample) {
            return `⚠️ ${val}`
          }
          return val
        }
      }
    },
    series: [
      {
        name: '薪资中位数',
        type: 'bar',
        barWidth: 18,
        itemStyle: {
          borderRadius: [0, 4, 4, 0],
          color: (params: any) => {
            const raw = sorted[params.dataIndex]
            if (raw?.is_low_sample) return '#dcdfe6'
            return '#1890ff'
          }
        },
        label: {
          show: true,
          position: 'right',
          formatter: (params: any) => {
            const raw = sorted[params.dataIndex]
            if (!raw || raw.median === null || raw.median === undefined) return '暂无有效薪资'
            return `¥${raw.median.toLocaleString()} (N=${raw.sample_count})`
          },
          fontSize: 11,
          color: '#606266'
        },
        data: medians
      }
    ]
  }

  setCategoryOption(option, true)
}

function renderRegionChart(data: RegionSalaryStat[]) {
  if (!regionChartRef.value) return

  // Top 15 provinces with highest medians or all valid
  const ranked = data
    .filter((d) => d.province !== '未注明' && d.median !== null)
    .slice(0, 15)
    .reverse()

  if (ranked.length === 0) {
    clearRegion()
    return
  }

  const provinces = ranked.map((d) => d.province)
  const medians = ranked.map((d) => d.median || 0)

  const option = {
    title: {
      text: '重点省级行政区薪资中位数排行 (Top 15)',
      subtext: '仅核算有效闭区间岗位中点，按降序排列',
      left: 10,
      top: 10,
      textStyle: { fontSize: 15, fontWeight: 600, color: '#1f2d3d' },
      subtextStyle: { fontSize: 12, color: '#909399' }
    },
    tooltip: {
      trigger: 'axis',
      axisPointer: { type: 'shadow' },
      formatter: (params: any) => {
        const item = ranked[params[0].dataIndex]
        if (!item) return ''
        return `
          <div style="font-weight: 600; margin-bottom: 6px;">${item.province}</div>
          <div>薪资中位数: <strong>${item.median !== null && item.median !== undefined ? `¥${item.median.toLocaleString()} / 月` : '-'}</strong></div>
          <div>25分位数 (P25): ${item.p25 !== null && item.p25 !== undefined ? `¥${item.p25.toLocaleString()}` : '-'}</div>
          <div>75分位数 (P75): ${item.p75 !== null && item.p75 !== undefined ? `¥${item.p75.toLocaleString()}` : '-'}</div>
          <div>总样本: ${item.sample_count} 组 | 有效核算: ${item.eligible_count} 组</div>
          ${item.is_low_sample ? '<div style="color: #e6a23c; margin-top: 4px;">⚠️ 样本量不足5组</div>' : ''}
          ${item.rank ? `<div style="color: #52c41a;">地域位次: 第 ${item.rank} 名</div>` : ''}
        `
      }
    },
    grid: {
      top: 70,
      left: 110,
      right: 50,
      bottom: 30
    },
    xAxis: {
      type: 'value',
      name: '元/月',
      nameTextStyle: { color: '#909399', fontSize: 11 },
      splitLine: { lineStyle: { type: 'dashed', color: '#f0f0f0' } }
    },
    yAxis: {
      type: 'category',
      data: provinces,
      axisLabel: { fontSize: 12, color: '#606266' }
    },
    series: [
      {
        name: '省份中位数',
        type: 'bar',
        barWidth: 18,
        itemStyle: {
          borderRadius: [0, 4, 4, 0],
          color: (params: any) => {
            const raw = ranked[params.dataIndex]
            if (raw?.is_low_sample) return '#dcdfe6'
            return '#52c41a'
          }
        },
        label: {
          show: true,
          position: 'right',
          formatter: (params: any) => {
            const raw = ranked[params.dataIndex]
            if (!raw || raw.median === null || raw.median === undefined) return '暂无有效薪资'
            return `¥${raw.median.toLocaleString()} (N=${raw.eligible_count})`
          },
          fontSize: 11,
          color: '#606266'
        },
        data: medians
      }
    ]
  }

  setRegionOption(option, true)
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
  <div class="salary-view">
    <!-- Two Main Charts Row -->
    <div class="charts-row">
      <!-- Category Ranking Chart -->
      <el-card shadow="never" class="chart-card">
        <div ref="categoryChartRef" class="chart-container" />
      </el-card>

      <!-- Region Ranking Chart -->
      <el-card shadow="never" class="chart-card">
        <div ref="regionChartRef" class="chart-container" />
      </el-card>
    </div>

    <!-- Detailed Statistics Table -->
    <el-card shadow="never" class="table-card">
      <template #header>
        <div class="table-header">
          <div class="table-title">
            <el-icon><TrendCharts /></el-icon>
            <span>技术类别薪资四分位与样本量透视表</span>
          </div>
          <el-tag size="small" type="info">共 {{ categoryStats.length }} 个岗位类别</el-tag>
        </div>
      </template>

      <el-table :data="categoryStats" stripe border style="width: 100%" v-loading="loading">
        <el-table-column prop="rank" label="位次" width="70" align="center">
          <template #default="{ row }">
            <el-tag v-if="row.rank" size="small" :type="row.rank <= 3 ? 'danger' : 'info'" effect="plain">
              {{ row.rank }}
            </el-tag>
            <span v-else class="text-muted">-</span>
          </template>
        </el-table-column>

        <el-table-column prop="category" label="岗位类别" min-width="140">
          <template #default="{ row }">
            <span class="font-bold">{{ row.category }}</span>
            <el-tag v-if="row.is_low_sample" type="warning" size="small" class="ml-2">
              低样本预警
            </el-tag>
          </template>
        </el-table-column>

        <el-table-column prop="median" label="薪资中位数 (元/月)" min-width="150" align="right">
          <template #default="{ row }">
            <span v-if="row.median !== null" class="salary-highlight">
              ¥{{ row.median.toLocaleString() }}
            </span>
            <span v-else class="text-muted">暂无有效中点</span>
          </template>
        </el-table-column>

        <el-table-column prop="p25" label="25分位数 (P25)" min-width="130" align="right">
          <template #default="{ row }">
            {{ row.p25 !== null ? `¥${row.p25.toLocaleString()}` : '-' }}
          </template>
        </el-table-column>

        <el-table-column prop="p75" label="75分位数 (P75)" min-width="130" align="right">
          <template #default="{ row }">
            {{ row.p75 !== null ? `¥${row.p75.toLocaleString()}` : '-' }}
          </template>
        </el-table-column>

        <el-table-column prop="eligible_count" label="有效核算样本" width="130" align="center">
          <template #default="{ row }">
            <el-tag size="small" type="success" effect="plain">{{ row.eligible_count }} 组</el-tag>
          </template>
        </el-table-column>

        <el-table-column prop="sample_count" label="总样本量" width="110" align="center">
          <template #default="{ row }">
            {{ row.sample_count }} 组
          </template>
        </el-table-column>

        <el-table-column label="样本状态" width="130" align="center">
          <template #default="{ row }">
            <el-tag v-if="row.is_low_sample" type="warning" size="small">
              <el-icon><Warning /></el-icon> N &lt; 5 预警
            </el-tag>
            <el-tag v-else type="success" size="small">样本充足</el-tag>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- Region Breakdown Table -->
    <el-card shadow="never" class="table-card">
      <template #header>
        <div class="table-header">
          <div class="table-title">
            <el-icon><Location /></el-icon>
            <span>省级行政区薪资核算透视表</span>
          </div>
          <el-tag size="small" type="info">共 {{ regionStats.length }} 个地区</el-tag>
        </div>
      </template>

      <el-table :data="regionStats" stripe border style="width: 100%" max-height="400" v-loading="loading">
        <el-table-column prop="rank" label="位次" width="70" align="center">
          <template #default="{ row }">
            <el-tag v-if="row.rank" size="small" :type="row.rank <= 3 ? 'danger' : 'info'" effect="plain">
              {{ row.rank }}
            </el-tag>
            <span v-else class="text-muted">-</span>
          </template>
        </el-table-column>

        <el-table-column prop="province" label="省份/地区" min-width="140">
          <template #default="{ row }">
            <span class="font-bold">{{ row.province }}</span>
            <el-tag v-if="row.is_low_sample" type="warning" size="small" class="ml-2">
              低样本
            </el-tag>
          </template>
        </el-table-column>

        <el-table-column prop="median" label="薪资中位数 (元/月)" min-width="150" align="right">
          <template #default="{ row }">
            <span v-if="row.median !== null" class="salary-highlight">
              ¥{{ row.median.toLocaleString() }}
            </span>
            <span v-else class="text-muted">暂无有效样本</span>
          </template>
        </el-table-column>

        <el-table-column prop="p25" label="25分位数 (P25)" min-width="130" align="right">
          <template #default="{ row }">
            {{ row.p25 !== null ? `¥${row.p25.toLocaleString()}` : '-' }}
          </template>
        </el-table-column>

        <el-table-column prop="p75" label="75分位数 (P75)" min-width="130" align="right">
          <template #default="{ row }">
            {{ row.p75 !== null ? `¥${row.p75.toLocaleString()}` : '-' }}
          </template>
        </el-table-column>

        <el-table-column prop="eligible_count" label="有效核算样本" width="130" align="center">
          <template #default="{ row }">
            <el-tag size="small" type="success" effect="plain">{{ row.eligible_count }} 组</el-tag>
          </template>
        </el-table-column>

        <el-table-column prop="sample_count" label="总样本量" width="110" align="center">
          <template #default="{ row }">
            {{ row.sample_count }} 组
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<style scoped>
.salary-view {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.charts-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
}

@media (max-width: 992px) {
  .charts-row {
    grid-template-columns: 1fr;
  }
}

.chart-card,
.table-card {
  border-radius: 8px;
  border: 1px solid #e4e7ed;
  background: #ffffff;
}

.chart-container {
  height: 480px;
  width: 100%;
}

.table-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.table-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 15px;
  font-weight: 600;
  color: #1f2d3d;
}

.salary-highlight {
  font-weight: 700;
  color: #ff6a00;
}

.text-muted {
  color: #909399;
}

.font-bold {
  font-weight: 600;
}

.ml-2 {
  margin-left: 8px;
}
</style>
