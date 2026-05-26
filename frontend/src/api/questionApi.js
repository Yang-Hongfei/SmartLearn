import client from './client'

export const questionApi = {
  list(params = {}) {
    return client.get('/questions', { params })
  },
  getById(id) {
    return client.get(`/questions/${id}`)
  },
  random() {
    return client.get('/questions/random')
  },
  next(currentId, topic = '') {
    return client.get('/questions/next', { params: { currentId, topic } })
  },
  prev(currentId, topic = '') {
    return client.get('/questions/prev', { params: { currentId, topic } })
  },
  count() {
    return client.get('/questions/count')
  },
  topics() {
    return client.get('/questions/topics')
  },
  incorrect() {
    return client.get('/questions/incorrect')
  },
  delete(id) {
    return client.delete(`/questions/${id}`)
  }
}
