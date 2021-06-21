import request from '@/utils/request'

export function getShiftPlan(param) {
  return request({
    url: '/shift_plan/get_all_page_search',
    method: 'get',
    params:param
  })
}

export function addShiftPlan(param) {
  return request({
    url: '/shift_plan/create',
    method: 'post',
    data:param
  })
}

export function deleteShiftPlan(param) {
  return request({
    url: '/shift_plan/delete',
    method: 'post',
    data:param
  })
}