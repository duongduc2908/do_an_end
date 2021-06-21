import request from '@/utils/request'


export function saveOrganizationUnit(param) {
  return request({
    url: `/organization_unit/${param.state==1 ? 'create' : param.state==2 ? `update?_id=${param._id}` : 'delete'}`,
    method: 'post',
    data:param
  })
}

export function getOrganizationUnits(param) {
  return request({
    url: `/organization_unit/get_all_page_search`,
    method: 'get',
    params:param
  })
}

export function getList(param) {
  return request({
    url: `/organization_unit/get_list`,
    method: 'get'
  })
}

