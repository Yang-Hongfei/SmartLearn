<script setup>
import { ref, onMounted } from 'vue'
import { configApi } from '../../api/configApi'
import { ElMessage } from 'element-plus'

defineProps({ visible: Boolean })
const emit = defineEmits(['close'])

const apiKey = ref('')
const status = ref(null)
const saving = ref(false)

async function loadStatus() {
  const saved = localStorage.getItem('sm_ds_key') || ''
  apiKey.value = saved
  try {
    status.value = await configApi.getApiKeyStatus()
  } catch (e) { /* ignore */ }
  // Auto-configure from localStorage on mount
  if (saved) {
    try { await configApi.setApiKey(saved) } catch (e) { /* ignore */ }
  }
}

async function saveKey() {
  const key = apiKey.value.trim()
  if (!key) return
  saving.value = true
  try {
    await configApi.setApiKey(key)
    localStorage.setItem('sm_ds_key', key)
    ElMessage.success('API Key 已保存')
    loadStatus()
    emit('close')
  } catch (e) {
    ElMessage.error(e.message || '保存失败')
  }
  saving.value = false
}

async function clearKey() {
  apiKey.value = ''
  localStorage.removeItem('sm_ds_key')
  try { await configApi.clearApiKey() } catch (e) { /* ignore */ }
  ElMessage.info('API Key 已清除')
  loadStatus()
}

onMounted(loadStatus)
</script>

<template>
  <div v-if="visible" class="soverlay" @click.self="emit('close')">
    <div class="sdialog">
      <div class="sdialog-header">
        <h3>设置</h3>
        <button class="sdialog-close" @click="emit('close')">&times;</button>
      </div>

      <div class="sdialog-body">
        <div class="sfield">
          <label class="slabel">DeepSeek API Key</label>
          <div class="sstatus" v-if="status">
            <span class="sdot" :class="status.configured ? 'sdot--ok' : 'sdot--none'"></span>
            {{ status.configured ? `已配置 (${status.masked})` : '未配置' }}
          </div>
          <input
            v-model="apiKey"
            type="password"
            class="sinput"
            placeholder="sk-..."
            @keyup.enter="saveKey"
          />
          <p class="shint">Key 保存在你的浏览器中，不同用户互不影响</p>
        </div>
      </div>

      <div class="sdialog-footer">
        <button class="sbtn sbtn--ghost" @click="clearKey">清除</button>
        <button class="sbtn sbtn--ghost" @click="emit('close')">取消</button>
        <button class="sbtn sbtn--primary" :disabled="!apiKey.trim() || saving" @click="saveKey">
          {{ saving ? '保存中...' : '保存' }}
        </button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.soverlay { position: fixed; inset: 0; background: rgba(0,0,0,0.3); display: flex; align-items: center; justify-content: center; z-index: 1000; }
.sdialog { background: #fff; border: 1px solid #e5e7eb; border-radius: 10px; width: 420px; box-shadow: 0 4px 24px rgba(0,0,0,0.08); }
.sdialog-header { display: flex; align-items: center; justify-content: space-between; padding: 20px 24px 0; }
.sdialog-header h3 { font-size: 17px; font-weight: 600; color: #1a1a1a; margin: 0; }
.sdialog-close { background: none; border: none; font-size: 20px; color: #9ca3af; cursor: pointer; padding: 0; line-height: 1; }
.sdialog-close:hover { color: #4b5563; }
.sdialog-body { padding: 20px 24px; }
.sfield { display: flex; flex-direction: column; gap: 8px; }
.slabel { font-size: 13px; font-weight: 500; color: #374151; }
.sstatus { font-size: 12px; color: #6b7280; display: flex; align-items: center; gap: 6px; }
.sdot { width: 6px; height: 6px; border-radius: 50%; }
.sdot--ok { background: #4a9a2e; }
.sdot--none { background: #d1d5db; }
.sinput { padding: 9px 12px; border-radius: 6px; border: 1px solid #e5e7eb; font: inherit; font-size: 14px; outline: none; color: #1a1a1a; }
.sinput:focus { border-color: #4b7fd9; }
.sinput::placeholder { color: #b0b7c3; }
.shint { font-size: 11px; color: #b0b7c3; margin: 0; }
.sdialog-footer { display: flex; justify-content: flex-end; gap: 8px; padding: 0 24px 20px; }
.sbtn { padding: 8px 20px; border-radius: 6px; font-size: 13px; cursor: pointer; border: none; }
.sbtn--ghost { background: #f3f4f6; color: #6b7280; }
.sbtn--ghost:hover { background: #e5e7eb; }
.sbtn--primary { background: #1a1a1a; color: #fff; }
.sbtn--primary:hover { background: #333; }
.sbtn:disabled { opacity: 0.3; cursor: not-allowed; }
</style>
