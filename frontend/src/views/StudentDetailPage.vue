<template>
  <div class="student-detail-page" v-loading="loading">
    <el-page-header @back="router.back()" content="学员详情" />

    <el-card v-if="student" class="info-card">
      <template #header>
        <div class="card-header">
          <span>{{ student.name }} - 基本信息</span>
          <el-button
            v-if="authStore.isCoach"
            type="primary"
            size="small"
            @click="showEditDialog"
          >
            编辑
          </el-button>
        </div>
      </template>
      <el-descriptions :column="3" border>
        <el-descriptions-item label="姓名">{{ student.name }}</el-descriptions-item>
        <el-descriptions-item label="性别">{{ student.gender === 'M' ? '男' : '女' }}</el-descriptions-item>
        <el-descriptions-item label="年龄">{{ student.age }}</el-descriptions-item>
        <el-descriptions-item label="班组">{{ student.group_name }}</el-descriptions-item>
        <el-descriptions-item label="入队年份">{{ student.enrollment_year }}</el-descriptions-item>
        <el-descriptions-item label="出生日期">{{ student.birth_date }}</el-descriptions-item>
      </el-descriptions>
    </el-card>

    <el-card class="tabs-card">
      <el-tabs v-model="activeTab">
        <el-tab-pane label="训练记录" name="training">
          <el-table :data="trainingList" stripe border>
            <el-table-column prop="week_number" label="周次" width="80" />
            <el-table-column prop="year" label="年份" width="80" />
            <el-table-column prop="technique_score" label="技术" width="80" />
            <el-table-column prop="fitness_score" label="体能" width="80" />
            <el-table-column prop="match_score" label="比赛" width="80" />
            <el-table-column prop="notes" label="备注" />
          </el-table>
        </el-tab-pane>

        <el-tab-pane label="体测评估" name="assessments">
          <el-table :data="assessmentList" stripe border>
            <el-table-column prop="week_number" label="周次" width="80" />
            <el-table-column prop="year" label="年份" width="80" />
            <el-table-column prop="speed" label="速度" width="80" />
            <el-table-column prop="strength" label="力量" width="80" />
            <el-table-column prop="endurance" label="耐力" width="80" />
            <el-table-column prop="agility" label="敏捷" width="80" />
            <el-table-column prop="flexibility" label="柔韧" width="80" />
            <el-table-column prop="total_score" label="总分" width="80" />
          </el-table>
          <div style="margin-top: 16px">
            <el-button type="primary" @click="goToGrowth">查看成长曲线</el-button>
          </div>
        </el-tab-pane>

        <el-tab-pane label="教练评语" name="comments">
          <el-table :data="commentList" stripe border>
            <el-table-column prop="year" label="年份" width="80" />
            <el-table-column prop="month" label="月份" width="80" />
            <el-table-column prop="content" label="评语内容" />
            <el-table-column v-if="authStore.isCoach" label="操作" width="160">
              <template #default="{ row }">
                <el-button type="primary" link size="small" @click="goToCommentEdit(row)">编辑</el-button>
                <el-button type="danger" link size="small" @click="handleDeleteComment(row)">删除</el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-tab-pane>

        <el-tab-pane label="晋升记录" name="promotions">
          <el-table :data="promotionList" stripe border>
            <el-table-column prop="year" label="年份" width="80" />
            <el-table-column prop="quarter" label="季度" width="80" />
            <el-table-column prop="total_score" label="综合得分" width="100" />
            <el-table-column prop="rank_percent" label="排名百分比" width="120">
              <template #default="{ row }">
                {{ (row.rank_percent * 100).toFixed(1) }}%
              </template>
            </el-table-column>
            <el-table-column prop="status" label="状态" width="100">
              <template #default="{ row }">
                <el-tag :type="statusType(row.status)">{{ statusLabel(row.status) }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="notes" label="备注" />
          </el-table>
        </el-tab-pane>
      </el-tabs>
    </el-card>

    <StudentFormDialog
      v-model:visible="editDialogVisible"
      :student="student"
      @save="handleUpdateStudent"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { getStudentApi, updateStudentApi } from '@/api/student'
import { getTrainingByStudentApi } from '@/api/training'
import { getAssessmentsByStudentApi } from '@/api/assessment'
import { getCommentsByStudentApi, deleteCommentApi } from '@/api/comment'
import { getStudentPromotionsApi } from '@/api/promotion'
import { ElMessage, ElMessageBox } from 'element-plus'
import StudentFormDialog from '@/components/StudentFormDialog.vue'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()

const loading = ref(true)
const student = ref<any>(null)
const activeTab = ref('training')
const trainingList = ref<any[]>([])
const assessmentList = ref<any[]>([])
const commentList = ref<any[]>([])
const promotionList = ref<any[]>([])
const editDialogVisible = ref(false)

const studentId = Number(route.params.id)

onMounted(async () => {
  await loadAll()
})

async function loadAll() {
  loading.value = true
  try {
    student.value = await getStudentApi(studentId)
    await Promise.all([loadTraining(), loadAssessments(), loadComments(), loadPromotions()])
  } catch {
    ElMessage.error('加载学员数据失败')
  } finally {
    loading.value = false
  }
}

async function loadTraining() {
  try {
    const res = await getTrainingByStudentApi(studentId)
    trainingList.value = Array.isArray(res) ? res : []
  } catch { trainingList.value = [] }
}

async function loadAssessments() {
  try {
    const res = await getAssessmentsByStudentApi(studentId)
    assessmentList.value = Array.isArray(res) ? res : []
  } catch { assessmentList.value = [] }
}

async function loadComments() {
  try {
    const res = await getCommentsByStudentApi(studentId)
    commentList.value = Array.isArray(res) ? res : []
  } catch { commentList.value = [] }
}

async function loadPromotions() {
  try {
    const res = await getStudentPromotionsApi(studentId)
    promotionList.value = Array.isArray(res) ? res : []
  } catch { promotionList.value = [] }
}

function showEditDialog() {
  editDialogVisible.value = true
}

async function handleUpdateStudent(data: any) {
  try {
    await updateStudentApi(studentId, data)
    ElMessage.success('学员信息已更新')
    editDialogVisible.value = false
    student.value = await getStudentApi(studentId)
  } catch {
    ElMessage.error('更新失败')
  }
}

async function handleDeleteComment(row: any) {
  try {
    await ElMessageBox.confirm('确认删除该评语？', '提示', { type: 'warning' })
    await deleteCommentApi(row.id)
    ElMessage.success('已删除')
    loadComments()
  } catch { /* cancelled */ }
}

function goToGrowth() {
  router.push(`/growth-curve/${studentId}`)
}

function goToCommentEdit(row: any) {
  router.push({ path: '/comments', query: { studentId: String(studentId), commentId: String(row.id) } })
}

function statusType(status: string) {
  if (status === 'confirmed') return 'success'
  if (status === 'rejected') return 'danger'
  return 'warning'
}

function statusLabel(status: string) {
  if (status === 'confirmed') return '已晋升'
  if (status === 'rejected') return '已拒绝'
  return '待审核'
}
</script>

<style scoped>
.student-detail-page {
  padding-top: 16px;
}

.info-card {
  margin-top: 16px;
}

.tabs-card {
  margin-top: 16px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>
