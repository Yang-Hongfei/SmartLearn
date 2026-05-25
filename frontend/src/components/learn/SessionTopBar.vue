<script setup>
import { useRouter } from 'vue-router'

const props = defineProps({
  pdfName: String,
  currentNode: Number,
  totalNodes: Number,
})

const emit = defineEmits(['skipToTest'])

const router = useRouter()

function goBack() {
  router.push('/learn-hub')
}
</script>

<template>
  <div class="topbar">
    <button class="topbar-back" @click="goBack">&larr; 返回</button>
    <span class="topbar-name">{{ pdfName }}</span>
    <span class="topbar-progress">{{ currentNode }} / {{ totalNodes }}</span>
    <button class="topbar-skip" @click="emit('skipToTest')">直接测试</button>
  </div>
</template>

<style scoped>
.topbar {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 12px 24px;
  border-bottom: 1px solid rgba(255,255,255,0.08);
}

.topbar-back {
  background: none;
  border: none;
  color: rgba(255,255,255,0.45);
  font-size: 13px;
  cursor: pointer;
  padding: 0;
}
.topbar-back:hover { color: rgba(255,255,255,0.75); }

.topbar-name {
  font-size: 14px;
  font-weight: 500;
  color: rgba(255,255,255,0.85);
  flex: 1;
}

.topbar-progress {
  font-size: 12px;
  color: rgba(255,255,255,0.35);
  font-variant-numeric: tabular-nums;
}

.topbar-skip {
  background: rgba(255,193,7,0.08);
  border: 1px solid rgba(255,193,7,0.15);
  color: rgba(255,193,7,0.65);
  font-size: 12px;
  padding: 4px 12px;
  border-radius: 4px;
  cursor: pointer;
  transition: background 0.15s, border-color 0.15s;
}
.topbar-skip:hover {
  background: rgba(255,193,7,0.15);
  border-color: rgba(255,193,7,0.3);
}
</style>
