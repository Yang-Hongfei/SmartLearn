<script setup>
import { ref } from 'vue'
import { pdfApi } from '../../api/pdfApi.js'

const emit = defineEmits(['uploaded'])
const uploading = ref(false)
const tips = ref('')
const dragOver = ref(false)

async function handleFile(file) {
  if (!file.name.toLowerCase().endsWith('.pdf')) {
    tips.value = '仅支持 PDF 文件！'
    return
  }
  tips.value = ''
  uploading.value = true
  try {
    const result = await pdfApi.upload(file)
    emit('uploaded', result)
  } catch (e) {
    tips.value = '上传失败: ' + e.message
  } finally {
    uploading.value = false
  }
}

function onDrop(e) {
  dragOver.value = false
  const file = e.dataTransfer?.files?.[0]
  if (file) handleFile(file)
}
</script>

<template>
  <div class="upload-area">
    <label
      class="upload-zone"
      :class="{ 'upload-zone--over': dragOver }"
      @dragover.prevent="dragOver = true"
      @dragleave="dragOver = false"
      @drop.prevent="onDrop"
    >
      <input type="file" accept=".pdf" class="upload-input" @change="e => e.target.files[0] && handleFile(e.target.files[0])" />
      <div class="upload-icon">+</div>
      <div class="upload-text">点击选择或拖拽 PDF 文件到此处</div>
      <div class="upload-tip">支持 .pdf 格式，最大 200MB</div>
    </label>
    <div v-if="uploading" class="upload-status">
      <div class="upload-spinner"></div>
      <p>正在解析 PDF，请稍候...</p>
    </div>
    <div v-if="tips" class="upload-error">{{ tips }}</div>
  </div>
</template>

<style scoped>
.upload-area { max-width: 500px; margin: 0 auto; }
.upload-zone { display: flex; flex-direction: column; align-items: center; gap: 10px; padding: 40px 20px; border: 2px dashed #d1d5db; border-radius: 10px; cursor: pointer; transition: border-color 0.15s, background 0.15s; position: relative; }
.upload-zone:hover { border-color: #9ca3af; background: #fafafa; }
.upload-zone--over { border-color: #4b7fd9; background: rgba(75,127,217,0.04); }
.upload-input { position: absolute; inset: 0; opacity: 0; cursor: pointer; }
.upload-icon { font-size: 36px; color: #d1d5db; font-weight: 300; }
.upload-text { font-size: 14px; color: #6b7280; }
.upload-tip { font-size: 12px; color: #b0b7c3; }
.upload-status { text-align: center; margin-top: 16px; }
.upload-spinner { width: 24px; height: 24px; border: 2px solid #e5e7eb; border-top-color: #4b7fd9; border-radius: 50%; animation: spin 0.8s linear infinite; margin: 0 auto 8px; }
@keyframes spin { to { transform: rotate(360deg); } }
.upload-status p { font-size: 13px; color: #6b7280; margin: 0; }
.upload-error { text-align: center; margin-top: 8px; font-size: 13px; color: #e5534b; }
</style>
