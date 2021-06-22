<template>
  <div class="app-container">
    <div
      class="filter-container"
      v-if="checkRolePermission('View', subsystem_code, false)"
    >
      <div style="display: flex;justify-content: space-between">
        <div>
          <el-input
            v-model="listQuery.text_search"
            placeholder="Search"
            style="width: 200px;"
            class="filter-item"
            @keyup.enter.native="handleFilter"
          />
          <el-select
            v-model="listQuery.OrganizationUnitID"
            placeholder="Phòng ban"
            clearable
            class="filter-item"
            style="width: 200px"
          >
            <el-option
              v-for="item in organization_unit"
              :key="item.key"
              :label="item.display_name + '(' + item.key + ')'"
              :value="item.key"
            />
          </el-select>
          <el-select
            v-if="this.show_detail"
            v-model="listQuery.TimeSheet"
            placeholder="Bảng chấm công"
            clearable
            class="filter-item"
            style="width: 220px"
          >
            <el-option
              v-for="item in list_time_sheet"
              :key="item.key"
              :label="item.display_name"
              :value="item.key"
            />
          </el-select>

          <label
            v-if="!this.show_detail"
            class="label_date"
            style="margin-left:20px"
            >Từ ngày:
          </label>
          <el-date-picker
            style="width: 200px;"
            class="filter-item"
            v-model="listQuery.start_date"
            type="datetime"
            placeholder="Please pick a date"
            format="yyyy-MM-dd"
            value-format="yyyy-MM-dd"
            v-if="!this.show_detail"
          />
          <label
            v-if="!this.show_detail"
            class="label_date"
            style="margin-left:20px"
            >Den ngay:
          </label>
          <el-date-picker
            style="width: 200px;"
            class="filter-item"
            v-model="listQuery.to_date"
            type="datetime"
            placeholder="Please pick a date"
            format="yyyy-MM-dd"
            value-format="yyyy-MM-dd"
            v-if="!this.show_detail"
          />
          <el-button
            class="filter-item"
            type="primary"
            icon="el-icon-search"
            style="margin-left:20px"
            @click="handleFilter"
          >
            Tìm kiếm
          </el-button>
          <el-button
            @click="addTimeSheet"
            class="filter-item"
            style="margin-left: 10px;"
            type="primary"
            icon="el-icon-edit"
            v-if="checkRolePermission('Add', subsystem_code, false)"
          >
            Them
          </el-button>
        </div>
      </div>
    </div>
    <div v-if="this.show_detail">
      <div class="flex">
        <div style="margin-top:15px" @click="handle_back()">
          <el-button type="primary" style="justify-content: center">
            <i class="el-icon-back" />
          </el-button>
        </div>
        <div class="center">
          <h1>{{ this.name_time_sheet }}</h1>
        </div>
      </div>
      <div>
        <el-table
          key="1"
          v-loading="listLoading"
          :data="list"
          border
          fit
          highlight-current-row
          style="margin-top:20px"
          :v-if="list"
        >
          <el-table-column label="Họ tên" align="center" width="200px" fixed>
            <template slot-scope="{ row }">
              <span>{{ row.user_fullname }}</span>
            </template>
          </el-table-column>
          <el-table-column
            label="Mã nhân viên"
            align="center"
            width="200px"
            fixed
          >
            <template slot-scope="{ row }">
              <span>{{ row.MaNV }}</span>
            </template>
          </el-table-column>
          <el-table-column label="Tổng hợp" align="center" width="200px" fixed>
            <template slot-scope="{ row }">
              <span
                >{{ row.totals_check_day
                }}<span style="font-size:12px;color:red"> (thực tế)</span> /
              </span>
              <span
                >{{ row.totals_plan_day
                }}<span style="font-size:12px;color:red"> (được giao)</span>
              </span>
            </template>
          </el-table-column>

          <el-table-column
            align="center"
            width="200px"
            v-for="index in 31"
            :key="index"
            :label="`Ngày ` + index"
          >
            <template slot-scope="{ row }">
              <div
                style="width:150px;height:150px"
                v-for="(day, idx) in row[`Day` + index]"
                :key="idx"
                class="cursor"
                @click="hander_click_box(row[`Day` + index])"
              >
                <div class="view_thu">{{ day.thu }}</div>
                <div class="view_ngay">{{ day.day }}</div>
                <div>Ca làm: {{ day.WorkingShiftName }}</div>
                <div>Tổng công: {{ day.Working_days }}</div>
                <hr />
              </div>
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
      </div>
    </div>
    <div v-if="!this.show_detail">
      <div>
        <el-table
          key="0"
          v-loading="listLoading"
          :data="list"
          border
          fit
          highlight-current-row
          style="margin-top:20px"
          :v-if="list"
        >
          <el-table-column
            label="Tên bảng chấm công"
            align="center"
            width="250px"
          >
            <template slot-scope="{ row }">
              <el-button @click="handleShowDetail(row)">
                <div style="color:#1890ff;font-style: italic;" class="cursor">
                  {{ row.TimeSheetName }}
                </div>
                <div style="font-size: 10px;">click xem</div>
              </el-button>
            </template>
          </el-table-column>
          <el-table-column label="Phòng ban" align="center" width="200px">
            <template slot-scope="{ row }">
              <span>{{ row.OrganizationUnitName }}</span>
            </template>
          </el-table-column>
          <el-table-column label="Chức danh" align="center" width="200px">
            <template slot-scope="{ row }">
              <div v-for="job_pos in row.JobPositionNames" :key="job_pos">
                {{ job_pos }}
              </div>
            </template>
          </el-table-column>
          <el-table-column label="Từ ngày" align="center">
            <template slot-scope="{ row }">
              <span>{{ row.FromDate | parseTime("{y}-{m}-{d}") }}</span>
            </template>
          </el-table-column>
          <el-table-column label="Đến ngày" align="center">
            <template slot-scope="{ row }">
              <span>{{ row.ToDate | parseTime("{y}-{m}-{d}") }}</span>
            </template>
          </el-table-column>
          <el-table-column label="Người tạo" align="center" width="200px">
            <template slot-scope="{ row }">
              <span>{{ row.CreateBy }}</span>
            </template>
          </el-table-column>
          <el-table-column label="Ngày tạo" align="center" width="200px">
            <template slot-scope="{ row }">
              <span>{{ row.CreateDate | parseTime("{y}-{m}-{d}") }}</span>
            </template>
          </el-table-column>
          <el-table-column align="center" label="Hành động">
            <template slot-scope="{ row }">
              <el-button
                type="primary"
                size="small"
                v-if="checkRolePermission('Edit', subsystem_code, false)"
                @click="handleEdit(row)"
                >Sửa</el-button
              >
              <el-button
                type="danger"
                size="small"
                v-if="checkRolePermission('Delete', subsystem_code, false)"
                @click="confirmDeleteTimeSheet(row)"
                >Xóa</el-button
              >
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
      </div>
    </div>
    <div>
      <el-dialog
        v-if="dialogFormVisible"
        width="1000px"
        height="1000px"
        :visible.sync="dialogFormVisible"
        :title="this.view_cham_cong"
      >
        <div>
          <div>
            <el-table
              key="2"
              :data="this.box_click"
              border
              fit
              highlight-current-row
              style="margin-top:20px"
            >
              <el-table-column
                label="Giờ kế hoạch"
                align="center"
                width="479px"
              >
                <template slot-scope="{ row }">
                  <div class="flex">
                    <div style="width:200px">
                      <div>Bắt đầu</div>
                      <span>{{ row.StartTime }}</span>
                    </div>
                    <div style="width:200px">
                      <div>Kết thúc</div>
                      <span>{{ row.EndTime }}</span>
                    </div>
                  </div>
                </template>
              </el-table-column>
              <el-table-column label="Giờ thực tế" align="center" width="479px">
                <template slot-scope="{ row }">
                  <div class="flex">
                    <div style="width:200px">
                      <div>Bắt đầu</div>
                      <span>{{ row.CheckStartTime }}</span>
                    </div>
                    <div style="width:200px">
                      <div>Kết thúc</div>
                      <span>{{ row.CheckEndTime }}</span>
                    </div>
                  </div>
                </template>
              </el-table-column>
            </el-table>
          </div>
          <div>
            <el-table
              key="2"
              :data="this.box_click"
              border
              fit
              highlight-current-row
              style="margin-top:20px;"
            >
              <el-table-column
                label="Phạt đi muộn"
                align="center"
                width="479px"
              >
                <template slot-scope="{ row }">
                  <div class="flex">
                    <div style="width:200px">
                      <div>Ngày</div>
                      <span>{{ row.penalty_day_in }}</span>
                    </div>
                    <div style="width:200px">
                      <div>Giờ</div>
                      <span>{{ row.penalty_hour_in }}</span>
                    </div>
                  </div>
                </template>
              </el-table-column>
              <el-table-column label="Phạt về sớm" align="center" width="479px">
                <template slot-scope="{ row }">
                  <div class="flex">
                    <div style="width:200px">
                      <div>Ngày</div>
                      <span>{{ row.penalty_day_out }}</span>
                    </div>
                    <div style="width:200px">
                      <div>Giờ</div>
                      <span>{{ row.penalty_hour_out }}</span>
                    </div>
                  </div>
                </template>
              </el-table-column>
            </el-table>
          </div>
          <div>
            <el-table
              key="2"
              :data="this.box_click"
              border
              fit
              highlight-current-row
              style="margin-top:20px"
            >
              <el-table-column
                label="Tổng công kế hoạch"
                align="center"
                width="479px"
              >
                <template slot-scope="{ row }">
                  <div class="flex">
                    <div style="width:200px">
                      <div>Ngày</div>
                      <span>{{ row.Working_plan_day }}</span>
                    </div>
                    <div style="width:200px">
                      <div>Giờ</div>
                      <span>{{ row.Working_plan_hour }}</span>
                    </div>
                  </div>
                </template>
              </el-table-column>
              <el-table-column
                label="Tổng công thực tế"
                align="center"
                width="479px"
              >
                <template slot-scope="{ row }">
                  <div class="flex">
                    <div style="width:200px">
                      <div>Ngày</div>
                      <span>{{ row.Working_days }}</span>
                    </div>
                    <div style="width:200px">
                      <div>Giờ</div>
                      <span>{{ row.Working_hours }}</span>
                    </div>
                  </div>
                </template>
              </el-table-column>
            </el-table>
          </div>
        </div>
        <div slot="footer" class="dialog-footer">
          <el-button @click="dialogFormVisible = false">
            Đóng
          </el-button>
        </div>
      </el-dialog>
      <el-dialog
        v-if="dialogAddVisible"
        width="900px"
        height="900px"
        :visible.sync="dialogAddVisible"
        title="Thêm mới bảng chấm công"
      >
        <el-form
          ref="dataForm"
          label-position="left"
          label-width="150px"
          style="margin:0 50px"
        >
          <div>
            <el-form-item label="Tên bảng công " prop="TimeSheetName">
              <el-input v-model="temp.TimeSheetName" />
            </el-form-item>
            <el-form-item label="Bộ phận" prop="OrganizationUnitID">
              <el-select
                v-model="temp.OrganizationUnitID"
                class="filter-item"
                placeholder="Chọn phòng ban"
                @change="click_Organization"
                style="width:100%"
              >
                <el-option
                  v-for="item in organization_unit"
                  :key="item.key"
                  :label="item.display_name"
                  :value="item.key"
                />
              </el-select>
            </el-form-item>
            <el-form-item label="Vị trí" prop="JobPositionID">
              <el-select
                v-model="temp.JobPositionIDs"
                class="filter-item"
                placeholder="Chọn vị trí"
                multiple
                filterable
                style="width:100%"
              >
                <el-option
                  v-for="item in job_position"
                  :key="item.key"
                  :label="item.display_name"
                  :value="item.key"
                />
              </el-select>
            </el-form-item>
          </div>
          <div class="flex">
            <el-form-item label="Từ ngày" prop="FromDate" style="width:100%">
              <el-date-picker
                v-model="temp.FromDate"
                type="date"
                placeholder="Chọn ngày"
                value-format="yyyy-MM-dd"
                format="yyyy-MM-dd"
              />
            </el-form-item>
            <el-form-item label="Đến ngày" prop="ToDate">
              <el-date-picker
                v-model="temp.ToDate"
                type="date"
                placeholder="Chọn ngày"
                value-format="yyyy-MM-dd"
                format="yyyy-MM-dd"
              />
            </el-form-item>
          </div>
          <div>
            <el-form-item label="Dùng tính lương" prop="WorkCalculator">
              <el-checkbox v-model="temp.WorkCalculator"> </el-checkbox>
            </el-form-item>
          </div>
        </el-form>
        <div slot="footer" class="dialog-footer">
          <el-button @click="dialogAddVisible = false">
            Hủy
          </el-button>
          <el-button type="primary" @click="saveSheetPlan">
            Xác nhận
          </el-button>
        </div>
      </el-dialog>
    </div>
  </div>
</template>
<script>
import Pagination from "@/components/Pagination";
import moment from "moment";
import checkRolePermission from "@/utils/permission";
export default {
  components: { Pagination },
  data() {
    return {
      tableKey: 0,
      total: 0,
      listQuery: {
        page: 1,
        limit: 10,
        text_search: undefined,
        OrganizationUnitID: undefined,
        TimeSheet: undefined,
        start_date: undefined,
        to_date: undefined
      },
      subsystem_code: "BANG_CHAM_CONG",
      param: {},
      listLoading: false,
      list: null,
      organization_unit: [],
      list_time_sheet: null,
      name_time_sheet: null,
      dialogFormVisible: false,
      box_click: null,
      show_detail: false,
      dialogAddVisible: false,
      temp: {
        TimeSheetName: "",
        OrganizationUnitID: "",
        JobPositionIDs: "",
        FromDate: "",
        ToDate: "",
        WorkCalculator: "",
        state:""
      },
      dialogType:'',
      organization_unit: [],
      job_position: []
    };
  },
  created() {
    this.getlist_dropbox();
    this.getList();
  },
  methods: {
    saveSheetPlan() {
      debugger
      // this.$refs["dataForm"].validate(valid => {
      // if (valid) {
      if(this.dialogType =="new"){
        this.temp.state = 1
      }
      if(this.dialogType =="edit"){
        this.temp.state = 2
      }
      this.$store
        .dispatch(`timesheet_detail/addTimeSheet`, this.temp)
        .then(res => {
          this.$notify({
            title: "Thông báo",
            message: "Save bảng lương thành công",
            type: "success",
            duration: 2000
          });
          this.getList();
          this.dialogAddVisible = false;
        });

      // }
      // });
    },
    click_Organization(data, edit = false) {
      let param = {
        OrganizationUnitID: data
      };
      this.$store.dispatch(`job_position/getByOg`, param).then(res => {
        this.job_position = res;
      });
      if (!edit) {
        this.temp.JobPositionIDs = "";
      }
    },
    checkRolePermission,
    handleFilter() {
      this.listQuery.page = 1;
      this.getList();
    },
    handle_back() {
      this.show_detail = false;
      this.listQuery.TimeSheet = null;
      this.getList();
    },
    handleShowDetail(row) {
      this.listQuery.TimeSheet = row._id;
      this.show_detail = true;
      this.getList(row);
    },
    getList(row = null) {
      this.list = [];
      this.listLoading = true;
      let query_filter = `{"$and": [`;
      if (this.show_detail) {
        query_filter += this.listQuery?.text_search
          ? `{"$or":[{"TimeSheetName": {"$regex": "${this.listQuery.text_search}", "$options": "$i"}},
                                                                       {"user_fullname": {"$regex": "${this.listQuery.text_search}", "$options": "$i"}},
                                                                       {"OrganizationUnitName": {"$regex": "${this.listQuery.text_search}", "$options": "$i"}}]},`
          : "";
      } else {
        query_filter += this.listQuery?.text_search
          ? `{"$or":[{"TimeSheetName": {"$regex": "${this.listQuery.text_search}", "$options": "$i"}},
                                                                       {"CreateBy": {"$regex": "${this.listQuery.text_search}", "$options": "$i"}},
                                                                       {"OrganizationUnitName": {"$regex": "${this.listQuery.text_search}", "$options": "$i"}}]},`
          : "";
      }

      query_filter += parseInt(this.listQuery?.OrganizationUnitID)
        ? `{"OrganizationUnitID": { "$regex" : "${this.listQuery.OrganizationUnitID}", "$options": "$i"}},`
        : "";
      query_filter += parseInt(this.listQuery?.TimeSheet)
        ? `{"TimeSheetID": { "$regex" : "${this.listQuery.TimeSheet}", "$options": "$i"}},`
        : "";
      query_filter += `]}`;
      let index = query_filter.lastIndexOf(",");
      if (index > 0) {
        query_filter =
          query_filter.substring(0, index) + query_filter.slice(index + 1);
      }
      this.param = {
        page_size: this.listQuery.limit,
        page_number: this.listQuery.page,
        query_filter: query_filter,
        start_date: this.listQuery.start_date,
        to_date: this.listQuery.to_date
      };
      if (this.show_detail) {
        this.$store
          .dispatch(`timesheet_detail/get_all_page_search`, this.param)
          .then(res => {
            debugger;
            this.list = res.results;
            if (res.results.length > 0) {
              this.name_time_sheet = res.results[0].TimeSheetName.toUpperCase();
            }

            this.total = res.totals;
            this.listLoading = false;
          });
      } else {
        this.$store
          .dispatch(`time_sheet/get_all_page_search`, this.param)
          .then(res => {
            debugger;
            this.list = res.results;
            this.total = res.totals;
            this.listLoading = false;
          });
      }
      this.$store.dispatch(`organization_unit/getList`).then(res => {
        this.organization_unit = res;
      });
    },
    getlist_dropbox() {
      this.$store.dispatch(`timesheet_detail/get_list`).then(res => {
        this.list_time_sheet = res;
      });
    },
    hander_click_box(day) {
      this.box_click = day;
      console.log(this.box_click);
      this.view_cham_cong =
        "Chấm công " +
        day[0].thu +
        " ngày " +
        moment(day[0].check_in_date).format("DD-MM-YYYY");
      this.view_cham_cong = this.view_cham_cong.toUpperCase();
      this.dialogFormVisible = true;
    },
    addTimeSheet() {
      if (this.checkRolePermission("Add", this.subsystem_code)) {
        this.dialogAddVisible = true;
        this.dialogType = "new";
      }
    },
    handleEdit(row) {
      if (this.checkRolePermission("Edit", this.subsystem_code)) {
        this.dialogType = "edit";
        this.temp = row;
        this.click_Organization(this.temp.OrganizationUnitID,true)
        this.dialogAddVisible = true;
      }
    },
    confirmDeleteTimeSheet(data, e) {
      if(this.checkRolePermission("Delete",this.subsystem_code)){
      this.temp = Object.assign({}, data);
      this.temp.state = 3;
      this.$confirm(
        `Ban co muon xoa bang cong ${this.temp.TimeSheetName}?`,
        "Thong bao",
        {
          confirmButtonText: "Xoa",
          cancelButtonText: "Huy",
          type: "warning"
        }
      )
        .then(async () => {
          await this.deleteTimeSheet();
        })
        .catch(err => {
          console.error(err);
        });
      }
    },
    deleteTimeSheet() {
      this.$store.dispatch(`timesheet_detail/addTimeSheet`, this.temp).then(res => {
        this.$notify({
          title: "Thông báo",
          dangerouslyUseHTMLString: true,
          message: `Xoa bang cong thanh cong`,
          type: "success"
        });
        this.getList();
      });
    },
  }
};
</script>
<style scoped>
.view_thu {
  color: red;
  font-style: italic;
}
.view_ngay {
  color: red;
  font-weight: bold;
  font-size: large;
}
.center {
  width: 30%;
  height: 50%;
  margin: auto;
}
</style>
