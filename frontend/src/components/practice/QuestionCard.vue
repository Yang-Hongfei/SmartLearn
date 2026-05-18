<script setup>
import { computed } from 'vue'
import ChoiceOptionList from './ChoiceOptionList.vue'
import FillBlankInput from './FillBlankInput.vue'
import { QUESTION_TYPES } from '../../utils/constants.js'

const props = defineProps({
  question: Object,
  showCorrectAnswer: Boolean
})
const emit = defineEmits(['update:answer'])

const isChoice = computed(() =>
  props.question?.type === 'single_choice' || props.question?.type === 'true_false'
)

function parseOptions(opts) {
  if (!opts) return []
  try {
    return typeof opts === 'string' ? JSON.parse(opts) : opts
  } catch { return [] }
}
</script>

<template>
  <el-card class="question-card" shadow="hover">
    <template #header>
      <div class="card-header">
        <el-tag v-if="question.topic" type="info" size="small">{{ question.topic }}</el-tag>
        <el-tag :type="question.difficulty >= 4 ? 'danger' : question.difficulty >= 3 ? 'warning' : ''" size="small">
          {{ '⭐'.repeat(question.difficulty || 1) }}
        </el-tag>
        <el-tag type="primary" size="small">{{ QUESTION_TYPES[question.type] || question.type }}</el-tag>
        <span class="question-id">#{{ question.id }}</span>
      </div>
    </template>
    <div class="question-content">{{ question.content }}</div>
    <div v-if="isChoice" class="answer-area">
      <ChoiceOptionList :options="parseOptions(question.options)" @select="(v) => emit('update:answer', v)" />
    </div>
    <div v-else class="answer-area">
      <FillBlankInput @update:model-value="(v) => emit('update:answer', v)" />
    </div>
    <div v-if="showCorrectAnswer && question.correctAnswer" class="correct-answer">
      <el-divider />
      <div class="answer-label">标准答案：</div>
      <div class="answer-text">{{ question.correctAnswer }}</div>
    </div>
  </el-card>
</template>

<style scoped>
.question-card { max-width: 800px; margin: 0 auto; }
.card-header { display: flex; align-items: center; gap: 8px; flex-wrap: wrap; }
.question-id { margin-left: auto; color: #909399; font-size: 13px; }
.question-content { font-size: 16px; line-height: 1.8; margin-bottom: 20px; white-space: pre-wrap; }
.answer-area { margin-top: 16px; }
.correct-answer { margin-top: 8px; }
.answer-label { font-weight: bold; color: #67c23a; margin-bottom: 8px; }
.answer-text { background: #f0f9eb; padding: 12px; border-radius: 6px; white-space: pre-wrap; line-height: 1.8; }
</style>
