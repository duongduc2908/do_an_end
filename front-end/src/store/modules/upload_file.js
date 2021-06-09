import { remove_img,add_file } from '@/api/upload_file'


const actions = {
  remove_img(path) {
    return new Promise((resolve, reject) => {
        remove_img({ file_path: path.trim() }).then(response => {
        const { data } = response
        resolve(data)
      }).catch(error => {
        reject(error)
      })
    })
  },
  add_file(context,payload) {
    return new Promise((resolve, reject) => {
        add_file(payload).then(response => {
        resolve(response)
      }).catch(error => {
        reject(error)
      })
    })
  },
}

export default {
  namespaced: true,
  actions
}
