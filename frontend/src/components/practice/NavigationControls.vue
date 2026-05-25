<script setup>
defineProps({ currentIndex: Number, total: Number })
const emit = defineEmits(['prev', 'next'])
</script>

<template>
  <div class="nav">
    <button class="nav-btn" @click="emit('prev')">&larr; 上一题</button>
    <span class="nav-indicator">{{ currentIndex }} / {{ total || '?' }}</span>
    <button class="nav-btn" @click="emit('next')">下一题 &rarr;</button>
  </div>
</template>

<style scoped>
.nav { display: flex; justify-content: center; align-items: center; gap: 16px; margin-top: 24px; }
.nav-btn { padding: 7px 18px; border-radius: 5px; font-size: 13px; cursor: pointer; border: 1px solid #e5e7eb; background: #fff; color: #6b7280; transition: color 0.15s, border-color 0.15s; }
.nav-btn:hover { color: #1a1a1a; border-color: #d1d5db; }
.nav-indicator { font-size: 13px; color: #9ca3af; font-variant-numeric: tabular-nums; }
</style>
