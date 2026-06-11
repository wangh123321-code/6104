import http from './index'

export function loginApi(username: string, password: string) {
  const formData = new URLSearchParams()
  formData.append('username', username)
  formData.append('password', password)
  return http.post('/auth/login', formData, {
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
  })
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
