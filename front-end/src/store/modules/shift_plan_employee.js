
import { addShiftPlanEmployee} from '@/api/shift_plan_employee'

const mutations = {
}
const actions = {
  async addShiftPlanEmployee (context, payload) {
    return new Promise((resolve, reject) => {
        addShiftPlanEmployee(payload).then(response => {
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
