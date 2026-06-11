<template>
  <div class="training-page">
    <h2 class="page-title">训练记录录入</h2>

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
            <el-form-item label="技术评分" prop="technique_score">
              <el-slider v-model="form.technique_score" :min="0" :max="100" show-input />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="体能评分" prop="fitness_score">
              <el-slider v-model="form.fitness_score" :min="0" :max="100" show-input />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="比赛评分" prop="match_score">
              <el-slider v-model="form.match_score" :min="0" :max="100" show-input />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row>
          <el-col :span="24">
            <el-form-item label="备注">
              <el-input v-model="form.notes" type="textarea" :rows="2" placeholder="训练备注" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item>
          <el-button type="primary" :loading="submitting" @click="handleSubmit">提交记录</el-button>
          <el-button @click="resetForm">重置</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <el-card class="table-card">
      <template #header><span>最近训练记录</span></template>
      <el-table :data="recentTrainings" stripe border v-loading="tableLoading">
        <el-table-column prop="student_name" label="学员" width="100" />
        <el-table-column prop="year" label="年份" width="80" />
        <el-table-column prop="week_number" label="周次" width="80" />
        <el-table-column prop="technique_score" label="技术" width="80" />
        <el-table-column prop="fitness_score" label="体能" width="80" />
        <el-table-column prop="match_score" label="比赛" width="80" />
        <el-table-column prop="notes" label="备注" />
      </el-table>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { getStudentsApi } from '@/api/student'
import { createTrainingApi, getTrainingByStudentApi } from '@/api/training'
import { ElMessage, type FormInstance } from 'element-plus'

const formRef = ref<FormInstance>()
const submitting = ref(false)
const tableLoading = ref(false)
const studentOptions = ref<any[]>([])
const recentTrainings = ref<any[]>([])

const now = new Date()
const form = reactive({
  student_id: null as number | null,
  year: now.getFullYear(),
  week_number: 1,
  technique_score: 50,
  fitness_score: 50,
  match_score: 50,
  notes: ''
})

const rules = {
  student_id: [{ required: true, message: '请选择学员', trigger: 'change' }],
  year: [{ required: true, message: '请输入年份', trigger: 'blur' }],
  week_number: [{ required: true, message: '请输入周次', trigger: 'blur' }],
  technique_score: [{ required: true, message: '请设置技术评分', trigger: 'change' }],
  fitness_score: [{ required: true, message: '请设置体能评分', trigger: 'change' }],
  match_score: [{ required: true, message: '请设置比赛评分', trigger: 'change' }]
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
    await createTrainingApi({
      student_id: form.student_id!,
      week_number: form.week_number,
      year: form.year,
      technique_score: form.technique_score,
      fitness_score: form.fitness_score,
      match_score: form.match_score,
      notes: form.notes || undefined
    })
    ElMessage.success('训练记录已提交')
    await loadRecentTrainings()
    resetForm()
  } catch {
    ElMessage.error('提交失败')
  } finally {
    submitting.value = false
  }
}

async function loadRecentTrainings() {
  if (!form.student_id) return
  tableLoading.value = true
  try {
    const res = await getTrainingByStudentApi(form.student_id)
    recentTrainings.value = Array.isArray(res) ? res : []
  } catch {
    recentTrainings.value = []
  } finally {
    tableLoading.value = false
  }
}

function resetForm() {
  formRef.value?.resetFields()
  form.technique_score = 50
  form.fitness_score = 50
  form.match_score = 50
  form.notes = ''
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

.table-card {
  margin-top: 20px;
}
</style>
