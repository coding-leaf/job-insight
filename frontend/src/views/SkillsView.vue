<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import { Cpu, Document } from '@element-plus/icons-vue'
import { useFilterStore } from '@/stores/filter'
import { getSkillsTop } from '@/api/stats'
import { useECharts } from '@/composables/useECharts'
import type { SkillsTopData } from '@/types/job'

const filterStore = useFilterStore()

const loading = ref(false)
const skillsData = ref<SkillsTopData | null>(null)

const barChartRef = ref<HTMLElement | null>(null)
const radarChartRef = ref<HTMLElement | null>(null)

const {
  setOption: setBarOption,
  showLoading: showBarLoading,
  hideLoading: hideBarLoading,
  clear: clearBar
} = useECharts(barChartRef)

const {
  setOption: setRadarOption,
  showLoading: showRadarLoading,
  hideLoading: hideRadarLoading,
  clear: clearRadar
} = useECharts(radarChartRef)

function customProgressColor(percentage: number): string {
  if (percentage < 15) return '#909399'
  if (percentage < 35) return '#1890ff'
  return '#722ed1'
}

async function loadData() {
  loading.value = true
  showBarLoading()
  showRadarLoading()
  try {
    const data = await getSkillsTop({
      ...filterStore.activeParams,
      limit: 20
    })
    skillsData.value = data
    renderBarChart(data)
    renderRadarChart(data)
  } catch (err) {
    console.error('Failed to load skills top data', err)
  } finally {
    loading.value = false
    hideBarLoading()
    hideRadarLoading()
  }
}

function renderBarChart(data: SkillsTopData) {
  if (!barChartRef.value) return

  const skills = [...(data.skills || [])].reverse()
  if (skills.length === 0) {
    clearBar()
    return
  }
  const names = skills.map((s) => s.skill_name)
  const annotatedRatios = skills.map((s) =>
    s.ratio_annotated !== null ? Number((s.ratio_annotated * 100).toFixed(1)) : 0
  )
  const totalRatios = skills.map((s) =>
    s.ratio_total !== null ? Number((s.ratio_total * 100).toFixed(1)) : 0
  )

  const option = {
    title: {
      text: 'Top 20 核心技能渗透率 (严格双分母口径对比)',
      subtext: `打标基准分母 L = ${data.tagged_skills_jobs} 组 | 全量样本分母 N = ${data.total_jobs} 组`,
      left: 10,
      top: 10,
      textStyle: { fontSize: 15, fontWeight: 600, color: '#1f2d3d' },
      subtextStyle: { fontSize: 12, color: '#909399' }
    },
    tooltip: {
      trigger: 'axis',
      axisPointer: { type: 'shadow' },
      formatter: (params: any) => {
        const item = skills[params[0].dataIndex]
        if (!item) return ''
        const annPct = item.ratio_annotated !== null ? (item.ratio_annotated * 100).toFixed(1) : '-'
        const totPct = item.ratio_total !== null ? (item.ratio_total * 100).toFixed(1) : '-'
        return `
          <div style="font-weight: 600; margin-bottom: 6px;">技能: ${item.skill_name}</div>
          <div>频次 (至少出现1次): <strong>${item.count.toLocaleString()}</strong> 组岗位</div>
          <div style="color: #722ed1; margin-top: 4px;">
            • 打标基准比例: <strong>${annPct}%</strong> (${item.count} / ${data.tagged_skills_jobs})
          </div>
          <div style="color: #1890ff;">
            • 全量基准比例: <strong>${totPct}%</strong> (${item.count} / ${data.total_jobs})
          </div>
        `
      }
    },
    legend: {
      data: ['打标基准比 (K/L)', '全量基准比 (K/N)'],
      top: 12,
      right: 20,
      textStyle: { fontSize: 12, color: '#606266' }
    },
    grid: {
      top: 70,
      left: 110,
      right: 50,
      bottom: 30
    },
    xAxis: {
      type: 'value',
      name: '渗透率 (%)',
      nameTextStyle: { color: '#909399', fontSize: 11 },
      splitLine: { lineStyle: { type: 'dashed', color: '#f0f0f0' } }
    },
    yAxis: {
      type: 'category',
      data: names,
      axisLabel: { fontSize: 12, color: '#606266' }
    },
    series: [
      {
        name: '打标基准比 (K/L)',
        type: 'bar',
        barWidth: 10,
        itemStyle: {
          borderRadius: [0, 3, 3, 0],
          color: '#722ed1'
        },
        data: annotatedRatios
      },
      {
        name: '全量基准比 (K/N)',
        type: 'bar',
        barWidth: 10,
        itemStyle: {
          borderRadius: [0, 3, 3, 0],
          color: '#1890ff'
        },
        data: totalRatios
      }
    ]
  }

  setBarOption(option, true)
}

function renderRadarChart(data: SkillsTopData) {
  if (!radarChartRef.value) return

  const topSkills = (data.skills || []).slice(0, 8)
  if (topSkills.length < 3) {
    // If fewer than 3 skills, radar chart cannot form a polygon
    clearRadar()
    return
  }

  const indicator = topSkills.map((s) => ({
    name: s.skill_name,
    max: 100
  }))

  const annotatedValues = topSkills.map((s) =>
    s.ratio_annotated !== null ? Number((s.ratio_annotated * 100).toFixed(1)) : 0
  )
  const totalValues = topSkills.map((s) =>
    s.ratio_total !== null ? Number((s.ratio_total * 100).toFixed(1)) : 0
  )

  const option = {
    title: {
      text: '核心技能综合渗透画像 (Top 8)',
      subtext: '百分比 (0 - 100%)',
      left: 'center',
      top: 10,
      textStyle: { fontSize: 15, fontWeight: 600, color: '#1f2d3d' },
      subtextStyle: { fontSize: 12, color: '#909399' }
    },
    tooltip: {
      trigger: 'item'
    },
    legend: {
      data: ['打标基准', '全量基准'],
      bottom: 10,
      textStyle: { fontSize: 12, color: '#606266' }
    },
    radar: {
      indicator,
      radius: '62%',
      center: ['50%', '52%'],
      splitArea: {
        show: true,
        areaStyle: {
          color: ['rgba(250, 250, 250, 0.3)', 'rgba(235, 240, 250, 0.5)']
        }
      }
    },
    series: [
      {
        name: '技能雷达画像',
        type: 'radar',
        data: [
          {
            value: annotatedValues,
            name: '打标基准',
            itemStyle: { color: '#722ed1' },
            areaStyle: { color: 'rgba(114, 46, 209, 0.2)' }
          },
          {
            value: totalValues,
            name: '全量基准',
            itemStyle: { color: '#1890ff' },
            areaStyle: { color: 'rgba(24, 144, 255, 0.2)' }
          }
        ]
      }
    ]
  }

  setRadarOption(option, true)
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
  <div class="skills-view">
    <!-- Methodology Banner -->
    <el-card shadow="never" class="methodology-card">
      <div class="methodology-banner">
        <el-icon class="method-icon"><Document /></el-icon>
        <div class="method-text">
          <div class="method-title">技能口径与统计分母说明 (严格遵循《JobInsight 统计口径》)</div>
          <div class="method-desc">
            1. <strong>严格双分母呈现</strong>：<strong>打标基准比 K(s)/L</strong>（以含技能标签岗位组为分母）与 <strong>全量基准比 K(s)/N</strong>（以当前全部筛选岗位组为分母）必须并列呈现，严禁混淆分母。<br />
            2. 同一组内的多份证据、重复技能均只计一次频次，技能标签展开不虚增岗位数。<br />
            3. 当前快照下无标签不代表岗位不需要技能，24 个字典技能不等于行业全貌，本系统杜绝断言“最佳技能路线”。
          </div>
        </div>
      </div>
    </el-card>

    <!-- Top Metric Overview Banner -->
    <div class="skills-kpi-bar">
      <div class="kpi-item">
        <span class="label">当前匹配岗位总量 (N)</span>
        <span class="val">{{ skillsData?.total_jobs?.toLocaleString() ?? 0 }} 组</span>
      </div>
      <div class="kpi-item">
        <span class="label">含技能标签岗位组 (L)</span>
        <span class="val text-purple">{{ skillsData?.tagged_skills_jobs?.toLocaleString() ?? 0 }} 组</span>
      </div>
      <div class="kpi-item">
        <span class="label">样本技能标注覆盖率 (L/N)</span>
        <span class="val text-blue">
          {{
            skillsData?.coverage_ratio !== null && skillsData?.coverage_ratio !== undefined
              ? (skillsData.coverage_ratio * 100).toFixed(1)
              : '0.0'
          }}%
        </span>
      </div>
      <div class="kpi-item">
        <span class="label">呈现核心技能数</span>
        <span class="val text-green">{{ skillsData?.skills?.length ?? 0 }} 项</span>
      </div>
    </div>

    <!-- Charts Row -->
    <div class="charts-row">
      <!-- Top 20 Bar Chart -->
      <el-card shadow="never" class="chart-card bar-card">
        <div ref="barChartRef" class="chart-container" />
      </el-card>

      <!-- Radar Chart -->
      <el-card shadow="never" class="chart-card radar-card">
        <div ref="radarChartRef" class="chart-container" />
      </el-card>
    </div>

    <!-- Skills Table -->
    <el-card shadow="never" class="table-card">
      <template #header>
        <div class="table-header">
          <div class="table-title">
            <el-icon><Cpu /></el-icon>
            <span>Top 技能出现频次与双分母渗透透视表</span>
          </div>
          <el-tag size="small" type="primary" effect="plain">
            共 {{ skillsData?.skills?.length ?? 0 }} 项核心技能
          </el-tag>
        </div>
      </template>

      <el-table
        :data="skillsData?.skills || []"
        stripe
        border
        style="width: 100%"
        v-loading="loading"
      >
        <el-table-column type="index" label="排名" width="70" align="center" />

        <el-table-column prop="skill_name" label="核心技能 / 技术栈" min-width="160">
          <template #default="{ row }">
            <el-tag type="primary" size="default" effect="light" class="skill-badge">
              {{ row.skill_name }}
            </el-tag>
          </template>
        </el-table-column>

        <el-table-column prop="count" label="命中岗位组频次 (K)" min-width="140" align="right">
          <template #default="{ row }">
            <span class="font-bold">{{ row.count.toLocaleString() }}</span> 组
          </template>
        </el-table-column>

        <el-table-column prop="ratio_annotated" label="打标基准比 (K / L)" min-width="160" align="right">
          <template #default="{ row }">
            <div class="ratio-cell text-purple">
              <span class="ratio-pct">
                {{ row.ratio_annotated !== null ? (row.ratio_annotated * 100).toFixed(1) : '-' }}%
              </span>
              <span class="ratio-sub">({{ row.count }} / {{ skillsData?.tagged_skills_jobs }})</span>
            </div>
          </template>
        </el-table-column>

        <el-table-column prop="ratio_total" label="全量基准比 (K / N)" min-width="160" align="right">
          <template #default="{ row }">
            <div class="ratio-cell text-blue">
              <span class="ratio-pct">
                {{ row.ratio_total !== null ? (row.ratio_total * 100).toFixed(1) : '-' }}%
              </span>
              <span class="ratio-sub">({{ row.count }} / {{ skillsData?.total_jobs }})</span>
            </div>
          </template>
        </el-table-column>

        <el-table-column label="渗透深度" min-width="160">
          <template #default="{ row }">
            <el-progress
              :percentage="
                row.ratio_annotated !== null
                  ? Math.min(100, Math.round(row.ratio_annotated * 100))
                  : 0
              "
              :color="customProgressColor"
              :stroke-width="8"
            />
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<style scoped>
.skills-view {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.methodology-card {
  border-radius: 8px;
  background: #fdf6ec;
  border: 1px solid #faecd8;
}

.methodology-banner {
  display: flex;
  align-items: flex-start;
  gap: 12px;
}

.method-icon {
  font-size: 22px;
  color: #e6a23c;
  margin-top: 2px;
}

.method-title {
  font-size: 14px;
  font-weight: 700;
  color: #1f2d3d;
  margin-bottom: 6px;
}

.method-desc {
  font-size: 12px;
  color: #595959;
  line-height: 1.6;
}

.skills-kpi-bar {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
  background: #ffffff;
  padding: 16px 24px;
  border-radius: 8px;
  border: 1px solid #e4e7ed;
}

@media (max-width: 800px) {
  .skills-kpi-bar {
    grid-template-columns: repeat(2, 1fr);
  }
}

.kpi-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.label {
  font-size: 12px;
  color: #8c8c8c;
}

.val {
  font-size: 20px;
  font-weight: 700;
  color: #262626;
}

.text-purple {
  color: #722ed1;
}

.text-blue {
  color: #1890ff;
}

.text-green {
  color: #52c41a;
}

.charts-row {
  display: grid;
  grid-template-columns: 60% 40%;
  gap: 20px;
}

@media (max-width: 1024px) {
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
  height: 520px;
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

.skill-badge {
  font-weight: 600;
}

.font-bold {
  font-weight: 700;
  color: #262626;
}

.ratio-cell {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
}

.ratio-pct {
  font-weight: 700;
  font-size: 14px;
}

.ratio-sub {
  font-size: 11px;
  opacity: 0.75;
}
</style>
