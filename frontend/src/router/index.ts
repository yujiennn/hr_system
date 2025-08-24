import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/counter'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      redirect: '/login'
    },
    {
      path: '/login',
      name: 'login',
      component: () => import('../views/LoginView.vue'),
      meta: { requiresGuest: true }
    },
    {
      path: '/employee',
      name: 'employee',
      component: () => import('../views/EmployeeLayout.vue'),
      meta: { requiresAuth: true, role: 'employee' },
      children: [
        {
          path: '',
          redirect: '/employee/dashboard'
        },
        {
          path: 'dashboard',
          name: 'employee-dashboard',
          component: () => import('../views/employee/DashboardView.vue')
        },
        {
          path: 'attendance',
          name: 'employee-attendance',
          component: () => import('../views/employee/AttendanceView.vue')
        },
        {
          path: 'leave',
          name: 'employee-leave',
          component: () => import('../views/employee/LeaveView.vue')
        },
        {
          path: 'salary',
          name: 'employee-salary',
          component: () => import('../views/employee/SalaryView.vue')
        },
        {
          path: 'performance',
          name: 'employee-performance',
          component: () => import('../views/employee/PerformanceView.vue')
        },

        {
          path: 'profile',
          name: 'employee-profile',
          component: () => import('../views/employee/ProfileView.vue')
        },
        {
          path: 'face-registration',
          name: 'employee-face-registration',
          component: () => import('../views/employee/FaceRegistrationView.vue')
        }
      ]
    },
    {
      path: '/manager',
      name: 'manager',
      component: () => import('../views/ManagerLayout.vue'),
      meta: { requiresAuth: true, role: 'manager' },
      children: [
        {
          path: '',
          redirect: '/manager/dashboard'
        },
        {
          path: 'dashboard',
          name: 'manager-dashboard',
          component: () => import('../views/manager/DashboardView.vue')
        },
        {
          path: 'employees',
          name: 'manager-employees',
          component: () => import('../views/manager/EmployeeManagementView.vue')
        },
        {
          path: 'attendance',
          name: 'manager-attendance',
          component: () => import('../views/manager/AttendanceStatsView.vue')
        },
        {
          path: 'leave',
          name: 'manager-leave',
          component: () => import('../views/manager/LeaveApprovalView.vue')
        },
        {
          path: 'performance',
          name: 'manager-performance',
          component: () => import('../views/manager/PerformanceEvaluationView.vue')
        },
        {
          path: 'salary',
          name: 'manager-salary',
          component: () => import('../views/manager/SalaryManagementView.vue')
        },
        {
          path: 'profile',
          name: 'manager-profile',
          component: () => import('../views/employee/ProfileView.vue')
        }
      ]
    },
    {
      path: '/admin',
      name: 'admin',
      component: () => import('../views/AdminLayout.vue'),
      meta: { requiresAuth: true, role: 'admin' },
      children: [
        {
          path: '',
          redirect: '/admin/dashboard'
        },
        {
          path: 'dashboard',
          name: 'admin-dashboard',
          component: () => import('../views/admin/DashboardView.vue')
        },
        {
          path: 'users',
          name: 'admin-users',
          component: () => import('../views/admin/UserManagementView.vue')
        },
        {
          path: 'departments',
          name: 'admin-departments',
          component: () => import('../views/admin/DepartmentManagementView.vue')
        },
        {
          path: 'performance',
          name: 'admin-performance',
          component: () => import('../views/admin/PerformanceManagementView.vue')
        },
        {
          path: 'system',
          name: 'admin-system',
          component: () => import('../views/admin/SystemConfigView.vue')
        },
        {
          path: 'profile',
          name: 'admin-profile',
          component: () => import('../views/admin/ProfileView.vue')
        }
      ]
    }
  ],
})

// 路由守卫
router.beforeEach((to, from, next) => {
  const authStore = useAuthStore()
  
  if (to.meta.requiresAuth && !authStore.isAuthenticated) {
    next('/login')
  } else if (to.meta.requiresGuest && authStore.isAuthenticated) {
    // 根据用户角色重定向到对应页面
    const userRole = authStore.user?.user_type
    if (userRole === 'admin') {
      next('/admin')
    } else if (userRole === 'manager') {
      next('/manager')
    } else {
      next('/employee')
    }
  } else if (to.meta.role && authStore.user?.user_type !== to.meta.role && authStore.user?.user_type !== 'admin') {
    // 权限检查，管理员可以访问所有页面
    next('/login')
  } else {
    next()
  }
})

export default router
