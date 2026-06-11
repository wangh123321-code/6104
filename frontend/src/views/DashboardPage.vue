<template>
  <div class="dashboard-page">
    <template v-if="authStore.isCoach">
      <h2 class="page-title">教练工作台</h2>
      <el-row :gutter="20" class="summary-cards">
        <el-col :span="8">
          <el-card shadow="hover" class="stat-card">
            <div class="stat-value">{{ summary.totalStudents }}</div>
            <div class="stat-label">在训学员</div>
          </el-card>
        </el-col>
        <el-col :span="8">
          <el-card shadow="hover" class="stat-card">
            <div class="stat-value">{{ summary.weekTrainings }}</div>
            <div class="stat-label">本周训练记录</div>
          </el-card>
        </el-col>
        <el-col :span="8">
          <el-card shadow="hover" class="stat-card">
            <div class="stat-value">{{ summary.pendingPromotions }}</div>
            <div class="stat-label">待处理晋升</div>
          </el-card>
        </el-col>
      </el-row>
      <el-row :gutter="20" class="quick-links">
        <el-col :span="6">
          <el-card shadow="hover" class="link-card" @click="router.push('/students')">
            <el-icon :size="32" color="#409eff"><User /></el-icon>
            <div>学员管理</div>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card shadow="hover" class="link-card" @click="router.push('/training')">
            <el-icon :size="32" color="#67c23a"><EditPen /></el-icon>
            <div>训练录入</div>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card shadow="hover" class="link-card" @click="router.push('/assessments')">
            <el-icon :size="32" color="#e6a23c"><DataAnalysis /></el-icon>
            <div>体测录入</div>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card shadow="hover" class="link-card" @click="router.push('/promotions')">
            <el-icon :size="32" color="#f56c6c"><TrendCharts /></el-icon>
            <div>晋升管理</div>
          </el-card>
        </el-col>
      </el-row>
    </template>

    <template v-if="authStore.isParent">
      <h2 class="page-title">家长主页</h2>
      <el-card v-if="childInfo" shadow="hover" class="child-card">
        <template #header>
          <span>我的孩子 - {{ childInfo.name }}</span>
        </template>
        <el-descriptions :column="2" border>
          <el-descriptions-item label="性别">{{ childInfo.gender === 'M' ? '男' : '女' }}</el-descriptions-item>
          <el-descriptions-item label="班组">{{ childInfo.group_name }}</el-descriptions-item>
          <el-descriptions-item label="出生日期">{{ childInfo.birth_date }}</el-descriptions-item>
          <el-descriptions-item label="入队年份">{{ childInfo.enrollment_year }}</el-descriptions-item>
        </el-descriptions>
      </el-card>
      <el-row :gutter="20" style="margin-top: 20px">
        <el-col :span="12">
          <el-card shadow="hover">
            <template #header><span>最新体测</span></template>
            <div v-if="latestAssessment" class="assessment-summary">
              <p>周次: 第{{ latestAssessment.week_number }}周</p>
              <p>综合得分: {{ latestAssessment.total_score }}</p>
              <el-button type="primary" link @click="goToGrowth">查看成长曲线</el-button>
            </div>
            <el-empty v-else description="暂无体测记录" />
          </el-card>
        </el-col>
        <el-col :span="12">
          <el-card shadow="hover">
            <template #header><span>最新评语</span></template>
            <div v-if="latestComment" class="comment-summary">
              <p>{{ latestComment.year }}年{{ latestComment.month }}月</p>
              <p>{{ latestComment.content }}</p>
            </div>
            <el-empty v-else description="暂无评语" />
          </el-card>
        </el-col>
      </el-row>
    </template>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { getStudentsApi, getStudentApi } from '@/api/student'
import { getAssessmentsByStudentApi } from '@/api/assessment'
import { getCommentsByStudentApi } from '@/api/comment'
import { getPromotionsApi } from '@/api/promotion'
import { User, EditPen, DataAnalysis, TrendCharts } from '@element-plus/icons-vue'

const router = useRouter()
const authStore = useAuthStore()

const summary = ref({
  totalStudents: 0,
  weekTrainings: 0,
  pendingPromotions: 0
})
const childInfo = ref<any>(null)
const latestAssessment = ref<any>(null)
const latestComment = ref<any>(null)

onMounted(async () => {
  if (authStore.isCoach) {
    await loadCoachSummary()
  } else if (authStore.isParent) {
    await loadParentSummary()
  }
})

async function loadCoachSummary() {
  try {
    const students = await getStudentsApi()
    summary.value.totalStudents = Array.isArray(students) ? students.length : 0
    const now = new Date()
    const promRes = await getPromotionsApi({ year: now.getFullYear(), quarter: Math.ceil((now.getMonth() + 1) / 3) })
    const promList = Array.isArray(promRes) ? promRes : []
    summary.value.pendingPromotions = promList.filter((p: any) => p.status === 'pending').length
  } catch {
    // ignore
  }
}

async function loadParentSummary() {
  const user = authStore.user
  if (!user?.student_id) return
  try {
    childInfo.value = await getStudentApi(user.student_id)
    const assessments = await getAssessmentsByStudentApi(user.student_id)
    const assessmentList = Array.isArray(assessments) ? assessments : []
    latestAssessment.value = assessmentList.length > 0 ? assessmentList[assessmentList.length - 1] : null
    const comments = await getCommentsByStudentApi(user.student_id)
    const commentList = Array.isArray(comments) ? comments : []
    latestComment.value = commentList.length > 0 ? commentList[commentList.length - 1] : null
  } catch {
    // ignore
  }
}

function goToGrowth() {
  if (childInfo.value) {
    router.push(`/growth-curve/${childInfo.value.id}`)
  }
}
</script>

<style scoped>
.page-title {
  margin-bottom: 20px;
  color: #303133;
}

.stat-card {
  text-align: center;
  padding: 20px 0;
}

.stat-value {
  font-size: 36px;
  font-weight: bold;
  color: #409eff;
}

.stat-label {
  font-size: 14px;
  color: #909399;
  margin-top: 8px;
}

.quick-links {
  margin-top: 20px;
}

.link-card {
  text-align: center;
  cursor: pointer;
  padding: 20px 0;
  transition: transform 0.2s;
}

.link-card:hover {
  transform: translateY(-4px);
}

.link-card div {
  margin-top: 8px;
  color: #606266;
}

.child-card {
  margin-bottom: 16px;
}

.assessment-summary p,
.comment-summary p {
  margin-bottom: 8px;
  color: #606266;
}
</style>
