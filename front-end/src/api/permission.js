import request from '@/utils/request'

export function get_default_permission() {
  return request({
    url: 'subsystem_permission/get_all_sub_items',
    method: 'get',
  })
}

export function save_permission(data) {
  return request({
    url: `role_permission/${data.state == 1 ? 'create' : data.state == 2 ? 'update' : 'delete'}`,
    method: 'post',
    data:data
  })
}
