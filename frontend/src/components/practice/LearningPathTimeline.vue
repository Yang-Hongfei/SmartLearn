<script setup>
defineProps({ nodes: Array })
</script>

<template>
  <el-card shadow="never" class="path-card">
    <template #header><strong>🗺️ 建议学习路径</strong></template>
    <el-timeline>
      <el-timeline-item v-for="(node, idx) in nodes" :key="idx"
        :timestamp="`第 ${node.order} 步`" placement="top">
        <el-card shadow="hover">
          <strong>{{ node.knowledge_point?.name }}</strong>
          <p v-if="node.reason" class="node-reason">{{ node.reason }}</p>
          <p v-if="node.knowledge_point?.description" class="node-desc">{{ node.knowledge_point.description }}</p>
          <div class="node-meta">
            <el-tag size="small">难度 {{ '⭐'.repeat(node.knowledge_point?.difficulty || 1) }}</el-tag>
            <el-tag size="small" type="info">{{ node.knowledge_point?.category }}</el-tag>
          </div>
        </el-card>
      </el-timeline-item>
    </el-timeline>
  </el-card>
</template>

<style scoped>
.path-card { margin: 16px 0; }
.node-reason { color: #409eff; font-size: 13px; margin-top: 4px; }
.node-desc { color: #909399; font-size: 13px; margin-top: 4px; }
.node-meta { display: flex; gap: 6px; margin-top: 8px; }
</style>
