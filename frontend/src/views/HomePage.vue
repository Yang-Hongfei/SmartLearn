<script setup>
import { ref, onMounted, onBeforeUnmount } from 'vue'
import { useRouter } from 'vue-router'
import SettingsModal from '../components/common/SettingsModal.vue'

const router = useRouter()
const showSettings = ref(false)

function onOpenSettings() { showSettings.value = true }
onMounted(() => window.addEventListener('open-settings', onOpenSettings))
onBeforeUnmount(() => window.removeEventListener('open-settings', onOpenSettings))
</script>

<template>
  <div class="home">
    <button class="home-settings" @click="showSettings = true" title="设置 API Key">&#9881;</button>
    <div class="home-content">
      <div class="brand">
        <h1 class="brand-name">SmartLearn</h1>
        <p class="brand-desc">基于知识图谱的 AI 深度学习平台</p>
      </div>
      <div class="cta-row">
        <button class="cta-btn cta-primary" @click="router.push('/practice')">智能刷题</button>
        <button class="cta-btn cta-secondary" @click="router.push('/learn-hub')">AI 带学</button>
      </div>
    </div>
    <SettingsModal :visible="showSettings" @close="showSettings = false" />
  </div>
</template>

<style scoped>
.home { min-height: 100vh; display: flex; align-items: center; justify-content: center; background: #f8f9fb; position: relative; }
.home-settings { position: fixed; top: 16px; right: 16px; width: 36px; height: 36px; border-radius: 50%; border: 1px solid #e5e7eb; background: #fff; font-size: 18px; cursor: pointer; display: flex; align-items: center; justify-content: center; color: #6b7280; transition: color 0.15s, border-color 0.15s; }
.home-settings:hover { color: #1a1a1a; border-color: #9ca3af; }
.home-content { text-align: center; max-width: 520px; padding: 60px 40px; }
.brand { margin-bottom: 48px; }
.brand-name { font-size: 36px; font-weight: 700; color: #1a1a1a; letter-spacing: -0.5px; margin: 0 0 12px; }
.brand-desc { font-size: 16px; color: #6b7280; margin: 0; font-weight: 400; }
.cta-row { display: flex; gap: 16px; justify-content: center; }
.cta-btn { padding: 12px 32px; border-radius: 8px; font-size: 15px; font-weight: 500; cursor: pointer; border: none; transition: background 0.15s, box-shadow 0.15s; min-width: 140px; }
.cta-primary { background: #1a1a1a; color: #fff; }
.cta-primary:hover { background: #333; box-shadow: 0 2px 12px rgba(0,0,0,0.12); }
.cta-secondary { background: #fff; color: #1a1a1a; border: 1px solid #d1d5db; }
.cta-secondary:hover { background: #f3f4f6; border-color: #9ca3af; }
</style>
