<template>
  <el-dialog
    :model-value="visible"
    title="评语冲突 - 版本不一致"
    width="700px"
    @update:model-value="$emit('update:visible', $event)"
  >
    <p class="conflict-hint">其他用户已修改该评语，请选择处理方式：</p>
    <el-row :gutter="16">
      <el-col :span="12">
        <h4>服务器版本</h4>
        <div class="version-text">{{ serverText }}</div>
      </el-col>
      <el-col :span="12">
        <h4>您的版本</h4>
        <div class="version-text">{{ clientText }}</div>
      </el-col>
    </el-row>

    <div v-if="showMergeArea" class="merge-area">
      <h4>合并内容（请手动编辑）</h4>
      <el-input
        v-model="mergedText"
        type="textarea"
        :rows="6"
        placeholder="请合并两个版本的内容"
      />
    </div>

    <template #footer>
      <el-button @click="$emit('update:visible', false)">取消</el-button>
      <el-button v-if="!showMergeArea" type="warning" @click="showMergeArea = true">
        合并
      </el-button>
      <el-button v-if="showMergeArea" type="primary" :disabled="!mergedText.trim()" @click="handleMerge">
        提交合并
      </el-button>
      <el-button type="danger" @click="handleOverwrite">覆盖服务器版本</el-button>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'

const props = defineProps<{
  visible: boolean
  serverText: string
  clientText: string
}>()

const emit = defineEmits<{
  (e: 'update:visible', val: boolean): void
  (e: 'overwrite'): void
  (e: 'merge', mergedText: string): void
}>()

const showMergeArea = ref(false)
const mergedText = ref('')

watch(
  () => props.visible,
  (val) => {
    if (val) {
      showMergeArea.value = false
      mergedText.value = props.serverText + '\n\n--- 合并内容 ---\n\n' + props.clientText
    }
  }
)

function handleOverwrite() {
  emit('overwrite')
}

function handleMerge() {
  emit('merge', mergedText.value)
}
</script>

<style scoped>
.conflict-hint {
  color: #e6a23c;
  margin-bottom: 16px;
  font-size: 14px;
}

.version-text {
  background: #f5f7fa;
  padding: 12px;
  border-radius: 4px;
  min-height: 100px;
  white-space: pre-wrap;
  word-break: break-all;
  font-size: 13px;
  color: #606266;
  border: 1px solid #e4e7ed;
}

.merge-area {
  margin-top: 16px;
}

.merge-area h4 {
  margin-bottom: 8px;
}
</style>
