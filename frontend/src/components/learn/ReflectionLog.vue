<script setup>
import { ref } from 'vue'
import gsap from 'gsap'

defineProps({
  entries: { type: Array, default: () => [] },
})

const collapsed = ref(false)

function scoreWide(score) {
  if (score == null) return 0
  return Math.round(score * 100)
}

function onItemEnter(el, done) {
  gsap.fromTo(el, { opacity: 0, x: 20, height: 0 }, {
    opacity: 1, x: 0, height: 'auto',
    duration: 0.35, ease: 'power2.out',
    onComplete: done,
  })
}

function onItemLeave(el, done) {
  gsap.to(el, { opacity: 0, x: -10, duration: 0.2, ease: 'power2.in', onComplete: done })
}
</script>

<template>
  <div class="reflection" v-if="entries.length > 0">
    <button class="reflection-heading" @click="collapsed = !collapsed">
      <span class="reflection-chevron" :class="{ 'chevron--open': !collapsed }">&#9662;</span>
      分析记录
      <span class="reflection-count">{{ entries.length }}</span>
    </button>

    <TransitionGroup
      v-show="!collapsed"
      tag="div"
      class="reflection-list"
      @enter="onItemEnter"
      @leave="onItemLeave"
      appear
    >
      <div v-for="(entry, idx) in entries" :key="idx" class="reflection-item">
        <div class="reflection-score-row" v-if="entry.score != null">
          <span class="reflection-score" :class="{
            'score--high': entry.score >= 0.85,
            'score--mid': entry.score >= 0.5 && entry.score < 0.85,
            'score--low': entry.score < 0.5,
          }">{{ scoreWide(entry.score) }}%</span>
          <span class="reflection-level">{{ entry.level }}</span>
        </div>
        <p class="reflection-text">{{ entry.summary }}</p>
        <span class="reflection-tag" :class="{
          'reflection-tag--forward': entry.conclusion === 'forward',
          'reflection-tag--reinforce': entry.conclusion === 'reinforce',
          'reflection-tag--rollback': entry.conclusion === 'rollback',
        }">
          {{ entry.conclusion === 'forward' ? '前进' : entry.conclusion === 'reinforce' ? '巩固' : '回退' }}
        </span>
      </div>
    </TransitionGroup>
  </div>
</template>

<style scoped>
.reflection {
  padding: 20px;
  border-top: 1px solid rgba(255,255,255,0.06);
}

.reflection-heading {
  display: flex;
  align-items: center;
  gap: 6px;
  width: 100%;
  background: none;
  border: none;
  padding: 0;
  font-size: 11px;
  font-weight: 500;
  color: rgba(255,255,255,0.25);
  text-transform: uppercase;
  letter-spacing: 0.5px;
  margin-bottom: 12px;
  cursor: pointer;
  font-family: inherit;
}
.reflection-heading:hover { color: rgba(255,255,255,0.4); }

.reflection-chevron {
  font-size: 9px;
  transition: transform 0.2s;
}
.chevron--open { }

.reflection-count {
  margin-left: auto;
  font-size: 10px;
  color: rgba(255,255,255,0.15);
  font-variant-numeric: tabular-nums;
}

.reflection-list {
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.reflection-item {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.reflection-score-row {
  display: flex;
  align-items: center;
  gap: 8px;
}

.reflection-score {
  font-size: 13px;
  font-weight: 600;
  font-variant-numeric: tabular-nums;
}

.score--high { color: rgba(107,159,255,0.8); }
.score--mid  { color: rgba(255,193,7,0.7); }
.score--low  { color: rgba(255,107,107,0.7); }

.reflection-level {
  font-size: 11px;
  color: rgba(255,255,255,0.35);
}

.reflection-text {
  font-size: 12px;
  color: rgba(255,255,255,0.45);
  line-height: 1.5;
  margin: 0;
}

.reflection-tag {
  display: inline-block;
  align-self: flex-start;
  font-size: 10px;
  padding: 2px 8px;
  border-radius: 3px;
  font-weight: 500;
  letter-spacing: 0.3px;
}

.reflection-tag--forward {
  background: rgba(107,159,255,0.12);
  color: rgba(107,159,255,0.7);
}

.reflection-tag--reinforce {
  background: rgba(255,193,7,0.1);
  color: rgba(255,193,7,0.6);
}

.reflection-tag--rollback {
  background: rgba(255,107,107,0.1);
  color: rgba(255,107,107,0.6);
}
</style>
