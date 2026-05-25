<script setup>
defineProps({ stats: Object })
</script>

<template>
  <div class="sidebar">
    <div class="sidebar-heading">学习进度</div>
    <div class="sidebar-stat">
      <span class="stat-num">{{ stats?.total || 0 }}</span>
      <span class="stat-label">总题数</span>
    </div>
    <div class="sidebar-row sidebar-row--learned">
      <span>已学会</span>
      <strong>{{ stats?.learned || 0 }}</strong>
    </div>
    <div class="sidebar-row sidebar-row--unanswered">
      <span>未作答</span>
      <strong>{{ stats?.unanswered || 0 }}</strong>
    </div>
    <div class="sidebar-row sidebar-row--incorrect">
      <span>答错</span>
      <strong>{{ stats?.incorrect || 0 }}</strong>
    </div>
  </div>
</template>

<style scoped>
.sidebar { padding: 24px 20px; min-width: 180px; }
.sidebar-heading { font-size: 11px; font-weight: 500; color: #9ca3af; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 16px; }
.sidebar-stat { display: flex; flex-direction: column; margin-bottom: 20px; }
.stat-num { font-size: 36px; font-weight: 700; color: #1a1a1a; line-height: 1; }
.stat-label { font-size: 12px; color: #9ca3af; margin-top: 4px; }
.sidebar-row { display: flex; justify-content: space-between; padding: 8px 0; font-size: 13px; color: #6b7280; }
.sidebar-row--learned strong { color: #4a9a2e; }
.sidebar-row--unanswered strong { color: #9ca3af; }
.sidebar-row--incorrect strong { color: #e5534b; }
</style>
