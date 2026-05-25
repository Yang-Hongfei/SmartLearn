<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { pdfApi } from '../api/pdfApi'
import { learnApi } from '../api/learnApi'

const router = useRouter()
const imports = ref([])
const progressMap = ref({})
const uploading = ref(false)
const loading = ref(true)

const resumeList = computed(() =>
  imports.value.filter(p => progressMap.value[p.id])
)

const hasProgress = computed(() => resumeList.value.length > 0)

async function loadData() {
  loading.value = true
  try {
    const [impList, progList] = await Promise.all([
      pdfApi.imports({ userId: 1, page: 1, size: 100 }),
      learnApi.listProgress()
    ])
    imports.value = impList.records || impList.list || impList || []
    if (Array.isArray(progList)) {
      progressMap.value = {}
      progList.forEach(p => { progressMap.value[p.pdfImportId] = p })
    }
  } catch (e) {
    ElMessage.error(e.message)
  }
  loading.value = false
}

async function handleUpload(file) {
  uploading.value = true
  try {
    await pdfApi.upload(file)
    ElMessage.success('上传成功')
    await loadData()
  } catch (e) {
    ElMessage.error(e.message)
  }
  uploading.value = false
}

function handleSelect(pdf) {
  router.push(`/learn/session?pdfId=${pdf.id}`)
}

async function handleDelete(pdf, event) {
  event.stopPropagation()
  try {
    await ElMessageBox.confirm(`确定要删除「${pdf.filename}」的学习记录吗？题库不会删除。`, '删除学习记录', {
      confirmButtonText: '删除',
      cancelButtonText: '取消',
      type: 'warning',
    })
    await learnApi.deleteProgress(pdf.id)
    ElMessage.success('学习记录已删除')
    await loadData()
  } catch (e) {
    if (e !== 'cancel') ElMessage.error(e.message || '删除失败')
  }
}

function goBack() {
  router.push('/')
}

onMounted(loadData)
</script>

<template>
  <div class="hub">
    <div class="hub-inner">
      <div class="hub-top">
        <button class="back-link" @click="goBack">&larr; 返回首页</button>
        <span class="hub-title">AI 带学</span>
      </div>

      <div v-if="loading" class="hub-loading">
        <el-skeleton :rows="4" animated />
      </div>

      <template v-else>
        <section v-if="hasProgress" class="resume-section">
          <h2 class="section-heading">继续学习</h2>
          <div class="pdf-grid">
            <div
              v-for="pdf in resumeList" :key="pdf.id"
              class="pdf-card pdf-card--resume"
              @click="handleSelect(pdf)"
            >
              <button class="pdf-card-delete" @click="handleDelete(pdf, $event)" title="删除学习记录">&times;</button>
              <div class="pdf-card-name">{{ pdf.filename }}</div>
              <div class="pdf-card-meta">
                已学 {{ progressMap[pdf.id]?.completedCount || 0 }}/{{ progressMap[pdf.id]?.totalNodes || 0 }} 节点
              </div>
              <div class="pdf-card-time">{{ progressMap[pdf.id]?.updatedAt }}</div>
            </div>
          </div>
        </section>

        <section class="all-section">
          <h2 class="section-heading">{{ hasProgress ? '全部题库' : '选择题库开始学习' }}</h2>
          <div class="pdf-grid">
            <label class="pdf-card pdf-card--upload">
              <input
                type="file" accept=".pdf" style="display:none"
                @change="e => e.target.files[0] && handleUpload(e.target.files[0])"
              />
              <span class="upload-icon">+</span>
              <span class="upload-text">{{ uploading ? '上传中...' : '上传新题库' }}</span>
            </label>

            <div
              v-for="pdf in imports" :key="pdf.id"
              class="pdf-card"
              @click="handleSelect(pdf)"
            >
              <button
                v-if="progressMap[pdf.id]"
                class="pdf-card-delete"
                @click="handleDelete(pdf, $event)"
                title="删除学习记录"
              >&times;</button>
              <div class="pdf-card-name">{{ pdf.filename }}</div>
              <div class="pdf-card-meta" v-if="progressMap[pdf.id]">
                已学 {{ progressMap[pdf.id].completedCount }}/{{ progressMap[pdf.id].totalNodes }} 节点
              </div>
              <div class="pdf-card-meta pdf-card-meta--dim" v-else>未开始</div>
            </div>
          </div>

          <div v-if="imports.length === 0 && !uploading" class="empty-hint">
            还没有题库，上传第一份 PDF 开始 AI 带学
          </div>
        </section>
      </template>
    </div>
  </div>
</template>

<style scoped>
.hub {
  min-height: 100vh;
  background: #f8f9fb;
  padding: 40px;
}

.hub-inner {
  max-width: 720px;
  margin: 0 auto;
}

.hub-top {
  display: flex;
  align-items: center;
  gap: 20px;
  margin-bottom: 40px;
}

.back-link {
  background: none;
  border: none;
  font-size: 14px;
  color: #6b7280;
  cursor: pointer;
  padding: 0;
}
.back-link:hover { color: #1a1a1a; }

.hub-title {
  font-size: 20px;
  font-weight: 600;
  color: #1a1a1a;
}

.section-heading {
  font-size: 14px;
  font-weight: 500;
  color: #9ca3af;
  margin: 0 0 16px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.resume-section { margin-bottom: 40px; }

.pdf-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 12px;
}

.pdf-card {
  display: flex;
  flex-direction: column;
  gap: 6px;
  padding: 16px;
  border-radius: 8px;
  background: #fff;
  border: 1px solid #e5e7eb;
  cursor: pointer;
  text-align: left;
  font: inherit;
  color: inherit;
  transition: border-color 0.15s, box-shadow 0.15s;
  position: relative;
}
.pdf-card:hover {
  border-color: #9ca3af;
  box-shadow: 0 2px 8px rgba(0,0,0,0.06);
}

.pdf-card--resume {
  border-color: #d1d5db;
  background: #fafafa;
}

.pdf-card--upload {
  align-items: center;
  justify-content: center;
  border-style: dashed;
  border-color: #d1d5db;
  background: transparent;
  min-height: 96px;
  cursor: pointer;
}
.pdf-card--upload:hover { border-color: #9ca3af; background: #fafafa; }

.pdf-card-delete {
  position: absolute;
  top: 8px;
  right: 8px;
  width: 24px;
  height: 24px;
  border-radius: 4px;
  border: none;
  background: transparent;
  color: #9ca3af;
  font-size: 16px;
  cursor: pointer;
  display: none;
  align-items: center;
  justify-content: center;
  line-height: 1;
  transition: color 0.15s, background 0.15s;
}
.pdf-card:hover .pdf-card-delete { display: flex; }
.pdf-card-delete:hover { color: #e5534b; background: rgba(229,83,75,0.08); }

.pdf-card-name {
  font-size: 14px;
  font-weight: 500;
  color: #1a1a1a;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  padding-right: 20px;
}

.pdf-card-meta {
  font-size: 12px;
  color: #6b7280;
}
.pdf-card-meta--dim { color: #b0b7c3; }

.pdf-card-time {
  font-size: 11px;
  color: #9ca3af;
}

.upload-icon {
  font-size: 24px;
  color: #9ca3af;
  font-weight: 300;
}

.upload-text {
  font-size: 13px;
  color: #6b7280;
}

.empty-hint {
  text-align: center;
  color: #9ca3af;
  font-size: 14px;
  margin-top: 40px;
}

.hub-loading {
  max-width: 400px;
  margin: 40px auto;
}
</style>
