import { createRouter, createWebHistory, type RouteRecordRaw } from 'vue-router'
import { useFilterStore } from '@/stores/filter'

const routes: RouteRecordRaw[] = [
  {
    path: '/',
    redirect: '/workbench'
  },
  {
    path: '/workbench',
    name: 'Workbench',
    component: () => import('@/views/WorkbenchView.vue'),
    meta: { title: '求职工作台' }
  },
  {
    path: '/jobs',
    name: 'Jobs',
    component: () => import('@/views/JobsView.vue'),
    meta: { title: '岗位探索', showSlicer: true }
  },
  {
    path: '/shortlist',
    name: 'Shortlist',
    component: () => import('@/views/ShortlistView.vue'),
    meta: { title: '候选清单' }
  },
  {
    path: '/compare',
    name: 'Compare',
    component: () => import('@/views/CompareView.vue'),
    meta: { title: '岗位对比' }
  },
  {
    path: '/overview',
    name: 'Overview',
    component: () => import('@/views/OverviewView.vue'),
    meta: { title: '样本概况', showSlicer: true }
  },
  {
    path: '/salary',
    name: 'Salary',
    component: () => import('@/views/SalaryView.vue'),
    meta: { title: '薪资与地域分析', showSlicer: true }
  },
  {
    path: '/skills',
    name: 'Skills',
    component: () => import('@/views/SkillsView.vue'),
    meta: { title: '技能标签分析', showSlicer: true }
  },
  {
    path: '/:pathMatch(.*)*',
    redirect: '/workbench'
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

router.afterEach((to) => {
  const filterStore = useFilterStore()
  // Analytical slicing only belongs to the four analysis/exploration pages; the
  // workbench, shortlist and comparison must not inherit a hidden filter.
  if (to.meta.showSlicer === true) {
    filterStore.syncFromQuery(to.query)
  } else {
    filterStore.resetFilters()
  }
  if (to.meta.title) {
    document.title = `${to.meta.title} | JobInsight 职薪洞察`
  }
})

export default router
