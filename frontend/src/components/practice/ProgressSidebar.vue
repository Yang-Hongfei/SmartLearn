<script setup>
import { PRACTICE_STATUS } from '../../utils/constants.js'

defineProps({ stats: Object })
defineEmits(['filter'])
</script>

<template>
  <el-card shadow="hover" class="progress-sidebar">
    <template #header><strong>📊 学习进度</strong></template>
    <el-statistic title="总题数" :value="stats?.total || 0" />
    <el-divider />
    <div class="stat-row" style="color: #67c23a">
      已学会：<strong>{{ stats?.learned || 0 }}</strong>
    </div>
    <div class="stat-row" style="color: #909399">
      未作答：<strong>{{ stats?.unanswered || 0 }}</strong>
    </div>
    <div class="stat-row" style="color: #f56c6c">
      答错：<strong>{{ stats?.incorrect || 0 }}</strong>
    </div>
  </el-card>
</template>

<style scoped>
.progress-sidebar { width: 200px; }
.stat-row { padding: 6px 0; font-size: 14px; }
</style>
