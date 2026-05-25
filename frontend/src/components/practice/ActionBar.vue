<script setup>
defineProps({ answer: String, submitted: Boolean, showAiBtn: Boolean, loading: Boolean })
const emit = defineEmits(['submit', 'skip', 'learned', 'ai-analysis'])
</script>

<template>
  <div class="action-bar">
    <button class="act act--primary" :disabled="!answer" @click="emit('submit')">
      {{ loading ? '提交中...' : '提交答案' }}
    </button>
    <button class="act act--ghost" @click="emit('skip')">跳过</button>
    <button v-if="submitted" class="act act--success" @click="emit('learned')">标记已学会</button>
    <button v-if="showAiBtn" class="act act--ai" @click="emit('ai-analysis')">AI 解析</button>
  </div>
</template>

<style scoped>
.action-bar { display: flex; justify-content: center; gap: 10px; margin-top: 24px; flex-wrap: wrap; }
.act { padding: 9px 22px; border-radius: 6px; font-size: 14px; font-weight: 500; cursor: pointer; border: 1px solid transparent; transition: background 0.15s, border-color 0.15s; }
.act:disabled { opacity: 0.3; cursor: not-allowed; }
.act--primary { background: #1a1a1a; border-color: #1a1a1a; color: #fff; }
.act--primary:hover:not(:disabled) { background: #333; }
.act--ghost { background: #fff; border-color: #d1d5db; color: #6b7280; }
.act--ghost:hover { background: #f3f4f6; color: #374151; }
.act--success { background: #fff; border-color: rgba(103,194,58,0.3); color: #4a9a2e; }
.act--success:hover { background: rgba(103,194,58,0.05); }
.act--ai { background: #fff; border-color: rgba(212,160,23,0.25); color: #b8860b; }
.act--ai:hover { background: rgba(212,160,23,0.05); }
</style>
