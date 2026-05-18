<script setup>
defineProps({ options: Array })
const emit = defineEmits(['select'])
</script>

<template>
  <el-radio-group @change="(v) => emit('select', v)" class="option-group">
    <el-radio v-for="(opt, idx) in options" :key="idx" :value="opt" class="option-item">
      {{ opt }}
    </el-radio>
  </el-radio-group>
</template>

<style scoped>
.option-group { display: flex; flex-direction: column; gap: 8px; }
.option-item { padding: 8px 0; font-size: 15px; }
</style>
