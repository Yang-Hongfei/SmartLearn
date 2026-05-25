<script setup>
import { ref, computed, watch, onMounted, onBeforeUnmount } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import ModeSelector from '../components/practice/ModeSelector.vue'
import QuestionCard from '../components/practice/QuestionCard.vue'
import ActionBar from '../components/practice/ActionBar.vue'
import JudgeModeDialog from '../components/practice/JudgeModeDialog.vue'
import SelfJudgePanel from '../components/practice/SelfJudgePanel.vue'
import AiAnalysisPanel from '../components/practice/AiAnalysisPanel.vue'
import ProgressSidebar from '../components/practice/ProgressSidebar.vue'
import NavigationControls from '../components/practice/NavigationControls.vue'
import SettingsModal from '../components/common/SettingsModal.vue'
import { questionApi } from '../api/questionApi.js'
import { practiceApi } from '../api/practiceApi.js'

const router = useRouter()
const USER_ID = 1

const mode = ref('random')
const question = ref(null)
const answer = ref('')
const loading = ref(false)
const submitting = ref(false)
const stats = ref({ total: 0, learned: 0, unanswered: 0, incorrect: 0 })

const submitted = ref(false)
const showCorrectAnswer = ref(false)
const showJudgeDialog = ref(false)
const showSelfJudge = ref(false)
const currentRecordId = ref(null)
const isCorrect = ref(null)
const showAiAnalysis = ref(false)
const aiAnalysisData = ref(null)

const sequentialIdx = ref(0)
const totalQuestions = ref(0)
const topics = ref([])
const selectedTopic = ref('')
const showSettings = ref(false)

function onOpenSettings() { showSettings.value = true }
onMounted(() => window.addEventListener('open-settings', onOpenSettings))
onBeforeUnmount(() => { window.removeEventListener('open-settings', onOpenSettings) })

const incorrectIds = ref([])

const isEssay = computed(() => question.value?.type === 'essay')
const showAiBtn = computed(() => submitted.value && currentRecordId.value)

async function loadRandomQuestion() {
  loading.value = true; resetState()
  try { question.value = await questionApi.random(USER_ID) } catch (e) { ElMessage.error(e.message) }
  loading.value = false
}

async function loadSequentialQuestion(direction) {
  loading.value = true; resetState()
  try {
    const topic = selectedTopic.value || ''
    let q
    if (direction === 'next' && question.value) { q = await questionApi.next(question.value.id, topic); if (q) sequentialIdx.value++ }
    else if (direction === 'prev' && question.value) { q = await questionApi.prev(question.value.id, topic); if (q) sequentialIdx.value-- }
    else { q = await questionApi.next(0, topic); if (q) sequentialIdx.value = 1 }
    if (q) question.value = q
    else ElMessage.info(direction === 'next' ? '已是最后一题' : '已是第一题')
  } catch (e) { ElMessage.error(e.message) }
  loading.value = false
}

async function loadIncorrectQuestion(direction) {
  loading.value = true; resetState()
  try {
    if (incorrectIds.value.length === 0) { ElMessage.info('没有错题'); loading.value = false; return }
    if (direction === 'next') sequentialIdx.value = Math.min(sequentialIdx.value + 1, incorrectIds.value.length)
    else if (direction === 'prev') sequentialIdx.value = Math.max(sequentialIdx.value - 1, 1)
    else sequentialIdx.value = 1
    if (sequentialIdx.value < 1 || sequentialIdx.value > incorrectIds.value.length) {
      ElMessage.info(direction === 'next' ? '已是最后一题' : '已是第一题'); loading.value = false; return
    }
    question.value = await questionApi.getById(incorrectIds.value[sequentialIdx.value - 1])
  } catch (e) { ElMessage.error(e.message) }
  loading.value = false
}

function loadQuestion(direction) {
  if (mode.value === 'random') loadRandomQuestion()
  else if (mode.value === 'incorrect') loadIncorrectQuestion(direction)
  else loadSequentialQuestion(direction)
}

function resetState() {
  answer.value = ''; submitted.value = false; showCorrectAnswer.value = false
  showJudgeDialog.value = false; showSelfJudge.value = false
  currentRecordId.value = null; isCorrect.value = null
  showAiAnalysis.value = false; aiAnalysisData.value = null
}

async function handleSubmit() {
  if (!answer.value) return
  if (isEssay.value) { showJudgeDialog.value = true; return }
  submitting.value = true
  try {
    const result = await practiceApi.submit({ userId: USER_ID, questionId: question.value.id, userAnswer: answer.value, judgeMode: 'auto' })
    submitted.value = true; currentRecordId.value = result.recordId
    isCorrect.value = result.isCorrect; showCorrectAnswer.value = true
    ElMessage({ message: result.isCorrect ? '回答正确！' : '回答错误', type: result.isCorrect ? 'success' : 'error' })
    await loadStats(); if (mode.value === 'incorrect') await reloadIncorrect()
  } catch (e) { ElMessage.error(e.message) }
  submitting.value = false
}

async function handleJudgeChoice(judgeMode) {
  showJudgeDialog.value = false; submitting.value = true
  try {
    const result = await practiceApi.submit({ userId: USER_ID, questionId: question.value.id, userAnswer: answer.value, judgeMode })
    submitted.value = true; currentRecordId.value = result.recordId
    if (judgeMode === 'self') { showCorrectAnswer.value = true; showSelfJudge.value = true }
    else if (judgeMode === 'ai') { isCorrect.value = result.isCorrect; showAiAnalysis.value = true; aiAnalysisData.value = result.aiAnalysis }
    if (mode.value === 'incorrect') await reloadIncorrect()
  } catch (e) { ElMessage.error(e.message) }
  submitting.value = false
}

async function handleSelfJudge(correct) {
  if (!currentRecordId.value) return
  try { await practiceApi.selfJudge(currentRecordId.value, correct); showSelfJudge.value = false; isCorrect.value = correct; await loadStats(); if (mode.value === 'incorrect') await reloadIncorrect() } catch (e) { ElMessage.error(e.message) }
}

async function handleAiAnalysis() {
  if (!currentRecordId.value) return; submitting.value = true
  try { aiAnalysisData.value = await practiceApi.aiAnalysis(currentRecordId.value); showAiAnalysis.value = true } catch (e) { ElMessage.error(e.message) }
  submitting.value = false
}

async function handleLearned() {
  if (!currentRecordId.value) return
  try { await practiceApi.updateStatus(currentRecordId.value, 'learned'); ElMessage.success('已标记为学会'); await loadStats(); if (mode.value === 'incorrect') await reloadIncorrect() } catch (e) { ElMessage.error(e.message) }
}

function handleSkip() { question.value = null; loadQuestion('next') }

async function loadStats() { try { stats.value = await practiceApi.stats(USER_ID) } catch (e) { /* ignore */ } }
async function loadTotalCount() { try { totalQuestions.value = await questionApi.count() } catch (e) { /* ignore */ } }
async function loadTopics() { try { topics.value = await questionApi.topics() } catch (e) { /* ignore */ } }
async function reloadIncorrect() { try { const list = await questionApi.incorrect(USER_ID); incorrectIds.value = list.map(q => q.id); totalQuestions.value = incorrectIds.value.length } catch (e) { /* ignore */ } }
function onTopicChange() { resetState(); question.value = null; sequentialIdx.value = 0; loadSequentialQuestion('next') }

watch(mode, async () => {
  resetState(); question.value = null; sequentialIdx.value = 0
  if (mode.value === 'random') { totalQuestions.value = 0; loadRandomQuestion() }
  else if (mode.value === 'incorrect') { await reloadIncorrect(); loadIncorrectQuestion('next') }
  else { await loadTotalCount(); loadSequentialQuestion('next') }
})

onMounted(() => { loadStats(); loadTotalCount(); loadTopics(); loadRandomQuestion() })
</script>

<template>
  <div class="practice">
    <div class="practice-topbar">
      <button class="topbar-back" @click="router.push('/')">&larr; 首页</button>
      <span class="topbar-logo">SmartLearn</span>
      <nav class="topbar-nav">
        <button class="topbar-tab topbar-tab--active">刷题练习</button>
        <button class="topbar-tab" @click="router.push('/import')">PDF 导入</button>
      </nav>
      <button class="topbar-settings" @click="showSettings = true" title="设置 API Key">&#9881;</button>
    </div>
    <div class="practice-body">
      <div class="practice-main">
        <div class="top-bar">
          <ModeSelector v-model="mode" />
          <el-select
            v-if="mode === 'sequential'"
            v-model="selectedTopic" placeholder="全部分类" clearable filterable
            @change="onTopicChange" style="width:180px; margin-left:12px" size="small"
          >
            <el-option v-for="t in topics" :key="t" :label="t" :value="t" />
          </el-select>
        </div>

        <div v-if="loading" class="loading-area">
          <div class="skeleton-line skeleton-line--h2"></div>
          <div class="skeleton-line"></div>
          <div class="skeleton-line"></div>
          <div class="skeleton-line skeleton-line--short"></div>
        </div>

        <div v-else-if="question" class="question-area">
          <QuestionCard :question="question" :show-correct-answer="showCorrectAnswer" @update:answer="(v) => answer = v" />
          <ActionBar :answer="answer" :submitted="submitted" :show-ai-btn="showAiBtn" :loading="submitting" @submit="handleSubmit" @skip="handleSkip" @learned="handleLearned" @ai-analysis="handleAiAnalysis" />
          <SelfJudgePanel :visible="showSelfJudge" @judge="handleSelfJudge" />
          <NavigationControls v-if="mode !== 'random'" :current-index="sequentialIdx" :total="totalQuestions" @prev="loadQuestion('prev')" @next="loadQuestion('next')" />
        </div>

        <div v-else class="empty-area">
          <div class="empty-icon">📄</div>
          <p class="empty-text">题库为空</p>
          <p class="empty-hint">请先通过 PDF 导入添加题目</p>
        </div>
      </div>

      <div class="practice-sidebar">
        <ProgressSidebar :stats="stats" />
      </div>
    </div>

    <JudgeModeDialog :visible="showJudgeDialog" @choose="handleJudgeChoice" @close="showJudgeDialog = false" />
    <AiAnalysisPanel :analysis="aiAnalysisData" :visible="showAiAnalysis" @close="showAiAnalysis = false" />
    <SettingsModal :visible="showSettings" @close="showSettings = false" />
  </div>
</template>

<style scoped>
.practice { min-height: 100vh; background: #f8f9fb; }
.practice-topbar { display: flex; align-items: center; gap: 16px; padding: 0 24px; height: 48px; background: #fff; border-bottom: 1px solid #e5e7eb; }
.topbar-back { background: none; border: none; font-size: 13px; color: #6b7280; cursor: pointer; padding: 0; }
.topbar-back:hover { color: #1a1a1a; }
.topbar-logo { font-size: 15px; font-weight: 600; color: #1a1a1a; }
.topbar-nav { display: flex; gap: 4px; margin-left: 24px; }
.topbar-tab { padding: 6px 14px; border-radius: 4px; font-size: 13px; cursor: pointer; border: none; background: transparent; color: #6b7280; }
.topbar-tab:hover { color: #1a1a1a; }
.topbar-tab--active { background: #f3f4f6; color: #1a1a1a; font-weight: 500; }
.topbar-settings { margin-left: auto; width: 32px; height: 32px; border-radius: 50%; border: 1px solid #e5e7eb; background: #fff; font-size: 16px; cursor: pointer; display: flex; align-items: center; justify-content: center; color: #6b7280; }
.topbar-settings:hover { color: #1a1a1a; border-color: #9ca3af; }
.practice-body { display: flex; gap: 24px; max-width: 1100px; margin: 0 auto; padding: 24px; }
.practice-main { flex: 1; min-width: 0; }
.practice-sidebar { flex-shrink: 0; }
.top-bar { display: flex; align-items: center; margin-bottom: 24px; }
.question-area { }
.loading-area { max-width: 800px; margin: 40px auto; }
.skeleton-line { height: 14px; border-radius: 4px; background: #e5e7eb; margin-bottom: 14px; width: 100%; }
.skeleton-line--h2 { height: 22px; width: 40%; }
.skeleton-line--short { width: 60%; }
.empty-area { display: flex; flex-direction: column; align-items: center; justify-content: center; padding: 80px 40px; gap: 12px; }
.empty-icon { font-size: 48px; opacity: 0.3; }
.empty-text { font-size: 18px; color: #6b7280; margin: 0; }
.empty-hint { font-size: 13px; color: #9ca3af; margin: 0; }
</style>
