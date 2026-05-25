<script setup>
import { ref, watch } from 'vue'

const props = defineProps({
  content: { type: String, default: '' },
  knowledgePointName: { type: String, default: '' },
  reason: { type: String, default: '' },
  loading: { type: Boolean, default: false },
})

const emit = defineEmits(['learned'])

function simpleMarkdown(text) {
  if (!text) return ''
  return text
    .replace(/### (.+)/g, '<h3>$1</h3>')
    .replace(/## (.+)/g, '<h2>$1</h2>')
    .replace(/# (.+)/g, '<h1>$1</h1>')
    .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
    .replace(/\*(.+?)\*/g, '<em>$1</em>')
    .replace(/`{3}(\w*)\n?([\s\S]*?)`{3}/g, '<pre><code>$2</code></pre>')
    .replace(/`(.+?)`/g, '<code>$1</code>')
    .replace(/\n\n/g, '</p><p>')
    .replace(/\n/g, '<br>')
}
</script>

<template>
  <div class="explain">
    <div v-if="loading" class="explain-skeleton">
      <div class="skeleton-line skeleton-line--h2"></div>
      <div class="skeleton-line"></div>
      <div class="skeleton-line"></div>
      <div class="skeleton-line skeleton-line--short"></div>
      <div class="skeleton-line"></div>
      <div class="skeleton-line skeleton-line--short"></div>
    </div>

    <template v-else>
      <div class="explain-header">
        <h2 class="explain-title">{{ knowledgePointName }}</h2>
        <p class="explain-reason" v-if="reason">{{ reason }}</p>
      </div>

      <div class="explain-body" v-html="simpleMarkdown(content)"></div>

      <button class="learned-btn" @click="emit('learned')">
        学会了
      </button>
    </template>
  </div>
</template>

<style scoped>
.explain {
  display: flex;
  flex-direction: column;
  gap: 24px;
  padding: 32px 40px;
  max-width: 680px;
}

.explain-header {
  margin-bottom: 8px;
}

.explain-title {
  font-size: 22px;
  font-weight: 600;
  color: rgba(255,255,255,0.92);
  margin: 0 0 8px;
}

.explain-reason {
  font-size: 14px;
  color: rgba(255,255,255,0.4);
  margin: 0;
  line-height: 1.6;
}

.explain-body {
  font-size: 15px;
  line-height: 1.8;
  color: rgba(255,255,255,0.75);
}

.explain-body :deep(h1) { font-size: 20px; margin: 24px 0 12px; color: rgba(255,255,255,0.9); }
.explain-body :deep(h2) { font-size: 18px; margin: 20px 0 10px; color: rgba(255,255,255,0.85); }
.explain-body :deep(h3) { font-size: 16px; margin: 16px 0 8px; color: rgba(255,255,255,0.8); }
.explain-body :deep(p) { margin: 0 0 12px; }
.explain-body :deep(strong) { color: rgba(255,255,255,0.9); font-weight: 600; }
.explain-body :deep(code) {
  background: rgba(255,255,255,0.08);
  padding: 2px 6px;
  border-radius: 3px;
  font-size: 13px;
  font-family: 'JetBrains Mono', 'Fira Code', monospace;
}
.explain-body :deep(pre) {
  background: rgba(0,0,0,0.3);
  padding: 16px;
  border-radius: 6px;
  overflow-x: auto;
  margin: 12px 0;
}
.explain-body :deep(pre code) {
  background: none;
  padding: 0;
  font-size: 13px;
}

.learned-btn {
  align-self: flex-start;
  padding: 8px 28px;
  border-radius: 6px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  border: 1px solid rgba(255,255,255,0.2);
  background: rgba(255,255,255,0.06);
  color: rgba(255,255,255,0.8);
  transition: background 0.15s, border-color 0.15s;
  margin-top: 12px;
}
.learned-btn:hover {
  background: rgba(255,255,255,0.12);
  border-color: rgba(255,255,255,0.3);
}

.explain-skeleton {
  display: flex;
  flex-direction: column;
  gap: 14px;
  padding: 32px 40px;
}

.skeleton-line {
  height: 14px;
  border-radius: 4px;
  background: rgba(255,255,255,0.06);
  width: 100%;
}
.skeleton-line--h2 { height: 22px; width: 40%; margin-bottom: 8px; }
.skeleton-line--short { width: 60%; }
</style>
