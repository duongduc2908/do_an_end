
import { actionCamera, getDataTranning, saveDataTranning, saveCamera, getCameraPaging,insertFileCamera,changeFlag} from '@/api/camera'

const mutations = {
    setCameraActivated (state, payload) {
        // const place = state.places.find(p => p._id === payload.placeId)
        // const camera = place.cameras.find(c => c.camera_id === payload.cameraId)

        camera.activated = true
    },
}
const actions = {
  async actionCamera (context, payload) {
    // context.commit('setCameraActivated', payload)
    return new Promise((resolve, reject) => {
        actionCamera(payload).then(response => {
        const { data } = response
        resolve(data)
      }).catch(error => {
        reject(error)
      })
    })

  },

  async getDataTranning (context, payload) {
    return new Promise((resolve, reject) => {
      getDataTranning(payload).then(response => {
        const { data } = response
        resolve(data)
      }).catch(error => {
        reject(error)
      })
    })

  },
  async changeFlag (context, payload) {
    return new Promise((resolve, reject) => {
      changeFlag(payload).then(response => {
        const { data } = response
        resolve(data)
      }).catch(error => {
        reject(error)
      })
    })

  },
  async saveDataTranning (context, payload) {
    return new Promise((resolve, reject) => {
      saveDataTranning(payload).then(response => {
        const { data } = response
        resolve(data)
      }).catch(error => {
        reject(error)
      })
    })

  },

  async saveCamera (context, payload) {
    return new Promise((resolve, reject) => {
      saveCamera(payload).then(response => {
        const { data } = response
        resolve(data)
      }).catch(error => {
        reject(error)
      })
    })

  },
  
  async getCameraPaging (context, payload) {
    return new Promise((resolve, reject) => {
      getCameraPaging(payload).then(response => {
        const { data } = response
        resolve(data)
      }).catch(error => {
        reject(error)
      })
    })

  },
  async insertFileCamera (context, payload) {
    return new Promise((resolve, reject) => {
      insertFileCamera(payload).then(response => {
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
