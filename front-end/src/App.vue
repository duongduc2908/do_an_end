<template>
  <div id="app">
    <router-view />
  </div>
</template>

<script>
import Vue from 'vue'
import io from 'socket.io-client'
import "@/assets/styles/main.scss"
import VueSocketio from 'vue-socket-io';
import createShiftPlan from "@/utils/merge_date_plan"

export default {
  name: 'App',
  created(){
    this.initSocket();
  },
  methods:{
    initSocket(){
      const socket =  Vue.use(VueSocketio, 'http://localhost:4321/');
      this.$socket.on('imageConversionByClient', (obj) => {
        // let binary = ''
        // const bytes = new Uint8Array(obj.buffer)
        // const len = bytes.byteLength
        // for (let i = 0; i < len; i++) {
        //   binary += String.fromCharCode(bytes[i])
        // }
        // this.url = 'data:image/jpeg;base64,' + window.btoa(binary)
      });
      this.$socket.on('schedule_shift_plan',(obj)=>{
        obj.forEach(shift_plan => {
          createShiftPlan(shift_plan).forEach(day => {
            if(day.toISOString().slice(0, 10) == new Date().toISOString().slice(0, 10) ){
               shift_plan.ShiftPlanDay = day
               this.$store.dispatch(`shift_plan_employee/addShiftPlanEmployee`,shift_plan)
            }
          });
        });
        console.log(obj);
      })
    }
  }
}
</script>
