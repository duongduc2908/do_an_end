
import {getWorkingShift,save_WorkingShift} from '@/api/working_shift'

const mutations = {
}
const actions = {
  async getWorkingShift (context, payload) {
    return new Promise((resolve, reject) => {
        getWorkingShift(payload).then(response => {
        const { data } = response
        resolve(data)
      }).catch(error => {
        reject(error)
      })
    })

  },
  async save_WorkingShift (context, payload) {
    // context.commit('setCameraActivated', payload)
    return new Promise((resolve, reject) => {
      save_WorkingShift(payload).then(response => {
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
