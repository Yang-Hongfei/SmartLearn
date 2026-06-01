<script setup>
import { computed, watch, ref, nextTick } from 'vue'
import gsap from 'gsap'
import ChoiceOptionList from './ChoiceOptionList.vue'
import FillBlankInput from './FillBlankInput.vue'
import { QUESTION_TYPES } from '../../utils/constants.js'

const props = defineProps({ question: Object, showCorrectAnswer: Boolean })
const emit = defineEmits(['update:answer'])

const isChoice = computed(() =>
  props.question?.type === 'single_choice' || props.question?.type === 'true_false'
)

const correctRef = ref(null)

// Animate correct answer section appearing
watch(
  () => props.showCorrectAnswer,
  async (val) => {
    if (!val) return
    await nextTick()
    if (correctRef.value) {
      gsap.fromTo(correctRef.value, { opacity: 0, y: 10, height: 0 }, {
        opacity: 1, y: 0, height: 'auto',
        duration: 0.4, ease: 'power2.out',
      })
    }
  }
)

function parseOptions(opts) {
  if (!opts) return []
  try { return typeof opts === 'string' ? JSON.parse(opts) : opts } catch { return [] }
}
</script>

<template>
  <div class="qcard">
    <div class="qcard-header">
      <span class="qcard-topic" v-if="question.topic">{{ question.topic }}</span>
      <span class="qcard-diff">{{ '★'.repeat(question.difficulty || 1) }}</span>
      <span class="qcard-type">{{ QUESTION_TYPES[question.type] || question.type }}</span>
      <span class="qcard-id">#{{ question.id }}</span>
    </div>
    <div class="qcard-content">{{ question.content }}</div>
    <div v-if="isChoice" class="qcard-answer">
      <ChoiceOptionList :options="parseOptions(question.options)" @select="(v) => emit('update:answer', v)" />
    </div>
    <div v-else class="qcard-answer">
      <FillBlankInput @update:model-value="(v) => emit('update:answer', v)" />
    </div>
    <div v-if="showCorrectAnswer && question.correctAnswer" ref="correctRef" class="qcard-correct">
      <div class="correct-label">标准答案</div>
      <div class="correct-text">{{ question.correctAnswer }}</div>
    </div>
  </div>
</template>

<style scoped>
.qcard { max-width: 800px; margin: 0 auto; background: #fff; border: 1px solid #e5e7eb; border-radius: 10px; padding: 28px; }
.qcard-header { display: flex; align-items: center; gap: 10px; margin-bottom: 20px; }
.qcard-topic { font-size: 12px; color: #6b7280; background: #f3f4f6; padding: 3px 10px; border-radius: 4px; }
.qcard-diff { font-size: 11px; color: #d4a017; }
.qcard-type { font-size: 12px; color: #4b7fd9; background: rgba(75,127,217,0.08); padding: 3px 10px; border-radius: 4px; }
.qcard-id { margin-left: auto; font-size: 12px; color: #b0b7c3; }
.qcard-content { font-size: 16px; line-height: 1.8; color: #1a1a1a; margin-bottom: 24px; white-space: pre-wrap; }
.qcard-answer { margin-top: 16px; }
.qcard-correct { margin-top: 24px; padding-top: 20px; border-top: 1px solid #e5e7eb; }
.correct-label { font-size: 12px; font-weight: 500; color: #9ca3af; margin-bottom: 8px; }
.correct-text { background: #f8f9fb; border: 1px solid #e5e7eb; padding: 14px; border-radius: 6px; font-size: 14px; color: #4b5563; white-space: pre-wrap; line-height: 1.7; }
</style>
