<script setup>
defineProps({ analysis: Object })
</script>

<template>
  <div class="error">
    <div class="error-heading">错题解析</div>
    <span class="error-type" v-if="analysis.error_type">{{ analysis.error_type }}</span>
    <p class="error-detail" v-if="analysis.error_detail">{{ analysis.error_detail }}</p>
    <div class="error-explain" v-if="analysis.explanation">{{ analysis.explanation }}</div>
  </div>
</template>

<style scoped>
.error { margin-bottom: 20px; }
.error-heading { font-size: 14px; font-weight: 600; color: #4b5563; margin-bottom: 10px; }
.error-type { display: inline-block; font-size: 11px; padding: 2px 8px; border-radius: 3px; background: rgba(229,83,75,0.08); color: #e5534b; margin-bottom: 8px; }
.error-detail { font-size: 13px; color: #b8860b; margin: 0 0 10px; line-height: 1.6; }
.error-explain { font-size: 13px; line-height: 1.7; color: #4b5563; background: #f8f9fb; border: 1px solid #e5e7eb; padding: 14px; border-radius: 6px; white-space: pre-wrap; }
</style>
