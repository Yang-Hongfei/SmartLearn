import client from './client'

const USE_MOCK = false

const mockPlan = {
  pdfName: 'Java基础题库',
  learningPath: [
    { knowledgePoint: { id: 'kp_java_syntax', name: 'Java 基本语法', description: '变量、数据类型与运算符', difficulty: 1, category: '基础语法' }, reason: '这是 Java 编程的起点，掌握基本语法后才能编写最简单的程序' },
    { knowledgePoint: { id: 'kp_oop_class', name: '类与对象', description: '面向对象编程的核心概念', difficulty: 2, category: '面向对象' }, reason: '理解类和对象的关系是后续所有面向对象概念的基础' },
    { knowledgePoint: { id: 'kp_oop_inherit', name: '继承与多态', description: '代码复用与接口设计', difficulty: 3, category: '面向对象' }, reason: '在前置知识类与对象的基础上，学习如何通过继承扩展已有代码' },
    { knowledgePoint: { id: 'kp_exception', name: '异常处理', description: 'try-catch-finally 与自定义异常', difficulty: 2, category: '异常处理' }, reason: '编写健壮的 Java 程序必须掌握异常处理机制' },
    { knowledgePoint: { id: 'kp_collections', name: '集合框架', description: 'List、Set、Map 及其实现类', difficulty: 3, category: '集合' }, reason: '集合是 Java 中最常用的数据结构，贯穿所有业务开发' },
  ],
}

const mockQuestions = [
  { id: 'q1', type: 'single_choice', content: '以下哪个不是 Java 的基本数据类型？', options: ['int', 'boolean', 'String', 'double'], correctAnswer: 'String', knowledgePointIds: ['kp_java_syntax'], difficulty: 1 },
  { id: 'q2', type: 'single_choice', content: '面向对象的三大特性不包括？', options: ['封装', '继承', '多态', '抽象'], correctAnswer: '抽象', knowledgePointIds: ['kp_oop_class'], difficulty: 2 },
  { id: 'q3', type: 'single_choice', content: '以下关于继承的说法，正确的是？', options: ['Java 支持多继承', '子类可以访问父类的 private 成员', 'super 关键字用于调用父类构造方法', 'final 类可以被继承'], correctAnswer: 'super 关键字用于调用父类构造方法', knowledgePointIds: ['kp_oop_inherit'], difficulty: 3 },
  { id: 'q4', type: 'true_false', content: 'finally 块中的代码一定会被执行。', options: ['正确', '错误'], correctAnswer: '正确', knowledgePointIds: ['kp_exception'], difficulty: 1 },
  { id: 'q5', type: 'single_choice', content: 'ArrayList 和 LinkedList 的主要区别是？', options: ['一个有序一个无序', '底层数据结构不同，ArrayList 基于数组，LinkedList 基于链表', '一个线程安全一个不安全', '没有区别'], correctAnswer: '底层数据结构不同，ArrayList 基于数组，LinkedList 基于链表', knowledgePointIds: ['kp_collections'], difficulty: 3 },
]

const mockProgressList = [
  { pdfImportId: '1', completedCount: 3, totalNodes: 5, updatedAt: '3天前' },
]

function mockResponse(data, delay = 500) {
  return new Promise(resolve => setTimeout(() => resolve(data), delay))
}

export const learnApi = {
  generatePlan(pdfImportId) {
    if (USE_MOCK) return mockResponse({ ...mockPlan, pdfImportId })
    return client.post('/learn/plan', { pdfImportId })
  },

  getProgress(pdfImportId) {
    if (USE_MOCK) return mockResponse({
      pdfName: mockPlan.pdfName,
      learningPath: mockPlan.learningPath,
      currentNodeIndex: 0,
      currentNodeState: 'explain',
      reflectionLog: [],
    })
    return client.get('/learn/progress', { params: { pdfImportId } }).catch(() => null)
  },

  listProgress() {
    if (USE_MOCK) return mockResponse(mockProgressList)
    return client.get('/learn/progress-list')
  },

  submitAnswer(data) {
    if (USE_MOCK) {
      const isCorrect = data.userAnswer === data.question.correctAnswer
      return mockResponse({
        isCorrect,
        reflectionSummary: isCorrect
          ? '回答正确，该知识点掌握良好。'
          : `正确答案是 ${data.question.correctAnswer}，建议回顾相关概念。`,
        conclusion: isCorrect ? 'forward' : 'reinforce',
        nextQuestion: isCorrect ? null : { ...data.question, id: data.question.id + 'b' },
      })
    }
    return client.post('/learn/submit', data)
  },

  markLearned(data) {
    if (USE_MOCK) {
      const idx = mockPlan.learningPath.findIndex(
        n => (n.knowledgePoint.id || n.id) === data.knowledgePointId
      )
      const q = mockQuestions[idx % mockQuestions.length]
      return mockResponse({ question: q })
    }
    return client.post('/learn/mark-learned', data)
  },

  deleteProgress(pdfImportId) {
    return client.delete(`/learn/progress/${pdfImportId}`)
  },

  generateTest(pdfImportId) {
    return client.post('/learn/generate-test', { pdfImportId })
  },

  evaluateTest(pdfImportId, answers, threshold = 0.7) {
    return client.post('/learn/evaluate-test', { pdfImportId, answers, threshold })
  },
}
