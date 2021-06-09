import request from '@/utils/request'
import { array } from 'jszip/lib/support';

export function remove_img(img_path) {
  return request({
    url: 'file/remove_train',
    method: 'delete',
    data: img_path
  })
}
export function add_file(data) {
  debugger
  let formData = new FormData();
  data.listFile.forEach((val,index) => {
    formData.append('file'+index, val.file ? val.file : val);
  });
  let MaNV = data.MaNV
  return request({
    url: 'file/upload_train',
    method: 'post',
    data: formData,
    params:{MaNV:MaNV}
  })
}