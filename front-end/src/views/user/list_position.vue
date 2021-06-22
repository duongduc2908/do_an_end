<template>
  <div
    class="app-container"
    v-if="checkRolePermission('View', subsystem_code, false)"
  >
    <div class="filter-container">
      <div style="display: flex;justify-content: space-between">
        <div>
          <el-input
            v-model="listQuery.text_search"
            placeholder="Tim kiem vi tri"
            style="width: 200px;"
            class="filter-item"
            @keyup.enter.native="handleFilter"
          />
        </div>
      </div>

      <el-button
        class="filter-item"
        type="primary"
        icon="el-icon-search"
        @click="handleFilter"
      >
        Tìm kiếm
      </el-button>
      <el-button
        @click="addJobPosition"
        class="filter-item"
        style="margin-left: 10px;"
        type="primary"
        icon="el-icon-edit"
        v-if="checkRolePermission('Add', subsystem_code, false)"
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
      <el-table-column label="Tên vị trí" align="center">
        <template slot-scope="{ row }">
          <span>{{ row.JobPositionName }}</span>
        </template>
      </el-table-column>
      <el-table-column label="Mã vị trí" align="center">
        <template slot-scope="{ row }">
          <span>{{ row.JobPositionCode }}</span>
        </template>
      </el-table-column>
      <el-table-column label="Tên tổ chức" align="center">
        <template slot-scope="{ row }">
          <div v-for="og in row.OrganizationUnitName" :key="og">{{ og }}</div>
        </template>
      </el-table-column>
      <el-table-column
        label="Actions"
        align="center"
        width="300"
        class-name="small-padding fixed-width"
      >
        <template slot-scope="{ row, $index }">
          <el-button
            type="primary"
            size="mini"
            @click="editPosition(row)"
            v-if="checkRolePermission('Edit', subsystem_code, false)"
          >
            Sửa
          </el-button>
          <el-button
            size="mini"
            type="danger"
            @click="confirmDeleteJobPosition(row, $index)"
            v-if="checkRolePermission('Delete', subsystem_code, false)"
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
        label-width="70px"
        style="margin:0 50px;"
      >
        <div>
          <h2>Thông tin chung</h2>
        </div>
        <div class="w-100">
          <el-form-item label="Tên vị trí " prop="JobPositionName">
            <el-input v-model="temp.JobPositionName" />
          </el-form-item>
        </div>
        <div class="w-100">
          <el-form-item label="Mã vị trí " prop="JobPositionCode">
            <el-input v-model="temp.JobPositionCode" />
          </el-form-item>
        </div>
        <div class="w-100">
          <el-form-item label="Phòng ban" prop="OrganizationUnit">
            <el-select
              v-model="temp.OrganizationUnitID"
              multiple
              filterable
              default-first-option
              placeholder="Chọn danh sách phòng ban"
              style="width: 100%;"
            >
              <el-option
                v-for="item in organization_unit"
                :key="item.key"
                :label="item.display_name"
                :value="item.key"
              >
              </el-option>
            </el-select>
          </el-form-item>
        </div>
      </el-form>
      <div slot="footer" class="dialog-footer">
        <el-button @click="dialogFormVisible = false">
          Hủy
        </el-button>
        <el-button type="primary" @click="saveJobPosition">
          Xác nhận
        </el-button>
      </div>
    </el-dialog>
  </div>
</template>
<script>
import  checkRolePermission from "@/utils/permission"
import Pagination from "@/components/Pagination";
export default {
  components: { Pagination },
  data() {
    return {
      subsystem_code: "QL_BO_PHAN",
      organization_unit: [],
      temp: {
        _id: "",
        JobPositionName: "",
        JobPositionCode: "",
        OrganizationUnitID: [],
        state: ""
      },
      rules: {},
      dialogType: "",
      dialogFormVisible: false,
      listQuery: {
        page: 1,
        limit: 20,
        text_search: undefined
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
    checkRolePermission,
    getList() {
      this.listLoading = true;
      let query_filter = `{"$and": [`;
      query_filter += this.listQuery?.text_search
        ? `{"$or":[{"JobPositionName": {"$regex": "${this.listQuery.text_search}", "$options": "$i"}},
                                                                            {"JobPositionCode": {"$regex": "${this.listQuery.text_search}", "$options": "$i"}},
                                                                            {"OrganizationUnitName": {"$regex": "${this.listQuery.text_search}", "$options": "$i"}}]},`
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
      this.$store.dispatch(`job_position/getJobPositions`, param).then(res => {
        this.list = res.results;
        this.total = res.totals;
        this.listLoading = false;
      });
      this.$store.dispatch(`organization_unit/getList`).then(res => {
        console.log(res);
        this.organization_unit = res;
      });
    },
    handleFilter() {
      this.listQuery.page = 1;
      this.getList();
    },
    addJobPosition() {
      if (this.checkRolePermission("Add", this.subsystem_code)) {
        this.temp = {};
        // this.src='http://localhost:4321/avatar/default_avatar.png'
        this.temp.state = 1;
        this.dialogFormVisible = true;
        this.dialogType = "add";
      }
    },
    deleteJobPosition(data) {
      if (!data) {
        return;
      }
      data.state = 3;
      this.$store.dispatch("job_position/saveJobPosition", data).then(res => {
        this.getRoles();
        this.$notify({
          title: "Success",
          dangerouslyUseHTMLString: true,
          message: `
              <div>Tên ca: ${this.temp.WorkingShiftName}</div>
              <div>Mã ca: ${this.temp.WorkingShiftCode}</div>
            `,
          type: "success"
        });
      });
    },
    confirmDeleteJobPosition(row, $index) {
      if (this.checkRolePermission("Delete", this.subsystem_code)) {
        this.$confirm("Ban co chac muon xoa ca lam viec ?", "Warning", {
          confirmButtonText: "Confirm",
          cancelButtonText: "Cancel",
          type: "warning"
        })
          .then(async () => {
            await this.deleteJobPosition(row);
            this.list.splice($index, 1);
            this.$message({
              type: "success",
              message: "Delete succed!"
            });
          })
          .catch(err => {
            console.error(err);
          });
      }
    },
    saveJobPosition() {
      this.temp.state = this.dialogType === "edit" ? 2 : 1;
      debugger;
      this.$store
        .dispatch("job_position/saveJobPosition", this.temp)
        .then(res => {
          this.getList();
          this.dialogFormVisible = false;
          this.$notify({
            title: "Success",
            dangerouslyUseHTMLString: true,
            message: `
              <div>Tên vị trí : ${this.temp.JobPositionName}</div>
              <div>Mã vị trí: ${this.temp.JobPositionCode}</div>
            `,
            type: "success"
          });
        });
    },
    editPosition(data) {
      if (this.checkRolePermission("Edit", this.subsystem_code)) {
        this.dialogType = "edit";
        this.dialogFormVisible = true;
        this.temp = data;
      }
    }
  }
};
</script>
<style lang="scss">
.el-form-item__content {
  // margin-left: 24px !important;
  margin: 0px !important;
  width: calc(100% - 115px);
  display: flex;
}
.el-form-item__label {
  width: 105px !important;
}
.el-dialog {
  margin-top: 5vh !important;
}
</style>
