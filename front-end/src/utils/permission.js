import store from '@/store'

/**
 * @param {Array} value
 * @returns {Boolean}
 * @example see @/views/permission/directive.vue
 */
export function checkPermission(value) {
  if (value && value instanceof Array && value.length > 0) {
    const roles = store.getters && store.getters.roles
    const permissionRoles = value

    const hasPermission = roles.some(role => {
      return permissionRoles.includes(role)
    })
    return hasPermission
  } else {
    console.error(`need roles! Like v-permission="['admin','editor']"`)
    return false
  }
}

export default function checkRolePermission(action, subsystem_code, isShowMessage){
  const role_permissions = store.getters && store.getters.role_permissions;

  let item = role_permissions.find(x=>x.subsystem_code.toLowerCase() == subsystem_code.toLowerCase());
  if(item && item.permission_code.find(x=>x.code == action && x.isCheck)){
    return true;
  }
  if(isShowMessage){
    this.$notify({
      title: 'Thông báo',
      dangerouslyUseHTMLString: true,
      message: `Bạn không có quyền thực hiện thao tác này`,
      type: 'error'
    })
  }
  return false;
}
