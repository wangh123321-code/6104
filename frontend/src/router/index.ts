import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/LoginPage.vue'),
    meta: { requiresAuth: false }
  },
  {
    path: '/dashboard',
    name: 'Dashboard',
    component: () => import('@/views/DashboardPage.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/students',
    name: 'StudentList',
    component: () => import('@/views/StudentListPage.vue'),
    meta: { requiresAuth: true, roles: ['coach'] }
  },
  {
    path: '/students/:id',
    name: 'StudentDetail',
    component: () => import('@/views/StudentDetailPage.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/training',
    name: 'Training',
    component: () => import('@/views/TrainingPage.vue'),
    meta: { requiresAuth: true, roles: ['coach'] }
  },
  {
    path: '/assessments',
    name: 'Assessments',
    component: () => import('@/views/AssessmentPage.vue'),
    meta: { requiresAuth: true, roles: ['coach'] }
  },
  {
    path: '/comments',
    name: 'Comments',
    component: () => import('@/views/CommentPage.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/promotions',
    name: 'Promotions',
    component: () => import('@/views/PromotionPage.vue'),
    meta: { requiresAuth: true, roles: ['coach'] }
  },
  {
    path: '/growth-curve/:studentId',
    name: 'GrowthCurve',
    component: () => import('@/views/GrowthCurvePage.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/',
    redirect: '/dashboard'
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

router.beforeEach((to, _from, next) => {
  const authStore = useAuthStore()

  if (to.meta.requiresAuth && !authStore.isAuthenticated) {
    next({ name: 'Login', query: { redirect: to.fullPath } })
    return
  }

  if (to.meta.roles && Array.isArray(to.meta.roles)) {
    const userRole = authStore.userRole
    if (!to.meta.roles.includes(userRole)) {
      next({ name: 'Dashboard' })
      return
    }
  }

  if (to.name === 'Login' && authStore.isAuthenticated) {
    next({ name: 'Dashboard' })
    return
  }

  next()
})

export default router
