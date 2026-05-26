import client from './client'

export const practiceApi = {
  submit(data) {
    return client.post('/practice/submit', data)
  },
  selfJudge(recordId, isCorrect) {
    return client.put(`/practice/${recordId}/self-judge`, { isCorrect })
  },
  updateStatus(recordId, status) {
    return client.put(`/practice/${recordId}/status`, { status })
  },
  records(params) {
    return client.get('/practice/records', { params })
  },
  stats() {
    return client.get('/practice/stats')
  },
  aiAnalysis(recordId) {
    return client.post(`/practice/${recordId}/ai-analysis`)
  }
}
