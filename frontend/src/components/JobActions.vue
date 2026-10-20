<script setup lang="ts">
import { computed } from 'vue'
import { ElMessage } from 'element-plus'
import { Star, StarFilled, Operation } from '@element-plus/icons-vue'
import { useWorkspaceStore } from '@/stores/workspace'
import { MAX_COMPARE_JOBS } from '@/types/workspace'

interface Props {
  jobId: string
  /** `link` fits dense table rows; `button` fits drawer headers and cards. */
  variant?: 'link' | 'button'
}

const props = withDefaults(defineProps<Props>(), { variant: 'link' })

const workspace = useWorkspaceStore()

const isSaved = computed(() => workspace.isSaved(props.jobId))
const isComparing = computed(() => workspace.isComparing(props.jobId))
const compareLimitReached = computed(
  () => !isComparing.value && workspace.compareJobIds.length >= MAX_COMPARE_JOBS
)

function toggleSaved(event: Event) {
  event.stopPropagation()
  const saved = workspace.toggleSaved(props.jobId)
  ElMessage.success(saved ? '已加入候选清单' : '已从候选清单移除')
}

function toggleCompare(event: Event) {
  event.stopPropagation()
  if (isComparing.value) {
    workspace.removeFromCompare(props.jobId)
    return
  }
  const result = workspace.addToCompare(props.jobId)
  if (result === 'limit_reached') {
    ElMessage.warning(`最多同时比较 ${MAX_COMPARE_JOBS} 个岗位，请先在对比栏移除一个`)
  }
}
</script>

<template>
  <div class="job-actions" @click.stop>
    <el-tooltip :content="isSaved ? '取消收藏' : '收藏为候选'" placement="top">
      <el-button
        :type="isSaved ? 'warning' : 'default'"
        :link="variant === 'link'"
        :size="variant === 'link' ? 'small' : 'default'"
        :icon="isSaved ? StarFilled : Star"
        :aria-label="isSaved ? '取消收藏' : '收藏为候选'"
        :aria-pressed="isSaved"
        class="action-button"
        @click="toggleSaved"
      >
        {{ isSaved ? '已收藏' : '收藏' }}
      </el-button>
    </el-tooltip>

    <el-tooltip
      :content="
        compareLimitReached
          ? `最多同时比较 ${MAX_COMPARE_JOBS} 个岗位`
          : isComparing
            ? '从对比中移除'
            : '加入岗位对比'
      "
      placement="top"
    >
      <span class="compare-button-wrapper">
        <el-button
          :type="isComparing ? 'primary' : 'default'"
          :link="variant === 'link'"
          :size="variant === 'link' ? 'small' : 'default'"
          :icon="Operation"
          :aria-label="isComparing ? '从对比中移除' : '加入岗位对比'"
          :aria-pressed="isComparing"
          class="action-button"
          @click="toggleCompare"
        >
          {{ isComparing ? '对比中' : '对比' }}
        </el-button>
      </span>
    </el-tooltip>
  </div>
</template>

<style scoped>
.job-actions {
  display: flex;
  align-items: center;
  gap: 4px;
  flex-wrap: wrap;
}

.action-button {
  margin: 0;
}

.compare-button-wrapper {
  display: inline-flex;
}
</style>
