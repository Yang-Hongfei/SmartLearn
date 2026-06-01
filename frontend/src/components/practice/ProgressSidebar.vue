<script setup>
import { watch, ref, nextTick } from 'vue'
import gsap from 'gsap'

const props = defineProps({ stats: Object })

const totalEl = ref(null)

// Animate stats numbers counting up when they change
watch(
  () => props.stats,
  async (newStats) => {
    if (!newStats) return
    await nextTick()

    // Total count
    const totalTarget = newStats.total || 0
    if (totalEl.value) {
      const current = parseInt(totalEl.value.innerText) || 0
      gsap.fromTo(totalEl.value, { innerText: current }, {
        innerText: totalTarget,
        duration: 0.6,
        ease: 'power2.out',
        snap: { innerText: 1 },
      })
    }

    // Sidebar row numbers
    const rows = document.querySelectorAll('.sidebar-row strong')
    const targets = [newStats.learned || 0, newStats.unanswered || 0, newStats.incorrect || 0]
    rows.forEach((el, i) => {
      if (i < targets.length) {
        const cur = parseInt(el.innerText) || 0
        gsap.fromTo(el, { innerText: cur }, {
          innerText: targets[i],
          duration: 0.5,
          ease: 'power2.out',
          snap: { innerText: 1 },
          delay: i * 0.1,
        })
      }
    })
  },
  { deep: true, immediate: false }
)
</script>

<template>
  <div class="sidebar">
    <div class="sidebar-heading">学习进度</div>
    <div class="sidebar-stat">
      <span ref="totalEl" class="stat-num">{{ stats?.total || 0 }}</span>
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
.stat-num { font-size: 36px; font-weight: 700; color: #1a1a1a; line-height: 1; font-variant-numeric: tabular-nums; }
.stat-label { font-size: 12px; color: #9ca3af; margin-top: 4px; }
.sidebar-row { display: flex; justify-content: space-between; padding: 8px 0; font-size: 13px; color: #6b7280; }
.sidebar-row--learned strong { color: #4a9a2e; }
.sidebar-row--unanswered strong { color: #9ca3af; }
.sidebar-row--incorrect strong { color: #e5534b; }
</style>
