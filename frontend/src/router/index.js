import { createRouter, createWebHistory } from 'vue-router'
import PracticePage from '../views/PracticePage.vue'
import PdfImportPage from '../views/PdfImportPage.vue'

const routes = [
  { path: '/', redirect: '/practice' },
  { path: '/practice', component: PracticePage },
  { path: '/import', component: PdfImportPage }
]

export default createRouter({
  history: createWebHistory(),
  routes
})
