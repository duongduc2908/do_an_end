import { getOrganizationUnits,saveOrganizationUnit,getList } from '@/api/organization_unit'


const mutations = {
  
}

const actions = {
  async getOrganizationUnits (context, payload) {
    return new Promise((resolve, reject) => {
      getOrganizationUnits(payload).then(response => {
        const { data } = response
        resolve(data)
      }).catch(error => {
        reject(error)
      })
    })
  },
  async saveOrganizationUnit (context, payload) {
    return new Promise((resolve, reject) => {
      saveOrganizationUnit(payload).then(response => {
        const { data } = response
        resolve(data)
      }).catch(error => {
        reject(error)
      })
    })
  },
  async getList (context, payload) {
    return new Promise((resolve, reject) => {
      getList(payload).then(response => {
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
