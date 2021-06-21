<template>
  <div class="app-container">
    <div class="filter-container">
      <div style="display: flex;justify-content: space-between">
        <div>
          <el-input
            v-model="listQuery.text_search"
            placeholder="Tìm kiếm phòng ban"
            style="width: 200px;"
            class="filter-item"
            @keyup.enter.native="handleFilter"
          />
        </div>
      </div>

      <el-button
        v-waves
        class="filter-item"
        type="primary"
        icon="el-icon-search"
        @click="handleFilter"
      >
        Tìm kiếm
      </el-button>
      <el-button
        @click="addOrganizationUnit"
        class="filter-item"
        style="margin-left: 10px;"
        type="primary"
        icon="el-icon-edit"
      >
       Thêm mới
      </el-button>
    </div>

    <el-table
      v-if="list && list.length"
      :key="tableKey"
      v-loading="listLoading"
      :data="list"
      border
      fit
      highlight-current-row
      style="width: 100%;"
    >
      <el-table-column label="Tên phòng ban" align="center">
        <template slot-scope="{ row }">
          <span>{{ row.OrganizationUnitName }}</span>
        </template>
      </el-table-column>
      <el-table-column label="Mã phòng ban" align="center">
        <template slot-scope="{ row }">
          <span>{{ row.OrganizationUnitCode }}</span>
        </template>
      </el-table-column>
      <el-table-column
        label="Actions"
        align="center"
        width="300"
        class-name="small-padding fixed-width"
      >
        <template slot-scope="{ row, $index }">
          <el-button type="primary" size="mini" @click="editPosition(row)">
            Sửa
          </el-button>
          <el-button
            size="mini"
            type="danger"
            @click="confirmDeleteOrganizationUnit(row, $index)"
          >
            Xóa
          </el-button>
        </template>
      </el-table-column>
    </el-table>

    <pagination
      v-show="total > 0"
      :total="total"
      :page.sync="listQuery.page"
      :limit.sync="listQuery.limit"
      @pagination="getList"
    />

    <el-dialog
      v-if="dialogFormVisible"
      width="1000px"
      height="700px"
      :title="textMap[dialogStatus]"
      :visible.sync="dialogFormVisible"
    >
      <el-form
        ref="dataForm"
        :rules="rules"
        :model="temp"
        label-position="left"
        label-width="200px"
        style="margin:0 50px;"
      >
        <div>
          <h2>Thông tin chung</h2>
        </div>
        <div class="w-100">
          <el-form-item label="Tên phòng ban " prop="OrganizationUnitName">
            <el-input v-model="temp.OrganizationUnitName" />
          </el-form-item>
        </div>
        <div class="w-100">
          <el-form-item label="Mã phòng ban " prop="OrganizationUnitCode">
            <el-input v-model="temp.OrganizationUnitCode" />
          </el-form-item>
        </div>
      </el-form>
      <div slot="footer" class="dialog-footer">
        <el-button @click="dialogFormVisible = false">
          Hủy
        </el-button>
        <el-button type="primary" @click="saveOrganizationUnit">
         Xác nhận
        </el-button>
      </div>
    </el-dialog>
  </div>
</template>
<script>
import Pagination from "@/components/Pagination";
export default {
  components: { Pagination },
  data() {
    return {
      temp: {
        _id: "",
        OrganizationUnitName:"",
        OrganizationUnitCode:"",
        state: ""
      },
      rules: {
       
      },
      dialogType: "",
      dialogFormVisible: false,
      listQuery: {
        page: 1,
        limit: 20,
        text_search: undefined,
      },
      list: null,
      total: 0,
      listLoading: true,
      tableKey: 0,
      textMap: {
        update: "Edit",
        create: "Create"
      },
      dialogStatus: ""
    };
  },
  created() {
    this.getList();
  },
  methods: {
    getList() {
      this.listLoading = true;
      let query_filter = `{"$and": [`;
      query_filter += this.listQuery?.text_search
        ? `{"$or":[{"OrganizationUnitCode": {"$regex": "${this.listQuery.text_search}", "$options": "$i"}},
                    {"OrganizationUnitName": {"$regex": "${this.listQuery.text_search}", "$options": "$i"}},]},`
        : "";
      query_filter += `]}`;
      let index = query_filter.lastIndexOf(",");
      if (index > 0) {
        query_filter =
          query_filter.substring(0, index) + query_filter.slice(index + 1);
      }
      let param = {
        page_size: this.listQuery.limit,
        page_number: this.listQuery.page,
        query_filter: query_filter
      };
      console.log(param);
      this.$store.dispatch(`organization_unit/getOrganizationUnits`, param).then(res => {
        this.list = res.results;
        this.total = res.totals;
        this.listLoading = false;
      });
    },
    handleFilter() {
      this.listQuery.page = 1;
      this.getList();
    },
    addOrganizationUnit() {
      // if(this.checkRolePermission("Add",this.subsystem_code)){
      this.temp = {};
      this.temp.state = 1;
      this.dialogFormVisible = true;
      this.dialogType = "add";
      // }
    },
    deleteOrganizationUnit(data) {
      if (!data) {
        return;
      }
      data.state = 3;
      this.$store
        .dispatch("organization_unit/saveOrganizationUnit", data)
        .then(res => {
          this.getRoles();
          this.$notify({
            title: "Success",
            dangerouslyUseHTMLString: true,
            message: `
              <div>Ten ca: ${this.temp.WorkingShiftName}</div>
              <div>Ma ca: ${this.temp.WorkingShiftCode}</div>
            `,
            type: "success"
          });
        });
    },
    confirmDeleteOrganizationUnit(row, $index) {
      debugger;
      this.$confirm("Ban co chac muon xoa ca lam viec ?", "Warning", {
        confirmButtonText: "Confirm",
        cancelButtonText: "Cancel",
        type: "warning"
      })
        .then(async () => {
          await this.deleteOrganizationUnit(row);
          this.list.splice($index, 1);
          this.$message({
            type: "success",
            message: "Delete succed!"
          });
        })
        .catch(err => {
          console.error(err);
        });
    },
    saveOrganizationUnit() {
      this.temp.state = this.dialogType === "edit" ? 2 : 1;
      debugger
      this.$store.dispatch("organization_unit/saveOrganizationUnit", this.temp).then(res => {
          this.getList();
          this.dialogFormVisible = false;
          this.$notify({
            title: "Success",
            dangerouslyUseHTMLString: true,
            message: `
              <div>Tên phòng ban : ${this.temp.OrganizationUnitName}</div>
              <div>Mã phòng ban: ${this.temp.OrganizationUnitCode}</div>
            `,
            type: "success"
          });
        });
    },
    editPosition(data){
        this.dialogType = "edit"
        this.dialogFormVisible = true;
        this.temp = data
    }
  }
};
</script>
<style lang="scss">
.el-form-item__content {
  // margin-left: 24px !important;
  margin: 0px !important;
  width: calc(100% - 120px);
  display: flex;
}
.el-form-item__label {
  width: 120px !important;
}
.el-dialog {
  margin-top: 5vh !important;
}
</style>
