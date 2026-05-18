<script setup>
defineProps({ result: Object, visible: Boolean })
defineEmits(['close'])
</script>

<template>
  <el-dialog :modelValue="visible" title="导入结果" width="450px" @update:modelValue="emit('close')">
    <div v-if="result">
      <el-descriptions :column="1" border>
        <el-descriptions-item label="文件名">{{ result.filename }}</el-descriptions-item>
        <el-descriptions-item label="页数">{{ result.totalPages }}</el-descriptions-item>
        <el-descriptions-item label="提取题目数">
          <el-tag type="success">{{ result.questionsExtracted || 0 }} 题</el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="状态">
          <el-tag :type="result.status === 'completed' ? 'success' : 'danger'">
            {{ result.status === 'completed' ? '导入成功' : '导入失败' }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item v-if="result.errorMessage" label="错误信息">
          <span style="color:#f56c6c">{{ result.errorMessage }}</span>
        </el-descriptions-item>
      </el-descriptions>
    </div>
  </el-dialog>
</template>
