
import { getRoles } from '@/api/role'

const mutations = {
}
const actions = {
  async getRoles (context, payload) {
    debugger
    // context.commit('setCameraActivated', payload)
    return new Promise((resolve, reject) => {
        getRoles(payload).then(response => {
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
