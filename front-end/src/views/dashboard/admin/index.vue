<template>
  <div class="dashboard-editor-container" v-if="checkRolePermission('View', subsystem_code, false)">
    <!-- <github-corner class="github-corner" /> -->

    <panel-group @handleSetLineChartData="handleSetLineChartData" />
  </div>
</template>

<script>
import PanelGroup from "./components/PanelGroup";
import checkRolePermission from "@/utils/permission";

export default {
  name: "DashboardAdmin",
  components: {
    PanelGroup
  },
  methods: {
    handleSetLineChartData(type) {
      this.lineChartData = lineChartData[type];
    },
    checkRolePermission
  },
  data() {
    return {
      subsystem_code: "BANG_TIN",
    };
  }
};
</script>

<style lang="scss" scoped>
.dashboard-editor-container {
  padding: 15px;
  background-color: rgb(240, 242, 245);
  position: relative;
}
</style>
