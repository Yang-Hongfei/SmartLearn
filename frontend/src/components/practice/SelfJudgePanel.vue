<script setup>
defineProps({ visible: Boolean })
const emit = defineEmits(['judge', 'close'])
</script>

<template>
  <div v-if="visible" class="self-judge-panel">
    <el-alert title="请对比标准答案，自行判断对错" type="info" :closable="false" show-icon />
    <div class="judge-btn-group">
      <el-button type="success" size="large" @click="emit('judge', true)">✓ 回答正确</el-button>
      <el-button type="danger" size="large" @click="emit('judge', false)">✗ 回答错误</el-button>
    </div>
  </div>
</template>

<style scoped>
.self-judge-panel { margin-top: 16px; text-align: center; }
.judge-btn-group { display: flex; justify-content: center; gap: 16px; margin-top: 16px; }
</style>
