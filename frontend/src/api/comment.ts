import http from './index'

export function createCommentApi(data: {
  student_id: number
  month: number
  year: number
  content: string
}) {
  return http.post('/comments', data)
}

export function updateCommentApi(
  id: number,
  data: {
    content: string
    month?: number
    year?: number
    force?: boolean
  }
) {
  return http.put(`/comments/${id}`, data)
}

export function getCommentsByStudentApi(studentId: number, params?: { year?: number }) {
  return http.get(`/comments/student/${studentId}`, { params })
}

export function deleteCommentApi(id: number) {
  return http.delete(`/comments/${id}`)
}
