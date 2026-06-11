<template>
  <div class="promotion-page">
    <h2 class="page-title">季度晋升管理</h2>

    <div class="control-bar">
      <el-input-number v-model="selectedYear" :min="2020" :max="2030" style="width: 140px" />
      <el-select v-model="selectedQuarter" placeholder="选择季度" style="width: 120px; margin-left: 12px">
        <el-option :value="1" label="第一季度" />
        <el-option :value="2" label="第二季度" />
        <el-option :value="3" label="第三季度" />
        <el-option :value="4" label="第四季度" />
      </el-select>
      <el-button type="primary" style="margin-left: 16px" :loading="generating" @click="handleGenerate">
        自动生成晋升建议
      </el-button>
      <el-button style="margin-left: 8px" @click="loadPromotions">刷新列表</el-button>
    </div>

    <el-card>
      <el-table
        :data="promotionList"
        stripe
        border
        v-loading="loading"
        :default-sort="{ prop: 'composite_score', order: 'descending' }"
        @sort-change="handleSortChange"
      >
        <el-table-column prop="student_name" label="学员姓名" width="120" sortable />
        <el-table-column prop="composite_score" label="综合得分" width="120" sortable="custom">
          <template #default="{ row }">
            <span class="score-text">{{ row.composite_score?.toFixed(2) ?? '—' }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="rank_percentage" label="排名百分位" width="130" sortable>
          <template #default="{ row }">
            {{ row.rank_percentage?.toFixed(2) ?? '—' }}%
          </template>
        </el-table-column>
        <el-table-column prop="auto_suggested" label="自动推荐" width="100">
          <template #default="{ row }">
            <el-tag v-if="row.auto_suggested" type="success" size="small">推荐</el-tag>
            <el-tag v-else type="info" size="small">未推荐</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="statusType(row.status)">{{ statusLabel(row.status) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="notes" label="备注" show-overflow-tooltip />
        <el-table-column label="操作" width="260">
          <template #default="{ row }">
            <template v-if="row.status === 'suggested' || row.status === 'pending'">
              <el-button type="success" size="small" @click="openConfirmDialog(row, 'confirmed')">
                确认晋升
              </el-button>
              <el-button type="danger" size="small" @click="openConfirmDialog(row, 'rejected')">
                拒绝
              </el-button>
            </template>
            <el-button type="primary" link size="small" @click="goToGrowth(row)">
              成长曲线
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-dialog v-model="confirmDialogVisible" :title="confirmAction === 'confirmed' ? '确认晋升' : '拒绝晋升'" width="480px">
      <el-form label-width="100px">
        <el-form-item label="学员">
          {{ currentRow?.student_name }}
        </el-form-item>
        <el-form-item label="综合得分">
          {{ currentRow?.composite_score?.toFixed(2) ?? '—' }}
        </el-form-item>
        <el-form-item label="排名百分位">
          {{ currentRow?.rank_percentage?.toFixed(2) ?? '—' }}%
        </el-form-item>
        <el-form-item label="备注">
          <el-input v-model="confirmNotes" type="textarea" :rows="3" placeholder="请输入备注（可选）" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="confirmDialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="confirming" @click="handleConfirm">确认</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { generatePromotionsApi, getPromotionsApi, confirmPromotionApi } from '@/api/promotion'
import { ElMessage } from 'element-plus'

const router = useRouter()

const now = new Date()
const selectedYear = ref(now.getFullYear())
const selectedQuarter = ref(Math.ceil((now.getMonth() + 1) / 3))
const rawPromotionList = ref<any[]>([])
const loading = ref(false)
const generating = ref(false)
const confirmDialogVisible = ref(false)
const confirming = ref(false)
const confirmAction = ref('')
const confirmNotes = ref('')
const currentRow = ref<any>(null)
const sortProp = ref('composite_score')
const sortOrder = ref<'ascending' | 'descending'>('descending')

const promotionList = computed(() => {
  const list = [...rawPromotionList.value]
  if (!sortProp.value) return list
  list.sort((a, b) => {
    let va = a[sortProp.value]
    let vb = b[sortProp.value]
    if (typeof va === 'string') va = va.toLowerCase()
    if (typeof vb === 'string') vb = vb.toLowerCase()
    if (va === undefined || va === null) va = -Infinity
    if (vb === undefined || vb === null) vb = -Infinity
    let cmp = 0
    if (va < vb) cmp = -1
    else if (va > vb) cmp = 1
    return sortOrder.value === 'ascending' ? cmp : -cmp
  })
  return list
})

onMounted(() => {
  loadPromotions()
})

async function loadPromotions() {
  loading.value = true
  try {
    const res = await getPromotionsApi({ year: selectedYear.value, quarter: selectedQuarter.value })
    rawPromotionList.value = Array.isArray(res) ? res : []
  } catch {
    rawPromotionList.value = []
  } finally {
    loading.value = false
  }
}

async function handleGenerate() {
  generating.value = true
  try {
    await generatePromotionsApi(selectedYear.value, selectedQuarter.value)
    ElMessage.success('晋升建议已生成')
    await loadPromotions()
  } catch {
    ElMessage.error('生成失败')
  } finally {
    generating.value = false
  }
}

function openConfirmDialog(row: any, action: string) {
  currentRow.value = row
  confirmAction.value = action
  confirmNotes.value = ''
  confirmDialogVisible.value = true
}

async function handleConfirm() {
  if (!currentRow.value) return
  confirming.value = true
  try {
    await confirmPromotionApi(currentRow.value.id, {
      status: confirmAction.value,
      notes: confirmNotes.value || undefined
    })
    ElMessage.success(confirmAction.value === 'confirmed' ? '已确认晋升' : '已拒绝晋升')
    confirmDialogVisible.value = false
    await loadPromotions()
  } catch {
    ElMessage.error('操作失败')
  } finally {
    confirming.value = false
  }
}

function goToGrowth(row: any) {
  router.push(`/growth-curve/${row.student_id}`)
}

function handleSortChange({ prop, order }: { prop: string; order: string | null }) {
  sortProp.value = prop || 'composite_score'
  sortOrder.value = order === 'ascending' ? 'ascending' : 'descending'
}

function statusType(status: string) {
  if (status === 'confirmed') return 'success'
  if (status === 'rejected') return 'danger'
  if (status === 'not_recommended') return 'info'
  return 'warning'
}

function statusLabel(status: string) {
  if (status === 'confirmed') return '已晋升'
  if (status === 'rejected') return '已拒绝'
  if (status === 'not_recommended') return '未推荐'
  if (status === 'suggested') return '待审核'
  return '待审核'
}
</script>

<style scoped>
.page-title {
  margin-bottom: 20px;
  color: #303133;
}

.control-bar {
  display: flex;
  align-items: center;
  margin-bottom: 20px;
}

.score-text {
  font-weight: 600;
  color: #409eff;
}
</style>
