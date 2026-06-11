import http from './index'

export function createTrainingApi(data: {
  student_id: number
  week_number: number
  year: number
  technique_score: number
  fitness_score: number
  match_score: number
  notes?: string
}) {
  return http.post('/training', data)
}

export function getTrainingByStudentApi(studentId: number, params?: { year?: number }) {
  return http.get(`/training/student/${studentId}`, { params })
}

export function getTrainingApi(id: number) {
  return http.get(`/training/${id}`)
}
