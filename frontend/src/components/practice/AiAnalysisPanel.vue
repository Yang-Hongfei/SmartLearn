<script setup>
import { computed } from 'vue'
import ErrorAnalysisDisplay from './ErrorAnalysisDisplay.vue'
import WeakPointsList from './WeakPointsList.vue'
import LearningPathTimeline from './LearningPathTimeline.vue'

const props = defineProps({ analysis: Object, visible: Boolean })
const emit = defineEmits(['close'])

const isCorrect = computed(() => props.analysis?.is_correct)
const errorAnalysis = computed(() => props.analysis?.error_analysis)
const weakPoints = computed(() => props.analysis?.weak_point_analysis || [])
const learningPath = computed(() => props.analysis?.learning_path || [])
</script>

<template>
  <el-dialog :modelValue="visible" title="🤖 AI 诊断结果" width="700px" @update:modelValue="emit('close')">
    <div v-if="analysis">
      <el-result :icon="isCorrect ? 'success' : 'error'"
        :title="isCorrect ? '回答正确！' : '回答错误'"
        :sub-title="isCorrect ? '太棒了，你对这个知识点掌握得很好' : ''" />

      <ErrorAnalysisDisplay v-if="!isCorrect && errorAnalysis" :analysis="errorAnalysis" />
      <WeakPointsList v-if="weakPoints.length" :points="weakPoints" />
      <LearningPathTimeline v-if="learningPath.length" :nodes="learningPath" />
    </div>
  </el-dialog>
</template>
