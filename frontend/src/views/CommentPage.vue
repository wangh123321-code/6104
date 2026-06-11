<template>
  <div class="comment-page">
    <h2 class="page-title">教练评语</h2>

    <el-card class="form-card">
      <el-form
        ref="formRef"
        :model="form"
        :rules="rules"
        label-width="80px"
      >
        <el-row :gutter="20">
          <el-col :span="8">
            <el-form-item label="学员" prop="student_id">
              <el-select v-model="form.student_id" placeholder="选择学员" filterable style="width: 100%" @change="onStudentChange">
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
            <el-form-item label="月份" prop="month">
              <el-input-number v-model="form.month" :min="1" :max="12" style="width: 100%" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="评语" prop="content">
          <el-input
            v-model="form.content"
            type="textarea"
            :rows="4"
            placeholder="请输入月度评语"
          />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" :loading="submitting" @click="handleSubmit">
            {{ editingId ? '更新评语' : '提交评语' }}
          </el-button>
          <el-button v-if="editingId" @click="cancelEdit">取消编辑</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <el-card class="list-card">
      <template #header><span>评语列表</span></template>
      <el-table :data="commentList" stripe border v-loading="tableLoading">
        <el-table-column prop="year" label="年份" width="80" />
        <el-table-column prop="month" label="月份" width="80" />
        <el-table-column prop="content" label="评语内容" />
        <el-table-column v-if="authStore.isCoach" label="操作" width="160">
          <template #default="{ row }">
            <el-button type="primary" link size="small" @click="startEdit(row)">编辑</el-button>
            <el-button type="danger" link size="small" @click="handleDelete(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <CommentConflictDialog
      v-model:visible="conflictVisible"
      :server-text="conflictServerText"
      :client-text="conflictClientText"
      @overwrite="handleOverwrite"
      @merge="handleMerge"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { getStudentsApi } from '@/api/student'
import { createCommentApi, updateCommentApi, getCommentsByStudentApi, deleteCommentApi } from '@/api/comment'
import { ElMessage, ElMessageBox, type FormInstance } from 'element-plus'
import CommentConflictDialog from '@/components/CommentConflictDialog.vue'

const route = useRoute()
const authStore = useAuthStore()
const formRef = ref<FormInstance>()
const submitting = ref(false)
const tableLoading = ref(false)
const studentOptions = ref<any[]>([])
const commentList = ref<any[]>([])
const editingId = ref<number | null>(null)
const editingVersion = ref<number>(1)
const conflictVisible = ref(false)
const conflictServerText = ref('')
const conflictClientText = ref('')

const now = new Date()
const form = reactive({
  student_id: null as number | null,
  year: now.getFullYear(),
  month: now.getMonth() + 1,
  content: ''
})

const rules = {
  student_id: [{ required: true, message: '请选择学员', trigger: 'change' }],
  year: [{ required: true, message: '请输入年份', trigger: 'blur' }],
  month: [{ required: true, message: '请输入月份', trigger: 'blur' }],
  content: [{ required: true, message: '请输入评语内容', trigger: 'blur' }]
}

onMounted(async () => {
  try {
    const res = await getStudentsApi()
    studentOptions.value = Array.isArray(res) ? res : []
  } catch { /* ignore */ }

  if (route.query.studentId) {
    form.student_id = Number(route.query.studentId)
    await loadComments()
  }
  if (route.query.commentId) {
    const commentId = Number(route.query.commentId)
    const comment = commentList.value.find((c: any) => c.id === commentId)
    if (comment) {
      startEdit(comment)
    }
  }
})

function onStudentChange() {
  loadComments()
}

async function loadComments() {
  if (!form.student_id) return
  tableLoading.value = true
  try {
    const res = await getCommentsByStudentApi(form.student_id)
    commentList.value = Array.isArray(res) ? res : []
  } catch {
    commentList.value = []
  } finally {
    tableLoading.value = false
  }
}

async function handleSubmit() {
  const valid = await formRef.value?.validate().catch(() => false)
  if (!valid) return

  submitting.value = true
  try {
    if (editingId.value) {
      await updateCommentApi(editingId.value, {
        content: form.content,
        version: editingVersion.value
      })
      ElMessage.success('评语已更新')
      editingId.value = null
    } else {
      await createCommentApi({
        student_id: form.student_id!,
        month: form.month,
        year: form.year,
        content: form.content
      })
      ElMessage.success('评语已提交')
    }
    resetForm()
    await loadComments()
  } catch (err: any) {
    if (err.code === 409) {
      conflictServerText.value = err.serverData?.current_content || ''
      conflictClientText.value = form.content
      conflictVisible.value = true
    } else {
      ElMessage.error('操作失败')
    }
  } finally {
    submitting.value = false
  }
}

async function handleOverwrite() {
  if (!editingId.value) return
  try {
    await updateCommentApi(editingId.value, {
      content: form.content,
      version: editingVersion.value,
      force: true
    })
    ElMessage.success('评语已覆盖')
    conflictVisible.value = false
    editingId.value = null
    resetForm()
    await loadComments()
  } catch {
    ElMessage.error('覆盖失败')
  }
}

async function handleMerge(mergedText: string) {
  if (!editingId.value) return
  try {
    await updateCommentApi(editingId.value, {
      content: mergedText,
      version: editingVersion.value,
      force: true
    })
    ElMessage.success('评语已合并')
    conflictVisible.value = false
    editingId.value = null
    resetForm()
    await loadComments()
  } catch {
    ElMessage.error('合并失败')
  }
}

function startEdit(row: any) {
  editingId.value = row.id
  editingVersion.value = row.version
  form.student_id = row.student_id
  form.year = row.year
  form.month = row.month
  form.content = row.content
}

function cancelEdit() {
  editingId.value = null
  form.content = ''
}

async function handleDelete(row: any) {
  try {
    await ElMessageBox.confirm('确认删除该评语？', '提示', { type: 'warning' })
    await deleteCommentApi(row.id)
    ElMessage.success('已删除')
    await loadComments()
  } catch { /* cancelled */ }
}

function resetForm() {
  form.content = ''
  editingId.value = null
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

.list-card {
  margin-top: 20px;
}
</style>
