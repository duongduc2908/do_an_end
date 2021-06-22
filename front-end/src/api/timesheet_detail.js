import request from '@/utils/request'

export function get_all_page_search(param) {
  return request({
    url: 'timesheet_detail/get_all_page_search',
    method: 'get',
    params: param
  })
}

export function get_list() {
  return request({
    url: 'timesheet_detail/get_list',
    method: 'get'
  })
}

export function addTimeSheet(param) {
  debugger
  return request({
    url: `time_sheet/${param.state == 1 ? 'create' : param.state == 2 ? 'update' : 'delete'}`,
    method: 'post',
    data:param
  })
}