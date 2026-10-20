<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import { Close, Operation } from '@element-plus/icons-vue'
import { useWorkspaceStore } from '@/stores/workspace'
import { useJobDetails } from '@/composables/useJobDetails'
import { MAX_COMPARE_JOBS } from '@/types/workspace'

const router = useRouter()
const workspace = useWorkspaceStore()
const { records, load } = useJobDetails()

const visible = computed(() => workspace.compareJobIds.length > 0)
const compareReady = computed(() => workspace.compareJobIds.length >= 2)

function titleOf(id: string): string {
  const record = records.value[id]
  if (record?.status === 'success' && record.job) return record.job.title
  if (record?.status === 'not_found') return '当前数据中未找到'
  if (record?.status === 'error') return '加载失败'
  return '加载中…'
}

const loadingTitles = ref(false)

watch(
  () => workspace.compareJobIds.join(','),
  async (joined) => {
    if (!joined) {
      await load([])
      return
    }
    loadingTitles.value = true
    try {
      await load(joined.split(','))
    } finally {
      loadingTitles.value = false
    }
  },
  { immediate: true }
)

function goToCompare() {
  router.push({
    path: '/compare',
    query: { ids: [...workspace.compareJobIds] }
  })
}
</script>

<template>
  <div v-if="visible" class="compare-tray">
    <div class="tray-inner">
      <div class="tray-label">
        <el-icon><Operation /></el-icon>
        <span>对比栏 {{ workspace.compareJobIds.length }}/{{ MAX_COMPARE_JOBS }}</span>
      </div>

      <div class="tray-items" v-loading="loadingTitles">
        <div v-for="id in workspace.compareJobIds" :key="id" class="tray-item">
          <span class="tray-item-title" :title="`${titleOf(id)} (${id})`">{{ titleOf(id) }}</span>
          <el-button
            :icon="Close"
            size="small"
            text
            :aria-label="`移除对比项 ${titleOf(id)}`"
            @click="workspace.removeFromCompare(id)"
          />
        </div>
      </div>

      <div class="tray-actions">
        <el-button size="small" text @click="workspace.clearCompare()">清空</el-button>
        <el-tooltip :disabled="compareReady" content="至少选择 2 个岗位" placement="top">
          <span>
            <el-button type="primary" size="small" :disabled="!compareReady" @click="goToCompare">
              进入对比
            </el-button>
          </span>
        </el-tooltip>
      </div>
    </div>
  </div>
</template>

<style scoped>
.compare-tray {
  position: fixed;
  left: 0;
  right: 0;
  bottom: 0;
  z-index: 1200;
  background: #ffffff;
  border-top: 1px solid #e4e7ed;
  box-shadow: 0 -2px 12px rgba(0, 21, 41, 0.08);
}

.tray-inner {
  max-width: 1440px;
  margin: 0 auto;
  padding: 10px 24px;
  display: flex;
  align-items: center;
  gap: 16px;
  flex-wrap: wrap;
}

.tray-label {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 13px;
  font-weight: 600;
  color: #303133;
  white-space: nowrap;
}

.tray-items {
  display: flex;
  align-items: center;
  gap: 8px;
  flex: 1;
  min-width: 0;
  flex-wrap: wrap;
}

.tray-item {
  display: flex;
  align-items: center;
  gap: 2px;
  background: #f4f8ff;
  border: 1px solid #d9ecff;
  border-radius: 6px;
  padding: 2px 4px 2px 10px;
  max-width: 260px;
}

.tray-item-title {
  font-size: 12px;
  color: #303133;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.tray-actions {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-left: auto;
}

@media (max-width: 640px) {
  .tray-inner {
    padding: 8px 12px;
    gap: 8px;
  }

  .tray-actions {
    margin-left: 0;
  }
}
</style>
