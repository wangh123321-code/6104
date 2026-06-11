<template>
  <div class="growth-curve-page">
    <el-page-header @back="router.back()" content="成长曲线" />

    <div class="control-bar">
      <el-select v-model="selectedStudentId" placeholder="选择学员" filterable style="width: 240px" @change="loadData">
        <el-option
          v-for="s in studentOptions"
          :key="s.id"
          :label="s.name"
          :value="s.id"
        />
      </el-select>
      <el-input-number v-model="selectedYear" :min="2020" :max="2030" style="margin-left: 12px; width: 140px" @change="loadData" />
    </div>

    <el-card v-loading="loading" class="chart-card">
      <GrowthChart v-if="curveData.length > 0" :curve-data="curveData" />
      <el-empty v-else description="暂无成长数据" />
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { getStudentsApi, getStudentApi } from '@/api/student'
import { getGrowthCurveApi } from '@/api/assessment'
import GrowthChart from '@/components/GrowthChart.vue'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()

const loading = ref(false)
const studentOptions = ref<any[]>([])
const selectedStudentId = ref<number | null>(null)
const selectedYear = ref(new Date().getFullYear())
const curveData = ref<any[]>([])

onMounted(async () => {
  try {
    if (authStore.isCoach) {
      const res = await getStudentsApi()
      studentOptions.value = Array.isArray(res) ? res : []
    } else if (authStore.isParent && authStore.user?.student_id) {
      const student = await getStudentApi(authStore.user.student_id)
      studentOptions.value = [student]
      selectedStudentId.value = student.id
    }
  } catch { /* ignore */ }

  const paramId = Number(route.params.studentId)
  if (paramId && !isNaN(paramId)) {
    selectedStudentId.value = paramId
    await loadData()
  }
})

async function loadData() {
  if (!selectedStudentId.value) return
  loading.value = true
  try {
    const res = await getGrowthCurveApi(selectedStudentId.value, { year: selectedYear.value })
    curveData.value = Array.isArray(res) ? res : []
  } catch {
    curveData.value = []
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.growth-curve-page {
  padding-top: 16px;
}

.control-bar {
  display: flex;
  align-items: center;
  margin: 16px 0;
}

.chart-card {
  min-height: 400px;
}
</style>
