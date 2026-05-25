<script setup>
defineProps({ points: Array })
</script>

<template>
  <div class="weak">
    <div class="weak-heading">薄弱点分析</div>
    <div v-for="(wp, idx) in points" :key="idx" class="weak-item">
      <div class="weak-top">
        <span class="weak-name">{{ wp.knowledge_point_name }}</span>
        <span class="weak-mastery">{{ Math.round((wp.current_mastery || 0) * 100) }}%</span>
      </div>
      <div class="weak-bar"><div class="weak-fill" :style="{ width: Math.round((wp.current_mastery || 0) * 100) + '%', background: wp.current_mastery < 0.5 ? '#e5534b' : '#d4a017' }"></div></div>
      <p class="weak-reason" v-if="wp.reason">{{ wp.reason }}</p>
    </div>
  </div>
</template>

<style scoped>
.weak { margin-bottom: 20px; }
.weak-heading { font-size: 14px; font-weight: 600; color: #4b5563; margin-bottom: 14px; }
.weak-item { margin-bottom: 14px; }
.weak-top { display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px; }
.weak-name { font-size: 13px; color: #374151; }
.weak-mastery { font-size: 12px; color: #9ca3af; font-variant-numeric: tabular-nums; }
.weak-bar { height: 3px; background: #e5e7eb; border-radius: 2px; overflow: hidden; }
.weak-fill { height: 100%; border-radius: 2px; transition: width 0.3s; }
.weak-reason { font-size: 12px; color: #6b7280; margin: 6px 0 0; line-height: 1.5; }
</style>
