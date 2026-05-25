<script setup>
import { ref } from 'vue'

defineProps({ options: Array })
const emit = defineEmits(['select'])

const selected = ref('')
function select(opt) { selected.value = opt; emit('select', opt) }
</script>

<template>
  <div class="options">
    <button v-for="(opt, idx) in options" :key="idx" class="option" :class="{ 'option--selected': selected === opt }" @click="select(opt)">
      <span class="option-letter">{{ String.fromCharCode(65 + idx) }}</span>
      <span class="option-text">{{ opt }}</span>
    </button>
  </div>
</template>

<style scoped>
.options { display: flex; flex-direction: column; gap: 8px; }
.option { display: flex; align-items: flex-start; gap: 12px; padding: 12px 16px; border-radius: 6px; background: #f8f9fb; border: 1px solid #e5e7eb; cursor: pointer; text-align: left; font: inherit; color: inherit; transition: background 0.15s, border-color 0.15s; width: 100%; }
.option:hover { background: #f3f4f6; border-color: #d1d5db; }
.option--selected { background: rgba(75,127,217,0.06); border-color: rgba(75,127,217,0.3); }
.option-letter { font-size: 13px; font-weight: 600; color: #9ca3af; min-width: 20px; }
.option-text { font-size: 14px; color: #374151; line-height: 1.5; }
</style>
