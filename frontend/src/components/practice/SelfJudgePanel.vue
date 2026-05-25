<script setup>
defineProps({ visible: Boolean })
const emit = defineEmits(['judge', 'close'])
</script>

<template>
  <div v-if="visible" class="self-judge">
    <p class="self-judge-hint">请对比标准答案，自行判断对错</p>
    <div class="self-judge-btns">
      <button class="judge-btn judge-btn--correct" @click="emit('judge', true)">回答正确</button>
      <button class="judge-btn judge-btn--wrong" @click="emit('judge', false)">回答错误</button>
    </div>
  </div>
</template>

<style scoped>
.self-judge { margin-top: 16px; text-align: center; }
.self-judge-hint { font-size: 13px; color: #6b7280; margin: 0 0 16px; }
.self-judge-btns { display: flex; justify-content: center; gap: 12px; }
.judge-btn { padding: 9px 24px; border-radius: 6px; font-size: 14px; cursor: pointer; border: 1px solid transparent; }
.judge-btn--correct { background: rgba(103,194,58,0.06); border-color: rgba(103,194,58,0.2); color: #4a9a2e; }
.judge-btn--correct:hover { background: rgba(103,194,58,0.12); }
.judge-btn--wrong { background: rgba(255,107,107,0.06); border-color: rgba(255,107,107,0.2); color: #e5534b; }
.judge-btn--wrong:hover { background: rgba(255,107,107,0.12); }
</style>
