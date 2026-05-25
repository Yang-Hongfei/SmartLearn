<script setup>
defineProps({ visible: Boolean })
const emit = defineEmits(['choose', 'close'])
</script>

<template>
  <div v-if="visible" class="judge-overlay" @click.self="emit('close')">
    <div class="judge-dialog">
      <h3 class="judge-dialog-title">选择判题方式</h3>
      <p class="judge-dialog-desc">问答题无法自动判题，请选择：</p>
      <button class="judge-choice" @click="emit('choose', 'self')">查看答案（自主判题）</button>
      <div class="judge-divider">或</div>
      <button class="judge-choice" @click="emit('choose', 'ai')">AI 判题</button>
    </div>
  </div>
</template>

<style scoped>
.judge-overlay { position: fixed; inset: 0; background: rgba(0,0,0,0.3); display: flex; align-items: center; justify-content: center; z-index: 1000; }
.judge-dialog { background: #fff; border: 1px solid #e5e7eb; border-radius: 10px; padding: 32px; width: 380px; text-align: center; box-shadow: 0 4px 24px rgba(0,0,0,0.08); }
.judge-dialog-title { font-size: 17px; font-weight: 600; color: #1a1a1a; margin: 0 0 8px; }
.judge-dialog-desc { font-size: 13px; color: #6b7280; margin: 0 0 20px; }
.judge-choice { padding: 10px 24px; border-radius: 6px; font-size: 14px; cursor: pointer; border: 1px solid #e5e7eb; background: #f8f9fb; color: #374151; width: 100%; transition: background 0.15s; }
.judge-choice:hover { background: #f3f4f6; }
.judge-divider { font-size: 12px; color: #b0b7c3; margin: 10px 0; }
</style>
