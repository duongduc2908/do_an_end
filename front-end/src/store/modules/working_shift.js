
import { getWorkingShift} from '@/api/working_shift'

const mutations = {
}
const actions = {
  async getWorkingShift (context, payload) {
    debugger
    // context.commit('setCameraActivated', payload)
    return new Promise((resolve, reject) => {
        getWorkingShift(payload).then(response => {
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
