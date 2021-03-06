import Vue from 'vue'
import Router from 'vue-router'

Vue.use(Router)

/* Layout */
import Layout from '@/layout'

/* Router Modules */
import componentsRouter from './modules/components'
import chartsRouter from './modules/charts'
import tableRouter from './modules/table'
import nestedRouter from './modules/nested'

/**
 * Note: sub-menu only appear when route children.length >= 1
 * Detail see: https://panjiachen.github.io/vue-element-admin-site/guide/essentials/router-and-nav.html
 *
 * hidden: true                   if set true, item will not show in the sidebar(default is false)
 * alwaysShow: true               if set true, will always show the root menu
 *                                if not set alwaysShow, when item has more than one children route,
 *                                it will becomes nested mode, otherwise not show the root menu
 * redirect: noRedirect           if set noRedirect will no redirect in the breadcrumb
 * name:'router-name'             the name is used by <keep-alive> (must set!!!)
 * meta : {
    roles: ['admin','editor']    control the page roles (you can set multiple roles)
    title: 'title'               the name show in sidebar and breadcrumb (recommend set)
    icon: 'svg-name'/'el-icon-x' the icon show in the sidebar
    noCache: true                if set true, the page will no be cached(default is false)
    affix: true                  if set true, the tag will affix in the tags-view
    breadcrumb: false            if set false, the item will hidden in breadcrumb(default is true)
    activeMenu: '/example/list'  if set path, the sidebar will highlight the path you set
  }
 */

/**
 * constantRoutes
 * a base page that does not have permission requirements
 * all roles can be accessed
 */
export const constantRoutes = [
  {
    path: '/redirect',
    component: Layout,
    hidden: true,
    children: [
      {
        path: '/redirect/:path(.*)',
        component: () => import('@/views/redirect/index')
      }
    ]
  },
  {
    path: '/login',
    component: () => import('@/views/login/index'),
    hidden: true
  },
  {
    path: '/auth-redirect',
    component: () => import('@/views/login/auth-redirect'),
    hidden: true
  },
  {
    path: '/404',
    component: () => import('@/views/error-page/404'),
    hidden: true
  },
  {
    path: '/401',
    component: () => import('@/views/error-page/401'),
    hidden: true
  },
  {
    path: '/',
    component: Layout,
    redirect: '/dashboard',
    children: [
      {
        path: 'dashboard',
        component: () => import('@/views/dashboard/index'),
        name: 'B???ng tin',
        meta: { title: 'B???ng tin', icon: 'dashboard', affix: true }
      }
    ]
  },
  {
    path: '/profile',
    component: Layout,
    redirect: '/profile/index',
    hidden: true,
    children: [
      {
        path: 'index',
        component: () => import('@/views/profile/index'),
        name: 'Profile',
        meta: { title: 'Profile', icon: 'user', noCache: true }
      }
    ]
  }
]

/**
 * asyncRoutes
 * the routes that need to be dynamically loaded based on user roles
 */
export const asyncRoutes = [
  {
    path: '/user',
    component: Layout,
    redirect: '/table/complex-table',
    name: 'working-shift',
    meta: {
      title: 'Nh??n s??? ',
      icon: 'peoples',
      roles: ['admin']
    },
    children: [
      {
        path: 'list-user',
        component: () => import('@/views/user/list_user'),
        name: 'DynamicTable',
        meta: { title: 'QL nh??n s???' }
      },
      {
        path: 'bo-phan',
        component: () => import('@/views/user/list_position'),
        name: 'DragTable',
        meta: { title: 'Qu???n l?? b??? ph???n ' }
      },
      {
        path: 'phong-ban',
        component: () => import('@/views/user/list_organization'),
        name: 'DragTable',
        meta: { title: 'Qu???n l?? ph??ng ban ' }
      }]
  },
  {
  path: '/working-shift',
  component: Layout,
  redirect: '/table/complex-table',
  name: 'working-shift',
  meta: {
    title: 'Ca l??m vi???c ',
    icon: 'skill'
  },
  children: [
    {
      path: 'WorkingShift',
      component: () => import('@/views/working-shift/list_working_shift'),
      name: 'WorkingShift',
      meta: { title: 'Qu???n l?? ca' }
    },
    {
      path: 'inline-edit-table',
      component: () => import('@/views/ca-lam/list_shift_plan'),
      name: 'InlineEditTable',
      meta: { title: 'Ph??n ca chi ti???t' }
    }]
  },
  {
    path: '/camera',
    component: Layout,
    redirect: '/table/complex-table',
    name: 'Camera ch???m c??ng',
    meta: {
      title: 'Camera ch???m c??ng',
      icon: 'eye-open',
      roles: ['admin'] // you can set roles in root nav
    },
    children: [
      {
        path: 'list-camera',
        component: () => import('@/views/camera/list_camera'),
        name: 'Danh s??ch camera ',
        meta: {
          title: 'Danh s??ch camera ',
          roles: ['admin'] // or you can only set roles in sub nav
        }
      },
      {
        path: 'du-lieu-cham-cong',
        component: () => import('@/views/cham-cong/data_camera'),
        name: 'D??? li???u ch???m c??ng',
        meta: {
          title: 'D??? li???u ch???m c??ng',
          roles: ['admin']
          // if do not set roles, means: this page does not require permission
        }
      },
      {
        path: 'inline-edit-table',
        component: () => import('@/views/cham-cong/time_sheet_detail'),
        name: 'B???ng ch???m c??ng',
        meta: {
          title: 'B???ng ch???m c??ng',
          roles: ['admin']
        }
      }
    ]
  },
  {
    path: '/permission',
    component: Layout,
    redirect: '/permission/page',
    alwaysShow: true, // will always show the root menu
    name: 'Quy???n ng?????i d??ng',
    meta: {
      title: 'Quy???n ng?????i d??ng',
      icon: 'lock',
      roles: ['admin'] // you can set roles in root nav
    },
    children: [
      {
        path: 'role',
        component: () => import('@/views/permission/role'),
        name: 'Danh s??ch quy???n',
        meta: {
          title: 'Danh s??ch quy???n',
          roles: ['admin']
        }
      }
    ]
  },
  { path: '*', redirect: '/404', hidden: true }
]

const createRouter = () => new Router({
  // mode: 'history', // require service support
  scrollBehavior: () => ({ y: 0 }),
  routes: constantRoutes
})

const router = createRouter()

// Detail see: https://github.com/vuejs/vue-router/issues/1234#issuecomment-357941465
export function resetRouter() {
  const newRouter = createRouter()
  router.matcher = newRouter.matcher // reset router
}

export default router
