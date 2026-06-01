<script setup>
import { ref, watch, nextTick } from 'vue'
import gsap from 'gsap'

const props = defineProps({
  nodes: { type: Array, default: () => [] },
  currentNodeIndex: { type: Number, default: 0 },
})

const collapsed = ref(false)
const listRef = ref(null)

// Stagger entrance animation when nodes load or list expands
watch(
  () => [props.nodes.length, collapsed.value],
  async () => {
    if (collapsed.value || !listRef.value) return
    await nextTick()
    const items = listRef.value.querySelectorAll('.timeline-node')
    gsap.fromTo(items, { opacity: 0, x: -12 }, {
      opacity: 1, x: 0,
      duration: 0.3,
      stagger: 0.05,
      ease: 'power2.out',
    })
  },
  { flush: 'post' }
)

// Pulse animation on the current node dot when index changes
watch(
  () => props.currentNodeIndex,
  async (newIdx) => {
    await nextTick()
    if (!listRef.value) return
    const dots = listRef.value.querySelectorAll('.timeline-dot')
    const currentDot = dots[newIdx]
    if (currentDot) {
      gsap.fromTo(currentDot, { scale: 1.4 }, {
        scale: 1, duration: 0.5, ease: 'power2.out',
      })
    }
  }
)
</script>

<template>
  <div class="timeline">
    <button class="timeline-heading" @click="collapsed = !collapsed">
      <span class="timeline-chevron" :class="{ 'chevron--open': !collapsed }">&#9662;</span>
      学习路径
      <span class="timeline-count" v-if="nodes.length">{{ nodes.length }}</span>
    </button>

    <div ref="listRef" class="timeline-list" v-show="!collapsed">
      <div
        v-for="(node, idx) in nodes"
        :key="node.knowledgePoint?.id || idx"
        class="timeline-node"
        :class="{
          'timeline-node--done': idx < currentNodeIndex,
          'timeline-node--current': idx === currentNodeIndex,
          'timeline-node--pending': idx > currentNodeIndex,
        }"
      >
        <div class="timeline-dot"></div>
        <div class="timeline-line" v-if="idx < nodes.length - 1"></div>
        <div class="timeline-label">{{ node.knowledgePoint?.name || node.name }}</div>
      </div>
    </div>

    <div v-if="nodes.length === 0" class="timeline-empty">
      <div class="timeline-dot timeline-dot--dim"></div>
      <span class="timeline-empty-text">规划中...</span>
    </div>
  </div>
</template>

<style scoped>
.timeline {
  padding: 24px 20px;
}

.timeline-heading {
  display: flex;
  align-items: center;
  gap: 6px;
  width: 100%;
  background: none;
  border: none;
  padding: 0;
  font-size: 11px;
  font-weight: 500;
  color: rgba(255,255,255,0.3);
  text-transform: uppercase;
  letter-spacing: 0.5px;
  margin-bottom: 20px;
  cursor: pointer;
  font-family: inherit;
}
.timeline-heading:hover { color: rgba(255,255,255,0.45); }

.timeline-chevron { font-size: 9px; transition: transform 0.2s; }
.chevron--open { }

.timeline-count {
  margin-left: auto;
  font-size: 10px;
  color: rgba(255,255,255,0.15);
  font-variant-numeric: tabular-nums;
}

.timeline-list {
  display: flex;
  flex-direction: column;
}

.timeline-node {
  display: flex;
  align-items: flex-start;
  gap: 10px;
  position: relative;
  padding-bottom: 18px;
  opacity: 0; /* hidden until GSAP stagger reveals */
}

.timeline-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  flex-shrink: 0;
  margin-top: 6px;
  background: rgba(255,255,255,0.2);
  transition: background 0.3s, box-shadow 0.3s;
}

.timeline-node--done .timeline-dot {
  background: rgba(255,255,255,0.55);
}

.timeline-node--current .timeline-dot {
  background: #6b9fff;
  box-shadow: 0 0 8px rgba(107,159,255,0.35);
}

.timeline-node--pending .timeline-dot {
  background: rgba(255,255,255,0.12);
}

.timeline-line {
  position: absolute;
  left: 3.5px;
  top: 18px;
  width: 1px;
  height: calc(100% - 10px);
  background: rgba(255,255,255,0.08);
}

.timeline-label {
  font-size: 13px;
  color: rgba(255,255,255,0.5);
  line-height: 1.4;
  transition: color 0.3s;
}

.timeline-node--done .timeline-label {
  color: rgba(255,255,255,0.6);
}

.timeline-node--current .timeline-label {
  color: rgba(255,255,255,0.9);
  font-weight: 500;
}

.timeline-node--pending .timeline-label {
  color: rgba(255,255,255,0.25);
}

.timeline-empty {
  display: flex;
  align-items: center;
  gap: 10px;
  padding-bottom: 12px;
}

.timeline-dot--dim {
  opacity: 0.4;
}

.timeline-empty-text {
  font-size: 13px;
  color: rgba(255,255,255,0.2);
}
</style>
