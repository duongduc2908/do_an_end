
import { getShiftPlan} from '@/api/shift_plan'

const mutations = {
}
const actions = {
  async getShiftPlan (context, payload) {
    return new Promise((resolve, reject) => {
        getShiftPlan(payload).then(response => {
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
