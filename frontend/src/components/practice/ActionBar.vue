<script setup>
defineProps({
  answer: String,
  submitted: Boolean,
  showAiBtn: Boolean,
  loading: Boolean
})
const emit = defineEmits(['submit', 'skip', 'learned', 'ai-analysis'])
</script>

<template>
  <div class="action-bar">
    <el-button type="primary" :disabled="!answer" :loading="loading" @click="emit('submit')">
      提交答案
    </el-button>
    <el-button @click="emit('skip')">跳过</el-button>
    <el-button v-if="submitted" type="success" @click="emit('learned')">
      标记已学会
    </el-button>
    <el-button v-if="showAiBtn" type="warning" :loading="loading" @click="emit('ai-analysis')">
      🤖 AI 解析
    </el-button>
  </div>
</template>

<style scoped>
.action-bar { display: flex; justify-content: center; gap: 12px; margin-top: 20px; flex-wrap: wrap; }
</style>
