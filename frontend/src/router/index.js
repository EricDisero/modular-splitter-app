import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'
import { useAuthStore } from '../stores/auth'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: HomeView
    },
    {
      path: '/split',
      name: 'split',
      component: () => import('../views/SplitView.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/result/:jobId',
      name: 'result',
      component: () => import('../views/ResultView.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/about',
      name: 'about',
      component: () => import('../views/AboutView.vue')
    }
  ]
})

// Navigation guard to check for authentication
router.beforeEach((to, from, next) => {
  const authStore = useAuthStore()

  // Check if the route requires authentication
  if (to.meta.requiresAuth && !authStore.isAuthenticated) {
    // If not authenticated, redirect to home page
    next({ name: 'home' })
  } else {
    // Otherwise proceed as normal
    next()
  }
})

export default router