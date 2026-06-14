import { createRouter, createWebHashHistory } from 'vue-router'

const routes = [
  { path: '/', redirect: '/login' },
  { path: '/login', name: 'login', component: () => import('../views/Login.vue') },
  { path: '/work/dashboard', name: 'dashboard', component: () => import('../views/Dashboard.vue') },
  { path: '/work/projects/:id', name: 'project-detail', component: () => import('../views/ProjectDetail.vue') },
  { path: '/work/projects', name: 'projects', component: () => import('../views/Projects.vue') },
  { path: '/work/customers/:id', name: 'customer-detail', component: () => import('../views/CustomerDetail.vue') },
  { path: '/work/customers', name: 'customers', component: () => import('../views/Customers.vue') },
  { path: '/work/channels', name: 'channels', component: () => import('../views/Channels.vue') },
  { path: '/work/products', name: 'products', component: () => import('../views/ProductList.vue') },
  { path: '/work/sales', name: 'sales', component: () => import('../views/Sales.vue') },
  { path: '/work/reports', name: 'reports', component: () => import('../views/Reports.vue') },
]

const router = createRouter({
  history: createWebHashHistory(),
  routes,
})

router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('token')
  if (to.name !== 'login' && !token) {
    next({ name: 'login' })
  } else if (to.name === 'login' && token) {
    next({ name: 'dashboard' })
  } else {
    next()
  }
})

export default router
