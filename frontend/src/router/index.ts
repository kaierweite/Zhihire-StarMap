import { createRouter, createWebHistory } from 'vue-router'
import type { RouteRecordRaw } from 'vue-router'
import { useAuthStore } from '@/store/auth'
import type { UserRole } from '@/types/auth'

const routes: RouteRecordRaw[] = [
  // ---- Public routes ----
  {
    path: '/',
    name: 'Home',
    component: () => import('@/views/common/HomeView.vue'),
  },
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/common/LoginView.vue'),
  },
  {
    path: '/register',
    name: 'Register',
    component: () => import('@/views/common/RegisterView.vue'),
  },

  // ---- Job seeker (USER) routes ----
  {
    path: '/user',
    component: () => import('@/views/user/UserLayout.vue'),
    meta: { requiresAuth: true, role: 'USER' },
    children: [
      { path: '', redirect: '/user/profile' },
      { path: 'profile', name: 'UserProfile', component: () => import('@/views/user/UserProfile.vue') },
      { path: 'resume', name: 'ResumeCenter', component: () => import('@/views/user/ResumeCenter.vue') },
      { path: 'ability-map', name: 'AbilityMap', component: () => import('@/views/user/AbilityMap.vue') },
      { path: 'jobs', name: 'JobRecommend', component: () => import('@/views/user/JobRecommend.vue') },
      { path: 'jobs/search', name: 'JobSearch', component: () => import('@/views/user/JobSearch.vue') },
      { path: 'jobs/:id', name: 'JobDetail', component: () => import('@/views/user/JobDetail.vue') },
      { path: 'career-plan', name: 'CareerPlan', component: () => import('@/views/user/CareerPlan.vue') },
      { path: 'interview', name: 'InterviewHome', component: () => import('@/views/user/InterviewHome.vue') },
      { path: 'interview/chat', name: 'InterviewChat', component: () => import('@/views/user/InterviewChat.vue') },
      { path: 'interview/phone', name: 'InterviewPhone', component: () => import('@/views/user/InterviewPhone.vue') },
      { path: 'interview/video', name: 'InterviewVideo', component: () => import('@/views/user/InterviewVideo.vue') },
      { path: 'interview/report', name: 'InterviewReport', component: () => import('@/views/user/InterviewReport.vue') },
      { path: 'interview/question-bank', name: 'QuestionBank', component: () => import('@/views/user/QuestionBank.vue') },
      { path: 'resume/optimize', name: 'ResumeOptimize', component: () => import('@/views/user/ResumeOptimize.vue') },
      { path: 'social', name: 'Social', component: () => import('@/views/user/SocialView.vue') },
      { path: 'notifications', name: 'UserNotifications', component: () => import('@/views/user/UserNotifications.vue') },
    ],
  },

  // ---- Enterprise (COMPANY) routes ----
  {
    path: '/company',
    component: () => import('@/views/company/CompanyLayout.vue'),
    meta: { requiresAuth: true, role: 'COMPANY' },
    children: [
      { path: '', name: 'CompanyDashboard', component: () => import('@/views/company/CompanyDashboard.vue') },
      { path: 'profile', name: 'CompanyProfileEdit', component: () => import('@/views/company/CompanyProfile.vue') },
      { path: 'jobs', name: 'JobManage', component: () => import('@/views/company/JobManage.vue') },
      { path: 'jobs/publish', name: 'JobPublish', component: () => import('@/views/company/JobPublish.vue') },
      { path: 'jobs/detail/:id', name: 'CompanyJobDetail', component: () => import('@/views/company/JobDetail.vue') },
      { path: 'jobs/ability-map/:id', name: 'JobAbilityMap', component: () => import('@/views/company/JobAbilityMap.vue') },
      { path: 'screening', name: 'SmartScreening', component: () => import('@/views/company/SmartScreening.vue') },
      { path: 'candidates', name: 'CandidateRecommend', component: () => import('@/views/company/CandidateRecommend.vue') },
      { path: 'notifications', name: 'CompanyNotifications', component: () => import('@/views/company/CompanyNotifications.vue') },
    ],
  },

  // ---- Admin routes ----
  {
    path: '/admin',
    component: () => import('@/views/admin/AdminLayout.vue'),
    meta: { requiresAuth: true, role: 'ADMIN' },
    children: [
      { path: '', name: 'AdminDashboard', component: () => import('@/views/admin/AdminDashboard.vue') },
      { path: 'users', name: 'UserManage', component: () => import('@/views/admin/UserManage.vue') },
      { path: 'companies', name: 'CompanyManage', component: () => import('@/views/admin/CompanyManage.vue') },
      { path: 'audit', name: 'AuditManage', component: () => import('@/views/admin/AuditManage.vue') },
      { path: 'logs', name: 'SystemLogs', component: () => import('@/views/admin/SystemLogs.vue') },
      { path: 'ai-model', name: 'AIModelConfig', component: () => import('@/views/admin/AIModelConfig.vue') },
    ],
  },

  // ---- Catch-all ----
  {
    path: '/:pathMatch(.*)*',
    redirect: '/',
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

// Role-based navigation guard
router.beforeEach((to, _from, next) => {
  const authStore = useAuthStore()
  const requiresAuth = to.meta.requiresAuth as boolean | undefined
  const requiredRole = to.meta.role as UserRole | undefined

  if (!requiresAuth) {
    // Public route — allow
    // Redirect logged-in users away from login/register
    if (authStore.isLoggedIn && (to.name === 'Login' || to.name === 'Register')) {
      const roleRoutes: Record<UserRole, string> = {
        ADMIN: '/admin',
        USER: '/user',
        COMPANY: '/company',
      }
      next(roleRoutes[authStore.role as UserRole] || '/login')
      return
    }
    next()
    return
  }

  // Protected route — check auth
  if (!authStore.isLoggedIn) {
    next({ name: 'Login', query: { redirect: to.fullPath } })
    return
  }

  // Check role
  if (requiredRole && authStore.role !== requiredRole) {
    // Wrong role — send to their own dashboard
    const roleRoutes: Record<UserRole, string> = {
      ADMIN: '/admin',
      USER: '/user',
      COMPANY: '/company',
    }
    next(roleRoutes[authStore.role as UserRole] || '/login')
    return
  }

  next()
})

export default router
