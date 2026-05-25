<script setup>
import { ref, watch } from 'vue'

const emit = defineEmits(['update:modelValue'])
const text = ref('')
watch(text, (val) => emit('update:modelValue', val))
</script>

<template>
  <textarea v-model="text" class="fill-input" placeholder="输入你的答案..." rows="5"></textarea>
</template>

<style scoped>
.fill-input { width: 100%; padding: 12px 16px; border-radius: 6px; background: #f8f9fb; border: 1px solid #e5e7eb; color: #1a1a1a; font: inherit; font-size: 14px; resize: vertical; outline: none; transition: border-color 0.15s; box-sizing: border-box; }
.fill-input:focus { border-color: #4b7fd9; }
.fill-input::placeholder { color: #b0b7c3; }
</style>
