<script setup>
defineProps({ points: Array })
</script>

<template>
  <el-card shadow="never" class="weak-card">
    <template #header><strong>🎯 薄弱点分析</strong></template>
    <div v-for="(wp, idx) in points" :key="idx" class="weak-item">
      <div class="wp-header">
        <el-tag>{{ wp.knowledge_point_name }}</el-tag>
        <span class="mastery">掌握度: {{ Math.round((wp.current_mastery || 0) * 100) }}%</span>
      </div>
      <el-progress :percentage="Math.round((wp.current_mastery || 0) * 100)" :color="wp.current_mastery < 0.5 ? '#f56c6c' : '#e6a23c'" />
      <div class="wp-reason" v-if="wp.reason">{{ wp.reason }}</div>
    </div>
  </el-card>
</template>

<style scoped>
.weak-card { margin: 16px 0; }
.weak-item { margin-bottom: 16px; }
.wp-header { display: flex; align-items: center; gap: 8px; margin-bottom: 6px; }
.mastery { font-size: 13px; color: #909399; }
.wp-reason { margin-top: 4px; font-size: 13px; color: #606266; }
</style>
