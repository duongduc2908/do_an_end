import request from '@/utils/request'

export function getWorkingShift(param) {
  return request({
    url: '/working_shift/get_all_page_search',
    method: 'get',
    params:param
  })
}
export function save_WorkingShift(data) {
  return request({
    url: `working_shift/${data.state == 1 ? 'create' : data.state == 2 ? 'update' : 'delete'}`,
    method: 'post',
    data:data
  })
}