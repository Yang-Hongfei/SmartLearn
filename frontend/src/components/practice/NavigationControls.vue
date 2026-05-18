<script setup>
defineProps({ currentIndex: Number, total: Number })
const emit = defineEmits(['prev', 'next'])
</script>

<template>
  <div class="nav-controls">
    <el-button @click="emit('prev')" :icon="'ArrowLeft'">上一题</el-button>
    <span class="nav-indicator">
      {{ currentIndex }} / {{ total || '?' }}
    </span>
    <el-button @click="emit('next')" :icon="'ArrowRight'">下一题</el-button>
  </div>
</template>

<style scoped>
.nav-controls { display: flex; justify-content: center; align-items: center; gap: 16px; margin-top: 20px; }
.nav-indicator { color: #606266; font-size: 14px; }
</style>
