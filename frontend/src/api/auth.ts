import http from './index'

export function loginApi(username: string, password: string) {
  return http.post('/auth/login', { username, password })
}

export function registerApi(data: {
  username: string
  password: string
  role: string
  student_id?: number
}) {
  return http.post('/auth/register', data)
}

export function getMeApi() {
  return http.get('/auth/me')
}
