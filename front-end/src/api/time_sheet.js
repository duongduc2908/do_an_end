import request from '@/utils/request'

export function get_all_page_search(param) {
  return request({
    url: 'time_sheet/get_all_page_search',
    method: 'get',
    params: param
  })
}
