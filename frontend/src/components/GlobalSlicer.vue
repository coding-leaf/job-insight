<script setup lang="ts">
import { ref, onMounted, computed, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { Filter, RefreshRight, Connection } from '@element-plus/icons-vue'
import { useFilterStore } from '@/stores/filter'
import { getOptions } from '@/api/meta'
import type { MetaOptionsData } from '@/types/job'

const route = useRoute()
const router = useRouter()
const filterStore = useFilterStore()

const defaultCategories = [
  '算法与人工智能',
  '数据分析与大数据',
  '软件开发',
  '软件测试',
  '运维与云平台',
  '网络与信息安全',
  '硬件与芯片',
  '通信',
  '技术支持与实施',
  '项目与产品',
  '其他明确岗位'
]

const defaultProvinces = [
  '北京市', '天津市', '河北省', '山西省', '内蒙古自治区',
  '辽宁省', '吉林省', '黑龙江省', '上海市', '江苏省',
  '浙江省', '安徽省', '福建省', '江西省', '山东省',
  '河南省', '湖北省', '湖南省', '广东省', '广西壮族自治区',
  '海南省', '重庆市', '四川省', '贵州省', '云南省',
  '西藏自治区', '陕西省', '甘肃省', '青海省', '宁夏回族自治区',
  '新疆维吾尔自治区'
]

const defaultEducationLevels = [
  '博士及以上',
  '硕士及以上',
  '本科及以上',
  '大专及以上',
  '不限'
]

// The slicer belongs to the exploration/analysis pages only; it must never
// silently filter the shortlist or the comparison.
const visible = computed(() => route.meta.showSlicer === true)

const loading = ref(false)
const loaded = ref(false)
const options = ref<MetaOptionsData>({
  categories: defaultCategories,
  provinces: defaultProvinces,
  education_levels: defaultEducationLevels
})

// Local model bound to dropdowns, keeping in sync with store
const selectedCategory = ref<string | undefined>(filterStore.category)
const selectedProvince = ref<string | undefined>(filterStore.province)
const selectedEducation = ref<string | undefined>(filterStore.education)

// Watch store changes (e.g. from router / back-forward navigation)
watch(
  () => [filterStore.category, filterStore.province, filterStore.education],
  ([cat, prov, edu]) => {
    selectedCategory.value = cat
    selectedProvince.value = prov
    selectedEducation.value = edu
  },
  { immediate: true }
)

const activeFilterCount = computed(() => {
  let count = 0
  if (selectedCategory.value) count++
  if (selectedProvince.value) count++
  if (selectedEducation.value) count++
  return count
})

async function fetchOptions() {
  if (loaded.value) return
  loading.value = true
  try {
    const data = await getOptions()
    options.value = data
    loaded.value = true
  } catch (err) {
    console.error('Failed to load filter options', err)
  } finally {
    loading.value = false
  }
}

watch(visible, (isVisible) => {
  if (isVisible) fetchOptions()
})

function applyFilters() {
  filterStore.setCategory(selectedCategory.value)
  filterStore.setProvince(selectedProvince.value)
  filterStore.setEducation(selectedEducation.value)

  const query: Record<string, string> = { ...route.query } as Record<string, string>

  if (selectedCategory.value) {
    query.category = selectedCategory.value
  } else {
    delete query.category
  }

  if (selectedProvince.value) {
    query.province = selectedProvince.value
  } else {
    delete query.province
  }

  if (selectedEducation.value) {
    query.education = selectedEducation.value
  } else {
    delete query.education
  }

  // Reset page to 1 when changing global filter on jobs view
  if (query.page) {
    delete query.page
  }

  router.replace({ query })
}

function handleCategoryChange(val: string) {
  selectedCategory.value = val || undefined
  applyFilters()
}

function handleProvinceChange(val: string) {
  selectedProvince.value = val || undefined
  applyFilters()
}

function handleEducationChange(val: string) {
  selectedEducation.value = val || undefined
  applyFilters()
}

function handleReset() {
  selectedCategory.value = undefined
  selectedProvince.value = undefined
  selectedEducation.value = undefined
  filterStore.resetFilters()

  const query: Record<string, string> = { ...route.query } as Record<string, string>
  delete query.category
  delete query.province
  delete query.education
  delete query.page

  router.replace({ query })
}

onMounted(() => {
  if (visible.value) fetchOptions()
})
</script>

<template>
  <div v-if="visible" class="global-slicer">
    <div class="slicer-container">
      <div class="slicer-label">
        <el-icon class="label-icon"><Filter /></el-icon>
        <span class="label-text">分析范围</span>
        <el-badge
          v-if="activeFilterCount > 0"
          :value="activeFilterCount"
          type="primary"
          class="filter-badge"
        />
      </div>

      <div class="slicer-controls">
        <!-- Category selector -->
        <div class="control-item">
          <span class="control-prefix">岗位类别</span>
          <el-select
            v-model="selectedCategory"
            placeholder="全部分类"
            clearable
            filterable
            size="default"
            style="width: 170px"
            :loading="loading"
            @change="handleCategoryChange"
          >
            <el-option
              v-for="item in options.categories"
              :key="item"
              :label="item"
              :value="item"
            />
          </el-select>
        </div>

        <!-- Province selector -->
        <div class="control-item">
          <span class="control-prefix">省份</span>
          <el-select
            v-model="selectedProvince"
            placeholder="全国全部省份"
            clearable
            filterable
            size="default"
            style="width: 170px"
            :loading="loading"
            @change="handleProvinceChange"
          >
            <el-option
              v-for="item in options.provinces"
              :key="item"
              :label="item"
              :value="item"
            />
          </el-select>
        </div>

        <!-- Education selector -->
        <div class="control-item">
          <span class="control-prefix">岗位学历要求</span>
          <el-select
            v-model="selectedEducation"
            placeholder="全部学历要求"
            clearable
            filterable
            size="default"
            style="width: 170px"
            :loading="loading"
            @change="handleEducationChange"
          >
            <el-option
              v-for="item in options.education_levels"
              :key="item"
              :label="item"
              :value="item"
            />
          </el-select>
        </div>

        <!-- Reset button -->
        <el-button
          plain
          size="default"
          :icon="RefreshRight"
          :disabled="activeFilterCount === 0"
          @click="handleReset"
        >
          重置条件
        </el-button>
      </div>

      <div class="slicer-tips">
        <el-tooltip
          content="条件自动与页面地址同步，刷新、前进后退或切换页面时保持当前分析范围；候选清单与岗位对比不受影响"
          placement="top"
        >
          <div class="sync-indicator">
            <el-icon class="sync-icon"><Connection /></el-icon>
            <span class="sync-text">地址已同步</span>
          </div>
        </el-tooltip>
      </div>
    </div>
  </div>
</template>

<style scoped>
.global-slicer {
  background: #fafafa;
  border-bottom: 1px solid #ebeef5;
  position: sticky;
  top: 60px;
  z-index: 900;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.03);
}

.slicer-container {
  max-width: 1440px;
  margin: 0 auto;
  padding: 10px 24px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 12px;
}

.slicer-label {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 600;
  font-size: 13px;
  color: #303133;
}

.label-icon {
  color: #409eff;
  font-size: 15px;
}

.label-text {
  letter-spacing: 0.2px;
}

.filter-badge :deep(.el-badge__content) {
  top: -2px;
}

.slicer-controls {
  display: flex;
  align-items: center;
  gap: 14px;
  flex-wrap: wrap;
}

.control-item {
  display: flex;
  align-items: center;
  gap: 6px;
}

.control-prefix {
  font-size: 12px;
  color: #606266;
  white-space: nowrap;
}

.slicer-tips {
  display: flex;
  align-items: center;
}

.sync-indicator {
  display: flex;
  align-items: center;
  gap: 5px;
  font-size: 12px;
  color: #909399;
  cursor: help;
  padding: 4px 8px;
  border-radius: 4px;
  background: #f0f2f5;
  transition: all 0.2s ease;
}

.sync-indicator:hover {
  color: #409eff;
  background: #ecf5ff;
}

.sync-icon {
  font-size: 13px;
}
</style>
