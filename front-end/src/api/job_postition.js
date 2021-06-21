import request from '@/utils/request'


export function saveJobPosition(param) {
  return request({
    url: `/job_position/${param.state==1 ? 'create' : param.state==2 ? `update?_id=${param._id}` : 'delete'}`,
    method: 'post',
    data:param
  })
}

export function getJobPositions(param) {
  return request({
    url: `/job_position/get_all_page_search`,
    method: 'get',
    params:param
  })
}

export function getByOg(param) {
  return request({
    url: `/job_position/get_by_og`,
    method: 'get',
    params:param
  })
}

