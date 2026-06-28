<template>
  <div class="images-page" @keydown="handleKeydown" tabindex="0">
    <div class="page-header">
      <div>
        <h1>🖼️ 图片管理</h1>
        <p>管理博客图片资源 (source/imgs, source/cover)</p>
      </div>
      <div style="display:flex;gap:8px;">
        <button class="btn btn-outline" @click="triggerUpload">{{ uploading ? '上传中...' : '📤 上传图片' }}</button>
        <input ref="fileInput" type="file" accept="image/*" multiple hidden @change="handleUpload" />
      </div>
    </div>

    <!-- 目录切换 -->
    <div class="tabs">
      <button v-for="d in dirs" :key="d" :class="['tab', { active: activeDir === d }]"
        @click="activeDir = d; page=1;">
        📁 {{ d }}
      </button>
    </div>

    <!-- 图片网格 -->
    <div v-if="images.length > 0" class="image-grid">
      <div v-for="(img, idx) in pagedImages" :key="img.path" class="image-card"
        @click="openPreview(img, idx)">
        <img :src="imageSrc(img.path)" :alt="img.name" loading="lazy" />
        <div class="image-info">
          <span class="image-name" :title="img.name">{{ img.name }}</span>
          <span class="image-size">{{ img.size_display }}</span>
        </div>
        <div class="image-actions">
          <button class="btn btn-sm btn-outline" @click.stop="copyPath(img.path)">📋 复制</button>
          <button class="btn btn-sm btn-outline" @click.stop="copyMd(img.path, img.name)">⬇️ MD</button>
          <button class="btn btn-sm btn-danger" @click.stop="confirmDelete(img)">🗑️</button>
        </div>
      </div>
    </div>

    <!-- 空状态 -->
    <div v-else-if="!loading" class="empty-state">
      <div class="icon">📭</div>
      <p>暂无图片，点击"上传图片"添加</p>
    </div>

    <!-- 分页 -->
    <div class="pagination" v-if="totalPages > 1">
      <button :disabled="page === 1" @click="page--">‹ 上一页</button>
      <span class="current">{{ page }} / {{ totalPages }}</span>
      <button :disabled="page === totalPages" @click="page++">下一页 ›</button>
    </div>

    <!-- 加载中 -->
    <div class="loading" v-if="loading">加载中...</div>

    <!-- ========== 图片预览灯箱 ========== -->
    <Teleport to="body">
      <Transition name="lightbox">
        <div v-if="preview" class="lightbox-overlay" @click.self="closePreview">
          <!-- 顶部工具栏 -->
          <div class="lightbox-toolbar">
            <span class="lightbox-counter">{{ previewIdx + 1 }} / {{ previewList.length }}</span>
            <span class="lightbox-name">{{ preview.name }}</span>
            <div class="lightbox-tools">
              <button class="lightbox-btn" @click="copyPath(preview.path)" title="复制 URL">📋</button>
              <button class="lightbox-btn" @click="copyMd(preview.path, preview.name)" title="复制 Markdown">⬇️</button>
              <button class="lightbox-btn" @click="toggleZoom" title="缩放">🔍</button>
              <button class="lightbox-btn" @click="closePreview" title="关闭">✕</button>
            </div>
          </div>

          <!-- 上一张 -->
          <button v-if="previewList.length > 1" class="lightbox-arrow left" @click.stop="prevImage">
            ‹
          </button>

          <!-- 图片 -->
          <div class="lightbox-body" @click.self="closePreview">
            <img :src="imageSrc(preview.path)" :alt="preview.name"
              :class="['lightbox-img', { zoomed: zoomed }]"
              @click.stop="toggleZoom" />
          </div>

          <!-- 下一张 -->
          <button v-if="previewList.length > 1" class="lightbox-arrow right" @click.stop="nextImage">
            ›
          </button>

          <!-- 底部信息 -->
          <div class="lightbox-info">
            <div>
              <strong>{{ preview.name }}</strong>
              <span>{{ preview.size_display }}</span>
            </div>
            <code>{{ preview.path }}</code>
          </div>
        </div>
      </Transition>
    </Teleport>

    <!-- 删除确认 -->
    <div v-if="deleteTarget" class="modal-overlay" @click.self="deleteTarget = null">
      <div class="modal-box">
        <h3>确认删除</h3>
        <p>确定要删除 <strong>{{ deleteTarget.name }}</strong> 吗？此操作不可恢复。</p>
        <div class="modal-actions">
          <button class="btn btn-outline" @click="deleteTarget = null">取消</button>
          <button class="btn btn-danger" @click="doDelete">确认删除</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
import { getImages, uploadImage, deleteImage, imageSrc } from '../api'
import { useToast } from '../composables/useToast'

const toast = useToast()
const dirs = ['imgs', 'cover', 'music', 'css']
const activeDir = ref('imgs')
const images = ref([])
const loading = ref(false)
const page = ref(1)
const pageSize = 20
const preview = ref(null)
const previewIdx = ref(0)
const zoomed = ref(false)
const deleteTarget = ref(null)
const uploading = ref(false)
const fileInput = ref(null)

const totalPages = computed(() => Math.ceil(images.value.length / pageSize))
const pagedImages = computed(() => {
  const s = (page.value - 1) * pageSize
  return images.value.slice(s, s + pageSize)
})
const previewList = computed(() => pagedImages.value)

function triggerUpload() { fileInput.value?.click() }

async function handleUpload(e) {
  const files = e.target.files
  if (!files.length) return
  uploading.value = true
  let ok = 0
  for (const file of files) {
    try { await uploadImage(file, activeDir.value); ok++ }
    catch { toast.error(`上传 ${file.name} 失败`) }
  }
  if (ok) toast.success(`成功上传 ${ok} 张图片`)
  uploading.value = false
  fileInput.value.value = ''
  fetchImages()
}

async function fetchImages() {
  loading.value = true
  try { const data = await getImages(activeDir.value); images.value = data.images }
  catch { images.value = [] }
  finally { loading.value = false }
}

// ========== 图片预览 ==========

function openPreview(img, idx) {
  preview.value = img
  previewIdx.value = idx
  zoomed.value = false
}

function closePreview() {
  preview.value = null
  zoomed.value = false
}

function prevImage() {
  const list = previewList.value
  previewIdx.value = (previewIdx.value - 1 + list.length) % list.length
  preview.value = list[previewIdx.value]
  zoomed.value = false
}

function nextImage() {
  const list = previewList.value
  previewIdx.value = (previewIdx.value + 1) % list.length
  preview.value = list[previewIdx.value]
  zoomed.value = false
}

function toggleZoom() { zoomed.value = !zoomed.value }

function handleKeydown(e) {
  if (!preview.value) return
  if (e.key === 'Escape') closePreview()
  if (e.key === 'ArrowLeft') prevImage()
  if (e.key === 'ArrowRight') nextImage()
}

function copyPath(path) {
  navigator.clipboard.writeText(path).then(() => toast.success('URL 已复制'))
    .catch(() => toast.error('复制失败'))
}

function copyMd(path, name) {
  const md = `![${name}](${path})`
  navigator.clipboard.writeText(md).then(() => toast.success('Markdown 已复制'))
    .catch(() => toast.error('复制失败'))
}

function confirmDelete(img) { deleteTarget.value = img }

async function doDelete() {
  if (!deleteTarget.value) return
  try {
    await deleteImage(deleteTarget.value.path)
    toast.success('图片已删除')
    deleteTarget.value = null
    fetchImages()
  } catch { toast.error('删除失败') }
}

watch(activeDir, () => { page.value = 1; fetchImages() })
onMounted(fetchImages)
</script>

<style scoped>
.tabs {
  display: flex;
  gap: 8px;
  margin-bottom: 20px;
}
.tab {
  padding: 8px 20px;
  border: 1px solid var(--border);
  background: var(--card-bg);
  border-radius: 8px;
  cursor: pointer;
  font-size: 14px;
  transition: all 0.15s;
}
.tab:hover { border-color: var(--primary); }
.tab.active { background: var(--primary); color: white; border-color: var(--primary); }

.image-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
  gap: 12px;
}

.image-card {
  background: var(--card-bg);
  border: 1px solid var(--border);
  border-radius: 10px;
  overflow: hidden;
  cursor: pointer;
  transition: all 0.15s;
}
.image-card:hover { box-shadow: 0 4px 12px rgba(0,0,0,0.1); transform: translateY(-2px); }
.image-card img {
  width: 100%;
  height: 130px;
  object-fit: cover;
}
.image-info {
  padding: 8px 10px 4px;
}
.image-name {
  display: block;
  font-size: 12px;
  font-weight: 500;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.image-size {
  font-size: 11px;
  color: var(--text-secondary);
}
.image-actions {
  display: flex;
  gap: 4px;
  padding: 0 10px 10px;
}

/* ========== 灯箱预览 ========== */

.lightbox-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.92);
  z-index: 3000;
  display: flex;
  flex-direction: column;
  user-select: none;
}

.lightbox-toolbar {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 12px 20px;
  color: #ccc;
  font-size: 14px;
  background: rgba(0, 0, 0, 0.4);
}

.lightbox-name {
  flex: 1;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.lightbox-tools { display: flex; gap: 4px; }

.lightbox-btn {
  background: rgba(255,255,255,0.1);
  border: none;
  color: #ddd;
  font-size: 18px;
  padding: 6px 10px;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.15s;
}
.lightbox-btn:hover { background: rgba(255,255,255,0.25); color: white; }

.lightbox-body {
  flex: 1;
  display: flex;
  justify-content: center;
  align-items: center;
  overflow: hidden;
  padding: 20px;
}

.lightbox-img {
  max-width: 100%;
  max-height: 100%;
  object-fit: contain;
  cursor: zoom-in;
  transition: transform 0.3s ease;
}
.lightbox-img.zoomed {
  cursor: zoom-out;
  transform: scale(1.8);
}

.lightbox-arrow {
  position: absolute;
  top: 50%;
  transform: translateY(-50%);
  background: rgba(255,255,255,0.08);
  border: none;
  color: white;
  font-size: 48px;
  padding: 20px 16px;
  cursor: pointer;
  transition: all 0.15s;
  line-height: 1;
}
.lightbox-arrow:hover { background: rgba(255,255,255,0.2); }
.lightbox-arrow.left { left: 0; border-radius: 0 8px 8px 0; }
.lightbox-arrow.right { right: 0; border-radius: 8px 0 0 8px; }

.lightbox-info {
  background: rgba(0,0,0,0.5);
  padding: 12px 20px;
  color: #aaa;
  font-size: 13px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 16px;
}
.lightbox-info strong { color: #ddd; }
.lightbox-info code {
  background: rgba(255,255,255,0.1);
  padding: 4px 10px;
  border-radius: 4px;
  font-size: 12px;
  color: #aaa;
}

/* 灯箱进出动画 */
.lightbox-enter-active { transition: opacity 0.2s ease; }
.lightbox-leave-active { transition: opacity 0.15s ease; }
.lightbox-enter-from,
.lightbox-leave-to { opacity: 0; }
</style>
