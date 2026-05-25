import { createRouter, createWebHistory } from 'vue-router'
import HomePage from '../views/HomePage.vue'
import PracticePage from '../views/PracticePage.vue'
import PdfImportPage from '../views/PdfImportPage.vue'
import LearnHubPage from '../views/LearnHubPage.vue'
import LearnSessionPage from '../views/LearnSessionPage.vue'
import LoginPage from '../views/LoginPage.vue'
import { isLoggedIn } from '../api/authApi'

const routes = [
  { path: '/login', component: LoginPage },
  { path: '/', component: HomePage },
  { path: '/practice', component: PracticePage, meta: { auth: true } },
  { path: '/import', component: PdfImportPage, meta: { auth: true } },
  { path: '/learn-hub', component: LearnHubPage, meta: { auth: true } },
  { path: '/learn/session', component: LearnSessionPage, meta: { auth: true } },
]

const router = createRouter({ history: createWebHistory(), routes })

router.beforeEach((to, from, next) => {
  if (to.meta.auth && !isLoggedIn()) {
    next('/login')
  } else {
    next()
  }
})

export default router
