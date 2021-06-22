<template>
  <div class="app-container">
    <div class="filter-container" v-if="checkRolePermission('View',subsystem_code,false)">
      <div style="display: flex;justify-content: space-between">
        <div>
          <el-input
            v-model="listQuery.text_search"
            placeholder="Tìm kiếm ca làm việc"
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
        @click="addWorkingShift"
        class="filter-item"
        style="margin-left: 10px;"
        type="primary"
        icon="el-icon-edit"
        v-if="checkRolePermission('Add',subsystem_code,false)"
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
      <el-table-column
        label="Mã ca"
        align="center"
      >
        <template slot-scope="{ row }">
          <span>{{ row.WorkingShiftCode }}</span>
        </template>
      </el-table-column>
      <el-table-column label="Giờ bắt đầu" width="150px" align="center">
        <template slot-scope="{ row }">
          <span>{{converttime(row.StartTime)}}</span>
        </template>
      </el-table-column>
      <el-table-column label="Giờ kết thúc" width="150px" align="center">
        <template slot-scope="{ row }">
          <span>{{converttime(row.EndTime) }}</span>
        </template>
      </el-table-column>
      <el-table-column label="Tên ca" width="250px" align="center">
        <template slot-scope="{ row }">
          <span>{{ row.WorkingShiftName }}</span>
        </template>
      </el-table-column>
      <el-table-column label="Ngày tạo" width="200px" align="center">
        <template slot-scope="{ row }">
          <span>{{ row.CreateDate | parseTime("{y}-{m}-{d}") }}</span>
        </template>
      </el-table-column>
      <el-table-column label="Giờ làm việc" width="200px" align="center">
        <template slot-scope="{ row }">
          <span>{{ row.WorkingHour }}</span>
        </template>
      </el-table-column>
      <el-table-column label="Tỷ lệ" width="150px" align="center">
        <template slot-scope="{ row }">
          <span>{{ row.WorkingRateWeekday }}</span>
        </template>
      </el-table-column>
      <el-table-column
        label="Hành động"
        align="center"
        width="300"
        class-name="small-padding fixed-width"
      >
        <template slot-scope="{ row, $index }">
          <el-button type="primary" size="mini" @click="editWorkingShift(row)" v-if="checkRolePermission('Edit',subsystem_code,false)">
            Sửa
          </el-button>
          <el-button
            size="mini"
            type="danger"
            @click="confirmDeleteWorkingShift(row, $index)"
            v-if="checkRolePermission('Delete',subsystem_code,false)"
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
        <div class="flex">
          <div class="w-50">
            <el-form-item label="Tên ca " prop="WorkingShiftName">
              <el-input v-model="temp.WorkingShiftName" />
            </el-form-item>
          </div>
          <div class="w-50">
            <el-form-item label="Mã ca " prop="WorkingShiftCode">
              <el-input v-model="temp.WorkingShiftCode" />
            </el-form-item>
          </div>
        </div>
        <div class="flex">
          <div class="start-time" style="width: 240px !important;">
            <el-form-item label="Giờ bắt đầu" prop="StartTime">
              <el-time-picker
                v-model="temp.StartTime"
                type="time"
                format="hh:mm A"
                value-format="hh:mm A"
              />
            </el-form-item>
          </div>
          <div style="width: 150px !important;">
            <el-form-item label="Cham vao " prop="CheckStartTime">
              <el-checkbox v-model="temp.CheckStartTime" />
            </el-form-item>
          </div>
          <div style="width: 240px !important;">
            <el-form-item class="w-full" label="Từ" prop="StartTimeInFrom">
              <el-time-picker
                v-model="temp.StartTimeInFrom"
                type="time"
                format="hh:mm A"
                value-format="hh:mm A"
              />
            </el-form-item>
          </div>
          <div style="width: 240px !important;">
            <el-form-item class=" w-full" label="Đến" prop="StartTimeInTo">
              <el-time-picker
                v-model="temp.StartTimeInTo"
                type="time"
                format="hh:mm A"
                value-format="hh:mm A"
              />
            </el-form-item>
          </div>
        </div>
        <div class="flex">
          <div class="start-time" style="width: 240px !important;">
            <el-form-item label="Giờ kết thúc" prop="EndTime">
              <el-time-picker
                v-model="temp.EndTime"
                type="time"
                format="hh:mm A"
                value-format="hh:mm A"
              />
            </el-form-item>
          </div>
          <div style="width: 150px !important;">
            <el-form-item label="Cham ra " prop="CheckEndTime">
              <el-checkbox v-model="temp.CheckEndTime" />
            </el-form-item>
          </div>
          <div style="width: 240px !important;">
            <el-form-item class="w-full" label="Từ" prop="EndTimeInFrom">
              <el-time-picker
                v-model="temp.EndTimeInFrom"
                type="time"
                format="hh:mm A"
                value-format="hh:mm A"
              />
            </el-form-item>
          </div>
          <div style="width: 240px !important;">
            <el-form-item class=" w-full" label="Đến" prop="EndTimeInTo">
              <el-time-picker
                v-model="temp.EndTimeInTo"
                type="time"
                format="hh:mm A"
                value-format="hh:mm A"
              />
            </el-form-item>
          </div>
        </div>

        <div>
          <h2>Tính công</h2>
        </div>
        <div class="flex tinh-cong">
          <div class="w-35">
            <el-form-item label="Giờ công " prop="WorkingHour">
               <el-input-number
                v-model="temp.WorkingHour"
                placeholder="0"
                :min="0"
                :max="24"
                :step="0.01"
              ></el-input-number>
            </el-form-item>
          </div>
          <div class="w-35">
            <el-form-item label="Ngày công " prop="WorkingDate">
               <el-input-number
                v-model="temp.WorkingDate"
                placeholder="0"
                :min="0"
                :max="31"
                :step="0.01"
              ></el-input-number>
            </el-form-item>
          </div>
          <div class="w-35">
           
          </div>
        </div>
        <div class="flex tinh-cong">
          <div class="w-35">
            <el-form-item label="Hệ số ngày thường " prop="WorkingRateWeekday">
               <el-input-number
                v-model="temp.WorkingRateWeekday"
                placeholder="0"
                :min="0"
                :max="30"
                :step="0.01"
              ></el-input-number>
            </el-form-item>
          </div>
          <div class="w-35">
            <el-form-item label="Hệ số ngày lễ " prop="WorkingRateHoliday">
              <el-input-number
                v-model="temp.WorkingRateHoliday"
                placeholder="0"
                :min="0"
                :max="30"
                :step="0.01"
              ></el-input-number>
            </el-form-item>
          </div>
          <div class="w-35">
             <el-form-item label="Hệ số ngày nghỉ " prop="WorkingRateWeekend">
              <el-input-number
                v-model="temp.WorkingRateWeekend"
                placeholder="0"
                :min="0"
                :max="30"
                :step="0.01"
              ></el-input-number>
            </el-form-item>
          </div>
        </div>
        <div class="flex check-tinh-cong">
          <el-form-item
            label="Neu khong cham vao bi tru "
            prop="IsShowWithoutCheckin"
            label-width="100% !important"
          >
            <el-checkbox
              v-model="temp.IsShowWithoutCheckin"
              style="width: auto !important;"
            />
          </el-form-item>
        </div>
        <div class="flex tinh-cong">
          <div class="w-35">
            <el-form-item label="Giờ công " prop="WorkingHourWithoutCheckin">
               <el-input-number
                v-model="temp.WorkingHourWithoutCheckin"
                placeholder="0"
                :min="0"
                :max="24"
                :step="0.01"
              ></el-input-number>
            </el-form-item>
          </div>
          <div class="w-35">
            <el-form-item label="Ngày công " prop="WorkingDayWithoutCheckin">
              <el-input-number
                v-model="temp.WorkingDayWithoutCheckin"
                placeholder="0"
                :min="0"
                :max="31"
                :step="0.01"
              ></el-input-number>
            </el-form-item>
          </div>
          <div class="w-35"></div>
        </div>
        <div class="flex check-tinh-cong">
          <el-form-item
            label="Neu khong cham ra bi tru "
            prop="IsShowWithoutCheckOut"
            label-width="100% !important"
          >
            <el-checkbox
              v-model="temp.IsShowWithoutCheckOut"
              style="width: 24px !important;"
            />
          </el-form-item>
        </div>
        <div class="flex tinh-cong">
          <div class="w-35">
            <el-form-item label="Giờ công " prop="WorkingHourWithoutCheckOut">
               <el-input-number
                v-model="temp.WorkingHourWithoutCheckOut"
                placeholder="0"
                :min="0"
                :max="24"
                :step="0.01"
              ></el-input-number>
            </el-form-item>
          </div>
          <div class="w-35">
            <el-form-item label="Ngày công " prop="WorkingDayWithoutCheckOut">
              <el-input-number
                v-model="temp.WorkingDayWithoutCheckOut"
                placeholder="0"
                :min="0"
                :max="31"
                :step="0.01"
              ></el-input-number>
            </el-form-item>
          </div>
          <div class="w-35"></div>
        </div>
      </el-form>
      <div slot="footer" class="dialog-footer">
        <el-button @click="dialogFormVisible = false">
          Hủy
        </el-button>
        <el-button type="primary" @click="saveWorkingShift">
          Xác nhận
        </el-button>
      </div>
    </el-dialog>
  </div>
</template>
<script>
import Pagination from "@/components/Pagination";
import checkRolePermission from "@/utils/permission";
import moment from 'moment'
import { deepClone } from '@/utils'
export default {
  components: { Pagination },
  data() {
    return {
      subsystem_code:"QUAN_LY_CA",
      temp: {
        _id:"",
        WorkingShiftCode: "",
        WorkingShiftName: "",
        StartTime: "",
        EndTime: "",
        CheckStartTime: "",
        CheckEndTime: "",
        StartTimeInFrom: "",
        StartTimeInTo: "",
        EndTimeInFrom: "",
        EndTimeInTo: "",
        IsShowWithoutCheckin:"",
        IsShowWithoutCheckOut:"",
        WorkingHourWithoutCheckin: "",
        WorkingDayWithoutCheckin: "",
        WorkingHourWithoutCheckOut: "",
        WorkingDayWithoutCheckOut: "",
        WorkingRateWeekday: "",
        WorkingRateWeekend: "",
        WorkingRateHoliday: "",
        WorkingHour: "",
        WorkingDate: "",
        state:""
      },
      rules: {
        WorkingShiftName: [
          { required: true, message: "Yêu cầu nhập tên ca", trigger: "change" }
        ],
        WorkingShiftCode: [
          {
            required: true,
            message: "Yêu cầu nhập mã ca",
            trigger: "change"
          }
        ],
        StartTime: [
          {
            required: true,
            message: "Giờ bắt đầu không được trống",
            trigger: "change"
          }
        ],
        EndTime: [
          {
            required: true,
            message: "Giờ kết thúc không được trống",
            trigger: "change"
          }
        ]
      },
      dialogType:'',
      dialogFormVisible: false,
      listQuery: {
        page: 1,
        limit: 20,
        text_search: undefined,
        is_training: undefined,
        OrganizationUnitID: undefined,
        JobPositionID: undefined,
        start_date: undefined,
        to_date: undefined,
        sort: "+id"
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
    converttime(date){
      return moment(date, ["h:mm A"]).format("HH:mm");
    },
    editWorkingShift(scope) {
      if(this.checkRolePermission("Edit",this.subsystem_code)){
      this.dialogType = 'edit'
      this.dialogFormVisible = true
      this.temp = deepClone(scope)
      }
    },
    getList() {
      this.listLoading = true;
      let query_filter = `{"$and": [`;
      query_filter += this.listQuery?.text_search
        ? `{"$or":[{"WorkingShiftName": {"$regex": "${this.listQuery.text_search}", "$options": "$i"}},
                                                                            {"WorkingShiftCode": {"$regex": "${this.listQuery.text_search}", "$options": "$i"}},
                                                                            {"ModifieBy": {"$regex": "${this.listQuery.text_search}", "$options": "$i"}}]},`
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
      this.$store.dispatch(`working_shift/getWorkingShift`, param).then(res => {
        this.list = res.results;
        this.total = res.totals;
        this.listLoading = false;
      });
    },
    handleFilter() {
      this.listQuery.page = 1;
      this.getList();
    },
    addWorkingShift() {
      if(this.checkRolePermission("Add",this.subsystem_code)){
        this.temp = {};
        // this.src='http://localhost:4321/avatar/default_avatar.png'
        this.temp.state = 1;
        this.dialogFormVisible = true;
        this.dialogType = 'add'
      }
    },
    deleteWorkingShift(data){
      if(!data){
        return;
      }
      data.state = 3;
      this.$store.dispatch("working_shift/save_WorkingShift",data).then(res=>{
        this.getRoles();
        this.$notify({
          title: 'Success',
          dangerouslyUseHTMLString: true,
          message: `
              <div>Tên ca: ${this.temp.WorkingShiftName}</div>
              <div>Mã ca: ${this.temp.WorkingShiftCode}</div>
            `,
          type: 'success'
        })
      })
    },
    confirmDeleteWorkingShift(row,$index) {
      if(this.checkRolePermission("Delete",this.subsystem_code)){
      this.$confirm('Bạn có chắc muốn xóa ca làm việc ?', 'Cảnh báo', {
        confirmButtonText: 'Xác nhận',
        cancelButtonText: 'Hủy',
        type: 'warning'
      })
        .then(async() => {
          await this.deleteWorkingShift(row)
          this.list.splice($index, 1)
          this.$message({
            type: 'success',
            message: 'Delete succed!'
          })
        })
        .catch(err => { console.error(err) })
      }
    },
    saveWorkingShift() {
      this.temp.state = this.dialogType === 'edit' ? 2 : 1;
      debugger
      this.$store.dispatch("working_shift/save_WorkingShift",this.temp).then(res=>{
        this.getList();
        this.dialogFormVisible = false;
        this.$notify({
          title: 'Success',
          dangerouslyUseHTMLString: true,
          message: `
              <div>Tên ca: ${this.temp.WorkingShiftName}</div>
              <div>Mã ca: ${this.temp.WorkingShiftCode}</div>
            `,
          type: 'success'
        })
      })
      console.log(this.role);
      this.dialogVisible = false
    },
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
.start-time {
  .el-form-item__content {
    width: calc(100% - 115px) !important;
  }
}
.tinh-cong {
  .el-form-item__label {
    width: 150px !important;
  }
  .el-form-item__content {
    width: calc(100% - 160px) !important;
  }
}
.check-tinh-cong {
  .el-form-item__content {
    width: auto !important;
  }
}
.el-dialog {
  margin-top: 5vh !important;
}
</style>
