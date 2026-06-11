import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { loginApi, getMeApi } from '@/api/auth'
import router from '@/router'

export const useAuthStore = defineStore('auth', () => {
  const token = ref<string>(localStorage.getItem('token') || '')
  const user = ref<any>(null)

  const isAuthenticated = computed(() => !!token.value)
  const userRole = computed(() => user.value?.role || '')
  const isCoach = computed(() => userRole.value === 'coach')
  const isParent = computed(() => userRole.value === 'parent')

  async function login(username: string, password: string) {
    const res = await loginApi(username, password)
    token.value = res.access_token
    localStorage.setItem('token', res.access_token)
    await fetchUser()
  }

  async function fetchUser() {
    try {
      const res = await getMeApi()
      user.value = res
    } catch {
      logout()
    }
  }

  function logout() {
    token.value = ''
    user.value = null
    localStorage.removeItem('token')
    router.push('/login')
  }

  return {
    token,
    user,
    isAuthenticated,
    userRole,
    isCoach,
    isParent,
    login,
    fetchUser,
    logout
  }
})
