<script setup>
import { computed } from 'vue'
import ErrorAnalysisDisplay from './ErrorAnalysisDisplay.vue'
import WeakPointsList from './WeakPointsList.vue'
import LearningPathTimeline from './LearningPathTimeline.vue'
import { useGsapModal } from '../../composables/useGsapModal'

const props = defineProps({ analysis: Object, visible: Boolean })
const emit = defineEmits(['close'])

const { show, overlayRef, dialogRef } = useGsapModal(() => props.visible, { scale: true })

const isCorrect = computed(() => props.analysis?.is_correct)
const errorAnalysis = computed(() => props.analysis?.error_analysis)
const weakPoints = computed(() => props.analysis?.weak_point_analysis || [])
const learningPath = computed(() => props.analysis?.learning_path || [])
</script>

<template>
  <div v-if="show" ref="overlayRef" class="ai-overlay" @click.self="emit('close')">
    <div ref="dialogRef" class="ai-panel">
      <div class="ai-header">
        <h3 class="ai-title">{{ isCorrect ? '回答正确' : '回答错误' }}</h3>
        <button class="ai-close" @click="emit('close')">&times;</button>
      </div>
      <p class="ai-sub" v-if="isCorrect">你对这个知识点掌握得很好</p>
      <div class="ai-body">
        <ErrorAnalysisDisplay v-if="!isCorrect && errorAnalysis" :analysis="errorAnalysis" />
        <WeakPointsList v-if="weakPoints.length" :points="weakPoints" />
        <LearningPathTimeline v-if="learningPath.length" :nodes="learningPath" />
      </div>
    </div>
  </div>
</template>

<style scoped>
.ai-overlay { position: fixed; inset: 0; background: rgba(0,0,0,0.3); display: flex; align-items: center; justify-content: center; z-index: 1000; }
.ai-panel { background: #fff; border: 1px solid #e5e7eb; border-radius: 10px; padding: 32px; width: 680px; max-height: 85vh; overflow-y: auto; box-shadow: 0 4px 24px rgba(0,0,0,0.08); }
.ai-header { display: flex; align-items: center; justify-content: space-between; margin-bottom: 8px; }
.ai-title { font-size: 20px; font-weight: 600; color: #1a1a1a; margin: 0; }
.ai-close { background: none; border: none; font-size: 22px; color: #9ca3af; cursor: pointer; padding: 0; line-height: 1; }
.ai-close:hover { color: #4b5563; }
.ai-sub { font-size: 14px; color: #6b7280; margin: 0 0 24px; }
</style>
