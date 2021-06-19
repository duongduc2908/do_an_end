<template>
  <div class="app-container">
    <div class="filter-container">
      <div style="display: flex;justify-content: space-between">
        <div>
          <el-input
            v-model="listQuery.text_search"
            placeholder="MNV/Ten/MayChamCong"
            style="width: 200px;"
            class="filter-item"
            @keyup.enter.native="handleFilter"
          />
          <el-select
            v-model="listQuery.OrganizationUnitID"
            placeholder="Phong ban"
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
            v-model="listQuery.TimeSheet"
            placeholder="Bang cham cong"
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
          <el-select
            v-model="listQuery.JobPositionID"
            placeholder="Chuc vu"
            clearable
            class="filter-item"
            style="width: 130px"
          >
            <el-option
              v-for="item in job_position"
              :key="item.key"
              :label="item.display_name + '(' + item.key + ')'"
              :value="item.key"
            />
          </el-select>

          <label class="label_date" style="margin-left:20px">Tu ngay: </label>
          <el-date-picker
            style="width: 200px;"
            class="filter-item"
            v-model="listQuery.start_date"
            type="datetime"
            placeholder="Please pick a date"
            format="yyyy-MM-dd hh:mm"
            value-format="yyyy-MM-dd hh:mm"
          />
          <label class="label_date" style="margin-left:20px">Den ngay: </label>
          <el-date-picker
            style="width: 200px;"
            class="filter-item"
            v-model="listQuery.to_date"
            type="datetime"
            placeholder="Please pick a date"
            format="yyyy-MM-dd hh:mm"
            value-format="yyyy-MM-dd hh:mm"
          />
          <el-button
            v-waves
            class="filter-item"
            type="primary"
            icon="el-icon-search"
            style="margin-left:20px"
            @click="handleFilter"
          >
            Search
          </el-button>
        </div>
      </div>
    </div>
    <div>
      <h1 style="text-align: center;">{{ this.name_time_sheet }}</h1>
    </div>
    <div>
      <el-table
        :key="tableKey"
        v-loading="listLoading"
        :data="list"
        border
        fit
        highlight-current-row
        style="margin-top:20px"
        :v-if="list"
      >
        <el-table-column label="Ho ten" align="center" width="200px" fixed >
          <template slot-scope="{ row }">
            <span>{{ row.user_fullname }}</span>
          </template>
        </el-table-column>
        <el-table-column
          label="Ma nhan vien"
          align="center"
          width="200px"
          fixed
        >
          <template slot-scope="{ row }">
            <span>{{ row.MaNV }}</span>
          </template>
        </el-table-column>

        <el-table-column
          align="center"
          width="200px"
          v-for="index in 31"
          :key="index"
          :label="`Ngay ` + index"
        >
          <template slot-scope="{ row }">
            <div
              style="width:150px;height:150px"
              v-for="day in row[`Day` + index]"
              :key="day"
              class="cursor"
              @click="hander_click_box(row[`Day` + index])"
            >
              <div class="view_thu">{{ day.thu }}</div>
              <div class="view_ngay">{{ day.day }}</div>
              <div>Ca lam: {{ day.WorkingShiftName }}</div>
              <div>Tong cong: {{ day.Working_days }}</div>
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
    <div>
      <el-dialog
        v-if="dialogFormVisible"
        width="700px"
        height="700px"
        :visible.sync="dialogFormVisible"
      >
        <div class="flex" style="justify-content: space-between;">
        </div>
        <div slot="footer" class="dialog-footer">
        <el-button @click="dialogFormVisible = false">
            Cancel
        </el-button>
        <el-button type="primary">
            Confirm
        </el-button>
        </div>
      </el-dialog>
    </div>
  </div>
</template>
<script>
import Pagination from "@/components/Pagination";
const organization_unit = [
  { key: "1", display_name: "Phong hanh chinh" },
  { key: "2", display_name: "Phong phat trien phan mem" },
  { key: "3", display_name: "Phong nghien cuu" },
  { key: "4", display_name: "Phong kiem thu" }
];
const job_position = [
  { key: "1", display_name: "Thuc tap" },
  { key: "2", display_name: "Chuyen vien" },
  { key: "3", display_name: "Chuyen gia" },
  { key: "4", display_name: "Pho giam doc" },
  { key: "5", display_name: "Giam doc" }
];
export default {
  components: { Pagination },
  data() {
    return {
      tableKey: 0,
      total: 0,
      listQuery: {
        page: 1,
        limit: 5,
        text_search: undefined,
        OrganizationUnitID: undefined,
        JobPositionID: undefined,
        TimeSheet: undefined
      },
      listLoading: false,
      list: null,
      organization_unit,
      job_position,
      list_time_sheet: null,
      name_time_sheet: null,
      dialogFormVisible: false,
      box_click:null
    };
  },
  created() {
    this.getlist_dropbox();
  },
  methods: {
    handleFilter() {
      this.listQuery.page = 1;
      this.getList();
    },
    getList() {
      this.list = [];
      this.listLoading = true;
      let query_filter = `{"$and": [`;
      query_filter += this.listQuery?.text_search
        ? `{"$or":[{"EmployeeName": {"$regex": "${this.listQuery.text_search}", "$options": "$i"}},
                                                                       {"EmployeeCode": {"$regex": "${this.listQuery.text_search}", "$options": "$i"}},
                                                                       {"TimeKeeperName": {"$regex": "${this.listQuery.text_search}", "$options": "$i"}}]},`
        : "";
      query_filter += parseInt(this.listQuery?.OrganizationUnitID)
        ? `{"OrganizationUnitID": { "$regex" : "${this.listQuery.OrganizationUnitID}", "$options": "$i"}},`
        : "";
      query_filter += parseInt(this.listQuery?.JobPositionID)
        ? `{"JobPositionID": {"$regex": "${this.listQuery.JobPositionID}", "$options": "$i"}},`
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
      let param = {
        page_size: this.listQuery.limit,
        page_number: this.listQuery.page,
        query_filter: query_filter
      };
      console.log(param);

      this.$store
        .dispatch(`timesheet_detail/get_all_page_search`, param)
        .then(res => {
          debugger;
          this.list = res.results;
          if (res.results.length > 0) {
            this.name_time_sheet = res.results[0].TimeSheetName.toUpperCase();
          }

          this.total = res.totals;
          this.listLoading = false;
        });
    },
    getlist_dropbox() {
      this.$store.dispatch(`timesheet_detail/get_list`).then(res => {
        this.list_time_sheet = res;
      });
    },
    hander_click_box(day) {
      this.box_click = day;
      this.dialogFormVisible=true
    }
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
</style>
