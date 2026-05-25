<script setup>
defineProps({ nodes: Array })
</script>

<template>
  <div class="path">
    <div class="path-heading">建议学习路径</div>
    <div class="path-list">
      <div v-for="(node, idx) in nodes" :key="idx" class="path-node">
        <div class="path-dot">{{ node.order }}</div>
        <div class="path-line" v-if="idx < nodes.length - 1"></div>
        <div class="path-body">
          <strong class="path-name">{{ node.knowledge_point?.name }}</strong>
          <p class="path-reason" v-if="node.reason">{{ node.reason }}</p>
          <div class="path-meta">
            <span class="path-diff">{{ '★'.repeat(node.knowledge_point?.difficulty || 1) }}</span>
            <span class="path-cat">{{ node.knowledge_point?.category }}</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.path-heading { font-size: 14px; font-weight: 600; color: #4b5563; margin-bottom: 14px; }
.path-list { display: flex; flex-direction: column; }
.path-node { display: flex; gap: 14px; position: relative; padding-bottom: 18px; }
.path-dot { width: 24px; height: 24px; border-radius: 50%; background: rgba(75,127,217,0.08); color: #4b7fd9; display: flex; align-items: center; justify-content: center; font-size: 11px; font-weight: 600; flex-shrink: 0; }
.path-line { position: absolute; left: 11px; top: 28px; width: 1px; height: calc(100% - 10px); background: #e5e7eb; }
.path-body { flex: 1; }
.path-name { font-size: 14px; color: #1a1a1a; }
.path-reason { font-size: 12px; color: #4b7fd9; margin: 4px 0; line-height: 1.5; }
.path-meta { display: flex; gap: 8px; margin-top: 6px; }
.path-diff { font-size: 11px; color: #d4a017; }
.path-cat { font-size: 11px; color: #9ca3af; }
</style>
