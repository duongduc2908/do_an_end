<template>
  <div class="components-container">
    <div class="editor-container">
      <dropzone id="myVueDropzone" url="http://localhost:4321/api/v1/file/upload_train/" @outputSaveFile="outputSaveFile" :objConfirm="objConfirm" @dropzone-error="dropzoneE" />
    </div>
  </div>
</template>

<script>
import Dropzone from '@/views/user/upload-file-train/Dropzone'

export default {
  name: 'UploadImageTrain',
  components: { Dropzone },
  props:{
    objConfirm:{value:false},
  },
  methods: {
    dropzoneS(file) {
      console.log(file)
      this.$message({ message: 'Upload success', type: 'success' })
    },
    dropzoneE(){
      this.$message({ message: 'Chi duoc chon 10 file', type: 'error' })
    },
    outputSaveFile(data){
      this.$emit('outputSaveFile',data);
    }
  }
}
</script>

