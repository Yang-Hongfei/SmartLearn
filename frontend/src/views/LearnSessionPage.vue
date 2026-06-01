<script setup>
import { ref, computed, onMounted, onBeforeUnmount, watch, nextTick } from 'vue'
import { useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import gsap from 'gsap'
import SettingsModal from '../components/common/SettingsModal.vue'
import SessionTopBar from '../components/learn/SessionTopBar.vue'
import ExplainView from '../components/learn/ExplainView.vue'
import QuizView from '../components/learn/QuizView.vue'
import PathTimeline from '../components/learn/PathTimeline.vue'
import ReflectionLog from '../components/learn/ReflectionLog.vue'
import { learnApi } from '../api/learnApi'

const route = useRoute()

const pdfId = ref(route.query.pdfId || '')
const pdfName = ref('')

// 'planning' | 'explain' | 'quiz' | 'reflecting' | 'done' | 'testing' | 'evaluating' | 'passed' | 'result'
const status = ref('planning')
const prevStatus = ref('')
const learningPath = ref([])
const currentNodeIndex = ref(0)
const currentNodeState = ref('explain')
const currentQuestion = ref(null)
const reflectionLog = ref([])

const loading = ref(false)
const reflectingStart = ref(0)
const reflectingElapsed = ref(0)
let reflectingTimer = null

// Test state
const testQuestions = ref([])
const testIndex = ref(0)
const testAnswers = ref([])
const testResult = ref(null)
const pendingAction = ref('')    // 'forward' | 'reinforce' | 'rollback'
const lastScore = ref(null)      // { score, level, summary, isCorrect }
const showSettings = ref(false)
const rollbackTargetId = ref('')
const PASS_THRESHOLD = 0.7

function onOpenSettings() { showSettings.value = true }
onMounted(() => window.addEventListener('open-settings', onOpenSettings))
onBeforeUnmount(() => window.removeEventListener('open-settings', onOpenSettings))

const currentNode = computed(() => learningPath.value[currentNodeIndex.value])
const totalNodes = computed(() => learningPath.value.length)
const testQuestion = computed(() => testQuestions.value[testIndex.value])

const explainKey = ref(0)
const quizKey = ref(0)
const testKey = ref(0)

// ---- Transition direction tracking ----
// Determine if the transition is "forward" or "backward" for animation
const forwardTransitions = new Set([
  'planning→explain', 'explain→quiz', 'quiz→reflecting',
  'reflecting→result', 'result→explain', 'result→quiz',
  'done→testing', 'testing→evaluating', 'evaluating→passed',
  'evaluating→done', 'quiz→result',
])

function getTransitionDirection(from, to) {
  if (forwardTransitions.has(`${from}→${to}`)) return 'forward'
  return 'backward'
}

// ---- GSAP transition hooks for session-main content ----
function onContentEnter(el, done) {
  const dir = getTransitionDirection(prevStatus.value, status.value)
  const yStart = dir === 'forward' ? 18 : -18
  gsap.fromTo(el, { opacity: 0, y: yStart }, {
    opacity: 1, y: 0, duration: 0.3, ease: 'power2.out',
    onComplete() {
      // After content enters, animate score counter if on result page
      if (status.value === 'result' && lastScore.value) {
        animateScoreCounter(el)
      }
      done()
    }
  })
}

function onContentLeave(el, done) {
  const dir = getTransitionDirection(prevStatus.value, status.value)
  const yEnd = dir === 'forward' ? -10 : 10
  gsap.to(el, { opacity: 0, y: yEnd, duration: 0.18, ease: 'power2.in', onComplete: done })
}

// ---- Score counter animation ----
function animateScoreCounter(el) {
  const pctEl = el.querySelector('.result-pct--anim')
  if (!pctEl || !lastScore.value) return
  const target = Math.round((lastScore.value.score || 0) * 100)
  gsap.fromTo(pctEl, { innerText: 0 }, {
    innerText: target,
    duration: 0.8,
    ease: 'power2.out',
    snap: { innerText: 1 },
    onUpdate() {
      // Force integer display
      const val = Math.round(parseFloat(pctEl.innerText) || 0)
      pctEl.innerText = val + '%'
    },
    onComplete() {
      pctEl.innerText = target + '%'
    }
  })
}

// ---- Content transition key ----
// Forces Vue Transition to re-fire on every status change
const contentKey = ref(0)
watch(status, (newVal, oldVal) => {
  if (oldVal) prevStatus.value = oldVal
  contentKey.value++
})

// ---- Status watchers ----
watch(status, (val) => {
  if (val === 'reflecting' || val === 'evaluating') {
    reflectingStart.value = Date.now()
    reflectingElapsed.value = 0
    reflectingTimer = setInterval(() => {
      reflectingElapsed.value = Math.floor((Date.now() - reflectingStart.value) / 1000)
    }, 1000)
  } else {
    if (reflectingTimer) { clearInterval(reflectingTimer); reflectingTimer = null }
  }
})

onBeforeUnmount(() => {
  if (reflectingTimer) clearInterval(reflectingTimer)
})

async function initSession() {
  loading.value = true
  status.value = 'planning'
  try {
    const prog = await learnApi.getProgress(pdfId.value)
    if (prog && prog.learningPath) {
      learningPath.value = prog.learningPath
      pdfName.value = prog.pdfName || ''
      currentNodeIndex.value = prog.currentNodeIndex || 0
      currentNodeState.value = prog.currentNodeState || 'explain'
      reflectionLog.value = prog.reflectionLog || []
      if (currentNodeState.value === 'quiz' && prog.currentQuestion) {
        currentQuestion.value = prog.currentQuestion
        status.value = 'quiz'
      } else if (currentNodeState.value === 'quiz') {
        status.value = 'planning'
        await handleLearned()
      } else {
        status.value = 'explain'
      }
      explainKey.value++
      quizKey.value++
    } else {
      const plan = await learnApi.generatePlan(pdfId.value)
      learningPath.value = plan.learningPath
      pdfName.value = plan.pdfName || ''
      status.value = 'explain'
      explainKey.value++
    }
  } catch (e) {
    ElMessage.error(e.message || '加载失败')
    status.value = 'done'
  }
  loading.value = false
}

async function handleLearned() {
  loading.value = true
  try {
    const result = await learnApi.markLearned({
      pdfImportId: pdfId.value,
      knowledgePointId: currentNode.value?.knowledgePoint?.id || currentNode.value?.id,
    })
    const question = result.question
    if (question && question.content && question.content.trim()) {
      currentQuestion.value = question
      currentNodeState.value = 'quiz'
      status.value = 'quiz'
      quizKey.value++
    } else {
      advanceToNext()
    }
  } catch (e) {
    ElMessage.error(e.message)
  }
  loading.value = false
}

async function handleSubmitAnswer({ answer }) {
  loading.value = true
  status.value = 'reflecting'
  try {
    const result = await learnApi.submitAnswer({
      pdfImportId: pdfId.value,
      knowledgePointId: currentNode.value?.knowledgePoint?.id || currentNode.value?.id,
      questionId: currentQuestion.value?.id,
      userAnswer: answer,
      question: currentQuestion.value,
    })

    reflectionLog.value.push({
      nodeId: currentNode.value?.knowledgePoint?.id || currentNode.value?.id,
      nodeName: currentNode.value?.knowledgePoint?.name || currentNode.value?.name,
      summary: result.reflectionSummary || '',
      conclusion: result.conclusion,
      score: result.score,
      level: result.level,
      timestamp: new Date().toISOString(),
    })

    lastScore.value = {
      score: result.score,
      level: result.level,
      summary: result.reflectionSummary,
      isCorrect: result.isCorrect,
    }
    pendingAction.value = result.conclusion
    status.value = 'result'
  } catch (e) {
    ElMessage.error(e.message || '分析请求失败，请重试')
    status.value = 'quiz'
    quizKey.value++
  }
  loading.value = false
}

async function continueAfterResult() {
  const action = pendingAction.value
  lastScore.value = null
  pendingAction.value = ''

  if (action === 'forward') {
    advanceToNext()
  } else if (action === 'reinforce') {
    await handleLearned()
  } else if (action === 'rollback') {
    const targetIdx = learningPath.value.findIndex(
      n => (n.knowledgePoint?.id || n.id) === result.rollbackToNodeId
    )
    if (targetIdx >= 0) currentNodeIndex.value = targetIdx
    currentNodeState.value = 'explain'
    currentQuestion.value = null
    status.value = 'explain'
    explainKey.value++
  }
}

function advanceToNext() {
  if (currentNodeIndex.value < learningPath.value.length - 1) {
    currentNodeIndex.value++
    currentNodeState.value = 'explain'
    currentQuestion.value = null
    status.value = 'explain'
    explainKey.value++
  } else {
    status.value = 'done'
  }
}

// ---- Test flow ----

async function startTest() {
  loading.value = true
  status.value = 'planning'
  try {
    const result = await learnApi.generateTest(pdfId.value)
    testQuestions.value = result.testQuestions || []
    if (testQuestions.value.length === 0) {
      ElMessage.info('题库中没有更多题目可测试')
      status.value = 'done'
      loading.value = false
      return
    }
    testIndex.value = 0
    testAnswers.value = []
    testResult.value = null
    status.value = 'testing'
    testKey.value++
  } catch (e) {
    ElMessage.error(e.message || '生成测试失败')
    status.value = 'done'
  }
  loading.value = false
}

function handleTestSubmit({ answer }) {
  testAnswers.value.push({
    questionId: testQuestion.value?.id,
    question: testQuestion.value?.content,
    userAnswer: answer,
    correctAnswer: testQuestion.value?.correctAnswer,
  })

  if (testIndex.value < testQuestions.value.length - 1) {
    testIndex.value++
    testKey.value++
  } else {
    evaluateTest()
  }
}

async function evaluateTest() {
  loading.value = true
  status.value = 'evaluating'
  try {
    const result = await learnApi.evaluateTest(pdfId.value, testAnswers.value, PASS_THRESHOLD)
    testResult.value = result

    if (result.passed) {
      status.value = 'passed'
    } else {
      if (result.newLearningPath && result.newLearningPath.length > 0) {
        learningPath.value = result.newLearningPath
        currentNodeIndex.value = 0
        currentNodeState.value = 'explain'
        reflectionLog.value = []
        testQuestions.value = []
        testAnswers.value = []
        status.value = 'explain'
        explainKey.value++
      } else {
        status.value = 'done'
      }
    }
  } catch (e) {
    ElMessage.error(e.message || '评估失败')
    status.value = 'done'
  }
  loading.value = false
}

onMounted(initSession)
</script>

<template>
  <div class="session">
    <SessionTopBar
      :pdf-name="pdfName"
      :current-node="status === 'testing' ? testIndex + 1 : currentNodeIndex + 1"
      :total-nodes="status === 'testing' ? testQuestions.length : totalNodes"
      @skip-to-test="startTest"
    />

    <div class="session-body">
      <div class="session-main">
        <Transition mode="out-in" @enter="onContentEnter" @leave="onContentLeave" appear>
          <div :key="contentKey" class="session-content-wrap">
            <!-- Planning -->
            <ExplainView v-if="status === 'planning'" :key="'plan'" :loading="true" />

            <!-- Explain -->
            <ExplainView
              v-else-if="status === 'explain'"
              :key="'explain-' + explainKey"
              :content="currentNode?.explanation || ''"
              :knowledge-point-name="currentNode?.knowledgePoint?.name || currentNode?.name || ''"
              :reason="currentNode?.reason || ''"
              :loading="loading"
              @learned="handleLearned"
            />

            <!-- Quiz -->
            <QuizView
              v-else-if="status === 'quiz'"
              :key="'quiz-' + quizKey"
              :question="currentQuestion"
              :loading="loading"
              @submit="handleSubmitAnswer"
            />

            <!-- Test question -->
            <div v-else-if="status === 'testing'" class="test-area">
              <div class="test-header">
                <span class="test-label">综合测试</span>
                <span class="test-progress">{{ testIndex + 1 }} / {{ testQuestions.length }}</span>
              </div>
              <QuizView
                :key="'test-' + testKey"
                :question="testQuestion"
                @submit="handleTestSubmit"
              />
            </div>

            <!-- Reflecting / Evaluating -->
            <div v-else-if="status === 'reflecting' || status === 'evaluating'" class="session-reflecting">
              <div class="reflecting-indicator"><div class="reflecting-bar"></div></div>
              <p class="reflecting-text">{{ status === 'evaluating' ? 'AI 正在评估综合测试...' : 'AI 正在分析你的答案...' }}</p>
              <p class="reflecting-elapsed" v-if="reflectingElapsed > 1">{{ reflectingElapsed }}s</p>
              <p class="reflecting-hint">答对即时返回，答错需要 AI 深度分析（通常 5-15 秒）</p>
            </div>

            <!-- Result: show score + analysis, let user decide next step -->
            <div v-else-if="status === 'result'" class="session-result">
              <div class="result-card">
                <div class="result-score" :class="{
                  'result-score--high': lastScore?.score >= 0.85,
                  'result-score--mid': lastScore?.score >= 0.5 && lastScore?.score < 0.85,
                  'result-score--low': lastScore?.score < 0.5,
                }">
                  <span class="result-pct result-pct--anim">0%</span>
                  <span class="result-level">{{ lastScore?.level }}</span>
                </div>
                <p class="result-summary">{{ lastScore?.summary }}</p>
                <div class="result-actions">
                  <button v-if="pendingAction === 'forward'" class="result-btn result-btn--forward" @click="continueAfterResult">
                    下一知识点
                  </button>
                  <button v-else-if="pendingAction === 'reinforce'" class="result-btn result-btn--reinforce" @click="continueAfterResult">
                    再来一题巩固
                  </button>
                  <button v-else-if="pendingAction === 'rollback'" class="result-btn result-btn--rollback" @click="continueAfterResult">
                    回顾基础知识
                  </button>
                </div>
              </div>
            </div>

            <!-- Done: all nodes completed -->
            <div v-else-if="status === 'done'" class="session-done">
              <h2 class="done-title">本阶段学习完成</h2>
              <p class="done-desc">你已完成 {{ totalNodes }} 个知识点的学习。</p>
              <button class="test-btn" @click="startTest">开始综合测试</button>
              <router-link to="/learn-hub" class="done-link">返回题库</router-link>
            </div>

            <!-- Passed: test passed -->
            <div v-else-if="status === 'passed'" class="session-done">
              <h2 class="done-title">恭喜！综合测试通过</h2>
              <p class="done-desc">
                掌握度 {{ Math.round((testResult?.mastery || 0) * 100) }}%，
                {{ testResult?.passed ? '已达到' : '未达到' }} {{ Math.round(PASS_THRESHOLD * 100) }}% 的通过线。
              </p>
              <div class="test-summary" v-if="testResult">
                <div class="test-mastery" :class="testResult.mastery >= PASS_THRESHOLD ? 'mastery--pass' : 'mastery--fail'">
                  {{ Math.round(testResult.mastery * 100) }}%
                </div>
                <div class="test-weak" v-if="testResult.weakPoints?.length">
                  <span class="test-weak-label">薄弱知识点：</span>
                  {{ testResult.weakPoints.join('、') }}
                </div>
              </div>
              <router-link to="/learn-hub" class="done-link">返回题库</router-link>
            </div>
          </div>
        </Transition>
      </div>

      <div class="session-sidebar">
        <PathTimeline :nodes="learningPath" :current-node-index="currentNodeIndex" />
        <ReflectionLog :entries="reflectionLog" />
      </div>
    </div>
    <SettingsModal :visible="showSettings" @close="showSettings = false" />
  </div>
</template>

<style scoped>
.session {
  min-height: 100vh;
  background: #141518;
  display: flex;
  flex-direction: column;
}
.session-body { flex: 1; display: flex; overflow: hidden; }
.session-main {
  flex: 7; overflow-y: auto; display: flex; justify-content: center; padding: 40px 0;
}
.session-content-wrap {
  width: 100%;
  max-width: 720px;
  display: flex;
  justify-content: center;
}
.session-content-wrap > * { width: 100%; }
.session-sidebar {
  flex: 3; border-left: 1px solid rgba(255,255,255,0.06); overflow-y: auto;
  display: flex; flex-direction: column; min-width: 260px; max-width: 340px;
}

/* Test */
.test-area { padding: 24px 0; }
.test-header {
  display: flex; align-items: center; justify-content: space-between;
  padding: 0 40px; margin-bottom: 8px;
}
.test-label { font-size: 14px; font-weight: 600; color: rgba(255,255,255,0.7); }
.test-progress { font-size: 13px; color: rgba(255,255,255,0.3); }

/* Reflecting */
.session-reflecting {
  display: flex; flex-direction: column; align-items: center; justify-content: center;
  gap: 12px; padding: 80px 40px;
}
.reflecting-indicator { width: 200px; height: 3px; background: rgba(255,255,255,0.06); border-radius: 2px; overflow: hidden; margin-bottom: 8px; }
.reflecting-bar { height: 100%; width: 30%; background: rgba(107,159,255,0.5); border-radius: 2px; animation: reflecting-slide 1.2s ease-in-out infinite; }
@keyframes reflecting-slide { 0% { transform: translateX(-30%); } 100% { transform: translateX(330%); } }
.reflecting-text { font-size: 15px; color: rgba(255,255,255,0.5); margin: 0; }
.reflecting-elapsed { font-size: 13px; color: rgba(255,255,255,0.25); margin: 0; font-variant-numeric: tabular-nums; }
.reflecting-hint { font-size: 12px; color: rgba(255,255,255,0.15); margin: 8px 0 0; }

/* Done */
.session-done {
  display: flex; flex-direction: column; align-items: center; justify-content: center;
  gap: 12px; padding: 80px 40px; text-align: center;
}
.done-title { font-size: 22px; font-weight: 600; color: rgba(255,255,255,0.85); margin: 0; }
.done-desc { font-size: 14px; color: rgba(255,255,255,0.4); margin: 0; line-height: 1.6; }

.test-btn {
  padding: 10px 32px; border-radius: 6px; font-size: 15px; font-weight: 500;
  cursor: pointer; border: 1px solid rgba(107,159,255,0.3);
  background: rgba(107,159,255,0.1); color: #6b9fff;
  transition: background 0.15s, border-color 0.15s; margin-bottom: 8px;
}
.test-btn:hover { background: rgba(107,159,255,0.18); border-color: rgba(107,159,255,0.5); }

.done-link {
  font-size: 13px; color: rgba(255,255,255,0.3); text-decoration: none;
  padding: 6px 16px; border-radius: 4px;
  border: 1px solid rgba(255,255,255,0.08); transition: background 0.15s;
}
.done-link:hover { background: rgba(255,255,255,0.05); }

/* Test result */
.test-summary { margin: 8px 0; }
.test-mastery { font-size: 36px; font-weight: 700; font-variant-numeric: tabular-nums; }
.mastery--pass { color: rgba(107,159,255,0.8); }
.mastery--fail { color: rgba(255,193,7,0.7); }
.test-weak { font-size: 13px; color: rgba(255,255,255,0.35); margin-top: 8px; }
.test-weak-label { color: rgba(255,255,255,0.25); }

/* Result card */
.session-result {
  display: flex; align-items: flex-start; justify-content: center;
  padding: 60px 0;
}
.result-card {
  display: flex; flex-direction: column; align-items: center; gap: 20px;
  padding: 40px 48px; border-radius: 12px;
  background: rgba(255,255,255,0.04); border: 1px solid rgba(255,255,255,0.06);
  max-width: 440px; width: 100%;
}
.result-score {
  display: flex; flex-direction: column; align-items: center; gap: 4px;
}
.result-pct { font-size: 48px; font-weight: 700; font-variant-numeric: tabular-nums; line-height: 1; }
.result-score--high .result-pct { color: rgba(107,159,255,0.9); }
.result-score--mid  .result-pct { color: rgba(255,193,7,0.8); }
.result-score--low  .result-pct { color: rgba(255,107,107,0.8); }
.result-level { font-size: 14px; font-weight: 500; color: rgba(255,255,255,0.5); }
.result-summary {
  font-size: 14px; color: rgba(255,255,255,0.5); line-height: 1.7;
  text-align: center; margin: 0;
}
.result-actions { display: flex; gap: 12px; margin-top: 8px; }
.result-btn {
  padding: 10px 28px; border-radius: 6px; font-size: 14px; font-weight: 500;
  cursor: pointer; border: none; transition: background 0.15s;
}
.result-btn--forward { background: rgba(107,159,255,0.15); color: #6b9fff; }
.result-btn--forward:hover { background: rgba(107,159,255,0.25); }
.result-btn--reinforce { background: rgba(255,193,7,0.12); color: rgba(255,193,7,0.85); }
.result-btn--reinforce:hover { background: rgba(255,193,7,0.2); }
.result-btn--rollback { background: rgba(255,107,107,0.1); color: rgba(255,107,107,0.8); }
.result-btn--rollback:hover { background: rgba(255,107,107,0.18); }
</style>
