<script setup lang="ts">
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import {
  DataAnalysis,
  TrendCharts,
  Cpu,
  Search,
  InfoFilled
} from '@element-plus/icons-vue'

const route = useRoute()

const navItems = [
  { path: '/overview', label: '综合总览', icon: DataAnalysis },
  { path: '/salary', label: '薪资与地域', icon: TrendCharts },
  { path: '/skills', label: '技能图谱', icon: Cpu },
  { path: '/jobs', label: '岗位透视检索', icon: Search }
]

const currentQuery = computed(() => {
  return route.query
})
</script>

<template>
  <header class="global-header">
    <div class="header-container">
      <div class="brand-area">
        <div class="brand-icon-wrapper">
          <el-icon :size="22" class="brand-icon"><DataAnalysis /></el-icon>
        </div>
        <div class="brand-info">
          <span class="brand-title">JobInsight</span>
          <span class="brand-subtitle">职薪洞察</span>
        </div>
      </div>

      <nav class="nav-links">
        <router-link
          v-for="item in navItems"
          :key="item.path"
          :to="{ path: item.path, query: currentQuery }"
          class="nav-item"
          active-class="is-active"
        >
          <el-icon class="nav-item-icon"><component :is="item.icon" /></el-icon>
          <span class="nav-item-text">{{ item.label }}</span>
        </router-link>
      </nav>

      <div class="header-actions">
        <el-tag type="primary" effect="plain" class="baseline-badge" round>
          <el-icon><InfoFilled /></el-icon>
          <span>基准总量：<strong>2,251</strong> 组</span>
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
  padding: 0 24px;
}

.brand-area {
  display: flex;
  align-items: center;
  gap: 10px;
  cursor: pointer;
  user-select: none;
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
  gap: 8px;
  height: 100%;
}

.nav-item {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 0 16px;
  height: 40px;
  border-radius: 6px;
  color: #606266;
  text-decoration: none;
  font-size: 14px;
  font-weight: 500;
  transition: all 0.2s ease;
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

.header-actions {
  display: flex;
  align-items: center;
}

.baseline-badge {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
  padding: 6px 14px;
  background-color: #f4f4f5;
  border-color: #dcdfe6;
  color: #606266;
}

.baseline-badge strong {
  color: #303133;
  margin: 0 2px;
}
</style>
