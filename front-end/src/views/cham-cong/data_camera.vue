<template>
  <div class="app-container">
    <div class="filter-container" v-if="checkRolePermission('View', subsystem_code, false)"> 
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
            placeholder="Phòng ban"
            clearable
            class="filter-item"
            style="width: 200px"
            @change="click_Organization"
          >
            <el-option
              v-for="item in organization_unit"
              :key="item.key"
              :label="item.display_name + '(' + item.key + ')'"
              :value="item.key"
              
            />
          </el-select>
          <el-select
            v-model="listQuery.JobPositionID"
            placeholder="Chức vụ"
            clearable
            class="filter-item"
            style="width: 130px"
          >
            <el-option
              v-for="item in job_position"
              :key="item.key"
              :label="item.display_name"
              :value="item.key"
            />
          </el-select>

          <label class="label_date" style="margin-left:20px">Từ ngày: </label>
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
            class="filter-item"
            type="primary"
            icon="el-icon-search"
            style="margin-left:20px"
            @click="handleFilter"
          >
            Tìm kiếm
          </el-button>
        </div>
      </div>
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
      >
        <el-table-column label="Họ tên" align="center">
          <template slot-scope="{ row }">
            <span>{{ row.EmployeeName }}</span>
          </template>
        </el-table-column>
        <el-table-column label="Mã nhân viên" align="center">
          <template slot-scope="{ row }">
            <span>{{ row.EmployeeCode }}</span>
          </template>
        </el-table-column>
        <el-table-column label="Tổ chức" align="center">
          <template slot-scope="{ row }">
            <span>{{ row.OrganizationUnitName }}</span>
          </template>
        </el-table-column>
        <el-table-column label="Vị trí" align="center">
          <template slot-scope="{ row }">
            <span>{{ row.JobPositionName }}</span>
          </template>
        </el-table-column>
        <el-table-column label="Ngày chấm công" align="center">
          <template slot-scope="{ row }">
            <span>{{ row.CheckTime | parseTime("{y}-{m}-{d} {h}:{m}") }}</span>
          </template>
        </el-table-column>
         <el-table-column label="Máy chấm công" align="center">
          <template slot-scope="{ row }">
            <span>{{ row.TimeKeeperName}}</span>
          </template>
        </el-table-column>
        <el-table-column label="Hình ảnh" align="center">
          <template slot-scope="{ row }">
            <img class="img-current w-full" :src="row.ImagePath" />
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
</template>
<script>
import Pagination from "@/components/Pagination";
import checkRolePermission from "@/utils/permission";
export default {
  components: { Pagination },
  data() {
    return {
      total: 0,
      listQuery: {
        page: 1,
        limit: 5,
        text_search: undefined,
        OrganizationUnitID: undefined,
        JobPositionID: undefined,
        start_date: undefined,
        to_date: undefined
      },
      subsystem_code: "DU_LIEU_CHAM_CONG",
      tableKey:1,
      listLoading: true,
      list: null,
      organization_unit:[],
      job_position:[]
    };
  },
  created() {
    this.getList();
  },
  methods: {
    checkRolePermission,
    click_Organization(data){
      debugger
      let param = {
        "OrganizationUnitID":data
      }
       this.$store.dispatch(`job_position/getByOg`,param).then(res =>{
        console.log(res)
        this.job_position = res
        this.listQuery.JobPositionID = []
      })
    },
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
      query_filter += `]}`;
      let index = query_filter.lastIndexOf(",");
      if (index > 0) {
        query_filter =
          query_filter.substring(0, index) + query_filter.slice(index + 1);
      }
      let param = {
        page_size: this.listQuery.limit,
        page_number: this.listQuery.page,
        query_filter: query_filter,
        to_date: this.listQuery.to_date ? this.listQuery.to_date : undefined,
        start_date: this.listQuery.start_date
          ? this.listQuery.start_date
          : undefined
      };
      console.log(param);
      this.$store
        .dispatch(`timekeeper_data/get_all_page_search`, param)
        .then(res => {
          this.list = res.results;
          this.total = res.totals;
          this.listLoading = false;
        });
      this.$store.dispatch(`organization_unit/getList`).then(res =>{
        console.log(res)
        this.organization_unit = res
      })
    }
  }
};
</script>
