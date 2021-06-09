import request from '@/utils/request'

export function getShiftPlan(param) {
  return request({
    url: '/shift_plan/get_all_page_search',
    method: 'get',
    params:param
  })
}