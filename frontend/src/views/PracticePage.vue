<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import AppLayout from '../components/layout/AppLayout.vue'
import ModeSelector from '../components/practice/ModeSelector.vue'
import QuestionCard from '../components/practice/QuestionCard.vue'
import ActionBar from '../components/practice/ActionBar.vue'
import JudgeModeDialog from '../components/practice/JudgeModeDialog.vue'
import SelfJudgePanel from '../components/practice/SelfJudgePanel.vue'
import AiAnalysisPanel from '../components/practice/AiAnalysisPanel.vue'
import ProgressSidebar from '../components/practice/ProgressSidebar.vue'
import NavigationControls from '../components/practice/NavigationControls.vue'
import { questionApi } from '../api/questionApi.js'
import { practiceApi } from '../api/practiceApi.js'

const USER_ID = 1

const mode = ref('random')
const question = ref(null)
const answer = ref('')
const loading = ref(false)
const submitting = ref(false)
const stats = ref({ total: 0, learned: 0, unanswered: 0, incorrect: 0 })

// State
const submitted = ref(false)
const showCorrectAnswer = ref(false)
const showJudgeDialog = ref(false)
const showSelfJudge = ref(false)
const currentRecordId = ref(null)
const isCorrect = ref(null)
const showAiAnalysis = ref(false)
const aiAnalysisData = ref(null)

// Sequential / Incorrect mode state
const sequentialIdx = ref(0)
const totalQuestions = ref(0)
const topics = ref([])
const selectedTopic = ref('')
const incorrectIds = ref([])

const isEssay = computed(() => question.value?.type === 'essay')
const showAiBtn = computed(() => submitted.value && currentRecordId.value)

async function loadRandomQuestion() {
  loading.value = true
  resetState()
  try {
    const q = await questionApi.random(USER_ID)
    question.value = q
  } catch (e) {
    ElMessage.error(e.message)
  }
  loading.value = false
}

async function loadSequentialQuestion(direction) {
  loading.value = true
  resetState()
  try {
    const topic = selectedTopic.value || ''
    let q
    if (direction === 'next' && question.value) {
      q = await questionApi.next(question.value.id, topic)
      if (q) sequentialIdx.value++
    } else if (direction === 'prev' && question.value) {
      q = await questionApi.prev(question.value.id, topic)
      if (q) sequentialIdx.value--
    } else {
      q = await questionApi.next(0, topic)
      if (q) sequentialIdx.value = 1
    }
    if (q) {
      question.value = q
    } else {
      ElMessage.info(direction === 'next' ? '已是最后一题' : '已是第一题')
    }
  } catch (e) {
    ElMessage.error(e.message)
  }
  loading.value = false
}

async function loadIncorrectQuestion(direction) {
  loading.value = true
  resetState()
  try {
    if (incorrectIds.value.length === 0) {
      ElMessage.info('没有错题')
      loading.value = false
      return
    }
    if (direction === 'next') {
      sequentialIdx.value = Math.min(sequentialIdx.value + 1, incorrectIds.value.length)
    } else if (direction === 'prev') {
      sequentialIdx.value = Math.max(sequentialIdx.value - 1, 1)
    } else {
      sequentialIdx.value = 1
    }
    if (sequentialIdx.value < 1 || sequentialIdx.value > incorrectIds.value.length) {
      ElMessage.info(direction === 'next' ? '已是最后一题' : '已是第一题')
      loading.value = false
      return
    }
    const q = await questionApi.getById(incorrectIds.value[sequentialIdx.value - 1])
    question.value = q
  } catch (e) {
    ElMessage.error(e.message)
  }
  loading.value = false
}

function loadQuestion(direction) {
  if (mode.value === 'random') loadRandomQuestion()
  else if (mode.value === 'incorrect') loadIncorrectQuestion(direction)
  else loadSequentialQuestion(direction)
}

function resetState() {
  answer.value = ''
  submitted.value = false
  showCorrectAnswer.value = false
  showJudgeDialog.value = false
  showSelfJudge.value = false
  currentRecordId.value = null
  isCorrect.value = null
  showAiAnalysis.value = false
  aiAnalysisData.value = null
}

async function handleSubmit() {
  if (!answer.value) return

  if (isEssay.value) {
    showJudgeDialog.value = true
    return
  }

  submitting.value = true
  try {
    const result = await practiceApi.submit({
      userId: USER_ID,
      questionId: question.value.id,
      userAnswer: answer.value,
      judgeMode: 'auto'
    })
    submitted.value = true
    currentRecordId.value = result.recordId
    isCorrect.value = result.isCorrect
    showCorrectAnswer.value = true
    ElMessage({
      message: result.isCorrect ? '回答正确！' : '回答错误',
      type: result.isCorrect ? 'success' : 'error'
    })
    await loadStats()
    if (mode.value === 'incorrect') await reloadIncorrect()
  } catch (e) {
    ElMessage.error(e.message)
  }
  submitting.value = false
}

async function handleJudgeChoice(judgeMode) {
  showJudgeDialog.value = false
  submitting.value = true
  try {
    const result = await practiceApi.submit({
      userId: USER_ID,
      questionId: question.value.id,
      userAnswer: answer.value,
      judgeMode
    })
    submitted.value = true
    currentRecordId.value = result.recordId

    if (judgeMode === 'self') {
      showCorrectAnswer.value = true
      showSelfJudge.value = true
    } else if (judgeMode === 'ai') {
      isCorrect.value = result.isCorrect
      showAiAnalysis.value = true
      aiAnalysisData.value = result.aiAnalysis
      ElMessage({
        message: result.isCorrect ? 'AI 判断：回答正确' : 'AI 判断：回答错误',
        type: result.isCorrect ? 'success' : 'error'
      })
    }
    if (mode.value === 'incorrect') await reloadIncorrect()
  } catch (e) {
    ElMessage.error(e.message)
  }
  submitting.value = false
}

async function handleSelfJudge(correct) {
  if (!currentRecordId.value) return
  try {
    await practiceApi.selfJudge(currentRecordId.value, correct)
    showSelfJudge.value = false
    isCorrect.value = correct
    ElMessage({ message: correct ? '已标记为正确' : '已标记为错误', type: correct ? 'success' : 'error' })
    await loadStats()
    if (mode.value === 'incorrect') await reloadIncorrect()
  } catch (e) {
    ElMessage.error(e.message)
  }
}

async function handleAiAnalysis() {
  if (!currentRecordId.value) return
  submitting.value = true
  try {
    const result = await practiceApi.aiAnalysis(currentRecordId.value)
    aiAnalysisData.value = result
    showAiAnalysis.value = true
  } catch (e) {
    ElMessage.error(e.message)
  }
  submitting.value = false
}

async function handleLearned() {
  if (!currentRecordId.value) return
  try {
    await practiceApi.updateStatus(currentRecordId.value, 'learned')
    ElMessage.success('已标记为学会')
    await loadStats()
    if (mode.value === 'incorrect') await reloadIncorrect()
  } catch (e) {
    ElMessage.error(e.message)
  }
}

function handleSkip() {
  question.value = null
  loadQuestion('next')
}

async function loadStats() {
  try {
    stats.value = await practiceApi.stats(USER_ID)
  } catch (e) { /* ignore */ }
}

async function loadTotalCount() {
  try {
    totalQuestions.value = await questionApi.count()
  } catch (e) { /* ignore */ }
}

async function loadTopics() {
  try {
    topics.value = await questionApi.topics()
  } catch (e) { /* ignore */ }
}

async function reloadIncorrect() {
  try {
    const list = await questionApi.incorrect(USER_ID)
    incorrectIds.value = list.map(q => q.id)
    totalQuestions.value = incorrectIds.value.length
  } catch (e) { /* ignore */ }
}

function onTopicChange() {
  resetState()
  question.value = null
  sequentialIdx.value = 0
  loadSequentialQuestion('next')
}

watch(mode, async () => {
  resetState()
  question.value = null
  sequentialIdx.value = 0
  if (mode.value === 'random') {
    totalQuestions.value = 0
    loadRandomQuestion()
  } else if (mode.value === 'incorrect') {
    await reloadIncorrect()
    loadIncorrectQuestion('next')
  } else {
    await loadTotalCount()
    loadSequentialQuestion('next')
  }
})

onMounted(() => {
  loadStats()
  loadTotalCount()
  loadTopics()
  loadRandomQuestion()
})
</script>

<template>
  <AppLayout>
    <div class="practice-page">
      <div class="practice-main">
        <div class="top-bar">
          <ModeSelector v-model="mode" />
          <el-select v-if="mode === 'sequential'"
            v-model="selectedTopic" placeholder="全部分类" clearable
            @change="onTopicChange" style="width:200px; margin-left:12px">
            <el-option v-for="t in topics" :key="t" :label="t" :value="t" />
          </el-select>
        </div>

        <div v-if="loading" class="loading-area">
          <el-skeleton :rows="6" animated />
        </div>

        <div v-else-if="question" class="question-area">
          <QuestionCard :question="question" :show-correct-answer="showCorrectAnswer"
            @update:answer="(v) => answer = v" />

          <ActionBar :answer="answer" :submitted="submitted" :show-ai-btn="showAiBtn"
            :loading="submitting" @submit="handleSubmit" @skip="handleSkip"
            @learned="handleLearned" @ai-analysis="handleAiAnalysis" />

          <SelfJudgePanel :visible="showSelfJudge" @judge="handleSelfJudge" />

          <NavigationControls v-if="mode !== 'random'"
            :current-index="sequentialIdx" :total="totalQuestions"
            @prev="loadQuestion('prev')" @next="loadQuestion('next')" />
        </div>

        <div v-else class="empty-area">
          <el-empty description="题库为空，请先导入 PDF 题库" />
        </div>
      </div>

      <div class="practice-sidebar">
        <ProgressSidebar :stats="stats" />
      </div>
    </div>

    <JudgeModeDialog :visible="showJudgeDialog" @choose="handleJudgeChoice" @close="showJudgeDialog = false" />
    <AiAnalysisPanel :analysis="aiAnalysisData" :visible="showAiAnalysis" @close="showAiAnalysis = false" />
  </AppLayout>
</template>

<style scoped>
.practice-page { display: flex; gap: 24px; max-width: 1100px; margin: 0 auto; }
.practice-main { flex: 1; min-width: 0; }
.practice-sidebar { flex-shrink: 0; }
.top-bar { display: flex; align-items: center; margin-bottom: 20px; }
.question-area { }
.loading-area { max-width: 800px; margin: 40px auto; }
.empty-area { margin-top: 80px; }
</style>
