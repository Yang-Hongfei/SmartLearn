import { createRouter, createWebHistory } from 'vue-router'
import HomePage from '../views/HomePage.vue'
import PracticePage from '../views/PracticePage.vue'
import PdfImportPage from '../views/PdfImportPage.vue'
import LearnHubPage from '../views/LearnHubPage.vue'
import LearnSessionPage from '../views/LearnSessionPage.vue'

const routes = [
  { path: '/', component: HomePage },
  { path: '/practice', component: PracticePage },
  { path: '/import', component: PdfImportPage },
  { path: '/learn-hub', component: LearnHubPage },
  { path: '/learn/session', component: LearnSessionPage },
]

export default createRouter({
  history: createWebHistory(),
  routes
})
