<script setup>
import { useGsapModal } from '../../composables/useGsapModal'

const props = defineProps({ result: Object, visible: Boolean })
const emit = defineEmits(['close'])

const { show, overlayRef, dialogRef } = useGsapModal(() => props.visible)
</script>

<template>
  <div v-if="show" ref="overlayRef" class="modal-overlay" @click.self="emit('close')">
    <div ref="dialogRef" class="modal">
      <div class="modal-header">
        <h3 class="modal-title">导入结果</h3>
        <button class="modal-close" @click="emit('close')">&times;</button>
      </div>
      <div v-if="result" class="modal-body">
        <div class="modal-row"><span class="modal-label">文件名</span><span>{{ result.filename }}</span></div>
        <div class="modal-row"><span class="modal-label">页数</span><span>{{ result.totalPages || '-' }}</span></div>
        <div class="modal-row"><span class="modal-label">提取题目数</span><span class="modal-num">{{ result.questionsExtracted || 0 }} 题</span></div>
        <div class="modal-row"><span class="modal-label">状态</span>
          <span class="modal-tag" :class="result.status === 'completed' ? 'modal-tag--ok' : 'modal-tag--fail'">
            {{ result.status === 'completed' ? '导入成功' : '导入失败' }}
          </span>
        </div>
        <div v-if="result.errorMessage" class="modal-error">{{ result.errorMessage }}</div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.modal-overlay { position: fixed; inset: 0; background: rgba(0,0,0,0.3); display: flex; align-items: center; justify-content: center; z-index: 1000; }
.modal { background: #fff; border: 1px solid #e5e7eb; border-radius: 10px; padding: 28px 32px; width: 420px; box-shadow: 0 4px 24px rgba(0,0,0,0.08); }
.modal-header { display: flex; align-items: center; justify-content: space-between; margin-bottom: 20px; }
.modal-title { font-size: 17px; font-weight: 600; color: #1a1a1a; margin: 0; }
.modal-close { background: none; border: none; font-size: 20px; color: #9ca3af; cursor: pointer; padding: 0; line-height: 1; }
.modal-close:hover { color: #4b5563; }
.modal-body { display: flex; flex-direction: column; gap: 12px; }
.modal-row { display: flex; justify-content: space-between; font-size: 14px; color: #374151; }
.modal-label { color: #6b7280; }
.modal-num { color: #4a9a2e; font-weight: 600; }
.modal-tag { font-size: 12px; padding: 2px 10px; border-radius: 3px; }
.modal-tag--ok { background: rgba(103,194,58,0.08); color: #4a9a2e; }
.modal-tag--fail { background: rgba(229,83,75,0.08); color: #e5534b; }
.modal-error { font-size: 13px; color: #e5534b; background: rgba(229,83,75,0.04); padding: 10px; border-radius: 6px; }
</style>
