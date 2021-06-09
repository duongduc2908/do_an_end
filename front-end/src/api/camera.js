import request from '@/utils/request'

export function actionCamera(param) {
  return request({
    
    url: `http://localhost:4321/api/stream/connection_api/${!param.isActive ? "connect" : "disconnect"}?camera_id=${param._id}${ !param.isActive ? `&rtsp_link=${param.link_stream}&username&password&selectedProtocol=1`  : ""}`,
    method: 'get',
    params: param
  })
}
export function changeFlag(param) {
  return request({
    
    url: `http://localhost:4321/api/stream/connection_api/changeFlag`,
    method: 'get'
  })
}
export function getDataTranning(param) {
  return request({
    url: `http://localhost:4321/api/stream/connection_api/begin_train`,
    method: 'get',
    params: param
  })
}

export function saveDataTranning(param) {
  return request({
    url: `http://localhost:4321/api/stream/connection_api/train`,
    method: 'post',
    params:param
  })
}

export function saveCamera(param) {
  return request({
    url: `http://localhost:4321/api/v1/camera/${param.state==1 ? 'create' : param.state==2 ? `update?_id=${param._id}` : 'delete'}`,
    method: 'post',
    data:param
  })
}

export function getCameraPaging(param) {
  return request({
    url: `http://localhost:4321/api/v1/camera/get_all_page_search`,
    method: 'get',
    params:param
  })
}

export function insertFileCamera(param) {
  return request({
    url: `http://localhost:4321/api/v1/file/file_camera`,
    method: 'post',
    headers: {
      "Content-Type": "multipart/form-data",
    },
    data:param
  })
}

