<script setup>
import { ref, onMounted } from 'vue'
import { pdfApi } from '../../api/pdfApi.js'

const records = ref([])
const loading = ref(false)
const total = ref(0)
const page = ref(1)

const fetchData = async () => {
  loading.value = true
  try {
    const result = await pdfApi.imports({ page: page.value, size: 10 })
    records.value = result.records
    total.value = result.total
  } catch (e) { /* ignore */ }
  loading.value = false
}

const handleDelete = async (id) => {
  try { await pdfApi.deleteImport(id); fetchData() } catch (e) { /* ignore */ }
}

const statusText = (s) => ({ completed: '完成', processing: '处理中', failed: '失败' }[s] || '等待中')

onMounted(fetchData)
defineExpose({ refresh: fetchData })
</script>

<template>
  <div class="history">
    <div class="history-heading">导入历史</div>
    <div class="history-table" v-loading="loading">
      <div class="ht-row ht-row--head">
        <span class="ht-cell ht-cell--id">ID</span>
        <span class="ht-cell ht-cell--name">文件名</span>
        <span class="ht-cell ht-cell--pages">页数</span>
        <span class="ht-cell ht-cell--count">提取题数</span>
        <span class="ht-cell ht-cell--status">状态</span>
        <span class="ht-cell ht-cell--time">时间</span>
        <span class="ht-cell ht-cell--action">操作</span>
      </div>
      <div v-for="r in records" :key="r.id" class="ht-row">
        <span class="ht-cell ht-cell--id">{{ r.id }}</span>
        <span class="ht-cell ht-cell--name" :title="r.filename">{{ r.filename }}</span>
        <span class="ht-cell ht-cell--pages">{{ r.totalPages || '-' }}</span>
        <span class="ht-cell ht-cell--count">{{ r.questionsExtracted || 0 }}</span>
        <span class="ht-cell ht-cell--status">
          <span class="ht-tag" :class="'ht-tag--' + r.status">{{ statusText(r.status) }}</span>
        </span>
        <span class="ht-cell ht-cell--time">{{ (r.createdAt || '').substring(0, 16) }}</span>
        <span class="ht-cell ht-cell--action">
          <button class="ht-del" @click="handleDelete(r.id)">删除</button>
        </span>
      </div>
    </div>
    <div v-if="records.length === 0 && !loading" class="history-empty">暂无导入记录</div>
  </div>
</template>

<style scoped>
.history { }
.history-heading { font-size: 14px; font-weight: 600; color: #1a1a1a; margin-bottom: 12px; }
.history-table { background: #fff; border: 1px solid #e5e7eb; border-radius: 8px; overflow: hidden; }
.ht-row { display: flex; align-items: center; padding: 0 16px; height: 44px; font-size: 13px; border-bottom: 1px solid #f3f4f6; }
.ht-row:last-child { border-bottom: none; }
.ht-row--head { background: #f8f9fb; font-weight: 500; color: #6b7280; font-size: 12px; }
.ht-cell { flex-shrink: 0; color: #374151; }
.ht-cell--id { width: 50px; }
.ht-cell--name { flex: 1; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; min-width: 0; }
.ht-cell--pages { width: 60px; text-align: center; }
.ht-cell--count { width: 80px; text-align: center; }
.ht-cell--status { width: 80px; text-align: center; }
.ht-cell--time { width: 140px; color: #9ca3af; font-size: 12px; }
.ht-cell--action { width: 60px; text-align: center; }
.ht-tag { font-size: 11px; padding: 2px 8px; border-radius: 3px; }
.ht-tag--completed { background: rgba(103,194,58,0.08); color: #4a9a2e; }
.ht-tag--processing { background: rgba(212,160,23,0.08); color: #b8860b; }
.ht-tag--failed { background: rgba(229,83,75,0.08); color: #e5534b; }
.ht-tag--pending { background: #f3f4f6; color: #9ca3af; }
.ht-del { background: none; border: none; font-size: 12px; color: #e5534b; cursor: pointer; padding: 0; }
.ht-del:hover { text-decoration: underline; }
.history-empty { text-align: center; padding: 32px; color: #9ca3af; font-size: 13px; }
</style>
