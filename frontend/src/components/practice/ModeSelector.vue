<script setup>
defineProps({ modelValue: String })
const emit = defineEmits(['update:modelValue'])
</script>

<template>
  <div class="mode-selector">
    <el-segmented :modelValue="modelValue" :options="[
      { label: '随机刷题', value: 'random' },
      { label: '顺序刷题', value: 'sequential' },
      { label: '刷错题', value: 'incorrect' }
    ]" @change="(val) => emit('update:modelValue', val)" />
  </div>
</template>
