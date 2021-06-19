<template>
  <div class="dashboard-container">
    <component :is="currentRole" />
    <!-- <div @click="getDataTranning" v-if="!(listImg && listImg.length >=5) || !isTraining"
      class="cursor tags-view-item tags-view-item-active m-b-16" style="width: fit-content;margin-left: 24px">
      Lây dư liệu trainning 
    </div> -->
    <!-- <div @click="saveDataTranning" v-if="listImg && listImg.length >=5 && isTraining"
      class="cursor tags-view-item tags-view-item-active m-b-16" style="width: fit-content;margin-left: 24px">
      Traning 
    </div> -->
    <div class="p-24 flex" v-if=this.url>
      <div style="width:75%">
        <img class="img-current w-full" :src="url">
      </div>
      <div class="list-imt-his">
        <img v-for="(item,index) in listImg" :key="index" class="img-his" :src="item">
      </div>
    </div>
  </div>
</template>

<script>
import { mapGetters } from 'vuex'
import adminDashboard from './admin'
import editorDashboard from './editor'

export default {
  name: 'Dashboard',
  components: { adminDashboard, editorDashboard },
  data() {
    return {
      currentRole: 'adminDashboard',
      listImg: [],
      url: null,
      countImg:10,
      isTraining:false
    }
  },
  computed: {
    ...mapGetters([
      'roles',
    ])
  },
  created() {
    if (!this.roles.includes('admin')) {
      this.currentRole = 'editorDashboard'
    }
  },
  mounted() {
    this.$socket.on('imageConversionByClient', (obj) => {
      let binary = ''
      const bytes = new Uint8Array(obj.buffer)
      const len = bytes.byteLength
      for (let i = 0; i < len; i++) {
        binary += String.fromCharCode(bytes[i])
      }
      this.url = 'data:image/jpeg;base64,' + window.btoa(binary)
    }),

    this.$socket.on('imageBoxToClient', (obj) => {
      this.listImg.unshift(obj.img_path)
      if (this.listImg && this.listImg.length > this.countImg && !this.isTraining) {
        this.listImg.splice(this.countImg, 1)
      }
    })
  },
  methods:{
    /**
     * Created by DVDucDbuo_i
     */
    // getDataTranning(param=null){
    // this.isTraining = true;
    // this.listImg = [];
    // this.countImg = 5;
    //   param = {
    //     "full_name":""
    //   }
    //   return this.$store.dispatch(`camera/getDataTranning`, param);
    // },

    // saveDataTranning(){
    //   this.countImg = 10;
    //   this.$store.dispatch(`camera/saveDataTranning`, this.listImg);
    //   setTimeout(()=>{
    //     this.isTraining = false;
    //     this.listImg = [];
    //   },500)
    // }
  }

}
</script>

<style lang="scss" scoped>
.img-current{
  height: 772px;
}
.list-imt-his{
  overflow: auto;
  width: 25%;
  height: 772px;
}
.img-his{
  margin: 0 16px 8px 16px;
  width: calc(100% - 32px);
  height: 250px;
}
.tags-view-item {
    .el-icon-close {
      width: 16px;
      height: 16px;
      vertical-align: 2px;
      border-radius: 50%;
      text-align: center;
      transition: all .3s cubic-bezier(.645, .045, .355, 1);
      transform-origin: 100% 50%;
      &:before {
        transform: scale(.6);
        display: inline-block;
        vertical-align: -3px;
      }
      &:hover {
        background-color: #b4bccc;
        color: #fff;
      }
    }
  }

.tags-view-item-active{
    background-color: #42b983;
    color: #fff;
    border-color: #42b983;
    padding: 8px;
    border-radius: 4px;
    font-size: 13px;
  }
  .tags-view-item-unactive{
    background-color: #ef4d4d !important;
    border-color: #ef4d4d !important;
  }
</style>
