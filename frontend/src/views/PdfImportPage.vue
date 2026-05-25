<script setup>
import { ref, onMounted, onBeforeUnmount } from 'vue'
import { useRouter } from 'vue-router'
import SettingsModal from '../components/common/SettingsModal.vue'
import UploadDragger from '../components/pdf/UploadDragger.vue'
import ImportHistoryTable from '../components/pdf/ImportHistoryTable.vue'
import ImportResultModal from '../components/pdf/ImportResultModal.vue'
import { logout } from '../api/authApi'

const router = useRouter()
const historyTable = ref(null)
const resultModal = ref({ visible: false, data: null })
const showSettings = ref(false)

function onOpenSettings() { showSettings.value = true }
async function handleLogout() { await logout(); router.push('/login') }
onMounted(() => window.addEventListener('open-settings', onOpenSettings))
onBeforeUnmount(() => { window.removeEventListener('open-settings', onOpenSettings) })

function handleUploaded(result) {
  resultModal.value = { visible: true, data: result }
  historyTable.value?.refresh()
}
</script>

<template>
  <div class="import-page">
    <div class="import-topbar">
      <button class="topbar-back" @click="router.push('/')">&larr; 首页</button>
      <span class="topbar-logo">SmartLearn</span>
      <nav class="topbar-nav">
        <button class="topbar-tab" @click="router.push('/practice')">刷题练习</button>
        <button class="topbar-tab topbar-tab--active">PDF 导入</button>
      </nav>
      <div class="topbar-actions">
        <button class="topbar-btn" @click="handleLogout" title="退出登录">&#10154;</button>
        <button class="topbar-btn" @click="showSettings = true" title="设置 API Key">&#9881;</button>
      </div>
    </div>
    <div class="import-body">
      <div class="import-hint">
        <p>支持包含问答对的面试题/教材 PDF，系统会自动识别章节标题、题目编号、题型，提取完整的 Q&A 对导入题库。</p>
        <p>文件大小上限：200MB，大文件会自动分块处理。</p>
      </div>
      <div class="upload-section">
        <UploadDragger @uploaded="handleUploaded" />
      </div>
      <ImportHistoryTable ref="historyTable" />
      <ImportResultModal :visible="resultModal.visible" :result="resultModal.data" @close="resultModal.visible = false" />
      <SettingsModal :visible="showSettings" @close="showSettings = false" />
    </div>
  </div>
</template>

<style scoped>
.import-page { min-height: 100vh; background: #f8f9fb; }
.import-topbar { display: flex; align-items: center; gap: 16px; padding: 0 24px; height: 48px; background: #fff; border-bottom: 1px solid #e5e7eb; }
.topbar-back { background: none; border: none; font-size: 13px; color: #6b7280; cursor: pointer; padding: 0; }
.topbar-back:hover { color: #1a1a1a; }
.topbar-logo { font-size: 15px; font-weight: 600; color: #1a1a1a; }
.topbar-nav { display: flex; gap: 4px; margin-left: 24px; }
.topbar-tab { padding: 6px 14px; border-radius: 4px; font-size: 13px; cursor: pointer; border: none; background: transparent; color: #6b7280; }
.topbar-tab:hover { color: #1a1a1a; }
.topbar-tab--active { background: #f3f4f6; color: #1a1a1a; font-weight: 500; }
.topbar-actions { margin-left: auto; display: flex; gap: 6px; }
.topbar-btn { width: 32px; height: 32px; border-radius: 50%; border: 1px solid #e5e7eb; background: #fff; font-size: 14px; cursor: pointer; display: flex; align-items: center; justify-content: center; color: #6b7280; }
.topbar-btn:hover { color: #1a1a1a; border-color: #9ca3af; }
.import-body { max-width: 900px; margin: 0 auto; padding: 24px; }
.import-hint { background: #fff; border: 1px solid #e5e7eb; border-radius: 8px; padding: 16px 20px; margin-bottom: 24px; }
.import-hint p { font-size: 13px; color: #6b7280; margin: 0; line-height: 1.7; }
.upload-section { margin-bottom: 24px; }
</style>
