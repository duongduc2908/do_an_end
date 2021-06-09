import request from '@/utils/request'

export function login(data) {
  return request({
    url: 'auth/login',
    method: 'post',
    data
  })
}

export function getInfo() {
  return request({
    url: 'user/get_info',
    method: 'get',
  })
}

export function logout() {
  return request({
    url: 'auth/logout',
    method: 'delete'
  })
}

export function get_all_page_search(param) {
  return request({
    url: 'user/get_all_page_search',
    method: 'get',
    params: param
  })
}

export function saveUser(data) {
  return request({
    url: `user/${data.state == 1 ? 'create' : data.state == 2 ? 'update' : 'delete'}`,
    method: 'post',
    data: data
  })
}

export function train(data) {
  return request({
    url: `http://localhost:4321/api/stream/connection_api/train`,
    method: 'post'
  })
}

export function insertFileAvatar(param) {
  return request({
    url: 'file/avatar',
    method: 'post',
    headers: {
      "Content-Type": "multipart/form-data",
    },
    data: param
  })
}
