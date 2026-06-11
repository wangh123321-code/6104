<template>
  <div class="assessment-page">
    <h2 class="page-title">体测评估录入</h2>

    <el-card class="form-card">
      <el-form
        ref="formRef"
        :model="form"
        :rules="rules"
        label-width="100px"
      >
        <el-row :gutter="20">
          <el-col :span="8">
            <el-form-item label="学员" prop="student_id">
              <el-select v-model="form.student_id" placeholder="选择学员" filterable style="width: 100%">
                <el-option
                  v-for="s in studentOptions"
                  :key="s.id"
                  :label="s.name"
                  :value="s.id"
                />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="年份" prop="year">
              <el-input-number v-model="form.year" :min="2020" :max="2030" style="width: 100%" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="周次" prop="week_number">
              <el-input-number v-model="form.week_number" :min="1" :max="52" style="width: 100%" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="8">
            <el-form-item label="速度" prop="speed">
              <el-slider v-model="form.speed" :min="0" :max="100" show-input />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="力量" prop="strength">
              <el-slider v-model="form.strength" :min="0" :max="100" show-input />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="耐力" prop="endurance">
              <el-slider v-model="form.endurance" :min="0" :max="100" show-input />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="8">
            <el-form-item label="敏捷" prop="agility">
              <el-slider v-model="form.agility" :min="0" :max="100" show-input />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="柔韧" prop="flexibility">
              <el-slider v-model="form.flexibility" :min="0" :max="100" show-input />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="综合得分">
              <div class="total-score">{{ totalScore }}</div>
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item>
          <el-button type="primary" :loading="submitting" @click="handleSubmit">提交评估</el-button>
          <el-button @click="resetForm">重置</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <el-card class="table-card">
      <template #header><span>最近评估记录</span></template>
      <el-table :data="recentAssessments" stripe border v-loading="tableLoading">
        <el-table-column prop="student_name" label="学员" width="100" />
        <el-table-column prop="year" label="年份" width="80" />
        <el-table-column prop="week_number" label="周次" width="80" />
        <el-table-column prop="speed" label="速度" width="70" />
        <el-table-column prop="strength" label="力量" width="70" />
        <el-table-column prop="endurance" label="耐力" width="70" />
        <el-table-column prop="agility" label="敏捷" width="70" />
        <el-table-column prop="flexibility" label="柔韧" width="70" />
        <el-table-column prop="total_score" label="总分" width="80" />
      </el-table>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { getStudentsApi } from '@/api/student'
import { createAssessmentApi, getAssessmentsByStudentApi } from '@/api/assessment'
import { ElMessage, type FormInstance } from 'element-plus'

const formRef = ref<FormInstance>()
const submitting = ref(false)
const tableLoading = ref(false)
const studentOptions = ref<any[]>([])
const recentAssessments = ref<any[]>([])

const now = new Date()
const form = reactive({
  student_id: null as number | null,
  year: now.getFullYear(),
  week_number: 1,
  speed: 50,
  strength: 50,
  endurance: 50,
  agility: 50,
  flexibility: 50
})

const totalScore = computed(() => {
  return Math.round((form.speed + form.strength + form.endurance + form.agility + form.flexibility) / 5)
})

const rules = {
  student_id: [{ required: true, message: '请选择学员', trigger: 'change' }],
  year: [{ required: true, message: '请输入年份', trigger: 'blur' }],
  week_number: [{ required: true, message: '请输入周次', trigger: 'blur' }],
  speed: [{ required: true, message: '请设置速度评分', trigger: 'change' }],
  strength: [{ required: true, message: '请设置力量评分', trigger: 'change' }],
  endurance: [{ required: true, message: '请设置耐力评分', trigger: 'change' }],
  agility: [{ required: true, message: '请设置敏捷评分', trigger: 'change' }],
  flexibility: [{ required: true, message: '请设置柔韧评分', trigger: 'change' }]
}

onMounted(async () => {
  try {
    const res = await getStudentsApi()
    studentOptions.value = Array.isArray(res) ? res : []
  } catch { /* ignore */ }
})

async function handleSubmit() {
  const valid = await formRef.value?.validate().catch(() => false)
  if (!valid) return

  submitting.value = true
  try {
    await createAssessmentApi({
      student_id: form.student_id!,
      week_number: form.week_number,
      year: form.year,
      speed: form.speed,
      strength: form.strength,
      endurance: form.endurance,
      agility: form.agility,
      flexibility: form.flexibility
    })
    ElMessage.success('体测评估已提交')
    await loadRecentAssessments()
    resetForm()
  } catch {
    ElMessage.error('提交失败')
  } finally {
    submitting.value = false
  }
}

async function loadRecentAssessments() {
  if (!form.student_id) return
  tableLoading.value = true
  try {
    const res = await getAssessmentsByStudentApi(form.student_id)
    recentAssessments.value = Array.isArray(res) ? res : []
  } catch {
    recentAssessments.value = []
  } finally {
    tableLoading.value = false
  }
}

function resetForm() {
  formRef.value?.resetFields()
  form.speed = 50
  form.strength = 50
  form.endurance = 50
  form.agility = 50
  form.flexibility = 50
}
</script>

<style scoped>
.page-title {
  margin-bottom: 20px;
  color: #303133;
}

.form-card {
  margin-bottom: 20px;
}

.total-score {
  font-size: 28px;
  font-weight: bold;
  color: #409eff;
  text-align: center;
}

.table-card {
  margin-top: 20px;
}
</style>
