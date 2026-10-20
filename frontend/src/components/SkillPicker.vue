<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { CollectionTag, Refresh, Check } from '@element-plus/icons-vue'
import { getSkillsTop } from '@/api/stats'
import { useWorkspaceStore } from '@/stores/workspace'

const workspace = useWorkspaceStore()

const loading = ref(false)
const loadError = ref<string | null>(null)
const availableSkills = ref<string[]>([])
const selected = ref<string[]>(workspace.knownSkills ?? [])

watch(
  () => workspace.knownSkills,
  (value) => {
    selected.value = value === null ? [] : [...value]
  },
  { deep: true }
)

const selectionState = computed(() => {
  if (workspace.knownSkills === null) return '未设置'
  if (workspace.knownSkills.length === 0) return '已明确标记为暂未掌握任何标签'
  return `已在本地勾选 ${workspace.knownSkills.length} 项标签`
})

async function loadAvailableSkills() {
  loading.value = true
  loadError.value = null
  try {
    const data = await getSkillsTop({ limit: 100 })
    const names = data.skills.map((item) => item.skill_name)
    // Keep previously selected tags visible even if the current dictionary changed.
    const kept = workspace.knownSkills ?? []
    availableSkills.value = Array.from(new Set([...names, ...kept]))
  } catch (err) {
    console.error('Failed to load available skill tags', err)
    loadError.value = '技能标签加载失败'
  } finally {
    loading.value = false
  }
}

function saveSelection() {
  workspace.setKnownSkills(selected.value)
  ElMessage.success(
    selected.value.length === 0
      ? '已保存：当前没有已掌握的标签'
      : `已保存 ${selected.value.length} 项已掌握标签`
  )
}

function clearSelection() {
  selected.value = []
  workspace.setKnownSkills([])
}

function resetToUnset() {
  selected.value = []
  workspace.setKnownSkills(null)
}

onMounted(() => {
  loadAvailableSkills()
})
</script>

<template>
  <div class="skill-picker">
    <div class="picker-head">
      <div class="picker-title">
        <el-icon><CollectionTag /></el-icon>
        <span>我已掌握的技能标签</span>
      </div>
      <span class="picker-state" :class="{ 'is-unset': workspace.knownSkills === null }">
        {{ selectionState }}
      </span>
    </div>

    <p class="picker-hint">
      标签仅取自当前样本已标注的技能名称（接口返回 {{ availableSkills.length }} 项可用标签），
      不代表完整能力清单或熟练程度。选择结果只保存在本浏览器，不会上传，也不改变任何招聘数据。
    </p>

    <el-alert
      v-if="loadError"
      :title="loadError"
      type="warning"
      :closable="false"
      show-icon
      class="picker-alert"
    >
      <el-button size="small" :icon="Refresh" @click="loadAvailableSkills">重试</el-button>
    </el-alert>

    <el-select
      v-model="selected"
      multiple
      filterable
      clearable
      collapse-tags
      collapse-tags-tooltip
      :loading="loading"
      placeholder="选择你已掌握的标签（可多选）"
      class="picker-select"
      @clear="clearSelection"
    >
      <el-option v-for="name in availableSkills" :key="name" :label="name" :value="name" />
    </el-select>

    <div class="picker-actions">
      <el-button type="primary" :icon="Check" @click="saveSelection">保存到本浏览器</el-button>
      <el-button text @click="resetToUnset">标记为未设置</el-button>
    </div>

    <p v-if="!workspace.canPersist" class="picker-warning">
      浏览器不允许本地保存，本次选择仅在当前会话有效，刷新后可能丢失。
    </p>
  </div>
</template>

<style scoped>
.skill-picker {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.picker-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  flex-wrap: wrap;
}

.picker-title {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 14px;
  font-weight: 600;
  color: #1f2d3d;
}

.picker-state {
  font-size: 12px;
  color: #409eff;
  background: #ecf5ff;
  border-radius: 10px;
  padding: 2px 10px;
}

.picker-state.is-unset {
  color: #909399;
  background: #f4f4f5;
}

.picker-hint {
  margin: 0;
  font-size: 12px;
  color: #909399;
  line-height: 1.6;
}

.picker-alert {
  margin-bottom: 4px;
}

.picker-select {
  width: 100%;
}

.picker-actions {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
}

.picker-warning {
  margin: 0;
  font-size: 12px;
  color: #e6a23c;
}
</style>
