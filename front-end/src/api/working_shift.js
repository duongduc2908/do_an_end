import request from '@/utils/request'

export function getWorkingShift(param) {
  return request({
    url: '/working_shift/get_all_page_search',
    method: 'get',
    params:param
  })
}