import http from './index'

export function getStudentsApi(params?: { keyword?: string; group?: string }) {
  return http.get('/students', { params })
}

export function getStudentApi(id: number) {
  return http.get(`/students/${id}`)
}

export function createStudentApi(data: {
  name: string
  gender: string
  birth_date: string
  group_name: string
  enrollment_year: number
  parent_id?: number
}) {
  return http.post('/students', data)
}

export function updateStudentApi(
  id: number,
  data: {
    name?: string
    gender?: string
    birth_date?: string
    group_name?: string
    enrollment_year?: number
    parent_id?: number
  }
) {
  return http.put(`/students/${id}`, data)
}
