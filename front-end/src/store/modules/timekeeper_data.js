import { get_all_page_search } from '@/api/timekeeper_data'


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
  }
}

export default {
    namespaced: true,
    actions,
    mutations
}
