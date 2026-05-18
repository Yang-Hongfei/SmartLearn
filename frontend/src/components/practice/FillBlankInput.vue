<script setup>
import { ref, watch } from 'vue'

const emit = defineEmits(['update:modelValue'])
const text = ref('')

watch(text, (val) => emit('update:modelValue', val))
</script>

<template>
  <el-input v-model="text" type="textarea" :rows="5" placeholder="请输入你的答案..." />
</template>
