import { createRouter, createWebHistory, type RouteRecordRaw } from 'vue-router'
import { useFilterStore } from '@/stores/filter'

const routes: RouteRecordRaw[] = [
  {
    path: '/',
    redirect: '/overview'
  },
  {
    path: '/overview',
    name: 'Overview',
    component: () => import('@/views/OverviewView.vue'),
    meta: { title: '宏观综合总览' }
  },
  {
    path: '/salary',
    name: 'Salary',
    component: () => import('@/views/SalaryView.vue'),
    meta: { title: '薪资与地域分布' }
  },
  {
    path: '/skills',
    name: 'Skills',
    component: () => import('@/views/SkillsView.vue'),
    meta: { title: '技能图谱与技术栈' }
  },
  {
    path: '/jobs',
    name: 'Jobs',
    component: () => import('@/views/JobsView.vue'),
    meta: { title: '在招岗位多维检索' }
  },
  {
    path: '/:pathMatch(.*)*',
    redirect: '/overview'
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

router.afterEach((to) => {
  const filterStore = useFilterStore()
  filterStore.syncFromQuery(to.query)
  if (to.meta.title) {
    document.title = `${to.meta.title} | JobInsight 职薪洞察`
  }
})

export default router
