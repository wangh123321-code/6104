import http from './index'

export function createAssessmentApi(data: {
  student_id: number
  week_number: number
  year: number
  speed: number
  strength: number
  endurance: number
  agility: number
  flexibility: number
}) {
  return http.post('/assessments', data)
}

export function getAssessmentsByStudentApi(studentId: number, params?: { year?: number }) {
  return http.get(`/assessments/student/${studentId}`, { params })
}

export function getGrowthCurveApi(studentId: number, params?: { year?: number }) {
  return http.get(`/assessments/growth-curve/${studentId}`, { params })
}

export function archiveYearApi(year: number) {
  return http.post('/assessments/archive', { year })
}
