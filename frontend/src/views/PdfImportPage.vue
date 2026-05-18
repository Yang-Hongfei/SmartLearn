<script setup>
import { ref } from 'vue'
import AppLayout from '../components/layout/AppLayout.vue'
import UploadDragger from '../components/pdf/UploadDragger.vue'
import ImportHistoryTable from '../components/pdf/ImportHistoryTable.vue'
import ImportResultModal from '../components/pdf/ImportResultModal.vue'

const historyTable = ref(null)
const resultModal = ref({ visible: false, data: null })

function handleUploaded(result) {
  resultModal.value = { visible: true, data: result }
  historyTable.value?.refresh()
}
</script>

<template>
  <AppLayout>
    <div class="import-page">
      <el-alert title="导入说明" type="info" :closable="false" show-icon>
        <template #default>
          <p>支持的 PDF 格式：包含问答对的面试题/教材 PDF（如"面渣逆袭"系列）。</p>
          <p>系统会自动识别章节标题、题目编号、题型，并提取完整的 Q&A 对导入题库。</p>
          <p>文件大小上限：200MB，大文件会自动分块处理。</p>
        </template>
      </el-alert>

      <div class="upload-section">
        <UploadDragger @uploaded="handleUploaded" />
      </div>

      <ImportHistoryTable ref="historyTable" />

      <ImportResultModal
        :visible="resultModal.visible"
        :result="resultModal.data"
        @close="resultModal.visible = false" />
    </div>
  </AppLayout>
</template>

<style scoped>
.import-page { max-width: 900px; margin: 0 auto; }
.upload-section { margin-top: 30px; }
</style>
