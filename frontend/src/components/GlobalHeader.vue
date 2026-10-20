<script setup lang="ts">
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import {
  DataAnalysis,
  TrendCharts,
  Cpu,
  Search,
  House,
  Collection,
  ArrowDown
} from '@element-plus/icons-vue'
import { useWorkspaceStore } from '@/stores/workspace'
import { useFilterStore } from '@/stores/filter'

const route = useRoute()
const router = useRouter()
const workspace = useWorkspaceStore()
const filterStore = useFilterStore()

const FILTER_PATHS = ['/jobs', '/overview', '/salary', '/skills']

const primaryNav = [
  { path: '/workbench', label: '工作台', icon: House },
  { path: '/jobs', label: '岗位探索', icon: Search },
  { path: '/shortlist', label: '候选清单', icon: Collection }
]

const analysisNav = [
  { path: '/overview', label: '样本概况', icon: DataAnalysis },
  { path: '/salary', label: '薪资与地域', icon: TrendCharts },
  { path: '/skills', label: '技能标签', icon: Cpu }
]

// Carrying the analytical range between filtered pages is intentional; attaching it
// to the workbench, shortlist or comparison would imply a hidden filter.
const filterQuery = computed<Record<string, string>>(() =>
  FILTER_PATHS.includes(route.path) ? filterStore.toQuery() : {}
)

const isAnalysisActive = computed(() => analysisNav.some((item) => item.path === route.path))

function linkQuery(path: string) {
  return FILTER_PATHS.includes(path) ? filterQuery.value : {}
}
</script>

<template>
  <header class="global-header">
    <div class="header-container">
      <router-link to="/workbench" class="brand-area">
        <div class="brand-icon-wrapper">
          <el-icon :size="22" class="brand-icon"><DataAnalysis /></el-icon>
        </div>
        <div class="brand-info">
          <span class="brand-title">JobInsight</span>
          <span class="brand-subtitle">职薪洞察</span>
        </div>
      </router-link>

      <nav class="nav-links">
        <router-link
          v-for="item in primaryNav"
          :key="item.path"
          :to="{ path: item.path, query: linkQuery(item.path) }"
          class="nav-item"
          active-class="is-active"
        >
          <el-icon class="nav-item-icon"><component :is="item.icon" /></el-icon>
          <span class="nav-item-text">{{ item.label }}</span>
          <el-badge
            v-if="item.path === '/shortlist' && workspace.savedJobIds.length > 0"
            :value="workspace.savedJobIds.length"
            type="primary"
            class="nav-badge"
          />
        </router-link>

        <el-dropdown trigger="click" @command="(path: string) => router.push({ path, query: linkQuery(path) })">
          <span class="nav-item nav-dropdown" :class="{ 'is-active': isAnalysisActive }">
            <el-icon class="nav-item-icon"><DataAnalysis /></el-icon>
            <span class="nav-item-text">数据分析</span>
            <el-icon class="nav-caret"><ArrowDown /></el-icon>
          </span>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item
                v-for="item in analysisNav"
                :key="item.path"
                :command="item.path"
                :class="{ 'is-current': route.path === item.path }"
              >
                <el-icon><component :is="item.icon" /></el-icon>
                <span>{{ item.label }}</span>
              </el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
      </nav>

      <div class="header-actions">
        <el-tag type="info" effect="plain" class="sample-badge" round>
          <el-icon><DataAnalysis /></el-icon>
          <span>招聘样本数据</span>
        </el-tag>
      </div>
    </div>
  </header>
</template>

<style scoped>
.global-header {
  height: 60px;
  background: #ffffff;
  border-bottom: 1px solid #e4e7ed;
  position: sticky;
  top: 0;
  z-index: 1000;
  box-shadow: 0 1px 4px rgba(0, 21, 41, 0.04);
}

.header-container {
  max-width: 1440px;
  margin: 0 auto;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  padding: 0 24px;
}

.brand-area {
  display: flex;
  align-items: center;
  gap: 10px;
  cursor: pointer;
  user-select: none;
  text-decoration: none;
}

.brand-icon-wrapper {
  width: 36px;
  height: 36px;
  border-radius: 8px;
  background: linear-gradient(135deg, #1890ff 0%, #096dd9 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  color: #ffffff;
  box-shadow: 0 2px 6px rgba(24, 144, 255, 0.35);
  flex-shrink: 0;
}

.brand-info {
  display: flex;
  align-items: baseline;
  gap: 6px;
}

.brand-title {
  font-size: 18px;
  font-weight: 700;
  color: #1f2d3d;
  letter-spacing: -0.3px;
}

.brand-subtitle {
  font-size: 13px;
  font-weight: 600;
  color: #409eff;
}

.nav-links {
  display: flex;
  align-items: center;
  gap: 4px;
  height: 100%;
  flex-wrap: nowrap;
}

.nav-item {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 0 14px;
  height: 40px;
  border-radius: 6px;
  color: #606266;
  text-decoration: none;
  font-size: 14px;
  font-weight: 500;
  transition: all 0.2s ease;
  cursor: pointer;
  white-space: nowrap;
}

.nav-item:hover {
  color: #409eff;
  background: #f0f7ff;
}

.nav-item.is-active {
  color: #409eff;
  background: #ecf5ff;
  font-weight: 600;
}

.nav-item-icon {
  font-size: 16px;
}

.nav-caret {
  font-size: 12px;
  color: #909399;
}

.nav-dropdown {
  outline: none;
}

.nav-badge {
  margin-left: 2px;
}

.nav-badge :deep(.el-badge__content) {
  position: static;
  transform: none;
  font-size: 11px;
  padding: 0 5px;
  height: 16px;
  line-height: 16px;
}

.header-actions {
  display: flex;
  align-items: center;
  flex-shrink: 0;
}

.sample-badge {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
  padding: 6px 12px;
  background-color: #f4f4f5;
}

:deep(.el-dropdown-menu__item.is-current) {
  color: #409eff;
  font-weight: 600;
}

@media (max-width: 900px) {
  .header-container {
    padding: 0 12px;
    gap: 8px;
  }

  .nav-item {
    padding: 0 8px;
    font-size: 13px;
  }

  .header-actions {
    display: none;
  }
}

@media (max-width: 640px) {
  .brand-subtitle {
    display: none;
  }

  .brand-info {
    display: none;
  }

  .nav-item {
    padding: 0 6px;
    font-size: 12px;
    gap: 4px;
  }

  .nav-item-icon {
    display: none;
  }

  .nav-links {
    min-width: 0;
    overflow-x: auto;
    scrollbar-width: none;
  }

  .nav-links::-webkit-scrollbar {
    display: none;
  }
}
</style>
