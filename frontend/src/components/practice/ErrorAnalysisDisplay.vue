<script setup>
defineProps({ analysis: Object })
</script>

<template>
  <el-card shadow="never" class="error-card">
    <template #header><strong>📝 错题解析</strong></template>
    <div v-if="analysis.error_type">
      <el-tag type="danger" size="small">{{ analysis.error_type }}</el-tag>
    </div>
    <div class="error-detail" v-if="analysis.error_detail">{{ analysis.error_detail }}</div>
    <div class="explanation" v-if="analysis.explanation">{{ analysis.explanation }}</div>
  </el-card>
</template>

<style scoped>
.error-card { margin: 16px 0; }
.error-detail { margin-top: 8px; color: #e6a23c; }
.explanation { margin-top: 12px; line-height: 1.8; white-space: pre-wrap; background: #fdf6ec; padding: 12px; border-radius: 6px; }
</style>
