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
        class="filter-item"
        type="primary"
        icon="el-icon-search"
        @click="handleFilter"
      >
        Search
      </el-button>
      <el-button
        @click="handleaddShiftPlan"
        class="filter-item"
        style="margin-left: 10px;"
        type="primary"
        icon="el-icon-edit"
      >
        Add
      </el-button>
    </div>

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
        :model="detailDataX"
        label-position="left"
        label-width="70px"
        style="margin:0 50px;"
      >
        <div>
          <h2>Thong tin chung</h2>
        </div>
        <div class="flex">
          <div class="w-full">
            <el-form-item label="Ten bang phan ca" prop="ShiftPlanName">
              <el-input v-model="detailDataX.ShiftPlanName" />
            </el-form-item>
          </div>
        </div>
        <div></div>
        <div>
          <el-form-item
            prop="list_roles"
            style="margin-bottom:10px"
            label="Danh sach ca"
          >
            <el-select
              class="select-role"
              v-model="list_working_shift_selected"
              multiple
              filterable
              default-first-option
              placeholder="Chon danh sach ca"
              style="width: 100%;"
            >
              <el-option
                v-for="item in list_working_shift"
                :key="item.value"
                :label="item.text"
                :value="item"
              >
              </el-option>
            </el-select>
          </el-form-item>
        </div>

        <div>
          <h2>Thoi gian ap dung</h2>
        </div>
        <div style="margin-bottom:20px">
          <el-radio-group v-model="detailDataX.DateApplyType">
            <el-radio
              v-for="item in optionsRadio"
              :key="item.value"
              :label="item.label"
            ></el-radio>
          </el-radio-group>
        </div>
        <div v-if="detailDataX.DateApplyType" class="flex">
          <el-form-item label="Ngay bat dau">
            <el-date-picker
              v-model="detailDataX.FromDate"
              type="date"
              placeholder="Ngay bat dau"
              value-format="yyyy-MM-dd"
              format="yyyy-MM-dd"
            />
          </el-form-item>
          <el-form-item v-if="detailDataX.DateApplyType=='Tu ngay den ngay'"
            label="Ngay ket thuc"
            style="margin-left:100px"
          >
            <el-date-picker
              v-model="detailDataX.ToDate"
              type="date"
              placeholder="Ngay ket thuc"
              value-format="yyyy-MM-dd"
              format="yyyy-MM-dd"
            />
          </el-form-item>
        </div>
        <div v-if="detailDataX.DateApplyType">
          <el-form-item label="Lap theo">
            <div
              style="width:700px;height: fit-content(20em);background:#f0f2f5"
            >
              <div style="margin:40px">
                <div class="flex">
                  <div class="flex">
                    <el-select
                    v-model="detailDataX.RepeatType"
                    class="select-role"
                    @change="repeatTypeChange"
                    style="width: 100px;"
                  >
                    <el-option
                      v-for="item in cycleValueBox"
                      :key="item.GroupOfEmployeeID"
                      :label="item.GroupOfEmployeeName"
                      :value="item.GroupOfEmployeeID"
                      
                    >
                    </el-option>
                  </el-select>
                  
                  </div>
                  <div v-if="detailDataX.RepeatType!=1" class="flex">
                    <el-form-item style="margin-left:10px" label="Chu ky lap">
                    </el-form-item>
                    <el-input-number v-model="num_repeat" placeholder="empty" :min="0" :max=this.daymax></el-input-number>
                    <el-form-item
                      style="margin-left:10px"
                      :label="detailDataX.RepeatType==2 ? 'tuan' : 'thang'"
                      prop="ModifiedDate"
                    >
                    </el-form-item>
                  </div>
                </div>
              </div>
               <div style="margin-left:40px" v-if="this.detailDataX.RepeatType == 1">
                <el-radio-group v-model="IsWorkingDay">
                 <div class="flex">
                   <el-radio  label="Chu ky lap" style="margin-top:10px"></el-radio>
                    <el-input-number v-model="num_repeat" placeholder="empty" :min="0" :max=this.daymax></el-input-number>
                    <el-form-item
                      style="margin-left:10px"
                      label="Ngay"
                      prop="ModifiedDate"
                    >
                    </el-form-item>
                  
                 </div>
                 <div style="margin:20px 0px 40px 0px">
                    <el-radio label="Ngay lam viec thu 2 den thu 6"></el-radio>
                 </div>
                  
                </el-radio-group>
              </div>
              <div style="margin:40px" v-if="this.detailDataX.RepeatType != 1">
                <el-radio-group v-model="IsDayOfMonth">
                 
                  <div class="flex" v-if="this.detailDataX.RepeatType ==3">
                    <div style="margin:10px 10px 0px 0px">
                      <el-radio key="0" label="Vao" value="false"></el-radio>
                    </div>
                    <div>
                      <el-select
                        class="select-role"
                        placeholder="Chon mot"
                        style="width:205px"
                        v-model="DayOfWeekNumber"
                      >
                        <el-option
                          v-for="item in listDayRadioBox"
                          :key="item.WeekDayID"
                          :label="item.WeekDayName"
                          :value="item.WeekDayID"
                        >
                        </el-option>
                      </el-select>
                    </div>
                    <div style="margin-left:35px">
                      <el-select
                        v-model="WeekOfMonth"
                        class="select-role"
                        placeholder="Chon mot"
                        style="width:220px"
                      >
                        <el-option
                          v-for="item in cycleMonthBox"
                          :key="item.MonthID"
                          :label="item.MonthOrder"
                          :value="item.MonthID"
                        >
                        </el-option>
                      </el-select>
                    </div>
                  </div>
                  <div class="flex" v-if="this.detailDataX.RepeatType ==2">
                    <div>
                      <el-checkbox-group
                      v-model="DayOfWeek"
                      size="medium"
                      >
                        <el-checkbox
                          v-for="item in listDayCheckBox"
                          :key="item.DayValue"
                          :label="item"
                          style="margin-right:30px"
                        >
                        {{item.TextValue}}
                        </el-checkbox>
                      </el-checkbox-group>
                    </div>
                  </div>
                  <div style="margin-top:40px" v-if="this.detailDataX.RepeatType ==3">
                    <div class="flex">
                      <div style="margin:10px 10px 0px 0px">
                        <el-radio key="0" label="Vao ngay" value="true"></el-radio>
                      </div>
                      <div >
                        <el-input-number style="width:168px !important" v-model="DayOfMonth" placeholder="0" :min="0" :max="31"></el-input-number>
                      </div>
                    </div>
                  </div>
                </el-radio-group>
              </div>
            </div>
            
          </el-form-item>
        </div>
        <div>
          <h2>Doi tuong ap dung</h2>
        </div>
        <div>
          <div>
            <el-radio-group v-model="objectApplyType" @change="object_apply_type">
              <el-radio label="Co cau to chuc" value="0" key="0"></el-radio>
              <el-radio label="Danh sach nhan vien" value="1" key="1"></el-radio>
            </el-radio-group>
          </div>
          <div style="margin-top:40px" >
            <el-select
              class="select-role"
              v-model="list_object_selected"
              multiple
              filterable
              default-first-option
              placeholder="Chon doi tuong"
              v-if="this.data_object"
              style="width: 100%;"
            >
              <el-option
                v-for="item in data_object"
                :key="item.value"
                :label="item.text"
                :value="item"
              >
              </el-option>
            </el-select>
          </div>
         
        </div>
      </el-form>
      <div slot="footer" class="dialog-footer">
        <el-button type="success" @click="handleClickView"><span style="font-size:14px; "> Xem truoc</span></el-button>
        <el-button @click="dialogFormVisible = false">
          Huy
        </el-button>
        <el-button type="primary" @click="handleClickApply">
          Them
        </el-button>
       
      </div>
      <div>
        <el-table
          v-if="schedulerData && schedulerData.length"
          :key="tableKey"
          v-loading="listLoading"
          :data="schedulerData"
          border
          fit
          highlight-current-row
          style="margin-top:20px"
        >
          <el-table-column
            label="Ca lam viec"
            align="center"
          >
            <template slot-scope="{ row }">
              <span>{{ row.text }}</span>
            </template>
          </el-table-column>
          <el-table-column label="Ngay lam" align="center">
            <template slot-scope="{ row }">
              <span>{{ row.startDate | parseTime("{y}-{m}-{d}") }}</span>
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
    </el-dialog>
  </div>
</template>
<script>
import moment from "moment";
import Pagination from "@/components/Pagination"; // secondary package based on el-pagination
const organization_unit = [
  { value: "1", text: "Phong hanh chinh" },
  { value: "2", text: "Phong phat trien phan mem" },
  { value: "3", text: "Phong nghien cuu" },
  { value: "4", text: "Phong kiem thu" }
];
export default {
  name: "ShiftPlan",
  components: { Pagination },
  data() {
    return {
      daymax:1,
      dateApplyType:'Tu ngay den ngay',
      options: [],
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
      dialogFormVisible: true,
      listQuery: {
        page: 1,
        limit: 10,
        text_search: undefined,
        is_training: undefined,
        OrganizationUnitID: undefined,
        JobPositionID: undefined,
        start_date: undefined,
        to_date: undefined,
        sort: "+id"
      },
      dialogStatus: "",
      textMap: {
        update: "Edit",
        create: "Create"
      },
      currentListWorkingShift: [],
      currentListOrganozation: [],
      currentListEmployee: [],
      fromDate: new Date(),
      toDate: new Date(),

      schedulerEndDate: null,
      num_repeat:1,
      //------------Lặp ngày------------
      // Theo chu kỳ lặp hay theo ngày làm việc từ 2-> 6
      IsWorkingDay: false,
      // Số ngày lặp
      RepeatDay: 1,
      //------------Lặp tuần------------
      // Số tuần lặp
      RepeatWeek: 1,
      // Ngày lặp trong tuần
      DayOfWeek: [],
      //------------Lặp tháng------------
      // Số tháng lặp
      RepeatMonth: 1,
      // Kiểu lặp trong tháng (true: theo ngày | false: theo thứ)
      IsDayOfMonth: "Vao",
      // Ngày lặp (thứ 2)
      DayOfWeekNumber: 1,
      // Ngày trong tháng
      DayOfMonth: 1,
      // Lặp theo ngày của tháng (1 - Ngày đầu | 5 - Ngày cuối)
      WeekOfMonth: 1,
      // Doi tuong apply cho ca lam viec nay
      objectApplyType:'',
      data_object:null,
      list_working_shift: [],
      list_object_selected:[],
      list_working_shift_selected:[],
      // List giá trị radio Thời gian áp dụng
      optionsRadio: [
        {
          label: "Tu ngay den ngay",
          value: 1
        },
        {
          label: "Khong co ngay ket thuc",
          value: 2
        }
      ],
      // List giá trị lặp theo
      cycleValueBox: [
        {
          GroupOfEmployeeID: 1,
          GroupOfEmployeeName: "Ngay"
        },
        {
          GroupOfEmployeeID: 2,
          GroupOfEmployeeName: "Tuan"
        },
        {
          GroupOfEmployeeID: 3,
          GroupOfEmployeeName: "Thang"
        }
      ],
      // List giá trị lặp theo tháng
      cycleMonthBox: [
        {
          MonthID: 1,
          MonthOrder: "Ngay dau tien cua thang"
        },
        {
          MonthID: 5,
          MonthOrder: "Ngay cuoi cung cua thang"
        }
      ],
      listDayRadioBox: [
        {
          WeekDayID: 1,
          WeekDayName: "Thu 2"
        },
        {
          WeekDayID: 2,
          WeekDayName: "Thu 3"
        },
        {
          WeekDayID: 3,
          WeekDayName: "Thu 4"
        },
        {
          WeekDayID: 4,
          WeekDayName: "Thu 5"
        },
        {
          WeekDayID: 5,
          WeekDayName: "Thu 6"
        },
        {
          WeekDayID: 6,
          WeekDayName: "Thu 7"
        },
        {
          WeekDayID: 0,
          WeekDayName: "Chu nhat"
        }
      ],
      listDayCheckBox: [
        { DayValue: 0, CheckBoxValue: false, TextValue: "SUN" },
        { DayValue: 1, CheckBoxValue: false, TextValue: "MON" },
        { DayValue: 2, CheckBoxValue: false, TextValue: "TUE" },
        { DayValue: 3, CheckBoxValue: false, TextValue: "WED" },
        { DayValue: 4, CheckBoxValue: false, TextValue: "THU" },
        { DayValue: 5, CheckBoxValue: false, TextValue: "FRI" },
        { DayValue: 6, CheckBoxValue: false, TextValue: "SAT" }
      ],
      listDayinCurrentMonth: [],
      multipleBox: [],
      // Dữ liệu lịch
      listDayScheduler: [],
      listShiftScheduler: [],
      schedulerData: [],
      showPreview: true,
      detailDataX: { ...this.detailData},
      validateStartTime: {},
      validateToTime: {},
      saveLoading: false,
      total:0
    };
  },
  props: {
    detailData: {
      // Tên phân ca làm việc
      ShiftPlanName: "",
      // Danh sách ID ca làm việc
      WorkingShiftIDs: "",
      // Danh sách tên ca làm việc
      WorkingShiftNames: "",
      // Loại thời gian áp dụng(1- Từ ngày, đến ngày, 2- Không có ngày kết thúc, 3- Ngày cố định)
      DateApplyType: 1,
      // Từ ngày
      FromDate: "",
      // Đến ngày
      ToDate: "",
      // Loại lặp(1- Lặp theo tháng, 2 - THeo tuần, 3- Ngày)
      RepeatType: 2,
      // Config lặp
      RepeatConfig: "",
      // Đối tượng áp dụng (1: CCTC, 2: Nhân viên)
      ObjectType: 1,
      // Danh sách CCTC đổi
      OrganizationUnitIDs: "",
      // Danh sách CCTC đổi
      OrganizationUnitNames: "",
      // Danh sách CCTC đổi
      EmployeeIDs: "",
      // Danh sách CCTC đổi
      EmployeeNames: ""
    },
    initItemsCombobox: {
      type: [Array, Object],
      default: () => []
    }
  },
  created() {
    let currentDay = new Date();
    this.listDayinCurrentMonth = this.getDaysInMonth(
      currentDay.getMonth(),
      currentDay.getFullYear()
    );
    this.convertRepeatConfig(this.detailDataX);
  },
  methods: {
    handleaddShiftPlan() {
      // if(this.checkRolePermission("Add",this.subsystem_code)){
      this.detailDataX = {};
      this.detailDataX.State = 1;
      this.dialogFormVisible = true;
      let param = {
      };
      this.list_working_shift = []
      this.$store.dispatch(`working_shift/getWorkingShift`, param).then(res => {
        res.results.forEach(item => {
          this.list_working_shift.push({
            "text":item.WorkingShiftName,
            "value":item._id
          })
        });
      });
    },
    object_apply_type(){
      this.data_object = []
      this.list_object_selected = []
      let param = {
      };
      if(this.objectApplyType=='Co cau to chuc'){
        
        this.data_object = organization_unit
      }
      else{
        this.$store.dispatch(`user/get_all_page_search`, param).then(res => {
          res.results.forEach(item => {
            this.data_object.push({
              "text": item.full_name,
              "value": item._id
            })
          });
      });
      }
    },
    repeatTypeChange(){
      debugger
      if(this.detailDataX.RepeatType==2){
        this.daymax = 52
      }
      if(this.detailDataX.RepeatType==1){
        this.daymax = 31
      }
      if(this.detailDataX.RepeatType==3){
        this.daymax = 12
      }
    },
    handleFilter() {
      this.listQuery.page = 1;
      this.getList();
    },
    // handleCheckWeekChange(value){
    //   value.forEach(it => {
    //     this.listDayCheckBox[it].CheckBoxValue = true
    //   });
      
    // },
        /**
     * Lưu dữ liệu RepeatConfig theo Ngày
     * Created by thduong 18/12/2020
     */
    saveRepeatConfigDay() {
      debugger
      let config = {
        DayOfWeek: this.IsWorkingDay == "Chu ky lap" ? false : "MON-FRI",
        RepeatDay: this.num_repeat
      };
      this.detailDataX.RepeatConfig = config;
    },
    /**
     * Lưu dữ liệu RepeatConfig theo Tuần
     * Created by thduong 18/12/2020
     */
    saveRepeatConfigWeek() {
      
      let DayOfWeek = [];
      this.DayOfWeek.forEach(et=>{
        DayOfWeek.push(et.DayValue + 1)
      })
      let config = {
        DayOfWeek: this.DayOfWeek,
        RepeatWeek: this.RepeatWeek
      };
      this.detailDataX.RepeatConfig = config;
    },
    /**
     * Lưu dữ liệu RepeatConfig theo Tháng
     * Created by thduong 18/12/2020
     */
    saveRepeatConfigMonth() {
      let config = {
        RepeatMonth: this.num_repeat,
        WeekOfMonth: this.WeekOfMonth,
        IsDayOfMonth: this.IsDayOfMonth == "Vao"? false:true
      };
      config.IsDayOfMonth && (config.DayOfMonth = this.DayOfMonth);
      !config.IsDayOfMonth && (config.DayOfWeekNumber = this.DayOfWeekNumber + 1);
      this.detailDataX.RepeatConfig = config;
    },
    /**
     * Lưu Phân ca làm việc
     * Created by thduong 18/12/2020
     */
    addShiftPlan() {
      if (this.detailDataX.FromDate > this.detailDataX.ToDate &&this.detailDataX.DateApplyType == 1) {
        this.$notify._error("Ngay bat dau lon hon ngay ket thuc");
        return false;
      }
      if (this.detailDataX.ObjectType == 1 &&this.detailDataX.OrganizationUnitIDs.length == 0) {
        this.$notify._error("Chua chon doi tuong ap dung");
        return false;
      }
      if (this.detailDataX.ObjectType == 2 && this.detailDataX.EmployeeIDs.length == 0) {
        this.$notify._error("Chua chon doi tuong ap dung");
        return false;
      }
      // this.$store
    },
    handleClickView(){
      if(this.detailDataX.DateApplyType=='Tu ngay den ngay'){
          this.detailDataX.DateApplyType = 1
        }
        else{
          this.detailDataX.DateApplyType = 2
        }
        if(this.objectApplyType=='Co cau to chuc'){
          this.detailDataX.OrganizationUnitNames=[]
          this.detailDataX.OrganizationUnitIDs=[]
          this.list_object_selected.forEach(item => {
            
            this.detailDataX.OrganizationUnitNames.push(item.text)
            this.detailDataX.OrganizationUnitIDs.push(item.value)
          });
        }
        if(this.objectApplyType=='Danh sach nhan vien'){
          this.detailDataX.EmployeeNames=[]
          this.detailDataX.EmployeeIDs=[]
          this.list_object_selected.forEach(item => {
            
            this.detailDataX.EmployeeNames.push(item.text)
            this.detailDataX.EmployeeIDs.push(item.value)
          });
        
        }
        if(this.list_working_shift_selected.length){
          this.detailDataX.WorkingShiftIDs=[]
          this.detailDataX.WorkingShiftNames=[]
          this.list_working_shift_selected.forEach(item =>{
            this.detailDataX.WorkingShiftIDs.push(item.value)
            this.detailDataX.WorkingShiftNames.push(item.text)
          })
        }
        switch (this.detailDataX.RepeatType) {
          case 1:
            this.saveRepeatConfigDay();
            break;
          case 2:
            this.saveRepeatConfigWeek();
            break;
          case 3:
            this.saveRepeatConfigMonth();
            break;
          default:
            break;
        }
        this.createShiftPlan(this.detailDataX.RepeatType)
        this.total = this.schedulerData.length
    },
    /**
     * Hàm xử lý sự kiên bấm ÁP DỤNG
     * Created by thduong 29/12/2020
     */
    handleClickApply() {
      // if (this.$refs.validateObserver.validate()) {
        // xu ly doi tuong ap dung
        if(this.detailDataX.DateApplyType=='Tu ngay den ngay'){
          this.detailDataX.DateApplyType = 1
        }
        else{
          this.detailDataX.DateApplyType = 2
        }
        if(this.objectApplyType=='Co cau to chuc'){
          this.detailDataX.OrganizationUnitNames=[]
          this.detailDataX.OrganizationUnitIDs=[]
          this.list_object_selected.forEach(item => {
            
            this.detailDataX.OrganizationUnitNames.push(item.text)
            this.detailDataX.OrganizationUnitIDs.push(item.value)
          });
        }
        if(this.objectApplyType=='Danh sach nhan vien'){
          this.detailDataX.EmployeeNames=[]
          this.detailDataX.EmployeeIDs=[]
          this.list_object_selected.forEach(item => {
            
            this.detailDataX.EmployeeNames.push(item.text)
            this.detailDataX.EmployeeIDs.push(item.value)
          });
        
        }
        if(this.list_working_shift_selected.length){
          this.detailDataX.WorkingShiftIDs=[]
          this.detailDataX.WorkingShiftNames=[]
          this.list_working_shift_selected.forEach(item =>{
            this.detailDataX.WorkingShiftIDs.push(item.value)
            this.detailDataX.WorkingShiftNames.push(item.text)
          })
        }
        switch (this.detailDataX.RepeatType) {
          case 1:
            this.saveRepeatConfigDay();
            break;
          case 2:
            this.saveRepeatConfigWeek();
            break;
          case 3:
            this.saveRepeatConfigMonth();
            break;
          default:
            break;
        }
        
        if (this.detailDataX.State != 2) {
          this.addShiftPlan();
        }
        if (this.detailDataX.State == 2) {
          if (
            JSON.stringify(this.detailDataX) != JSON.stringify(this.detailData)
          ) {
            let title =
              "<b>Luu y:</b> Cac thiet lap cu cua bang phan ca nay se khong duoc luu lai";
            if (new Date(this.fromDate).getTime() < new Date().getTime()) {
              title =
                "Thoi gian phan ca da phat sinh du lieu cham cong.Ban co chac chan muon thay doi khong?";
            }
            this.$_Popup.confirmUpdate(
              "Cap nhap bang phan ca?",
              title,
              this.addShiftPlan
            );
          } else this.backToTimeWorking();
        }
        this.createShiftPlan(this.detailDataX.RepeatType)
    },
    /**
     * Lấy danh sách ngày trong tháng
     * CREATED BY THDUONG - 09/12/2020
     */
    getDaysInMonth(month, year) {
      var date = new Date(year, month, 1);
      var days = [];
      while (date.getMonth() === month) {
        let day = {
          Value: new Date(date).getDate()
        };
        days.push(day);
        date.setDate(date.getDate() + 1);
      }
      return days;
    },
    /**
     * Chuyển dữ liệu check box chọn thứ từ string sang array
     * Created by thduong 18/12/2020
     */
    bindingDayOfWeekData() {
      this.DayOfWeek = this.DayOfWeek.toString();
      let dayOfWeek = this.DayOfWeek.split(",");
      this.listDayCheckBox.forEach(el => {
        let value = el.DayValue + 1;
        if (dayOfWeek.includes(value.toString())) {
          el.CheckBoxValue = true;
        }
      });
    },
    /**
     * Chuyển chuỗi ID từ array sang string
     * Created by thduong 23/12/2020
     */
    beforeSavePlan(arr) {
      let str = "";
      arr.forEach((el, index) => {
        index == 0 && (str = str + el);
        index != 0 && (str = str + ";" + el);
      });
      return str;
    },
    /**
     * Thông báo quay lại bảng phân ca chi tiết
     * CREATED BY THDUONG - 29/12/2020
     */
    clickBack() {
      if (JSON.stringify(this.detailDataX) != JSON.stringify(this.detailData)) {
        this.$_Popup.confirmCloseForm(
          "",
          "",
          this.addShiftPlan,
          null,
          this.backToTimeWorking
        );
      } else {
        this.backToTimeWorking();
      }
    },
    /**
     * Quay lại bảng phân ca chi tiết
     * CREATED BY THDUONG - 03/12/2020
     */
    backToTimeWorking() {
      this.$emit("input", false);
    },
    /**
     * Hiển thị dữ liệu xem trước lên lịch
     * Created by thduong 18/12/2020
     */
    generateSchedulerData() {
      // Lấy danh sách mã ca nếu chưa có
      if (this.detailDataX.WorkingShiftIDs.length >0) {
        this.listShiftScheduler = [];
        this.detailDataX.WorkingShiftNames.forEach(element => {
          this.listShiftScheduler.push(element);
        });
        this.schedulerData = [];
        this.listShiftScheduler.forEach(el => {
          this.listDayScheduler.forEach(data => {
            let shift = {
              text: el,
              startDate: data
            };
            this.schedulerData.push(shift);
          });
        });
      } else {
        return
      }
    },
    /**
     * Lấy giá trị ngày đầu tiên của tháng
     * Created by thduong 13/12/2020
     */
    getFirstDayOfMonth(dateString, dayOfWeek) {
      var date = moment(dateString, "YYYY-MM-DD");

      var day = date.day();
      var diffDays = 0;

      if (day > dayOfWeek) {
        diffDays = 7 - (day - dayOfWeek);
      } else {
        diffDays = dayOfWeek - day;
      }
      return new Date(date.add(diffDays, "day"));
    },
    /**
     * Lấy giá trị ngày cuối của tháng
     * Created by thduong 13/12/2020
     */
    getLastDayOfMonth(dateString, dayOfWeek) {
      var date = moment(dateString, "YYYY-MM-DD");
      var day = date.day();
      var diffDays = 0;
      if (day >= dayOfWeek) {
        diffDays = day - dayOfWeek;
      } else {
        diffDays = 7 - (dayOfWeek - day);
      }
      return new Date(date.add(-diffDays, "day"));
    },
    /**
     * Tạo lịch phân ca
     * Created by thduong 14/12/2020
     */
    createShiftPlan(val) {
      debugger
      if (!this.showPreview) {
        return;
      }
      this.listDayScheduler = [];
      let startDate = new Date(this.detailDataX.FromDate);
      let endDate = new Date(this.detailDataX.ToDate).setHours(23, 59, 59);

      let config = this.detailDataX.RepeatConfig
      // Lặp theo ngày
      if (val == 1) {
        if (!config.DayOfWeek) {
          while (startDate <= endDate) {
            this.listDayScheduler.push(startDate);
            startDate = moment(startDate)
              .add(config.RepeatDay, "days")
              .toDate();
          }
        }
        // Từ thứ 2 -> thứ 6
        if (config.DayOfWeek) {
          while (startDate <= endDate) {
            if (startDate.getDay() != 0 && startDate.getDay() != 6) {
              this.listDayScheduler.push(startDate);
            }
            startDate = moment(startDate)
              .add(1, "days")
              .toDate();
          }
        }
      }
      // Lặp theo tuần
      if (val == 2) {
        if (this.detailDataX.DateApplyType == 2) {
          // endDate = new Date(this.$refs.MsScheduler.endViewDate);
        }
        this.RepeatWeek = this.num_repeat
        this.DayOfWeek.forEach(el => {
            startDate = new Date(this.detailDataX.FromDate);
            let check = 0;
            while (startDate <= endDate) {
              if (startDate.getDay() == el.DayValue) {
                check++;
                this.listDayScheduler.push(startDate);
              }
              if (startDate.getDay() == 0 && check > 0) {
                startDate = moment(startDate)
                  .add(this.RepeatWeek - 1, "weeks")
                  .toDate();
              }
              startDate = moment(startDate)
                .add(1, "days")
                .toDate();
            }
        });
      }
      // Lặp theo tháng
      if (val == 3) {
        if (this.detailDataX.DateApplyType == 2) {
          // endDate = new Date(this.$refs.MsScheduler.endViewDate);
        }
        this.RepeatMonth = this.num_repeat
        if (!config.IsDayOfMonth) {
          while (startDate <= endDate) {
            let checkDate = new Date();
            if (this.WeekOfMonth == 1) {
              let stringDate = moment(startDate)
                .set("date", 1)
                .toDate();
              checkDate = this.getFirstDayOfMonth(
                stringDate,
                this.DayOfWeekNumber
              );
            }
            if (this.WeekOfMonth == 5) {
              let stringDate = moment(startDate)
                .endOf("month")
                .toDate();
              checkDate = this.getLastDayOfMonth(
                stringDate,
                this.DayOfWeekNumber
              );
            }
            if (startDate <= checkDate && checkDate <= endDate) {
              this.listDayScheduler.push(checkDate);
            }
            startDate = moment(startDate)
              .add(this.RepeatMonth, "months")
              .set("date", 1)
              .toDate();
          }
        }
        if (config.IsDayOfMonth) {
          while (startDate <= endDate) {
            if (startDate.getDate() == this.DayOfMonth) {
              this.listDayScheduler.push(startDate);
              startDate = moment(startDate)
                .add(this.RepeatMonth, "months")
                .set("date", 1)
                .toDate();
            } else {
              startDate = moment(startDate)
                .add(1, "days")
                .toDate();
            }
          }
        }
      }
      this.generateSchedulerData();
    },
    /**
     * Gán dữ liệu RepeatConfig cho các biến lưu giá trị lặp
     * Created by thduong 18/12/2020
     */
    convertRepeatConfig(data) {
      this.detailDataX = data;
      this.fromDate = this.detailDataX.FromDate;
      this.toDate = this.detailDataX.ToDate;
      this.currentListEmployee = [...this.initItemsCombobox.Employee];
      this.currentListOrganozation = [...this.initItemsCombobox.Organization];
      this.currentListWorkingShift = [...this.initItemsCombobox.WorkingShifts];
      if (this.detailDataX.State == 1) {
        this.detailDataX.WorkingShiftIDs = null;
        this.detailData = JSON.parse(JSON.stringify(this.detailDataX));
      }
      if (this.detailDataX.State == 2) {
        let config = JSON.parse(data.RepeatConfig);
        switch (data.RepeatType) {
          case 1:
            this.RepeatMonth = config.RepeatMonth;
            this.WeekOfMonth = config.WeekOfMonth;
            this.IsDayOfMonth = config.IsDayOfMonth;
            this.IsDayOfMonth && (this.DayOfMonth = config.DayOfMonth);
            !this.IsDayOfMonth &&
              (this.DayOfWeekNumber = config.DayOfWeekNumber - 1);
            break;
          case 2:
            this.DayOfWeek = config.DayOfWeek;
            this.RepeatWeek = config.RepeatWeek;
            this.bindingDayOfWeekData();
            break;
          case 3:
            if (config.DayOfWeek == "?") {
              this.IsWorkingDay = false;
            } else this.IsWorkingDay = true;
            this.RepeatDay = config.RepeatDay;
            break;
          default:
            break;
        }
        this.detailData = JSON.parse(JSON.stringify(this.detailDataX));
        this.detailData.RepeatConfig = JSON.stringify(config);
        // Lấy data danh sách ca đã chọn
        this.listShiftScheduler = [];
        setTimeout(() => {
          this.createShiftPlan(this.detailDataX.RepeatType);
        }, 300);
      }
    },
    /**
     * Hàm check validate ngày bắt đầu lớn hơn ngày kết thúc
     * Created by pdthien 13/1/2020
     */
    checkValidateTime(startTime, toTime) {
      let obj = {
        isValid: false,
        message: "",
        rules: "custom"
      };
      if (startTime > toTime) {
        this.validateStartTime = JSON.parse(
          JSON.stringify({
            isValid: true,
            message: "Ngay bat dau phai nho hon ngay ket thuc",
            rules: "custom"
          })
        );
        this.validateToTime = JSON.parse(
          JSON.stringify({
            isValid: true,
            message: "Ngay ket thuc phai lon hon ngay bat dau",
            rules: "custom"
          })
        );
        return false;
      } else {
        this.validateStartTime = JSON.parse(JSON.stringify(obj));
        this.validateToTime = JSON.parse(JSON.stringify(obj));
        return true;
      }
    }
  }
}
</script>
<style lang="scss">
.el-form-item__content {
  // margin-left: 24px !important;
  margin: 0px !important;
  width: calc(100% - 150px);
  display: flex;
}
.el-form-item__label {
  width: 150px !important;
}
.start-time {
  .el-form-item__content {
    width: calc(100% - 115px) !important;
  }
}
.tinh-cong {
  .el-form-item__label {
    width: 100px !important;
  }
  .el-form-item__label {
    width: 150px !important;
  }
  .el-form-item__content {
    width: calc(100% - 210px) !important;
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