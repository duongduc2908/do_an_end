<template>
<div class="h-full">
  <div style="padding: 24px 50px;">
    <div>
      <h2>Danh sách camera</h2>
    </div>
    <div @click="addCamera" v-if="checkRolePermission('Add',subsystem_code,false)"
      class="cursor tags-view-item tags-view-item-active m-b-16" style="width: fit-content;">
      Thêm mới
    </div>
    
  </div>
   
  <div class="flex flex-wrap" style="padding: 24px 50px;max-height: calc(100vh - 358px);overflow: auto;">
      
    <!-- <div> -->
        <div v-for="(popupContent,index) in popup" :key="index" class="fit-content place-info bg-white shadow-lg rounded-lg overflow-hidden w-popup-place h-48 flex mr-2">
            <div class="w-48 h-full flex flex-col">
                <img  style="border-radius: 8px 0 0 8px;" class="location-image" alt="" :src="popupContent.link_image">
            </div>

            <div style="background-color: #fff;border-radius: 0 8px 8px 0;width: 350px;">
                <div class="p-16" style="height: calc(100% - 40px);">
                <div class="align-items flex justify-between m-b-24">
                    <div>
                    {{ popupContent.name }}
                    </div>
                    <div class="flex">
                      <el-button size="mini" class="filter-item" type="primary" v-if="checkRolePermission('Edit',subsystem_code,false)" @click="editCamera(popupContent)">
                      Sửa
                      </el-button>
                      <el-button size="mini" type="danger" @click="confirmDeleteCamera(popupContent)">
                        Xóa
                      </el-button>
                    </div>
                </div>

                <div class="mb-1 align-items flex items-center">
                    <CheckIcon class="mr-1 block text-green-600" />
                    <span class="text-green-800"> camera vận hành bình thường</span>
                    <!-- <span class="text-green-800">{{ cameras.length }}/{{ cameras.length }} camera vận hành bình thường</span> -->
                </div>
                </div>

                <div @click="popupContent.isActive=!popupContent.isActive;$store.dispatch(`camera/actionCamera`, popupContent)"
                class="cursor tags-view-item tags-view-item-active m-b-16 f-right" :class="{ 'tags-view-item-unactive' : !popupContent.isActive }">
                {{popupContent.isActive ? 'Kích hoạt' : 'Huy kích hoạt'}}
                </div>
            </div>
        </div>
    <!-- </div> -->
      <el-dialog v-if="dialogFormVisible" title="Thêm mới camera" :visible.sync="dialogFormVisible">
      <div class="flex">
        <el-form ref="dataForm" :rules="rules" :model="temp" label-position="left" label-width="160px" style="width: 400px; min-width:800px margin-left:50px;">
        <el-form-item label="Tên camera" prop="name">
          <el-input :required="true" message="Tên camera không được để trống" v-model="temp.name" />
        </el-form-item>
        <!-- <el-form-item label="Ten anh" prop="name_image">
          <el-input v-model="temp.name_image" />
        </el-form-item> -->
        <el-form-item label="Chọn ảnh" prop="link_image">
          <label for="import-file">
            <div class="flex btn-select">
              <div class="el-icon-upload"></div>
              <div class="m-l-8">
                Chọn ảnh
              </div>
            </div>
          </label>
        </el-form-item>
        <el-form-item label="Vị trí" prop="instruction">
          <el-input v-model="temp.instruction" />
        </el-form-item>
        <el-form-item label="Đường dẫn stream" prop="link_stream">
          <el-input v-model="temp.link_stream" />
        </el-form-item>
        <!-- <el-form-item label="Kich hoat" prop="isActive">
          <el-checkbox v-model="temp.isActive">
          </el-checkbox>
        </el-form-item> -->
      </el-form>
      <div class="img-select">
        <img class="img-current w-full" :src="src">
      </div>

      </div>
      <input id="import-file" type="file" @change="changeFile($event)" style="display:none">
      <div slot="footer" class="dialog-footer">
        <el-button @click="dialogFormVisible = false">
          Hủy
        </el-button>
        <el-button type="primary" @click="saveCamera">
          Xác nhận
        </el-button>
      </div>
      </el-dialog>

  </div>
  <pagination class="pagination" v-show="total>0" :total="total" :page.sync="listQuery.page" :limit.sync="listQuery.limit" @pagination="getCameraPaging" />
</div>
 
</template>

<script>
import CheckIcon from 'vue-material-design-icons/Check'
import Pagination from '@/components/Pagination' // secondary package based on el-pagination
// import AlertIcon from 'vue-material-design-icons/Alert'
// import HelpCircleIcon from 'vue-material-design-icons/HelpCircle'
import checkRolePermission from '@/utils/permission'
const calendarTypeOptions = [
  { key: 'CN', display_name: 'China' },
  { key: 'US', display_name: 'USA' },
  { key: 'JP', display_name: 'Japan' },
  { key: 'EU', display_name: 'Eurozone' }
]
const calendarTypeKeyValue = calendarTypeOptions.reduce((acc, cur) => {
  acc[cur.key] = cur.display_name
  return acc
}, {})
export default {
  components: {
    CheckIcon,
    Pagination
    // AlertIcon,
    // HelpCircleIcon
  },

  data () {
    return {
      src:"",
      file:null,
      subsystem_code:"DANH_SACH_CAMERA",
      state:0,
      list: null,
      total: 0,
      listLoading: true,
      listQuery: {
        page: 1,
        limit: 5,
      },
      calendarTypeOptions:calendarTypeOptions,
      statusOptions: ['published', 'draft', 'deleted'],
      dialogFormVisible: false,
      dialogStatus: '',
      textMap: {
        update: 'Edit',
        create: 'Create'
      },
      rules: {
        name: [{ required: true, message: 'Ten camera khong duoc de trong', trigger: 'change' }],
        // link_image: [{ required: true, message: 'Duong dan anh khong duoc de trong', trigger: 'change' }],
        link_stream: [{ required: true, message: 'Duong dan stream khong duoc de trong', trigger: 'change' }]
      },
        popup:[],
        cameraList: false,
        temp: {
        },
        
    }
  },
  created(){
    this.getCameraPaging();
  },

  methods: {
    changeFile(e){
      if(!e){
        return;
      }
      console.log(e);
      this.file = e.target.files[e.target.files.length-1]
      const reader = new FileReader();
      reader.readAsDataURL(this.file);
      reader.onload = (results) => {
        console.log(results);
        this.src = results.target.result;
      };
    },
    checkRolePermission,
    getCameraPaging(){
      let param={
        page_size:this.listQuery.limit,
        page_number: this.listQuery.page
      }
      this.$store.dispatch(`camera/getCameraPaging`, param).then(res=>{
        console.log(res);
        this.popup = res.results;
        this.total = res.totals;
      });
    },
    addCamera(){
      if(this.checkRolePermission("Add",this.subsystem_code)){
        this.temp={};
        this.src="";
        this.temp.state = 1;
        this.dialogFormVisible=true;
      }
    },
    editCamera(data){
      if(this.checkRolePermission("Edit",this.subsystem_code)){
        this.temp = JSON.parse(JSON.stringify(data));
        this.src = this.temp.link_image;
        this.file = null;
        this.temp.state = 2;
        this.dialogFormVisible=true;
      }
    },
    confirmDeleteCamera(data){
      if(this.checkRolePermission("Delete",this.subsystem_code)){
        this.temp = data;
        this.temp.state = 3;
        this.$confirm(`Ban co muon xoa camera ${this.temp.name}?`, 'Thong bao', {
        confirmButtonText: 'Xoa',
        cancelButtonText: 'Huy',
        type: 'warning'
        })
          .then(async() => {
            await this.deleteCamera()
          })
          .catch(err => { console.error(err) })
      }
    },
    saveCamera(){
      let me = this;
      this.$refs['dataForm'].validate(valid=>{
        if(valid){
          if(this.file){
            let formData = new FormData();
            formData.append('file',this.file)
            this.$store.dispatch(`camera/insertFileCamera`, formData).then(result=>{
              if(me.temp.state == 2){
                me.temp.link_image_old = me.temp.link_image;
              }
              me.temp.link_image = result.link;
              // me.temp.name = result.data.filename;
              me.$store.dispatch(`camera/saveCamera`, me.temp).then(res=>{
                this.$notify({
                title: 'Thông báo',
                message: 'Them camera thanh cong',
                type: 'success',
                duration: 2000
              })
                me.getCameraPaging();
              });
            });
            
          }
          else{
            me.$store.dispatch(`camera/saveCamera`, me.temp).then(res=>{
                this.$notify({
                title: 'Thông báo',
                message: 'Them camera thanh cong',
                type: 'success',
                duration: 2000
              })
                me.getCameraPaging();
              });
          }
          this.dialogFormVisible=false;
        }
      })
    },
    deleteCamera(){
      this.$store.dispatch(`camera/saveCamera`, this.temp).then(res=>{
        this.$notify({
          title: 'Thông báo',
          dangerouslyUseHTMLString: true,
          message: `Xoa camera thanh cong`,
          type: 'success'
        })
        this.getCameraPaging();
      });
    }

  }
}
</script>

<style lang="scss" scoped>
.place-info{
    // box-shadow: 3px 3px 3px grey;
    border-radius: 8px;
    margin: 0 24px 24px 0;
    height: 192px;
}
.location-image{
    width: 192px;
    height: 192px;
}
.tags-view-item {
    .el-icon-close {
      width: 16px;
      height: 16px;
      vertical-align: 2px;
      border-radius: 50%;
      text-align: center;
      transition: all .3s cubic-bezier(.645, .045, .355, 1);
      transform-origin: 100% 50%;
      &:before {
        transform: scale(.6);
        display: inline-block;
        vertical-align: -3px;
      }
      &:hover {
        background-color: #b4bccc;
        color: #fff;
      }
    }
  }

.tags-view-item-active{
    background-color: #42b983;
    color: #fff;
    border-color: #42b983;
    padding: 8px;
    border-radius: 4px;
    font-size: 13px;
  }
  .tags-view-item-unactive{
    background-color: #ef4d4d !important;
    border-color: #ef4d4d !important;
  }
  .img-select{
    width: calc(100% - 400px);
    margin-left: 24px;
    border-radius: 4px;
    border: 1px solid #DCDFE6;
  }
  .btn-select{
    height: 36px;
    align-items: center;
    cursor: pointer;
    color: #FFFFFF;
    background-color: #1890ff;
    border-color: #1890ff;
    padding: 10px 20px;
    font-size: 14px;
    border-radius: 4px;
    width: fit-content;
  }
  .pagination{
    margin: 24px;
    position: absolute;
    bottom: 24px;
    right: 24px;
    left: 24px;
  }
</style>