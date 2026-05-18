<script setup>
defineProps({ visible: Boolean })
const emit = defineEmits(['choose', 'close'])
</script>

<template>
  <el-dialog :modelValue="visible" title="选择判题方式" width="420px" :close-on-click-modal="false"
    @update:modelValue="(v) => !v && emit('close')">
    <p style="text-align:center; color:#606266; margin-bottom: 24px;">
      问答题无法自动判题，请选择判题方式：
    </p>
    <div class="judge-buttons">
      <el-button type="primary" size="large" @click="emit('choose', 'self')" style="width:100%">
        📝 查看答案（自主判题）
      </el-button>
      <div style="text-align:center;color:#909399;margin:8px 0">或</div>
      <el-button type="success" size="large" @click="emit('choose', 'ai')" style="width:100%">
        🤖 AI 判题
      </el-button>
    </div>
  </el-dialog>
</template>
