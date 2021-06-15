import request from '@/utils/request'

export function addShiftPlanEmployee(param) {
  return request({
    url: '/shift_plan_employee/create',
    method: 'post',
    data:param
  })
}