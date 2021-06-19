import request from '@/utils/request'

export function get_all_page_search(param) {
  return request({
    url: 'timekeeper_data/get_all_page_search',
    method: 'get',
    params: param
  })
}
