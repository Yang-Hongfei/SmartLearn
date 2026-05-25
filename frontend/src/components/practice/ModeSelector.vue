<script setup>
defineProps({ modelValue: String })
const emit = defineEmits(['update:modelValue'])
</script>

<template>
  <div class="mode">
    <button v-for="opt in [{k:'random',v:'随机刷题'},{k:'sequential',v:'顺序刷题'},{k:'incorrect',v:'刷错题'}]" :key="opt.k"
      class="mode-btn" :class="{ 'mode-btn--active': modelValue === opt.k }"
      @click="emit('update:modelValue', opt.k)"
    >{{ opt.v }}</button>
  </div>
</template>

<style scoped>
.mode { display: flex; gap: 4px; background: #fff; border-radius: 6px; padding: 3px; border: 1px solid #e5e7eb; }
.mode-btn { padding: 6px 16px; border-radius: 4px; font-size: 13px; cursor: pointer; border: none; background: transparent; color: #6b7280; transition: background 0.15s, color 0.15s; }
.mode-btn:hover { color: #374151; }
.mode-btn--active { background: #1a1a1a; color: #fff; }
</style>
