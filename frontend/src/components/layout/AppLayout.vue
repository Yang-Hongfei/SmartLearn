<script setup>
import { ref } from 'vue'
import { useRouter, useRoute } from 'vue-router'

const router = useRouter()
const route = useRoute()
const activeMenu = ref(route.path)
</script>

<template>
  <el-container class="app-layout">
    <el-header class="app-header">
      <div class="header-left">
        <span class="logo">📚 SmartLearn</span>
        <span class="subtitle">智能刷题平台</span>
      </div>
      <el-menu :default-active="activeMenu" mode="horizontal" @select="(key) => router.push(key)" class="header-menu">
        <el-menu-item index="/practice">
          <el-icon><Edit /></el-icon> 刷题练习
        </el-menu-item>
        <el-menu-item index="/import">
          <el-icon><Upload /></el-icon> PDF导入
        </el-menu-item>
      </el-menu>
    </el-header>
    <el-main>
      <slot />
    </el-main>
  </el-container>
</template>

<style scoped>
.app-layout { min-height: 100vh; background: #f5f7fa; }
.app-header {
  display: flex; align-items: center; justify-content: space-between;
  background: #fff; border-bottom: 1px solid #e4e7ed; padding: 0 24px;
}
.header-left { display: flex; align-items: center; gap: 12px; }
.logo { font-size: 20px; font-weight: bold; color: #409eff; }
.subtitle { font-size: 13px; color: #909399; }
.header-menu { border-bottom: none !important; }
</style>
