import client from './client'

export const configApi = {
  getApiKeyStatus() {
    return client.get('/config/api-key')
  },
  setApiKey(apiKey) {
    return client.post('/config/api-key', { apiKey })
  },
  clearApiKey() {
    return client.delete('/config/api-key')
  },
}
