<template>
  <div class="post-editor">
    <div class="page-header">
      <div>
        <h1>{{ isEdit ? '✏️ 编辑文章' : '✏️ 新建文章' }}</h1>
        <p v-if="isEdit">编辑已有文章，修改后保存即可</p>
        <p v-else>创建一篇新的博客文章</p>
      </div>
      <div style="display: flex; gap: 8px;">
        <!-- .md 文件上传 -->
        <input
          ref="mdFileInput"
          type="file"
          accept=".md,.markdown"
          style="display: none"
          @change="handleMdUpload"
        />
        <button class="btn btn-outline" @click="$refs.mdFileInput.click()" :disabled="saving"
          title="上传本地 .md 文件，自动提取标题、标签等信息">
          📄 上传 .md
        </button>
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

      <div class="editor-grid" :class="{ 'meta-hidden': !showMeta }">
        <!-- 左侧：元数据 -->
        <Transition name="slide-panel">
          <div v-if="showMeta" class="card meta-panel">
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
        </Transition>

        <!-- 右侧：Markdown 编辑区 -->
        <div class="card editor-panel">
          <div class="form-group" style="height: 100%; display: flex; flex-direction: column;">
            <div style="display: flex; justify-content: space-between; align-items: center;">
              <label>正文（Markdown 格式）</label>
              <button type="button" class="tb-btn" @click="showMeta = !showMeta" :title="showMeta ? '收起属性面板' : '展开属性面板'">
                {{ showMeta ? '⬅ 收起属性' : '⚙️ 属性' }}
              </button>
            </div>
            <!-- 编辑工具栏 -->
            <div class="editor-toolbar">
              <button type="button" class="tb-btn" @click="insertMd('**粗体**')" title="粗体"><b>B</b></button>
              <button type="button" class="tb-btn" @click="insertMd('*斜体*')" title="斜体"><i>I</i></button>
              <button type="button" class="tb-btn" @click="insertMd('`代码`')" title="行内代码">&lt;/&gt;</button>
              <button type="button" class="tb-btn" @click="insertMd('[链接](url)')" title="链接">🔗</button>
              <button type="button" class="tb-btn" @click="insertMd('\n```\n\n```\n')" title="代码块">📋</button>
              <span class="tb-sep"></span>
              <button type="button" class="tb-btn" @click="insertMd('> 引用')" title="引用">💬</button>
              <button type="button" class="tb-btn" @click="insertMd('- 列表项')" title="无序列表">📌</button>
              <button type="button" class="tb-btn" @click="insertMd('1. 列表项')" title="有序列表">🔢</button>
              <button type="button" class="tb-btn" @click="insertMd('---\n')" title="分隔线">➖</button>
              <span class="tb-sep"></span>
              <button type="button" class="tb-btn tb-primary" @click="showImageInserter = !showImageInserter" title="插入图片">
                🖼️ 插入图片
              </button>
            </div>
            <div ref="editorContainer" class="cm-editor-wrapper"></div>
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
                <div v-if="inserterImages.length === 0" class="inserter-empty">
                  暂无图片
                </div>
              </div>
            </div>
          </Transition>
        </div>
      </div>
    </div>

    <!-- 预览模式 -->
    <div v-else class="card">
      <div class="post-meta-preview">
        <span v-if="form.categories">📁 {{ form.categories }}</span>
        <span v-if="form.tags">🏷️ {{ form.tags }}</span>
        <span>📅 {{ form.date }}</span>
      </div>
      <div class="markdown-preview" v-html="renderedMarkdown"></div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, watch, onMounted, onUnmounted, nextTick } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { getPost, createPost, updatePost, uploadMdFile } from '../api'
import { getImages, imageSrc } from '../api'
import { useToast } from '../composables/useToast'
import { marked } from 'marked'

// CodeMirror 6
import { EditorView, keymap, placeholder, lineNumbers, highlightActiveLine, highlightActiveLineGutter } from '@codemirror/view'
import { EditorState } from '@codemirror/state'
import { defaultKeymap, history, historyKeymap, indentWithTab } from '@codemirror/commands'
import { syntaxHighlighting, defaultHighlightStyle, bracketMatching, indentOnInput, foldGutter, foldKeymap } from '@codemirror/language'
import { markdown, markdownLanguage } from '@codemirror/lang-markdown'
import { html } from '@codemirror/lang-html'
import { autocompletion, completionKeymap, closeBrackets, closeBracketsKeymap } from '@codemirror/autocomplete'
import { languages } from '@codemirror/language-data'

const route = useRoute()
const router = useRouter()
const toast = useToast()

const postId = computed(() => route.params.id)
const isEdit = computed(() => !!route.params.id)

const form = reactive({
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
const showMeta = ref(true)

const editorContainer = ref(null)
const editorView = ref(null)
const showImageInserter = ref(false)
const inserterDir = ref('imgs')
const inserterImages = ref([])
const mdFileInput = ref(null)

// 防止循环更新
let syncingFromEditor = false
let syncingFromForm = false

// 渲染 Markdown
const renderedMarkdown = computed(() => {
  try {
    return marked(form.content || '')
  } catch {
    return '<p>Markdown 渲染错误</p>'
  }
})

function togglePreview() {
  showPreview.value = !showPreview.value
}

// ========== CodeMirror 编辑器初始化 ==========

function createEditor() {
  if (!editorContainer.value) return

  const extensions = [
    // 行号 & 折叠
    lineNumbers(),
    highlightActiveLineGutter(),
    highlightActiveLine(),
    foldGutter(),

    // Markdown 语言支持（含代码块语法高亮）
    markdown({
      codeLanguages: languages,
      defaultCodeLanguage: null,
    }),

    // HTML 支持（标签自动闭合、属性补全）
    html({ autoCloseTags: true, selfClosingTags: true }),

    // 自动补全 & 括号闭合
    autocompletion(),
    closeBrackets(),

    // 语法高亮 & 括号匹配
    syntaxHighlighting(defaultHighlightStyle, { fallback: true }),
    bracketMatching(),

    // 自动缩进
    indentOnInput(),

    // 撤销历史
    history(),

    // 占位文本
    placeholder('在此编写 Markdown 内容...\n\n# 标题\n段落内容...\n\n![图片描述](./imgs/example.png)'),

    // 键盘映射
    keymap.of([
      ...defaultKeymap,
      ...historyKeymap,
      ...foldKeymap,
      ...completionKeymap,
      ...closeBracketsKeymap,
      indentWithTab,
    ]),

    // Tab 键大小 = 2 空格
    EditorState.tabSize.of(2),
  ]

  const state = EditorState.create({
    doc: form.content,
    extensions,
  })

  const view = new EditorView({
    state,
    parent: editorContainer.value,
    dispatchTransactions(trs) {
      view.update(trs)
      // 同步内容到 form.content
      if (trs.some(tr => tr.docChanged) && !syncingFromForm) {
        syncingFromEditor = true
        form.content = view.state.doc.toString()
        nextTick(() => { syncingFromEditor = false })
      }
    },
  })

  editorView.value = view
}

function destroyEditor() {
  editorView.value?.destroy()
  editorView.value = null
}

// ========== 内容同步 ==========

// 监听外部 content 变更（如 .md 上传、加载文章）同步到编辑器
watch(() => form.content, (newVal) => {
  if (syncingFromEditor) return
  const view = editorView.value
  if (!view) return

  const currentDoc = view.state.doc.toString()
  if (newVal === currentDoc) return

  syncingFromForm = true
  view.dispatch({
    changes: { from: 0, to: currentDoc.length, insert: newVal },
  })
  nextTick(() => { syncingFromForm = false })
})

// 加载文章（编辑模式）
async function fetchPost() {
  loadingPost.value = true
  try {
    const data = await getPost(postId.value)
    Object.assign(form, {
      title: data.title || '',
      date: data.date || '',
      categories: data.categories || '',
      tags: data.tags || '',
      summary: data.summary || '',
      content: data.content || '',
    })
    postFilename.value = data.filename || ''
  } catch {
    toast.error('加载文章失败')
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
  nextTick(() => createEditor())
})

onUnmounted(() => {
  destroyEditor()
})

async function handleSave() {
  if (!form.title.trim()) {
    toast.error('请输入文章标题')
    return
  }

  saving.value = true
  try {
    const payload = {
      title: form.title.trim(),
      date: form.date || new Date().toISOString().slice(0, 10),
      categories: form.categories.trim(),
      tags: form.tags.trim(),
      summary: form.summary.trim(),
      content: form.content,
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

// ========== .md 文件上传处理 ==========

async function handleMdUpload(e) {
  const file = e.target.files?.[0]
  if (!file) return

  try {
    toast.info('正在解析文件...')
    const data = await uploadMdFile(file)

    if (data.title) form.title = data.title
    if (data.date) form.date = data.date
    if (data.categories) form.categories = data.categories
    if (data.tags) form.tags = data.tags
    if (data.summary) form.summary = data.summary
    form.content = data.content || ''

    toast.success(`已加载: ${data.filename || file.name}`)
  } catch (err) {
    const msg = err?.response?.data?.detail || err.message || '文件解析失败'
    toast.error(msg)
  } finally {
    if (mdFileInput.value) {
      mdFileInput.value.value = ''
    }
  }
}

// ========== 编辑器工具栏 ==========

function insertMd(syntax) {
  const view = editorView.value
  if (!view) return

  view.focus()
  const { from, to } = view.state.selection.main
  const hasSelection = from !== to

  // 代码块特殊处理：包裹选中文本
  if (syntax.includes('```')) {
    if (hasSelection) {
      const selected = view.state.doc.sliceString(from, to)
      view.dispatch({
        changes: { from, to, insert: '\n```\n' + selected + '\n```\n' },
      })
    } else {
      view.dispatch({
        changes: { from, to, insert: syntax },
        selection: { anchor: from + 1, head: from + 1 },
      })
    }
    return
  }

  view.dispatch({
    changes: { from, to, insert: syntax },
    selection: { anchor: from + syntax.length },
  })
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
  transition: grid-template-columns 0.3s ease;
}

.editor-grid.meta-hidden {
  grid-template-columns: 1fr;
}

.meta-panel {
  position: sticky;
  top: 32px;
}

.editor-panel {
  min-height: calc(100vh - 280px);
}

/* CodeMirror 容器 */
.cm-editor-wrapper {
  flex: 1;
  min-height: calc(100vh - 430px);
  border: 1px solid var(--border);
  border-radius: 6px;
  overflow: hidden;
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

/* 侧边栏收起动画 */
.slide-panel-enter-active { transition: all 0.3s ease; }
.slide-panel-leave-active { transition: all 0.25s ease; }
.slide-panel-enter-from { opacity: 0; transform: translateX(-20px); }
.slide-panel-leave-to { opacity: 0; transform: translateX(-20px); }

.post-meta-preview {
  display: flex;
  gap: 16px;
  padding: 12px 0;
  margin-bottom: 16px;
  border-bottom: 1px solid var(--border);
  color: var(--text-secondary);
  font-size: 14px;
}

@media (max-width: 900px) {
  .editor-grid {
    grid-template-columns: 1fr !important;
  }
  .meta-panel {
    position: static;
  }
}
</style>

<!-- 非 scoped 样式：CodeMirror 6 在 scoped 下选择器不生效 -->
<style>
.cm-editor-wrapper .cm-editor {
  height: 100%;
  min-height: calc(100vh - 430px);
  font-family: 'JetBrains Mono', 'Fira Code', 'Consolas', 'Monaco', monospace;
  font-size: 14px;
  line-height: 1.7;
}

.cm-editor-wrapper .cm-editor.cm-focused {
  outline: none;
}

.cm-editor-wrapper .cm-editor .cm-scroller {
  overflow: auto;
  padding: 8px 0;
}

.cm-editor-wrapper .cm-editor .cm-content {
  padding: 0 12px;
}

/* 占位文本样式 */
.cm-editor-wrapper .cm-editor .cm-placeholder {
  color: #999;
}

/* 光标颜色 */
.cm-editor-wrapper .cm-editor .cm-cursor {
  border-left-color: var(--primary, #4a6cf7);
}

/* 选中文本颜色 */
.cm-editor-wrapper .cm-editor .cm-selectionBackground,
.cm-editor-wrapper .cm-editor.cm-focused .cm-selectionBackground {
  background: rgba(74, 108, 247, 0.2) !important;
}

/* 行号区域 */
.cm-editor-wrapper .cm-editor .cm-gutters {
  background: var(--bg, #f5f6fa);
  border-right: 1px solid var(--border, #e0e0e0);
  color: #aaa;
}

/* 折叠箭头 */
.cm-editor-wrapper .cm-editor .cm-foldGutter .cm-gutterElement:hover {
  color: var(--primary, #4a6cf7);
}
</style>