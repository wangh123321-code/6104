import http from './index'

export function generatePromotionsApi(year: number, quarter: number) {
  return http.post('/promotions/generate', { year, quarter })
}

export function getPromotionsApi(params: { year: number; quarter: number }) {
  return http.get('/promotions', { params })
}

export function confirmPromotionApi(id: number, data: { status: string; notes?: string }) {
  return http.put(`/promotions/${id}/confirm`, data)
}

export function getStudentPromotionsApi(studentId: number) {
  return http.get(`/promotions/student/${studentId}`)
}
