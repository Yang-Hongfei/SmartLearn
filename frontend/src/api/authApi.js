import client from './client'

export const authApi = {
  login(username, password) { return client.post('/auth/login', { username, password }) },
  register(username, password, nickname) { return client.post('/auth/register', { username, password, nickname }) },
  me() { return client.get('/auth/me') },
}

export function getToken() { return localStorage.getItem('sm_token') }
export function setToken(t) { localStorage.setItem('sm_token', t) }
export function removeToken() { localStorage.removeItem('sm_token'); localStorage.removeItem('sm_ds_key') }
export function isLoggedIn() { return !!getToken() }

export async function logout() {
  try { await client.delete('/config/api-key') } catch (e) { /* ignore */ }
  removeToken()
}
