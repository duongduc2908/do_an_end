<template>
  <div class="app-container" v-if="checkRolePermission('View', subsystem_code, false)">
    <el-button type="primary" @click="handleAddRole" v-if="checkRolePermission('Add', subsystem_code, false)">Thêm quyền</el-button>

    <el-table :data="rolesList" style="width: 100%;margin-top:30px;" border>
      <el-table-column align="center" label="Mã quyền" width="220">
        <template slot-scope="scope">
          {{ scope.row.role_id }}
        </template>
      </el-table-column>
      <el-table-column align="center" label="Tên quyền" width="220">
        <template slot-scope="scope">
          {{ scope.row.role_name }}
        </template>
      </el-table-column>
      <el-table-column align="header-center" label="Mô tả">
        <template slot-scope="scope">
          {{ scope.row.role_description }}
        </template>
      </el-table-column>
      <el-table-column align="center" label="Hành động">
        <template slot-scope="scope">
          <el-button type="primary" size="small" v-if="checkRolePermission('Edit', subsystem_code, false)" @click="handleEdit(scope)">Sửa</el-button>
          <el-button type="danger" size="small" v-if="checkRolePermission('Delete', subsystem_code, false)" @click="handleDelete(scope)">Xóa</el-button>
        </template>
      </el-table-column>
    </el-table>

    <el-dialog width="900px" v-if="dialogVisible" :visible.sync="dialogVisible" :title="dialogType==='edit'?'Sửa quyền':'Thêm quyền'">
      <el-form :model="role" label-width="80px" label-position="left">
        <el-form-item label="Tên quyền">
          <el-input v-model="role.role_name" placeholder="Tên quyền" />
        </el-form-item>
        <el-form-item label="Mô tả">
          <el-input
            v-model="role.role_description"
            :autosize="{ minRows: 2, maxRows: 4}"
            type="textarea"
            placeholder="Mô tả quyền"
          />
        </el-form-item>
        <el-form-item label="Menus">
          <div v-for="(item,index) in list_permission" :key="index" >

            <div class="flex" v-if="item.parent_name && item.isShowParent">
              <el-checkbox  v-model="item.isParentCheck" @change="changePermissionParent(item, item.parent_code)">
              </el-checkbox>
              <div class="w-200 m-l-8">{{item.parent_name}}</div>
            </div>
            <div class="flex">
              <div class="flex">
                <el-checkbox v-model="item.isCheck" @change="changePermissionParent(item)" :class="{'m-l-24':item.parent_code}">
                </el-checkbox>
                <div class="m-l-8 w-135">{{ item.subsystem_name }}</div>
              </div>
              <div class="flex" v-for="(item2,index2) in item.permission_code" :key="index2" :class="[item.parent_code ? 'm-l-48':'m-l-24']">
                <el-checkbox v-model="item2.isCheck" @change="changePermission(item2,item)">
                </el-checkbox>
                <div class="m-l-8" >{{ item2.name }}</div>
              </div>
            </div>
          </div>
        </el-form-item>
        <!-- <el-form-item style="margin-bottom:10px" label="Users">
          <multi-select v-model="role.list_users" :options="options"
                        :selected-options="items"
                        placeholder="Chon danh sach user"
                        @select="onSelect">
          </multi-select>
      </el-form-item> -->
      </el-form>
      <div style="text-align:right;">
        <el-button type="danger" @click="dialogVisible=false">Cancel</el-button>
        <el-button type="primary" @click="confirmRole">Confirm</el-button>
      </div>
    </el-dialog>
  </div>
</template>

<script>
import path from 'path'
import { deepClone } from '@/utils'
import checkRolePermission from "@/utils/permission";
// import _ from 'lodash'
// import { MultiSelect } from 'vue-search-select'
// import 'vue-search-select/dist/VueSearchSelect.css'

const defaultRole = {
  key: '',
  name: '',
  description: '',
  routes: []
}

export default {
  // components:{MultiSelect},
  data() {
    return {
      subsystem_code: "DANH_SACH_QUYEN",
      current_parent_code:"",
      routes: [],
      rolesList: [],
      dialogVisible: false,
      dialogType: 'new',
      checkStrictly: false,
      defaultProps: {
        children: 'children',
        label: 'title'
      },
      role:{
        role_name:"",
        role_description:"",
        list_permission:[],
        // list_users:[]
      },
      list_permission:[]
    }
  },
  computed: {
    routesData() {
      return this.routes
    }
  },
  created() {
    this.list_permission.forEach(item => {
      if(item.parent_code && this.current_parent_code != item.parent_code){
        this.current_parent_code = item.parent_code;
        item.isParentCheck = false;
        item.isShowParent = true;
        return;
      }
      item.isShowParent = false;
    });
    this.getRoles()
    
  },
  methods: {
    checkRolePermission,
    // onSelect (items, lastSelectItem) {
    //     this.items = items
    //     this.lastSelectItem = lastSelectItem
    //   },
    // // deselect option
    // reset () {
    //   this.items = [] // reset
    // },
    // // select option from parent component
    // selectFromParentComponent () {
    //   this.items = _.unionWith(this.items, [this.options[0]], _.isEqual)
    // },
    // getListUser() {
    //   this.options = []
    //   this.listLoading = true
    //   let query_filter =`{"$and": [`;
    //   query_filter += `]}`;
    //   let index = query_filter.lastIndexOf(",")
    //   if(index > 0){
    //     query_filter = query_filter.substring(0,index) + query_filter.slice(index+1)
    //   }
    //   let param={
    //     query_filter:query_filter,
    //     to_date:undefined,
    //     start_date :undefined
    //   }
    //   this.$store.dispatch(`user/get_all_page_search`, param).then(res=>{
         
    //     this.total = res.totals;
    //   });
    // },
    getRoles(){
      this.items = []
      this.$store.dispatch("role_permission/getRoles",{}).then(res=>{
        this.rolesList =res.roles;
      });
      
    },
    getMenu(){
      this.$store.dispatch("permission/get_default_permission").then(res=>{
      if(res && res.length){
          let parentName = "";
          res.forEach(element => {
            if(element.parent_name && parentName != element.parent_name){
              parentName = element.parent_name;
              element.isShowParent = true;
            }
          });
          this.list_permission = res
        }
      });
    },
    changePermissionParent(item, parent_code = null){
      if(!parent_code){
        if(item.permission_code && item.permission_code.length){
          item.permission_code.forEach(element => {
            element.isCheck = item.isCheck;
          });
        }
        let listItem = this.list_permission.filter(x=> x.parent_code == item.parent_code);
        let listItemCheck = this.list_permission.filter(x=> x.parent_code == item.parent_code && x.isCheck);
        if(listItem && listItemCheck ){
          listItem[0].isParentCheck = listItemCheck.length == listItem.length ? true : false;
        }
      }
      else{
        let data = this.list_permission.filter(x=> x.parent_code == parent_code);
        if(data && data.length){
          let isCheck;
          data.forEach((item,index) => {
            if(index == 0 ){
              isCheck =item.isParentCheck;
            }
            item.isCheck = isCheck;
            if(item.permission_code && item.permission_code.length){
              item.permission_code.forEach(element => {
                element.isCheck = isCheck;
              });
            }
          });
        }
      }
    },

    changePermission(item,itemParent){
      if(!item){
        return;
      }
      if(item.code == "View" ){
        if(!item.isCheck && itemParent){
          itemParent.permission_code.forEach(element => {
            element.isCheck = false;
          });
        }
      }
      else if(item.isCheck && itemParent){
        let itemView = itemParent.permission_code.find(x=>x.code=="View");
        if(itemView){
          itemView.isCheck = true;
        }
      }
      let listCheck = itemParent.permission_code.filter(x=>x.isCheck);

      itemParent.isCheck = listCheck && listCheck.length == itemParent.permission_code.length ? true : false;
      let listItem = this.list_permission.filter(x=> x.parent_code == itemParent.parent_code);
      let listItemCheck = this.list_permission.filter(x=> x.parent_code == itemParent.parent_code && x.isCheck);
      if(listItem && listItemCheck ){
        listItem[0].isParentCheck = listItemCheck.length == listItem.length ? true : false;
      }
    },

    // async getRoutes() {
    //   const res = await getRoutes()
    //   this.serviceRoutes = res.data
    //   this.routes = this.generateRoutes(res.data)
    // },

    // Reshape the routes structure so that it looks the same as the sidebar
    generateRoutes(routes, basePath = '/') {
      const res = []

      for (let route of routes) {
        // skip some route
        if (route.hidden) { continue }

        const onlyOneShowingChild = this.onlyOneShowingChild(route.children, route)

        if (route.children && onlyOneShowingChild && !route.alwaysShow) {
          route = onlyOneShowingChild
        }

        const data = {
          path: path.resolve(basePath, route.path),
          title: route.meta && route.meta.title

        }

        // recursive child routes
        if (route.children) {
          data.children = this.generateRoutes(route.children, data.path)
        }
        res.push(data)
      }
      return res
    },
    generateArr(routes) {
      let data = []
      routes.forEach(route => {
        data.push(route)
        if (route.children) {
          const temp = this.generateArr(route.children)
          if (temp.length > 0) {
            data = [...data, ...temp]
          }
        }
      })
      return data
    },
    handleAddRole() {
      if(this.checkRolePermission("Add",this.subsystem_code)){
      this.list_permission = []
      this.getMenu()
      this.role = Object.assign({}, defaultRole)
      if (this.$refs.tree) {
        this.$refs.tree.setCheckedNodes([])
      }
      this.dialogType = 'new'
      this.dialogVisible = true
      // this.getListUser()
      // this.items = []
      }
    },
    handleEdit(scope) {
      if(this.checkRolePermission("Edit",this.subsystem_code)){
      this.dialogType = 'edit'
      this.dialogVisible = true
      // this.getListUser()
      this.checkStrictly = true
      this.role = deepClone(scope.row)
      // this.items = deepClone(this.role.list_users)
      this.list_permission = deepClone(this.role.list_permission);
      let current_parentCode = "";
      this.list_permission.forEach(element => {
        element.isShowParent = false;
        if(element.parent_code && current_parentCode != element.parent_code){
          current_parentCode = element.parent_code;
          element.isParentCheck = false;
          element.isShowParent = true;
        }
        let item = element.permission_code.find(x=>!x.isCheck);
        element.isCheck = item ? false : true;
      });
      let list_parentcode = this.list_permission.filter((value, index, self) => self.map(x => x.parent_code).indexOf(value.parent_code) == index);
      if(list_parentcode && list_parentcode.length){
        list_parentcode.forEach(element => {
          let item = this.list_permission.filter(x=>x.parent_code == element.parent_code && x.parent_code);
          let itemCheck = this.list_permission.filter(x=>x.parent_code == element.parent_code && x.isCheck);
          if(item && itemCheck && item.length){
            item[0].isParentCheck = item.length == itemCheck.length ? true  : false;
          }
        });
      }
      
      // this.$nextTick(() => {
      //   const routes = this.generateRoutes(this.role.routes)
      //   this.$refs.tree.setCheckedNodes(this.generateArr(routes))
      //   // set checked state of a node not affects its father and child nodes
      //   this.checkStrictly = false
      // })
      }
    },
    handleDelete({ $index, row }) {
      if(this.checkRolePermission("Delete",this.subsystem_code)){
      this.$confirm('Bạn có muốn xóa quyền người dùng?', 'Cảnh báo', {
        confirmButtonText: 'Confirm',
        cancelButtonText: 'Cancel',
        type: 'warning'
      })
        .then(async() => {
          await this.deleteRole(row)
          this.rolesList.splice($index, 1)
          this.$message({
            type: 'success',
            message: 'Delete succed!'
          })
        })
        .catch(err => { console.error(err) })
      }
    },
    generateTree(routes, basePath = '/', checkedKeys) {
      const res = []

      for (const route of routes) {
        const routePath = path.resolve(basePath, route.path)

        // recursive child routes
        if (route.children) {
          route.children = this.generateTree(route.children, routePath, checkedKeys)
        }

        if (checkedKeys.includes(routePath) || (route.children && route.children.length >= 1)) {
          res.push(route)
        }
      }
      return res
    },
    deleteRole(data){
      if(!data){
        return;
      }
      data.state = 3;
      this.$store.dispatch("permission/save_permission",data).then(res=>{
        this.getRoles();
        this.$notify({
          title: 'Success',
          dangerouslyUseHTMLString: true,
          message: `
              <div>Role Name: ${this.role.role_name}</div>
              <div>Description: ${this.role.role_description}</div>
            `,
          type: 'success'
        })
      })
    },
    async confirmRole() {
      this.role.list_users = this.items
      this.role.list_permission = this.list_permission;
      this.role.state = this.dialogType === 'edit' ? 2 : 1;
      this.$store.dispatch("permission/save_permission",this.role).then(res=>{
        this.getRoles();
        this.$notify({
          title: 'Success',
          dangerouslyUseHTMLString: true,
          message: `
              <div>Role Name: ${this.role.role_name}</div>
              <div>Description: ${this.role.role_description}</div>
            `,
          type: 'success'
        })
      })
      console.log(this.role);
      this.dialogVisible = false
    },
    // reference: src/view/layout/components/Sidebar/SidebarItem.vue
    onlyOneShowingChild(children = [], parent) {
      let onlyOneChild = null
      const showingChildren = children.filter(item => !item.hidden)

      // When there is only one child route, the child route is displayed by default
      if (showingChildren.length === 1) {
        onlyOneChild = showingChildren[0]
        onlyOneChild.path = path.resolve(parent.path, onlyOneChild.path)
        return onlyOneChild
      }

      // Show parent if there are no child route to display
      if (showingChildren.length === 0) {
        onlyOneChild = { ... parent, path: '', noShowingChildren: true }
        return onlyOneChild
      }

      return false
    }
  }
}
</script>

<style lang="scss">

.app-container {
  .roles-table {
    margin-top: 30px;
  }
}
.el-dialog {
  margin-top: 2vh !important;
}
</style>
