<script setup>
import { ref, computed } from 'vue'

const props = defineProps({
  question: { type: Object, default: null },
  loading: { type: Boolean, default: false },
})

const emit = defineEmits(['submit'])

const selectedAnswer = ref('')
const submitting = ref(false)

const isChoice = computed(() =>
  props.question?.type === 'single_choice' || props.question?.type === 'true_false'
)

function handleSubmit() {
  if (!selectedAnswer.value.trim()) return
  submitting.value = true
  emit('submit', { answer: selectedAnswer.value.trim() })
}

function reset() {
  selectedAnswer.value = ''
  submitting.value = false
}

defineExpose({ reset })
</script>

<template>
  <div class="quiz">
    <div v-if="loading" class="quiz-skeleton">
      <div class="skeleton-line skeleton-line--h3"></div>
      <div class="skeleton-line"></div>
      <div class="skeleton-line skeleton-line--short"></div>
      <div class="skeleton-line skeleton-line--short"></div>
    </div>

    <template v-else-if="question">
      <div class="quiz-content">
        <p class="quiz-type">{{ question.type === 'single_choice' ? '单选题' : question.type === 'true_false' ? '判断题' : question.type === 'fill_blank' ? '填空题' : '问答题' }}</p>
        <p class="quiz-text">{{ question.content }}</p>
      </div>

      <div v-if="isChoice && question.options" class="quiz-options">
        <button
          v-for="(opt, idx) in question.options"
          :key="idx"
          class="quiz-option"
          :class="{ 'quiz-option--selected': selectedAnswer === opt }"
          @click="selectedAnswer = opt"
        >
          <span class="quiz-option-label">{{ String.fromCharCode(65 + idx) }}</span>
          <span class="quiz-option-text">{{ opt }}</span>
        </button>
      </div>

      <div v-else class="quiz-input-area">
        <textarea
          v-model="selectedAnswer"
          class="quiz-textarea"
          placeholder="输入你的答案..."
          rows="3"
        ></textarea>
      </div>

      <button
        class="quiz-submit"
        :disabled="!selectedAnswer.trim() || submitting"
        @click="handleSubmit"
      >
        {{ submitting ? '提交中...' : '提交答案' }}
      </button>
    </template>
  </div>
</template>

<style scoped>
.quiz {
  display: flex;
  flex-direction: column;
  gap: 24px;
  padding: 32px 40px;
  max-width: 680px;
}

.quiz-content {
  margin-bottom: 8px;
}

.quiz-type {
  font-size: 11px;
  font-weight: 500;
  color: rgba(255,255,255,0.3);
  text-transform: uppercase;
  letter-spacing: 0.5px;
  margin: 0 0 8px;
}

.quiz-text {
  font-size: 16px;
  line-height: 1.7;
  color: rgba(255,255,255,0.85);
  margin: 0;
}

.quiz-options {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.quiz-option {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  padding: 12px 16px;
  border-radius: 6px;
  background: rgba(255,255,255,0.04);
  border: 1px solid rgba(255,255,255,0.08);
  cursor: pointer;
  text-align: left;
  font: inherit;
  color: inherit;
  transition: background 0.15s, border-color 0.15s;
}
.quiz-option:hover {
  background: rgba(255,255,255,0.08);
  border-color: rgba(255,255,255,0.15);
}
.quiz-option--selected {
  background: rgba(255,255,255,0.1);
  border-color: rgba(255,255,255,0.25);
}

.quiz-option-label {
  font-size: 13px;
  font-weight: 600;
  color: rgba(255,255,255,0.35);
  min-width: 20px;
}

.quiz-option-text {
  font-size: 14px;
  color: rgba(255,255,255,0.8);
  line-height: 1.5;
}

.quiz-input-area {
  width: 100%;
}

.quiz-textarea {
  width: 100%;
  padding: 12px 16px;
  border-radius: 6px;
  background: rgba(255,255,255,0.06);
  border: 1px solid rgba(255,255,255,0.1);
  color: rgba(255,255,255,0.85);
  font: inherit;
  font-size: 14px;
  resize: vertical;
  outline: none;
  transition: border-color 0.15s;
}
.quiz-textarea:focus { border-color: rgba(255,255,255,0.25); }
.quiz-textarea::placeholder { color: rgba(255,255,255,0.2); }

.quiz-submit {
  align-self: flex-start;
  padding: 8px 24px;
  border-radius: 6px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  border: 1px solid rgba(255,255,255,0.2);
  background: rgba(255,255,255,0.1);
  color: rgba(255,255,255,0.85);
  transition: background 0.15s, border-color 0.15s;
}
.quiz-submit:hover:not(:disabled) {
  background: rgba(255,255,255,0.16);
  border-color: rgba(255,255,255,0.3);
}
.quiz-submit:disabled {
  opacity: 0.35;
  cursor: not-allowed;
}

.quiz-skeleton {
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
.skeleton-line--h3 { height: 20px; width: 30%; margin-bottom: 8px; }
.skeleton-line--short { width: 60%; }
</style>
