<script setup>
import { ref } from 'vue'
import { pdfApi } from '../../api/pdfApi.js'

const emit = defineEmits(['uploaded'])
const uploading = ref(false)
const tips = ref('')

const beforeUpload = (file) => {
  if (file.type !== 'application/pdf' && !file.name.toLowerCase().endsWith('.pdf')) {
    tips.value = '仅支持 PDF 文件！'
    return false
  }
  tips.value = ''
  return true
}

const handleUpload = async (options) => {
  uploading.value = true
  try {
    const result = await pdfApi.upload(options.file)
    emit('uploaded', result)
  } catch (e) {
    tips.value = '上传失败: ' + e.message
  } finally {
    uploading.value = false
  }
}
</script>

<template>
  <div class="upload-area">
    <el-upload drag :http-request="handleUpload" :before-upload="beforeUpload"
      :show-file-list="false" accept=".pdf">
      <el-icon :size="48"><UploadFilled /></el-icon>
      <div class="el-upload__text">点击或拖拽 PDF 文件到此处</div>
      <template #tip>
        <div class="el-upload__tip">支持 .pdf 格式，最大 200MB</div>
      </template>
    </el-upload>
    <div v-if="uploading" style="text-align:center; margin-top: 16px;">
      <el-progress :percentage="100" :indeterminate="true" />
      <p style="color:#909399;">正在解析 PDF，请稍候...</p>
    </div>
    <div v-if="tips" style="text-align:center; margin-top: 8px;">
      <el-tag type="danger">{{ tips }}</el-tag>
    </div>
  </div>
</template>

<style scoped>
.upload-area { max-width: 500px; margin: 0 auto; }
</style>
