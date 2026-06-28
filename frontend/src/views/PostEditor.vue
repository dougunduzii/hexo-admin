<template>
  <div class="post-editor">
    <div class="page-header">
      <div>
        <h1>{{ isEdit ? '✏️ 编辑文章' : '✏️ 新建文章' }}</h1>
        <p v-if="isEdit">编辑已有文章，修改后保存即可</p>
        <p v-else>创建一篇新的博客文章</p>
      </div>
      <div style="display: flex; gap: 8px;">
        <button class="btn btn-outline" @click="togglePreview" v-if="!saving">
          {{ showPreview ? '📝 编辑' : '👁️ 预览' }}
        </button>
        <button class="btn btn-primary" @click="handleSave" :disabled="saving">
          {{ saving ? '保存中...' : '💾 保存' }}
        </button>
      </div>
    </div>

    <!-- 加载中 -->
    <div v-if="loadingPost" class="loading">加载文章内容...</div>

    <!-- 编辑模式 -->
    <div v-else-if="!showPreview">
      <div class="card">
        <div class="form-group">
          <label>标题 *</label>
          <input
            v-model="form.title"
            type="text"
            placeholder="输入文章标题"
          />
        </div>
      </div>

      <div class="editor-grid">
        <!-- 左侧：元数据 -->
        <div class="card meta-panel">
          <h3 style="margin-bottom: 16px;">文章属性</h3>

          <div class="form-group">
            <label>日期</label>
            <input v-model="form.date" type="date" />
          </div>

          <div class="form-group">
            <label>分类</label>
            <input
              v-model="form.categories"
              type="text"
              placeholder="多个分类用英文逗号分隔，如: 前端, Vue"
            />
            <div class="form-hint">多个分类用逗号分隔。Hexo 支持层级分类: 父分类, 子分类</div>
          </div>

          <div class="form-group">
            <label>标签</label>
            <input
              v-model="form.tags"
              type="text"
              placeholder="多个标签用英文逗号分隔，如: Vue, JavaScript"
            />
            <div class="form-hint">多个标签用逗号分隔</div>
          </div>

          <div class="form-group">
            <label>摘要</label>
            <textarea
              v-model="form.summary"
              rows="3"
              placeholder="文章摘要（可选）"
            ></textarea>
          </div>

          <div v-if="isEdit" class="form-group">
            <label>文件名</label>
            <input :value="postFilename" type="text" disabled
              style="opacity: 0.6; cursor: not-allowed;" />
          </div>
        </div>

        <!-- 右侧：Markdown 编辑区 -->
        <div class="card editor-panel">
          <div class="form-group" style="height: 100%; display: flex; flex-direction: column;">
            <label>正文（Markdown 格式）</label>
            <!-- 编辑工具栏 -->
            <div class="editor-toolbar">
              <button type="button" class="tb-btn" @click="insertMd('**粗体**')" title="粗体"><b>B</b></button>
              <button type="button" class="tb-btn" @click="insertMd('*斜体*')" title="斜体"><i>I</i></button>
              <button type="button" class="tb-btn" @click="insertMd('`代码`')" title="行内代码">&lt;/&gt;</button>
              <button type="button" class="tb-btn" @click="insertMd('[链接](url)')" title="链接">🔗</button>
              <button type="button" class="tb-btn" @click="insertMd('\n```\n\n```\n')" title="代码块">📋</button>
              <span class="tb-sep"></span>
              <button type="button" class="tb-btn tb-primary" @click="showImageInserter = !showImageInserter" title="插入图片">
                🖼️ 插入图片
              </button>
            </div>
            <textarea
              ref="contentArea"
              v-model="form.content"
              placeholder="在此编写 Markdown 内容...

# 标题
段落内容...

![图片描述](./imgs/example.png)"
              class="md-editor"
            ></textarea>
          </div>

          <!-- 图片插入面板 -->
          <Transition name="slide">
            <div v-if="showImageInserter" class="image-inserter">
              <div class="inserter-header">
                <span>选择图片插入</span>
                <div class="inserter-tabs">
                  <button v-for="d in ['imgs', 'cover']" :key="d"
                    :class="['btn btn-sm', inserterDir === d ? 'btn-primary' : 'btn-outline']"
                    @click="loadInserterImages(d)">{{ d }}</button>
                </div>
              </div>
              <div class="inserter-grid">
                <div v-for="img in inserterImages" :key="img.path" class="inserter-item"
                  @click="insertImage(img)">
                  <img :src="imageSrc(img.path)" :alt="img.name" />
                  <span>{{ img.name }}</span>
                </div>
                <div v-if="inserterImages.length === 0" style="padding:20px;color:var(--text-secondary);text-align:center;grid-column:1/-1;">
                  加载中...
                </div>
              </div>
            </div>
          </Transition>
        </div>
      </div>
    </div>

    <!-- 预览模式 -->
    <div v-else-if="showPreview" class="card">
      <div class="card-header">
        <h2>👁️ 预览: {{ form.title || '(无标题)' }}</h2>
      </div>
      <div class="post-meta-preview">
        <span v-if="form.date">📅 {{ form.date }}</span>
        <span v-if="form.categories">📂 {{ form.categories }}</span>
        <span v-if="form.tags">🏷️ {{ form.tags }}</span>
      </div>
      <div class="markdown-preview" v-html="renderedContent"></div>
    </div>

    <!-- 底部操作栏 -->
    <div class="editor-footer" v-if="!showPreview">
      <button class="btn btn-outline" @click="goBack">取消</button>
      <button class="btn btn-primary btn-lg" @click="handleSave" :disabled="saving">
        {{ saving ? '保存中...' : '💾 保存文章' }}
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { getPost, createPost, updatePost, getImages, imageSrc } from '../api'
import { marked } from 'marked'
import DOMPurify from 'dompurify'
import { useToast } from '../composables/useToast'

const route = useRoute()
const router = useRouter()
const toast = useToast()

const isEdit = computed(() => !!route.params.id)
const postId = computed(() => route.params.id)

const form = ref({
  title: '',
  date: new Date().toISOString().slice(0, 10),
  categories: '',
  tags: '',
  summary: '',
  content: '',
})

const postFilename = ref('')
const saving = ref(false)
const loadingPost = ref(false)
const showPreview = ref(false)
const showImageInserter = ref(false)
const contentArea = ref(null)

// 图片插入面板
const inserterDir = ref('imgs')
const inserterImages = ref([])

// 配置 marked 安全选项
marked.setOptions({
  breaks: true,
  gfm: true,
})

// Markdown 渲染（经过 XSS 净化）
const renderedContent = computed(() => {
  if (!form.value.content) return '<p style="color:#999">暂无内容</p>'
  try {
    const raw = marked.parse(form.value.content)
    return DOMPurify.sanitize(raw)
  } catch {
    return '<p style="color:red">Markdown 解析错误</p>'
  }
})

function togglePreview() {
  showPreview.value = !showPreview.value
}

async function fetchPost() {
  if (!isEdit.value) return
  loadingPost.value = true
  try {
    const data = await getPost(Number(postId.value))
    form.value = {
      title: data.title || '',
      date: (data.date || '').slice(0, 10),
      categories: data.categories || '',
      tags: data.tags || '',
      summary: data.summary || '',
      content: data.content || '',
    }
    postFilename.value = data.filename || ''
  } catch {
    toast.error('获取文章失败')
    router.push('/posts')
  } finally {
    loadingPost.value = false
  }
}

// 路由变化时重新加载（编辑不同文章）
watch(() => route.params.id, (newId) => {
  if (newId) fetchPost()
})

// 首次加载
onMounted(() => {
  if (isEdit.value) fetchPost()
})

async function handleSave() {
  if (!form.value.title.trim()) {
    toast.error('请输入文章标题')
    return
  }

  saving.value = true
  try {
    const payload = {
      title: form.value.title.trim(),
      date: form.value.date || new Date().toISOString().slice(0, 10),
      categories: form.value.categories.trim(),
      tags: form.value.tags.trim(),
      summary: form.value.summary.trim(),
      content: form.value.content,
    }

    if (isEdit.value) {
      await updatePost(postId.value, payload)
      toast.success('文章已更新')
    } else {
      await createPost(payload)
      toast.success('文章已创建')
    }

    router.push('/posts')
  } catch {
    toast.error('保存失败，请重试')
  } finally {
    saving.value = false
  }
}

function goBack() {
  router.push('/posts')
}

// ========== 编辑器工具栏 ==========

function insertMd(syntax) {
  const el = contentArea.value
  if (!el) return
  const start = el.selectionStart
  const end = el.selectionEnd
  const text = form.value.content
  form.value.content = text.substring(0, start) + syntax + text.substring(end)
  // 恢复焦点和光标位置
  setTimeout(() => {
    el.focus()
    const pos = start + syntax.length
    el.setSelectionRange(pos, pos)
  }, 50)
}

function insertImage(img) {
  const md = `![${img.name}](${img.path})`
  insertMd(md)
  showImageInserter.value = false
}

async function loadInserterImages(dir) {
  inserterDir.value = dir
  inserterImages.value = []
  try {
    const data = await getImages(dir)
    inserterImages.value = data.images
  } catch {
    inserterImages.value = []
  }
}

// 首次打开面板时加载图片
watch(showImageInserter, (val) => {
  if (val) loadInserterImages('imgs')
})
</script>

<style scoped>
.editor-grid {
  display: grid;
  grid-template-columns: 300px 1fr;
  gap: 20px;
  margin-bottom: 20px;
  align-items: start;
}

.meta-panel {
  position: sticky;
  top: 32px;
}

.editor-panel {
  min-height: 500px;
}

.md-editor {
  flex: 1;
  min-height: 450px;
  font-family: 'JetBrains Mono', 'Fira Code', 'Consolas', 'Monaco', monospace;
  font-size: 14px;
  line-height: 1.7;
  resize: vertical;
  tab-size: 2;
}

/* 编辑器工具栏 */
.editor-toolbar {
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 6px 0;
  margin-bottom: 6px;
  border-bottom: 1px solid var(--border);
}

.tb-btn {
  border: 1px solid var(--border);
  background: var(--card-bg);
  padding: 4px 10px;
  border-radius: 4px;
  cursor: pointer;
  font-size: 13px;
  color: var(--text-secondary);
  transition: all 0.15s;
}
.tb-btn:hover { background: var(--bg); color: var(--text); border-color: #ccc; }
.tb-btn.tb-primary { color: var(--primary); border-color: var(--primary); font-weight: 500; }
.tb-btn.tb-primary:hover { background: var(--primary); color: white; }

.tb-sep {
  width: 1px;
  height: 20px;
  background: var(--border);
  margin: 0 4px;
}

/* 图片插入面板 */
.image-inserter {
  border-top: 1px solid var(--border);
  margin-top: 8px;
  padding-top: 12px;
  max-height: 260px;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.inserter-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
  font-size: 13px;
  font-weight: 500;
}

.inserter-tabs { display: flex; gap: 4px; }

.inserter-grid {
  flex: 1;
  overflow-y: auto;
  display: grid;
  grid-template-columns: repeat(5, 1fr);
  gap: 6px;
}

.inserter-item {
  border: 2px solid var(--border);
  border-radius: 6px;
  overflow: hidden;
  cursor: pointer;
  transition: border-color 0.15s;
  text-align: center;
}
.inserter-item:hover { border-color: var(--primary); }
.inserter-item img {
  width: 100%;
  height: 60px;
  object-fit: cover;
}
.inserter-item span {
  display: block;
  font-size: 10px;
  padding: 2px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

/* 下滑动画 */
.slide-enter-active { transition: all 0.2s ease; }
.slide-leave-active { transition: all 0.15s ease; }
.slide-enter-from { max-height: 0; opacity: 0; }
.slide-leave-to { max-height: 0; opacity: 0; }

.post-meta-preview {
  display: flex;
  gap: 16px;
  padding: 12px 0;
  margin-bottom: 16px;
  border-bottom: 1px solid var(--border);
  color: var(--text-secondary);
  font-size: 14px;
}

.editor-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  padding: 20px 0;
}

@media (max-width: 900px) {
  .editor-grid {
    grid-template-columns: 1fr;
  }
  .meta-panel {
    position: static;
  }
}
</style>
