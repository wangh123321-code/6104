<template>
  <el-dialog
    :model-value="visible"
    :title="student ? '编辑学员' : '添加学员'"
    width="560px"
    @update:model-value="$emit('update:visible', $event)"
    @close="resetForm"
  >
    <el-form ref="formRef" :model="form" :rules="rules" label-width="100px">
      <el-form-item label="姓名" prop="name">
        <el-input v-model="form.name" placeholder="请输入姓名" />
      </el-form-item>
      <el-form-item label="性别" prop="gender">
        <el-select v-model="form.gender" placeholder="请选择性别" style="width: 100%">
          <el-option label="男" value="M" />
          <el-option label="女" value="F" />
        </el-select>
      </el-form-item>
      <el-form-item label="出生日期" prop="birth_date">
        <el-date-picker
          v-model="form.birth_date"
          type="date"
          placeholder="选择日期"
          format="YYYY-MM-DD"
          value-format="YYYY-MM-DD"
          style="width: 100%"
        />
      </el-form-item>
      <el-form-item label="班组" prop="group_name">
        <el-input v-model="form.group_name" placeholder="请输入班组名称" />
      </el-form-item>
      <el-form-item label="入队年份" prop="enrollment_year">
        <el-input-number v-model="form.enrollment_year" :min="2000" :max="2030" style="width: 100%" />
      </el-form-item>
      <el-form-item label="家长ID" prop="parent_id">
        <el-input-number v-model="form.parent_id" :min="0" placeholder="家长用户ID（可选）" style="width: 100%" />
      </el-form-item>
    </el-form>
    <template #footer>
      <el-button @click="$emit('update:visible', false)">取消</el-button>
      <el-button type="primary" :loading="saving" @click="handleSave">保存</el-button>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { ref, reactive, watch } from 'vue'
import { type FormInstance } from 'element-plus'

const props = defineProps<{
  visible: boolean
  student: any
}>()

const emit = defineEmits<{
  (e: 'update:visible', val: boolean): void
  (e: 'save', data: any): void
}>()

const formRef = ref<FormInstance>()
const saving = ref(false)

const form = reactive({
  id: undefined as number | undefined,
  name: '',
  gender: '',
  birth_date: '',
  group_name: '',
  enrollment_year: new Date().getFullYear(),
  parent_id: undefined as number | undefined
})

const rules = {
  name: [{ required: true, message: '请输入姓名', trigger: 'blur' }],
  gender: [{ required: true, message: '请选择性别', trigger: 'change' }],
  birth_date: [{ required: true, message: '请选择出生日期', trigger: 'change' }],
  group_name: [{ required: true, message: '请输入班组', trigger: 'blur' }],
  enrollment_year: [{ required: true, message: '请输入入队年份', trigger: 'blur' }]
}

watch(
  () => props.visible,
  (val) => {
    if (val && props.student) {
      form.id = props.student.id
      form.name = props.student.name || ''
      form.gender = props.student.gender || ''
      form.birth_date = props.student.birth_date || ''
      form.group_name = props.student.group_name || ''
      form.enrollment_year = props.student.enrollment_year || new Date().getFullYear()
      form.parent_id = props.student.parent_id
    }
  }
)

async function handleSave() {
  const valid = await formRef.value?.validate().catch(() => false)
  if (!valid) return
  saving.value = true
  try {
    emit('save', { ...form })
  } finally {
    saving.value = false
  }
}

function resetForm() {
  formRef.value?.resetFields()
  form.id = undefined
  form.name = ''
  form.gender = ''
  form.birth_date = ''
  form.group_name = ''
  form.enrollment_year = new Date().getFullYear()
  form.parent_id = undefined
}
</script>
