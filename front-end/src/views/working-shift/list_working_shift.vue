<template>
  <div class="app-container">
    <div class="filter-container">
      <div style="display: flex;justify-content: space-between">
        <div>
          <el-input
            v-model="listQuery.text_search"
            placeholder="Tim kiem ca lam viec"
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
        Search
      </el-button>
      <el-button
        @click="addWorkingShift"
        class="filter-item"
        style="margin-left: 10px;"
        type="primary"
        icon="el-icon-edit"
      >
        Add
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
        label="Ma ca"
        prop="id"
        sortable="custom"
        align="center"
        width="100"
      >
        <template slot-scope="{ row }">
          <span>{{ row.WorkingShiftCode }}</span>
        </template>
      </el-table-column>
      <el-table-column label="Gio bat dau" width="150px" align="center">
        <template slot-scope="{ row }">
          <span>{{converttime(row.StartTime)}}</span>
        </template>
      </el-table-column>
      <el-table-column label="Gio ket thuc" width="150px" align="center">
        <template slot-scope="{ row }">
          <span>{{converttime(row.EndTime) }}</span>
        </template>
      </el-table-column>
      <el-table-column label="Ten ca" width="250px" align="center">
        <template slot-scope="{ row }">
          <span>{{ row.WorkingShiftName }}</span>
        </template>
      </el-table-column>
      <el-table-column label="Ngay tao" width="200px" align="center">
        <template slot-scope="{ row }">
          <span>{{ row.CreateDate | parseTime("{y}-{m}-{d}") }}</span>
        </template>
      </el-table-column>
      <el-table-column label="Gio lam viec" width="200px" align="center">
        <template slot-scope="{ row }">
          <span>{{ row.WorkingHour }}</span>
        </template>
      </el-table-column>
      <el-table-column label="Ty le" width="150px" align="center">
        <template slot-scope="{ row }">
          <span>{{ row.WorkingRateWeekday }}</span>
        </template>
      </el-table-column>
      <el-table-column
        label="Actions"
        align="center"
        width="300"
        class-name="small-padding fixed-width"
      >
        <template slot-scope="{ row, $index }">
          <el-button type="primary" size="mini" @click="editWorkingShift(row)">
            Edit
          </el-button>
          <el-button
            size="mini"
            type="danger"
            @click="confirmDeleteWorkingShift(row, $index)"
          >
            Delete
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
          <h2>Thong tin chung</h2>
        </div>
        <div class="flex">
          <div class="w-50">
            <el-form-item label="Ten ca " prop="WorkingShiftName">
              <el-input v-model="temp.WorkingShiftName" />
            </el-form-item>
          </div>
          <div class="w-50">
            <el-form-item label="Ma ca " prop="WorkingShiftCode">
              <el-input v-model="temp.WorkingShiftCode" />
            </el-form-item>
          </div>
        </div>
        <div class="flex">
          <div class="start-time" style="width: 240px !important;">
            <el-form-item label="Gio bat dau" prop="StartTime">
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
            <el-form-item class="w-full" label="Tu" prop="StartTimeInFrom">
              <el-time-picker
                v-model="temp.StartTimeInFrom"
                type="time"
                format="hh:mm A"
                value-format="hh:mm A"
              />
            </el-form-item>
          </div>
          <div style="width: 240px !important;">
            <el-form-item class=" w-full" label="Den" prop="StartTimeInTo">
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
            <el-form-item label="Gio ket thuc" prop="EndTime">
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
            <el-form-item class="w-full" label="Tu" prop="EndTimeInFrom">
              <el-time-picker
                v-model="temp.EndTimeInFrom"
                type="time"
                format="hh:mm A"
                value-format="hh:mm A"
              />
            </el-form-item>
          </div>
          <div style="width: 240px !important;">
            <el-form-item class=" w-full" label="Den" prop="EndTimeInTo">
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
          <h2>Tinh cong</h2>
        </div>
        <div class="flex tinh-cong">
          <div class="w-35">
            <el-form-item label="Gio cong " prop="WorkingHour">
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
            <el-form-item label="Ngay cong " prop="WorkingDate">
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
            <el-form-item label="He so ngay thuong " prop="WorkingRateWeekday">
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
            <el-form-item label="He so ngay le" prop="WorkingRateHoliday">
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
             <el-form-item label="He so ngay nghi " prop="WorkingRateWeekend">
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
            <el-form-item label="Gio cong " prop="WorkingHourWithoutCheckin">
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
            <el-form-item label="Ngay cong " prop="WorkingDayWithoutCheckin">
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
            <el-form-item label="Gio cong " prop="WorkingHourWithoutCheckOut">
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
            <el-form-item label="Ngay cong " prop="WorkingDayWithoutCheckOut">
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
          Cancel
        </el-button>
        <el-button type="primary" @click="saveWorkingShift">
          Confirm
        </el-button>
      </div>
    </el-dialog>
  </div>
</template>
<script>
import Pagination from "@/components/Pagination";
import moment from 'moment'
import { deepClone } from '@/utils'
export default {
  components: { Pagination },
  data() {
    return {
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
          { required: true, message: "Yeu cau nhap ten ca", trigger: "change" }
        ],
        WorkingShiftCode: [
          {
            required: true,
            message: "Yeu cau nhap ma ca",
            trigger: "change"
          }
        ],
        StartTime: [
          {
            required: true,
            message: "Gio bat dau khong duoc trong",
            trigger: "change"
          }
        ],
        EndTime: [
          {
            required: true,
            message: "Gio ket thuc khong duoc trong",
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
    converttime(date){
      return moment(date, ["h:mm A"]).format("HH:mm");
    },
    editWorkingShift(scope) {
      this.dialogType = 'edit'
      this.dialogFormVisible = true
      this.temp = deepClone(scope)
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
      // if(this.checkRolePermission("Add",this.subsystem_code)){
      this.temp = {};
      // this.src='http://localhost:4321/avatar/default_avatar.png'
      this.temp.state = 1;
      this.dialogFormVisible = true;
      this.dialogType = 'add'
      // }
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
              <div>Ten ca: ${this.temp.WorkingShiftName}</div>
              <div>Ma ca: ${this.temp.WorkingShiftCode}</div>
            `,
          type: 'success'
        })
      })
    },
    confirmDeleteWorkingShift(row,$index) {
      debugger
      this.$confirm('Ban co chac muon xoa ca lam viec ?', 'Warning', {
        confirmButtonText: 'Confirm',
        cancelButtonText: 'Cancel',
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
              <div>Ten ca: ${this.temp.WorkingShiftName}</div>
              <div>Ma ca: ${this.temp.WorkingShiftCode}</div>
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
