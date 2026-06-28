<template>
  <div class="settings-page">
    <div class="page-header">
      <h1>⚙️ 网站设置</h1>
      <p>管理 Butterfly 主题配置</p>
    </div>

    <!-- 加载中 -->
    <div v-if="loading" class="loading">加载配置中...</div>

    <!-- 设置内容 -->
    <template v-else>
      <!-- Tab 导航 -->
      <div class="tabs">
        <button v-for="t in tabs" :key="t.key" :class="['tab', { active: activeTab === t.key }]" @click="activeTab = t.key">
          {{ t.icon }} {{ t.label }}
        </button>
      </div>

      <!-- 外观设置 -->
      <div v-show="activeTab === 'appearance'" class="card">
        <h3>🖼️ 背景与图片</h3>
        <div class="form-grid">
          <div class="form-group">
            <label>网站背景</label>
            <div class="img-input-row">
              <input v-model="form.background" placeholder="./imgs/background.png" />
              <button class="btn btn-sm btn-outline" @click="pickImage('background')">浏览</button>
            </div>
          </div>
          <div class="form-group">
            <label>首页横幅 (index_img)</label>
            <div class="img-input-row">
              <input v-model="form.index_img" />
              <button class="btn btn-sm btn-outline" @click="pickImage('index_img')">浏览</button>
            </div>
          </div>
          <div class="form-group">
            <label>默认顶部图 (default_top_img)</label>
            <div class="img-input-row">
              <input v-model="form.default_top_img" />
              <button class="btn btn-sm btn-outline" @click="pickImage('default_top_img')">浏览</button>
            </div>
          </div>
          <div class="form-group">
            <label>头像 (avatar.img)</label>
            <div class="img-input-row">
              <input v-model="form.avatar.img" />
              <button class="btn btn-sm btn-outline" @click="pickImage('avatar_img')">浏览</button>
            </div>
          </div>
          <div class="form-group">
            <label>网站图标 (favicon)</label>
            <input v-model="form.favicon" />
          </div>
        </div>

        <h3>🎨 主题颜色</h3>
        <div class="form-grid">
          <div class="form-group" v-for="c in colorFields" :key="c.key">
            <label>{{ c.label }}</label>
            <div class="color-row">
              <input type="color" v-model="form.theme_color[c.key]" class="color-picker" />
              <input type="text" v-model="form.theme_color[c.key]" />
            </div>
          </div>
        </div>

        <h3>🌓 显示模式</h3>
        <div class="form-group">
          <label>默认显示模式</label>
          <select v-model="form.display_mode">
            <option value="light">浅色</option>
            <option value="dark">深色</option>
          </select>
        </div>
      </div>

      <!-- 导航设置 -->
      <div v-show="activeTab === 'nav'" class="card">
        <h3>📋 导航菜单</h3>
        <div class="menu-list">
          <div v-for="(item, idx) in menuList" :key="idx" class="menu-item">
            <input v-model="item.name" placeholder="名称" class="menu-name" />
            <input v-model="item.url" placeholder="链接" class="menu-url" />
            <input v-model="item.icon" placeholder="图标 class" class="menu-icon" />
            <button class="btn btn-sm btn-danger" @click="menuList.splice(idx, 1)">✕</button>
          </div>
        </div>
        <button class="btn btn-outline" @click="menuList.push({ name: '', url: '', icon: '' })">+ 添加菜单项</button>
      </div>

      <!-- 首页设置 -->
      <div v-show="activeTab === 'home'" class="card">
        <h3>🏠 首页设置</h3>
        <div class="form-group">
          <label>副标题（每行一个）</label>
          <textarea v-model="subtitleText" rows="4" placeholder="Keep passionate!"></textarea>
        </div>
        <div class="form-group">
          <label>首页布局列数</label>
          <select v-model.number="form.index_layout">
            <option :value="4">4 列</option>
            <option :value="3">3 列</option>
            <option :value="2">2 列</option>
          </select>
        </div>
        <div class="form-group">
          <label>文章摘要字数</label>
          <input v-model.number="form.index_post_content.length" type="number" />
        </div>
      </div>

      <!-- 侧边栏设置 -->
      <div v-show="activeTab === 'sidebar'" class="card">
        <h3>📌 侧边栏卡片</h3>
        <div class="form-grid">
          <div class="form-group">
            <label>公告内容</label>
            <textarea v-model="form.aside.card_announcement.content" rows="3" />
          </div>
          <div class="form-group">
            <label>最新文章数量</label>
            <input v-model.number="form.aside.card_recent_post.limit" type="number" />
          </div>
          <div class="form-group">
            <label>标签数量</label>
            <input v-model.number="form.aside.card_tags.limit" type="number" />
          </div>
        </div>
        <div class="checkbox-group">
          <label><input type="checkbox" v-model="form.aside.card_author.enable" /> 作者卡片</label>
          <label><input type="checkbox" v-model="form.aside.card_announcement.enable" /> 公告卡片</label>
          <label><input type="checkbox" v-model="form.aside.card_recent_post.enable" /> 最新文章</label>
          <label><input type="checkbox" v-model="form.aside.card_tags.enable" /> 标签云</label>
          <label><input type="checkbox" v-model="form.aside.card_archives.enable" /> 归档</label>
          <label><input type="checkbox" v-model="form.aside.card_webinfo.enable" /> 网站信息</label>
        </div>
      </div>

      <!-- 页脚设置 -->
      <div v-show="activeTab === 'footer'" class="card">
        <h3>📃 页脚设置</h3>
        <div class="form-group">
          <label>建站年份</label>
          <input v-model.number="form.footer.owner.since" type="number" />
        </div>
        <div class="checkbox-group">
          <label><input type="checkbox" v-model="form.footer.owner.enable" /> 显示网站所有者</label>
          <label><input type="checkbox" v-model="form.footer.copyright.enable" /> 显示版权信息</label>
        </div>
      </div>

      <!-- 保存按钮 -->
      <div class="save-bar">
        <p v-if="saveMsg" :class="saveOk ? 'msg-ok' : 'msg-err'">{{ saveMsg }}</p>
        <button class="btn btn-primary btn-lg" @click="handleSave" :disabled="saving">
          {{ saving ? '保存中...' : '💾 保存设置' }}
        </button>
      </div>
    </template>

    <!-- 图片选择弹窗 -->
    <div v-if="showImagePicker" class="modal-overlay" @click.self="showImagePicker = false">
      <div class="modal-box image-picker-modal">
        <h3>选择图片</h3>
        <div class="picker-tabs">
          <button v-for="d in ['imgs', 'cover']" :key="d"
            :class="['btn btn-sm', pickerDir === d ? 'btn-primary' : 'btn-outline']"
            @click="loadPickerImages(d)">{{ d }}</button>
        </div>
        <div class="picker-body">
          <div class="picker-grid">
            <div v-for="img in pickerImages" :key="img.path" class="picker-item"
              :class="{ selected: selectedImage === img.path }"
              @click="selectedImage = img.path">
              <img :src="imageSrc(img.path)" :alt="img.name" loading="lazy" />
              <span>{{ img.name }}</span>
            </div>
          </div>
          <!-- 选中预览 -->
          <div class="picker-preview" v-if="selectedImage">
            <img :src="imageSrc(selectedImage)" alt="预览" />
            <code>{{ selectedImage }}</code>
          </div>
        </div>
        <div class="modal-actions">
          <button class="btn btn-outline" @click="showImagePicker = false">取消</button>
          <button class="btn btn-primary" @click="confirmImagePick">确定</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import { getSettings, updateSettings, getImages, imageSrc } from '../api'
import { useToast } from '../composables/useToast'

const toast = useToast()
const loading = ref(true)
const saving = ref(false)
const saveMsg = ref('')
const saveOk = ref(true)
const activeTab = ref('appearance')

const tabs = [
  { key: 'appearance', label: '外观', icon: '🎨' },
  { key: 'nav', label: '导航', icon: '📋' },
  { key: 'home', label: '首页', icon: '🏠' },
  { key: 'sidebar', label: '侧边栏', icon: '📌' },
  { key: 'footer', label: '页脚', icon: '📃' },
]

const colorFields = [
  { key: 'main', label: '主题色' },
  { key: 'paginator', label: '分页色' },
  { key: 'button_hover', label: '按钮悬停' },
  { key: 'text_selection', label: '选中文字' },
  { key: 'link_color', label: '链接颜色' },
]

const form = ref({
  background: '',
  index_img: '',
  default_top_img: '',
  favicon: '',
  avatar: { img: '', effect: false },
  display_mode: 'light',
  theme_color: {},
  index_layout: 4,
  index_post_content: { method: 4, length: 200 },
  aside: {
    card_author: { enable: false },
    card_announcement: { enable: true, content: '' },
    card_recent_post: { enable: true, limit: 5, sort: 'date' },
    card_tags: { enable: true, limit: 40 },
    card_archives: { enable: true, type: 'monthly', limit: 8 },
    card_webinfo: { enable: true },
  },
  footer: {
    owner: { enable: false, since: 2026 },
    copyright: { enable: false },
  },
  nav: { menu: {} },
  subtitle: { enable: true, sub: [] },
})

const menuList = ref([])
const subtitleText = ref('')

// 同步 menu 列表
watch(menuList, (list) => {
  const menu = {}
  list.forEach(item => {
    if (item.name) {
      menu[item.name] = `${item.url} || ${item.icon}`
    }
  })
  form.value.nav.menu = menu
}, { deep: true })

// 同步副标题
watch(subtitleText, (val) => {
  form.value.subtitle.sub = val.split('\n').filter(s => s.trim())
})

// 图片选择
const showImagePicker = ref(false)
const pickerDir = ref('imgs')
const pickerImages = ref([])
const selectedImage = ref('')
const pickTarget = ref('')

function pickImage(target) {
  pickTarget.value = target
  selectedImage.value = form.value[target] || ''
  if (target === 'avatar_img') selectedImage.value = form.value.avatar?.img || ''
  showImagePicker.value = true
  loadPickerImages('imgs')
}

async function loadPickerImages(dir) {
  pickerDir.value = dir
  try {
    const data = await getImages(dir)
    pickerImages.value = data.images
  } catch { pickerImages.value = [] }
}

function confirmImagePick() {
  if (pickTarget.value === 'avatar_img') {
    if (!form.value.avatar) form.value.avatar = { img: '', effect: false }
    form.value.avatar.img = selectedImage.value
  } else {
    form.value[pickTarget.value] = selectedImage.value
  }
  showImagePicker.value = false
}

// 加载配置
async function loadSettings() {
  loading.value = true
  try {
    const data = await getSettings()
    if (data && data.background !== undefined) {
      form.value = {
        ...form.value,
        ...data,
        avatar: { img: '', effect: false, ...(data.avatar || {}) },
        theme_color: { ...form.value.theme_color, ...(data.theme_color || {}) },
        aside: deepMerge(form.value.aside, data.aside || {}),
        footer: deepMerge(form.value.footer, data.footer || {}),
        index_post_content: { ...form.value.index_post_content, ...(data.index_post_content || {}) },
      }
      // 解析菜单
      if (data.nav?.menu) {
        menuList.value = Object.entries(data.nav.menu).map(([name, val]) => {
          const parts = val.split(' || ')
          return { name, url: parts[0] || '', icon: parts[1] || '' }
        })
        if (menuList.value.length === 0) menuList.value.push({ name: '', url: '', icon: '' })
      }
      if (data.subtitle?.sub) {
        subtitleText.value = data.subtitle.sub.join('\n')
      }
    }
  } catch (err) {
    console.error('加载配置失败:', err)
    toast.error('加载配置失败')
  } finally {
    loading.value = false
  }
}

function deepMerge(a, b) {
  const r = { ...a }
  for (const k in b) {
    if (b[k] && typeof b[k] === 'object' && !Array.isArray(b[k])) {
      r[k] = deepMerge(r[k] || {}, b[k])
    } else {
      r[k] = b[k]
    }
  }
  return r
}

async function handleSave() {
  saving.value = true
  saveMsg.value = ''
  try {
    await updateSettings(form.value)
    saveOk.value = true
    saveMsg.value = '设置已保存'
    toast.success('设置已保存')
  } catch (err) {
    saveOk.value = false
    saveMsg.value = '保存失败'
    toast.error('保存失败')
  } finally {
    saving.value = false
    setTimeout(() => saveMsg.value = '', 3000)
  }
}

onMounted(loadSettings)
</script>

<style scoped>
.tabs {
  display: flex;
  gap: 4px;
  margin-bottom: 20px;
  background: var(--card-bg);
  border-radius: 10px;
  padding: 4px;
  border: 1px solid var(--border);
}

.tab {
  flex: 1;
  padding: 10px;
  border: none;
  background: transparent;
  border-radius: 7px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
  color: var(--text-secondary);
  transition: all 0.15s;
}

.tab:hover { color: var(--text); }
.tab.active {
  background: var(--primary);
  color: white;
}

h3 {
  font-size: 16px;
  margin: 24px 0 12px;
  padding-bottom: 8px;
  border-bottom: 1px solid var(--border);
}
h3:first-child { margin-top: 0; }

.form-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
}

.img-input-row {
  display: flex;
  gap: 8px;
}
.img-input-row input { flex: 1; }

.color-row {
  display: flex;
  gap: 8px;
  align-items: center;
}
.color-picker {
  width: 36px !important;
  height: 36px;
  padding: 2px !important;
  border-radius: 6px;
  cursor: pointer;
}

.menu-list { display: flex; flex-direction: column; gap: 8px; }
.menu-item { display: flex; gap: 8px; align-items: center; }
.menu-name { flex: 2; }
.menu-url { flex: 3; }
.menu-icon { flex: 2; }

.checkbox-group {
  display: flex;
  flex-wrap: wrap;
  gap: 16px;
  margin-top: 8px;
}
.checkbox-group label {
  display: flex;
  align-items: center;
  gap: 6px;
  font-weight: 400;
  cursor: pointer;
  font-size: 14px;
}
.checkbox-group input[type="checkbox"] { width: auto; }

.save-bar {
  display: flex;
  justify-content: flex-end;
  align-items: center;
  gap: 16px;
  margin-top: 20px;
}
.msg-ok { color: var(--success); font-size: 14px; }
.msg-err { color: var(--danger); font-size: 14px; }

/* 图片选择弹窗 */
.image-picker-modal { max-width: 750px; max-height: 80vh; overflow-y: auto; }
.picker-tabs { display: flex; gap: 8px; margin-bottom: 12px; }
.picker-body {
  display: grid;
  grid-template-columns: 1fr 200px;
  gap: 16px;
}
.picker-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 8px;
  max-height: 400px;
  overflow-y: auto;
  align-content: start;
}

.picker-preview {
  position: sticky;
  top: 0;
  background: var(--bg);
  border-radius: 8px;
  padding: 12px;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 10px;
  height: fit-content;
}
.picker-preview img {
  width: 100%;
  border-radius: 6px;
  object-fit: contain;
  max-height: 200px;
}
.picker-preview code {
  font-size: 11px;
  word-break: break-all;
  text-align: center;
  background: var(--card-bg);
  padding: 4px 6px;
  border-radius: 4px;
}

@media (max-width: 768px) {
  .picker-body { grid-template-columns: 1fr; }
  .picker-preview { display: none; }
}
.picker-item {
  border: 2px solid var(--border);
  border-radius: 8px;
  overflow: hidden;
  cursor: pointer;
  text-align: center;
  transition: border-color 0.15s;
}
.picker-item:hover { border-color: var(--primary); }
.picker-item.selected { border-color: var(--primary); box-shadow: 0 0 0 2px rgba(79,70,229,0.3); }
.picker-item img {
  width: 100%;
  height: 80px;
  object-fit: cover;
}
.picker-item span {
  display: block;
  font-size: 10px;
  padding: 4px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

@media (max-width: 768px) {
  .form-grid { grid-template-columns: 1fr; }
  .picker-grid { grid-template-columns: repeat(3, 1fr); }
}

</style>
