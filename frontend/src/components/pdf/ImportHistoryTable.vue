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
  } catch (e) { console.error(e) }
  loading.value = false
}

const handleDelete = async (id) => {
  try {
    await pdfApi.deleteImport(id)
    fetchData()
  } catch (e) { console.error(e) }
}

const statusType = (status) => {
  switch (status) {
    case 'completed': return 'success'
    case 'processing': return 'warning'
    case 'failed': return 'danger'
    default: return 'info'
  }
}
const statusText = (status) => {
  switch (status) {
    case 'completed': return '完成'
    case 'processing': return '处理中'
    case 'failed': return '失败'
    default: return '等待中'
  }
}

onMounted(fetchData)
defineExpose({ refresh: fetchData })
</script>

<template>
  <el-card shadow="hover" class="history-card">
    <template #header><strong>📋 导入历史</strong></template>
    <el-table :data="records" v-loading="loading" stripe>
      <el-table-column prop="id" label="ID" width="60" />
      <el-table-column prop="filename" label="文件名" min-width="200" show-overflow-tooltip />
      <el-table-column prop="totalPages" label="页数" width="80" />
      <el-table-column prop="questionsExtracted" label="提取题数" width="100" />
      <el-table-column prop="status" label="状态" width="100">
        <template #default="{ row }">
          <el-tag :type="statusType(row.status)">{{ statusText(row.status) }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="createdAt" label="时间" width="170">
        <template #default="{ row }">{{ row.createdAt?.substring(0, 16) }}</template>
      </el-table-column>
      <el-table-column label="操作" width="80">
        <template #default="{ row }">
          <el-popconfirm title="确定删除此导入及关联题目？" @confirm="handleDelete(row.id)">
            <template #reference>
              <el-button type="danger" size="small" :icon="'Delete'" circle />
            </template>
          </el-popconfirm>
        </template>
      </el-table-column>
    </el-table>
  </el-card>
</template>

<style scoped>
.history-card { margin-top: 24px; }
</style>
