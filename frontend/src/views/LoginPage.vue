<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { authApi, setToken } from '../api/authApi'

const router = useRouter()
const username = ref('')
const password = ref('')
const loading = ref(false)
const isRegister = ref(false)
const nickname = ref('')

async function submit() {
  if (!username.value.trim() || !password.value.trim()) return
  loading.value = true
  try {
    if (isRegister.value) {
      const res = await authApi.register(username.value.trim(), password.value, nickname.value.trim() || username.value.trim())
      setToken(res.token)
      ElMessage.success('注册成功')
    } else {
      const res = await authApi.login(username.value.trim(), password.value)
      setToken(res.token)
    }
    router.push('/')
  } catch (e) {
    ElMessage.error(e.message || '操作失败')
  }
  loading.value = false
}
</script>

<template>
  <div class="login">
    <div class="login-card">
      <h1 class="login-title">SmartLearn</h1>
      <p class="login-sub">{{ isRegister ? '创建账号' : '登录以继续' }}</p>

      <div class="login-field">
        <input v-model="username" class="login-input" placeholder="用户名" @keyup.enter="submit" />
      </div>
      <div class="login-field" v-if="isRegister">
        <input v-model="nickname" class="login-input" placeholder="昵称（选填）" @keyup.enter="submit" />
      </div>
      <div class="login-field">
        <input v-model="password" type="password" class="login-input" placeholder="密码" @keyup.enter="submit" />
      </div>

      <button class="login-btn" :disabled="loading" @click="submit">
        {{ loading ? '处理中...' : (isRegister ? '注册' : '登录') }}
      </button>

      <p class="login-toggle">
        {{ isRegister ? '已有账号？' : '没有账号？' }}
        <a href="#" @click.prevent="isRegister = !isRegister">{{ isRegister ? '去登录' : '去注册' }}</a>
      </p>
    </div>
  </div>
</template>

<style scoped>
.login { min-height: 100vh; display: flex; align-items: center; justify-content: center; background: #f8f9fb; }
.login-card { width: 360px; padding: 40px; text-align: center; }
.login-title { font-size: 28px; font-weight: 700; color: #1a1a1a; margin: 0 0 8px; }
.login-sub { font-size: 14px; color: #6b7280; margin: 0 0 28px; }
.login-field { margin-bottom: 14px; }
.login-input { width: 100%; padding: 10px 14px; border-radius: 6px; border: 1px solid #e5e7eb; font: inherit; font-size: 14px; outline: none; color: #1a1a1a; box-sizing: border-box; }
.login-input:focus { border-color: #4b7fd9; }
.login-btn { width: 100%; padding: 10px; border-radius: 6px; font-size: 15px; font-weight: 500; cursor: pointer; border: none; background: #1a1a1a; color: #fff; margin-top: 6px; }
.login-btn:disabled { opacity: 0.5; cursor: not-allowed; }
.login-toggle { font-size: 13px; color: #9ca3af; margin: 20px 0 0; }
.login-toggle a { color: #4b7fd9; text-decoration: none; }
</style>
