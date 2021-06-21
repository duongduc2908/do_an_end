import { getJobPositions,saveJobPosition,getByOg } from '@/api/job_postition'


const mutations = {
  
}

const actions = {
  async getJobPositions (context, payload) {
    return new Promise((resolve, reject) => {
      getJobPositions(payload).then(response => {
        const { data } = response
        resolve(data)
      }).catch(error => {
        reject(error)
      })
    })
  },
  async saveJobPosition (context, payload) {
    return new Promise((resolve, reject) => {
        saveJobPosition(payload).then(response => {
        const { data } = response
        resolve(data)
      }).catch(error => {
        reject(error)
      })
    })
  },
  async getByOg (context, payload) {
    return new Promise((resolve, reject) => {
        getByOg(payload).then(response => {
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
