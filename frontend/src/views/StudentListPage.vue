<template>
  <div class="student-list-page">
    <div class="page-header">
      <h2>学员管理</h2>
      <el-button type="primary" @click="showAddDialog">
        <el-icon><Plus /></el-icon>
        添加学员
      </el-button>
    </div>

    <div class="filter-bar">
      <el-input
        v-model="keyword"
        placeholder="搜索姓名"
        clearable
        style="width: 200px; margin-right: 12px"
        @clear="loadStudents"
        @keyup.enter="loadStudents"
      />
      <el-input
        v-model="groupFilter"
        placeholder="筛选班组"
        clearable
        style="width: 160px; margin-right: 12px"
        @clear="loadStudents"
        @keyup.enter="loadStudents"
      />
      <el-button type="primary" @click="loadStudents">搜索</el-button>
    </div>

    <el-table :data="students" stripe border v-loading="loading" @row-click="goToDetail">
      <el-table-column prop="name" label="姓名" width="120" />
      <el-table-column prop="gender" label="性别" width="80">
        <template #default="{ row }">
          {{ row.gender === 'M' ? '男' : '女' }}
        </template>
      </el-table-column>
      <el-table-column prop="age" label="年龄" width="80" />
      <el-table-column prop="group_name" label="班组" width="120" />
      <el-table-column prop="enrollment_year" label="入队年份" width="120" />
      <el-table-column label="操作" width="200">
        <template #default="{ row }">
          <el-button type="primary" link @click.stop="goToDetail(row)">查看</el-button>
          <el-button type="primary" link @click.stop="showEditDialog(row)">编辑</el-button>
          <el-button type="success" link @click.stop="goToGrowth(row)">成长曲线</el-button>
        </template>
      </el-table-column>
    </el-table>

    <StudentFormDialog
      v-model:visible="dialogVisible"
      :student="editingStudent"
      @save="handleSave"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { getStudentsApi, createStudentApi, updateStudentApi } from '@/api/student'
import { ElMessage } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'
import StudentFormDialog from '@/components/StudentFormDialog.vue'

const router = useRouter()
const students = ref<any[]>([])
const loading = ref(false)
const keyword = ref('')
const groupFilter = ref('')
const dialogVisible = ref(false)
const editingStudent = ref<any>(null)

onMounted(() => {
  loadStudents()
})

async function loadStudents() {
  loading.value = true
  try {
    const params: any = {}
    if (keyword.value) params.keyword = keyword.value
    if (groupFilter.value) params.group = groupFilter.value
    const res = await getStudentsApi(params)
    students.value = Array.isArray(res) ? res : []
  } catch {
    students.value = []
  } finally {
    loading.value = false
  }
}

function showAddDialog() {
  editingStudent.value = null
  dialogVisible.value = true
}

function showEditDialog(student: any) {
  editingStudent.value = { ...student }
  dialogVisible.value = true
}

async function handleSave(data: any) {
  try {
    if (data.id) {
      await updateStudentApi(data.id, data)
      ElMessage.success('学员信息已更新')
    } else {
      await createStudentApi(data)
      ElMessage.success('学员已添加')
    }
    dialogVisible.value = false
    loadStudents()
  } catch {
    ElMessage.error('操作失败')
  }
}

function goToDetail(row: any) {
  router.push(`/students/${row.id}`)
}

function goToGrowth(row: any) {
  router.push(`/growth-curve/${row.id}`)
}
</script>

<style scoped>
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.page-header h2 {
  color: #303133;
}

.filter-bar {
  display: flex;
  align-items: center;
  margin-bottom: 16px;
}
</style>
