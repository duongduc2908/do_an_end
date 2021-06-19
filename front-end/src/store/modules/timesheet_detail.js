import { get_all_page_search,get_list } from '@/api/timesheet_detail'


const mutations = {
  
}

const actions = {
  async get_all_page_search (context, payload) {
    return new Promise((resolve, reject) => {
      get_all_page_search(payload).then(response => {
        const { data } = response
        resolve(data)
      }).catch(error => {
        reject(error)
      })
    })
  },
  async get_list (context, payload) {
    return new Promise((resolve, reject) => {
      get_list(payload).then(response => {
        const { data } = response
        resolve(data)
      }).catch(error => {
        reject(error)
      })
    })
  }
}

export default {
    namespaced: true,
    actions,
    mutations
}
