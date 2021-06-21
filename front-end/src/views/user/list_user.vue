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
            placeholder="MNV/Tên/Email"
            style="width: 200px;"
            class="filter-item"
            @keyup.enter.native="handleFilter"
          />
          <el-select
            v-model="listQuery.is_training"
            placeholder="IsTraining"
            clearable
            style="width: 100px"
            class="filter-item"
          >
            <el-option
              v-for="item in training"
              :key="item.key"
              :label="item.display_name"
              :value="item.key"
            />
          </el-select>
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
            v-model="listQuery.JobPositionID"
            placeholder="Chức vụ"
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
        </div>

        <div>
          <label class="label_date">Từ ngày: </label>
          <el-date-picker
            style="width: 200px;"
            class="filter-item"
            v-model="listQuery.start_date"
            type="date"
            placeholder="Please pick a date"
            value-format="yyyy-MM-dd"
            format="yyyy-MM-dd"
          />
          <label class="label_date">Den ngay: </label>
          <el-date-picker
            style="width: 200px;"
            class="filter-item"
            v-model="listQuery.to_date"
            type="date"
            placeholder="Please pick a date"
            value-format="yyyy-MM-dd"
            format="yyyy-MM-dd"
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
        @click="addUser"
        class="filter-item"
        style="margin-left: 10px;"
        type="primary"
        icon="el-icon-edit"
        v-if="checkRolePermission('Add', subsystem_code, false)"
      >
        Thêm mới
      </el-button>
      <el-button
        v-waves
        :loading="downloadLoading"
        class="filter-item"
        type="primary"
        icon="el-icon-download"
        @click="handleDownload"
      >
        Export
      </el-button>
      <el-checkbox
        v-model="showJobPosition"
        class="filter-item"
        style="margin-left:15px;"
        @change="tableKey = tableKey + 1"
      >
        Vị trí công việc
      </el-checkbox>
      <el-checkbox
        v-model="showOgUnit"
        class="filter-item"
        style="margin-left:15px;"
        @change="tableKey = tableKey + 1"
      >
        Phòng ban
      </el-checkbox>
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
      @sort-change="sortChange"
    >
      <el-table-column
        label="MaNV"
        prop="id"
        sortable="custom"
        align="center"
        width="100"
        :class-name="getSortClass('id')"
      >
        <template slot-scope="{ row }">
          <span>{{ row.MaNV }}</span>
        </template>
      </el-table-column>
      <el-table-column label="Ngày tạo" width="150px" align="center">
        <template slot-scope="{ row }">
          <span>{{ row.CreateDate | parseTime("{y}-{m}-{d}") }}</span>
        </template>
      </el-table-column>
      <el-table-column label="Tên nhân viên" width="150px" align="center">
        <template slot-scope="{ row }">
          <span>{{ row.full_name }}</span>
        </template>
      </el-table-column>
      <el-table-column label="email" width="200px" align="center">
        <template slot-scope="{ row }">
          <span>{{ row.email }}</span>
        </template>
      </el-table-column>
      <el-table-column label="Ảnh đại diện" width="195px" align="center">
        <template slot-scope="{ row }">
          <img class="img-current w-full" :src="row.Avatar" />
        </template>
      </el-table-column>
      <el-table-column
        v-if="showJobPosition"
        label="Vị trí"
        width="150px"
        align="center"
      >
        <template slot-scope="{ row }">
          <span style="color:red;">{{ row.JobPositionName }}</span>
        </template>
      </el-table-column>
      <el-table-column
        v-if="showOgUnit"
        label="Phòng ban"
        width="150px"
        align="center"
      >
        <template slot-scope="{ row }">
          <span style="color:red;">{{ row.OrganizationUnitName }}</span>
        </template>
      </el-table-column>
      <el-table-column label="Status" class-name="status-col" width="100">
        <template slot-scope="{ row }">
          <el-tag :type="row.status | statusFilter">
            {{ row.status == "1" ? "Active" : "Diactive" }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column
        label="Hành động"
        align="center"
        width="300"
        class-name="small-padding fixed-width"
      >
        <template slot-scope="{ row, $index }">
          <el-button
            type="primary"
            size="mini"
            @click="editUser(row)"
            v-if="checkRolePermission('Edit', subsystem_code, false)"
          >
            Sửa
          </el-button>
          <el-button
            size="mini"
            type="danger"
            @click="confirmDeleteUser(row, $index)"
            v-if="checkRolePermission('Edit', subsystem_code, false)"
          >
            Xóa
          </el-button>
          <el-button
            v-if="
              !row.IsTrain &&
                checkRolePermission('Training', subsystem_code, false)
            "
            size="mini"
            type="primary"
            @click="traninUser(row)"
          >
            Traning
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
      width="1500px"
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
        <div class="flex" style="justify-content: space-between;">
          <div>
            <el-form-item label="Họ tên " prop="full_name">
              <el-input v-model="temp.full_name" />
            </el-form-item>
            <el-form-item label="Tên đăng nhập " prop="user_name">
              <el-input v-model="temp.user_name" />
            </el-form-item>
            <el-form-item label="Email " prop="email">
              <el-input v-model="temp.email" />
            </el-form-item>
            <el-form-item label="Mobile " prop="Mobile">
              <el-input
                v-model="temp.Mobile"
                type="tel"
                pattern="/^-?\d+\.?\d*$/"
                onKeyPress="if(this.value.length==10) return false;"
              />
            </el-form-item>
            <el-form-item label="Ngày phép " prop="NumberOfLeaveDay">
              <el-input v-model="temp.NumberOfLeaveDay" />
            </el-form-item>
            <el-form-item label="Địa chỉ " prop="Address">
              <el-input v-model="temp.Address" />
            </el-form-item>
          </div>
          <div>
            <input
              id="import-file"
              type="file"
              @change="changeFile($event)"
              style="display:none"
            />
            <el-form-item label="Bộ phận" prop="OrganizationUnitID">
              <el-select
                v-model="temp.OrganizationUnitID"
                class="filter-item"
                placeholder="Chọn phòng ban"
                @change="click_Organization"
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
                v-model="temp.JobPositionID"
                class="filter-item"
                placeholder="Chọn vị trí"
              >
                <el-option
                  v-for="item in job_position"
                  :key="item.key"
                  :label="item.display_name"
                  :value="item.key"
                />
              </el-select>
            </el-form-item>
            <el-form-item label="Giới tính" prop="Gender">
              <el-select
                v-model="temp.Gender"
                class="filter-item"
                placeholder="Chọn giới tính"
              >
                <el-option
                  v-for="item in GenderList"
                  :key="item.key"
                  :label="item.display_name"
                  :value="item.key"
                />
              </el-select>
            </el-form-item>
            <el-form-item label="Loại tài khoản" prop="group_role_id">
              <el-select
                v-model="temp.group_role_id"
                class="filter-item"
                placeholder="Chọn quyền người dùng"
              >
                <el-option
                  v-for="item in ListTypeAcc"
                  :key="item.key"
                  :label="item.label"
                  :value="item.key"
                />
              </el-select>
            </el-form-item>
            <el-form-item label="Ngày thuê" prop="HireDate">
              <el-date-picker
                v-model="temp.HireDate"
                type="date"
                placeholder="Chọn ngày thuê"
              />
            </el-form-item>
            <el-form-item label="Ngày nhận" prop="ReceiveDate">
              <el-date-picker
                v-model="temp.ReceiveDate"
                type="date"
                placeholder="Chọn ngày nhận"
              />
            </el-form-item>
            <el-form-item label="Ngày sinh" prop="BirthDay">
              <el-date-picker
                v-model="temp.BirthDay"
                type="date"
                placeholder="Chọn ngày sinh"
              />
            </el-form-item>
          </div>
          <div class="">
            <el-form-item label="Ảnh đại diện" prop="Avatar">
              <label for="import-file">
                <div class="flex btn-select">
                  <div class="el-icon-upload"></div>
                  <div class="m-l-8">
                    Chọn ảnh
                  </div>
                </div>
              </label>
            </el-form-item>
            <div class="img-select">
              <img
                style="width: 400px;height: 300px;border-radius: 8px;"
                class="img-current "
                :src="src"
              />
            </div>
          </div>
        </div>
        <div>
          <el-form-item
            prop="list_role_id"
            v-if="temp.group_role_id == 1"
            style="margin-bottom:10px"
            label="Danh sách vai trò"
          >
            <el-select
              class="select-role"
              v-model="temp.list_role_id"
              multiple
              filterable
              default-first-option
              placeholder="Chọn danh sách vai trò"
            >
              <el-option
                v-for="item in options"
                :key="item.value"
                :label="item.text"
                :value="item.value"
              >
              </el-option>
            </el-select>
          </el-form-item>
        </div>
        <div>
          <UploadImageTrain
            :objConfirm="objConfirm"
            @outputSaveFile="outputSaveFile"
          />
        </div>
      </el-form>
      <div slot="footer" class="dialog-footer">
        <el-button @click="dialogFormVisible = false">
          Hủy
        </el-button>
        <el-button type="primary" @click="saveUser">
          Xác nhận
        </el-button>
      </div>
    </el-dialog>

    <el-dialog
      :before-close="closeDialog"
      width="1000px"
      height="830px"
      :visible.sync="isVisibleTraning"
      title="Traning"
      class="tranin-user"
    >
      <div class="flex">
        <div
          class="list-imt-his flex"
          style="flex-wrap: wrap;height: 100%;max-height: 600px;overflow: auto;"
        >
          <img
            class="img-his"
            :src="url"
            style=" height: 45%;width: 45%;margin: 0 24px 12px 0;"
          />
        </div>
        <div
          class="list-imt-his flex"
          style="flex-wrap: wrap;height: 100%;max-height: 600px;overflow: auto;"
        >
          <img
            v-for="(item, index) in listImg"
            :key="index"
            class="img-his"
            :src="item"
            style=" height: 45%;width: 45%;margin: 0 24px 12px 0;"
          />
        </div>
      </div>
      <span slot="footer" class="dialog-footer">
        <el-button
          v-if="listImg && listImg.length >= 5"
          type="primary"
          @click="
            saveDataTranning();
            isVisibleTraning = false;
          "
          >Xác nhận</el-button
        >
      </span>
    </el-dialog>
  </div>
</template>

<script>
import { fetchPv, updateArticle } from "@/api/article";
import waves from "@/directive/waves"; // waves directive
import { parseTime } from "@/utils";
import Pagination from "@/components/Pagination"; // secondary package based on el-pagination
import checkRolePermission from "@/utils/permission";
import UploadImageTrain from "@/views/user/UploadImageTrain";

const GenderList = [
  { key: "0", display_name: "Nữ" },
  { key: "1", display_name: "Nam" }
];
export default {
  name: "ComplexTable",
  components: { Pagination, UploadImageTrain },
  directives: { waves },
  filters: {
    statusFilter(status) {
      const statusMap = {
        "1": "success",
        draft: "info",
        "0": "danger"
      };
      return statusMap[status];
    },
    typeFilter(type) {
      return calendarTypeKeyValue[type];
    }
  },
  data() {
    return {
      options: [],
      isVisibleTraning: false,
      socket: null,
      listImg: [],
      url: "",
      countImg: 10,
      isTraining: false,

      objConfirm: { value: false },
      src: "",
      file: undefined,
      tableKey: 0,
      list: null,
      total: 0,
      listLoading: true,
      subsystem_code: "QL_NHAN_SU",
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
      importanceOptions: [1, 2, 3],
      organization_unit:[],
      ListTypeAcc: [
        { key: "0", label: "Nhân viên" },
        { key: "1", label: "Quản trị" }
      ],
      job_position:[],
      GenderList,
      training: [
        { display_name: "Đã training", key: "1" },
        { display_name: "Chưa training", key: "0" }
      ],
      sortOptions: [
        { label: "ID Ascending", key: "+id" },
        { label: "ID Descending", key: "-id" }
      ],
      statusOptions: ["published", "draft", "deleted"],
      showJobPosition: false,
      showOgUnit: false,
      list_role_id: "",
      temp: {
        full_name: "",
        user_name: "",
        email: "",
        Mobile: "",
        NumberOfLeaveDay: "",
        Avatar: "",
        CreateDate: "",
        CreateBy: "",
        ModifiedDate: "",
        ModifiedBy: "",
        OrganizationUnitID: "",
        OrganizationUnitName: "",
        JobPositionID: "",
        JobPositionName: "",
        HireDate: "",
        ReceiveDate: "",
        state: 0,
        Address: "",
        BirthDay: "",
        IsTrain: "",
        link_Avatar_old: "",
        Gender: "",
        group_role_id: "",
        list_role_id: ""
      },
      dialogFormVisible: false,
      dialogStatus: "",
      textMap: {
        update: "Edit",
        create: "Create"
      },
      dialogPvVisible: false,
      pvData: [],
      list_commune:[],
      list_district:[],
      list_provincial:[],
      rules: {
        full_name: [
          { required: true, message: "Yêu cầu nhập họ tên", trigger: "change" }
        ],
        user_name: [
          {
            required: true,
            message: "Yêu cầu nhập tên đăng nhập",
            trigger: "change"
          }
        ],
        // BirthDay: [{ type: 'date', required: true, message: 'Yeu cau nhap ngay sinh', trigger: 'change' }],
        Mobile: [
          {
            min: 10,
            max: 10,
            message: "Số điện thoại phải yêu cầu 10 số.",
            trigger: "blur"
          },
          {
            required: true,
            pattern: /(^\d{10}$)|(^\d{10}$)|(^\d{10}(\d|X|x)$)/,
            message: "Nhập đúng số điện thoại.",
            trigger: "blur"
          }
        ],
        group_role_id: [
          {
            required: true,
            message: "Yêu cầu chọn quyền người dùng",
            trigger: "change"
          }
        ],
        JobPositionID: [
          {
            required: true,
            message: "Yêu cầu chọn vị trí ",
            trigger: "blur"
          }
        ],
        OrganizationUnitID: [
          { required: true, message: "Yêu cầu chọn tổ chức", trigger: "change" }
        ],
        list_role_id: [
          {
            required: true,
            message: "Yêu cầu chọn danh sách quyền",
            trigger: "blur"
          }
        ]
      },
      downloadLoading: false,
      current_user: null
    };
  },
  created() {
    this.getList();
    this.getPermission();
  },
  methods: {
    closeDialog() {
      this.$store.dispatch(`camera/changeFlag`);
      this.isVisibleTraning = false;
    },
    getSocketTraning() {
      this.$socket.on("imageConversionByClient", obj => {
        let binary = "";
        const bytes = new Uint8Array(obj.buffer);
        const len = bytes.byteLength;
        for (let i = 0; i < len; i++) {
          binary += String.fromCharCode(bytes[i]);
        }
        this.url = "data:image/jpeg;base64," + window.btoa(binary);
      }),
        console.log(this.current_user);
      let param = {
        MaNV: this.current_user.MaNV
      };
      this.listImg = [];
      this.$store.dispatch(`camera/getDataTranning`, param);
      this.$socket.on("imageBoxToClient", obj => {
        this.listImg.unshift(obj.img_path);
        if (
          this.listImg &&
          this.listImg.length > this.countImg &&
          !this.isTraining
        ) {
          this.listImg.splice(this.countImg, 1);
        }
      });
    },
    saveDataTranning() {
      this.countImg = 10;
      this.$store.dispatch(`camera/saveDataTranning`, this.listImg);
      setTimeout(() => {
        this.isTraining = false;
        this.listImg = [];
      }, 500);
    },

    traninUser(data) {
      if(this.checkRolePermission("Training",this.subsystem_code)){
        this.current_user = JSON.parse(JSON.stringify(data));
        this.isVisibleTraning = true;
        this.getSocketTraning();
      }
    },
    getPermission() {
      this.$store.dispatch("role_permission/getRoles", {}).then(res => {
        res.roles.forEach(us => {
          var item = {
            value: us.role_id,
            text: us.role_name + " - " + us.role_description
          };
          this.options.push(item);
        });
      });
    },
    changeFile(e) {
      if (!e) {
        return;
      }
      console.log(e);
      this.file = e.target.files[e.target.files.length - 1];
      const reader = new FileReader();
      reader.readAsDataURL(this.file);
      reader.onload = results => {
        console.log(results);
        this.src = results.target.result;
      };
    },
    checkRolePermission,

    getList() {
      this.listLoading = true;
      let query_filter = `{"$and": [`;
      query_filter += parseInt(this.listQuery?.is_training)
        ? `{"is_training": {"$regex": "${this.listQuery.is_training}", "$options": "$i"}},`
        : "";
      query_filter += this.listQuery?.text_search
        ? `{"$or":[{"email": {"$regex": "${this.listQuery.text_search}", "$options": "$i"}},
                                                                       {"MaNV": {"$regex": "${this.listQuery.text_search}", "$options": "$i"}},
                                                                       {"full_name": {"$regex": "${this.listQuery.text_search}", "$options": "$i"}}]},`
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
      this.$store.dispatch(`user/get_all_page_search`, param).then(res => {
        console.log(res);
        this.list = res.results;
        this.total = res.totals;
        this.listLoading = false;
      });
      this.$store.dispatch(`organization_unit/getList`).then(res =>{
      console.log(res)
      this.organization_unit = res
      })
    },

    handleFilter() {
      this.listQuery.page = 1;
      this.getList();
    },
    handleModifyStatus(row, status) {
      this.$message({
        message: "Success",
        type: "success"
      });
      row.status = status;
    },
    sortChange(data) {
      const { prop, order } = data;
      if (prop === "id") {
        this.sortByID(order);
      }
    },
    sortByID(order) {
      if (order === "ascending") {
        this.listQuery.sort = "+id";
      } else {
        this.listQuery.sort = "-id";
      }
      this.handleFilter();
    },
    resetTemp() {
      this.temp = {
        id: undefined,
        importance: 1,
        remark: "",
        timestamp: new Date(),
        title: "Thông báo",
        status: "published",
        type: ""
      };
    },
    handleCreate() {
      if(this.checkRolePermission("Add",this.subsystem_code)){
        this.resetTemp();
        this.dialogStatus = "create";
        this.dialogFormVisible = true;
        this.$nextTick(() => {
          this.$refs["dataForm"].clearValidate();
        });
      }
    },

    addUser() {
      if(this.checkRolePermission("Add",this.subsystem_code)){
        this.temp = {};
        this.src = "http://localhost:4321/avatar/default_avatar.png";
        this.temp.state = 1;
        this.dialogFormVisible = true;
      // this.list_roles=[]
      }
    },

    editUser(data) {
      // this.list_roles = []
      if(this.checkRolePermission("Edit",this.subsystem_code)){
        this.temp = Object.assign({}, data); // copy obj
        // if(this.temp.list_roles){
        //   this.list_roles = this.temp.list_roles

        // };
        this.src = this.temp.Avatar;
        this.file = null;
        this.temp.state = 2;
        this.dialogFormVisible = true;
      }
    },

    saveUser() {
      let me = this;
      // this.temp.list_roles = this.list_roles
      this.$refs["dataForm"].validate(valid => {
        if (valid) {
          let item_1 = this.job_position.find(
            x => x.key == this.temp.JobPositionID
          );
          if (item_1) {
            this.temp.JobPositionName = item_1.display_name;
          }
          let item_2 = this.organization_unit.find(
            x => x.key == this.temp.OrganizationUnitID
          );
          if (item_2) {
            this.temp.OrganizationUnitName = item_2.display_name;
          }
          if (this.file) {
            let formData = new FormData();
            formData.append("file", this.file);
            this.$store
              .dispatch(`user/insertFileAvatar`, formData)
              .then(result => {
                if (me.temp.state == 2) {
                  debugger;
                  me.temp.link_Avatar_old = me.temp.Avatar;
                }
                me.temp.Avatar = result.link_image;
                // me.temp.name = result.data.filename;
                this.objConfirm = JSON.parse(
                  JSON.stringify({ value: true, MaNV: this.temp.MaNV })
                );
              });
          } else {
            this.objConfirm = JSON.parse(
              JSON.stringify({ value: true, MaNV: this.temp.MaNV })
            );
          }
        }
      });
    },
    confirmDeleteUser(data, e) {
      if(this.checkRolePermission("Delete",this.subsystem_code)){
      this.temp = Object.assign({}, data);
      this.temp.state = 3;
      this.$confirm(
        `Ban co muon xoa user ${this.temp.full_name}?`,
        "Thong bao",
        {
          confirmButtonText: "Xoa",
          cancelButtonText: "Huy",
          type: "warning"
        }
      )
        .then(async () => {
          await this.deleteUser();
        })
        .catch(err => {
          console.error(err);
        });
      }
    },
    deleteUser() {
      this.$store.dispatch(`user/saveUser`, this.temp).then(res => {
        this.$notify({
          title: "Thông báo",
          dangerouslyUseHTMLString: true,
          message: `Xoa user thanh cong`,
          type: "success"
        });
        this.getList();
      });
    },
    outputSaveFile(data) {
      let me = this;
      if (data) {
        me.temp.IsTrain = true;
        me.$store.dispatch(`user/saveUser`, me.temp).then(res => {
          this.$store.dispatch(`user/train`, this.temp).then(res => {
            this.$notify({
              title: "Thông báo",
              message: "Them user thanh cong",
              type: "success",
              duration: 2000
            });
            this.getList();
          });
        });
      } else {
        me.temp.IsTrain = false;
        me.$store.dispatch(`user/saveUser`, me.temp).then(res => {
          this.$notify({
            title: "Thông báo",
            message: "Them user thanh cong",
            type: "success",
            duration: 2000
          });
          this.getList();
        });
      }
      this.dialogFormVisible = false;
    },

    handleUpdate(row) {
      this.temp = Object.assign({}, row); // copy obj
      this.temp.timestamp = new Date(this.temp.timestamp);
      this.dialogStatus = "update";
      this.dialogFormVisible = true;
      this.$nextTick(() => {
        this.$refs["dataForm"].clearValidate();
      });
    },
    click_Organization(data){
      debugger
      let param = {
        "OrganizationUnitID":data
      }
       this.$store.dispatch(`job_position/getByOg`,param).then(res =>{
        console.log(res)
        this.job_position = res
      })
      this.temp.JobPositionID =""
    },
    updateData() {
      this.$refs["dataForm"].validate(valid => {
        if (valid) {
          const tempData = Object.assign({}, this.temp);
          tempData.timestamp = +new Date(tempData.timestamp);
          updateArticle(tempData).then(() => {
            const index = this.list.findIndex(v => v.id === this.temp.id);
            this.list.splice(index, 1, this.temp);
            this.dialogFormVisible = false;
            this.$notify({
              title: "Success",
              message: "Update Successfully",
              type: "success",
              duration: 2000
            });
          });
        }
      });
    },
    handleDelete(row, index) {
      this.$notify({
        title: "Success",
        message: "Delete Successfully",
        type: "success",
        duration: 2000
      });
      this.list.splice(index, 1);
    },
    handleFetchPv(pv) {
      fetchPv(pv).then(response => {
        this.pvData = response.data.pvData;
        this.dialogPvVisible = true;
      });
    },
    handleDownload() {
      this.downloadLoading = true;
      import("@/vendor/Export2Excel").then(excel => {
        const tHeader = ["timestamp", "title", "type", "importance", "status"];
        const filterVal = [
          "timestamp",
          "title",
          "type",
          "importance",
          "status"
        ];
        const data = this.formatJson(filterVal);
        excel.export_json_to_excel({
          header: tHeader,
          data,
          filename: "table-list"
        });
        this.downloadLoading = false;
      });
    },
    formatJson(filterVal) {
      return this.list.map(v =>
        filterVal.map(j => {
          if (j === "timestamp") {
            return parseTime(v[j]);
          } else {
            return v[j];
          }
        })
      );
    },
    getSortClass: function(key) {
      const sort = this.listQuery.sort;
      return sort === `+${key}` ? "ascending" : "descending";
    },
    getProvincial(value=1){
      if(!value){
        this.list_provincial = [];
        return;
      }
      axios.get("assets/dist/tinh_tp.json").then(data => {
        this.list_provincial = Object.keys(data).map(key => data[key]).sort(function (a, b) {
          if (a.name < b.name) { return -1; }
          if (a.name > b.name) { return 1; }
          return 0;
        });
      })
    },
    getDistrict(value){
      if(!value){
        this.list_district = [];
        return;
      }
      axios.get(`assets/dist/quan-huyen/${value}.json`).then(data => {
        this.list_district = Object.keys(data).map(key => data[key]).sort(function (a, b) {
          if (a.name < b.name) { return -1; }
          if (a.name > b.name) { return 1; }
          return 0;
        });
      })
    },

    getCommune(value){
      if(!value){
        this.list_commune = [];
        return;
      }
      axios.get(`assets/dist/xa-phuong/${value}.json`).then(data => {
        this.list_commune = Object.keys(data).map(key => data[key]).sort(function (a, b) {
          if (a.name < b.name) { return -1; }
          if (a.name > b.name) { return 1; }
          return 0;
        });
      })
    }
  },
};
</script>
<style lang="scss">
.el-dialog__body {
  // max-height: 600px !important;
  overflow: auto !important;
}
.el-dialog {
  margin-top: 5vh !important;
}
.label_date {
  margin: 0px 10px 0px 10px;
}
.btn-select {
  height: 36px;
  align-items: center;
  cursor: pointer;
  color: #ffffff;
  background-color: #1890ff;
  border-color: #1890ff;
  padding: 10px 20px;
  font-size: 14px;
  border-radius: 4px;
  width: fit-content;
}
.el-form-item__content {
  margin-left: 24px !important;
  display: flex;
}
.el-form-item__label {
  width: 150px !important;
}

.train-user {
  .img-current {
    height: 772px;
  }
  .list-imt-his {
    overflow: auto;
    width: 25%;
    height: 772px;
  }
  .img-his {
    margin: 0 16px 8px 16px;
    width: calc(100% - 32px);
    height: 250px;
  }
}

.select-role {
  width: 692px;
}
</style>
