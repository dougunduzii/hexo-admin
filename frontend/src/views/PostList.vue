<template>
  <div class="post-list-page">
    <div class="page-header">
      <div>
        <h1>📄 文章管理</h1>
        <p>共 {{ total }} 篇文章</p>
      </div>
      <router-link to="/posts/new" class="btn btn-primary">✏️ 写文章</router-link>
    </div>

    <!-- 搜索栏 -->
    <div class="card">
      <div class="search-box">
        <input
          v-model="searchQuery"
          type="text"
          placeholder="搜索文章标题、内容、标签..."
          @keyup.enter="search"
        />
        <button class="btn btn-primary" @click="search">搜索</button>
        <button class="btn btn-outline" @click="clearSearch">清除</button>
      </div>
    </div>

    <!-- 文章表格 -->
    <div class="card" v-if="posts.length > 0">
      <div class="table-wrap">
        <table>
          <thead>
            <tr>
              <th>标题</th>
              <th>日期</th>
              <th>分类</th>
              <th>标签</th>
              <th>操作</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="post in posts" :key="post.id">
              <td>
                <router-link
                  :to="`/posts/${post.id}/edit`"
                  class="post-title-link"
                >
                  {{ post.title || '(无标题)' }}
                </router-link>
              </td>
              <td class="text-secondary">{{ post.date || '-' }}</td>
              <td>
                <span
                  v-for="cat in parseList(post.categories)"
                  :key="cat"
                  class="tag tag-blue"
                >{{ cat }}</span>
              </td>
              <td>
                <span
                  v-for="tag in parseList(post.tags)"
                  :key="tag"
                  class="tag tag-purple"
                >{{ tag }}</span>
              </td>
              <td class="actions">
                <router-link
                  :to="`/posts/${post.id}/edit`"
                  class="btn btn-sm btn-outline"
                >编辑</router-link>
                <button
                  class="btn btn-sm btn-danger"
                  @click="confirmDelete(post)"
                >删除</button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- 分页 -->
      <div class="pagination" v-if="totalPages > 1">
        <button :disabled="page === 1" @click="goPage(page - 1)">‹ 上一页</button>
        <button
          v-for="p in visiblePages"
          :key="p"
          :class="{ current: p === page }"
          @click="goPage(p)"
        >{{ p }}</button>
        <button :disabled="page === totalPages" @click="goPage(page + 1)">下一页 ›</button>
      </div>
    </div>

    <!-- 空状态 -->
    <div class="card empty-state" v-else-if="!loading">
      <div class="icon">📭</div>
      <p>还没有文章，开始写第一篇吧！</p>
      <router-link to="/posts/new" class="btn btn-primary" style="margin-top: 16px;">
        ✏️ 写文章
      </router-link>
    </div>

    <!-- 加载中 -->
    <div class="loading" v-if="loading">加载中...</div>

    <!-- 删除确认对话框 -->
    <div class="modal-overlay" v-if="showDeleteModal" @click.self="showDeleteModal = false">
      <div class="modal-box">
        <h3>确认删除</h3>
        <p>确定要删除文章「{{ deleteTarget?.title }}」吗？此操作不可恢复。</p>
        <div class="modal-actions">
          <button class="btn btn-outline" @click="showDeleteModal = false">取消</button>
          <button class="btn btn-danger" @click="doDelete">确认删除</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { getPosts, deletePost } from '../api'

const posts = ref([])
const total = ref(0)
const page = ref(1)
const pageSize = 20
const searchQuery = ref('')
const loading = ref(false)

const showDeleteModal = ref(false)
const deleteTarget = ref(null)

const totalPages = computed(() => Math.ceil(total.value / pageSize))

const visiblePages = computed(() => {
  const pages = []
  const tp = totalPages.value
  const current = page.value
  let start = Math.max(1, current - 2)
  let end = Math.min(tp, current + 2)

  if (end - start < 4) {
    if (start === 1) end = Math.min(tp, start + 4)
    else start = Math.max(1, end - 4)
  }

  for (let i = start; i <= end; i++) pages.push(i)
  return pages
})

function parseList(str) {
  if (!str) return []
  return str.split(',').map(s => s.trim()).filter(Boolean)
}

async function fetchPosts() {
  loading.value = true
  try {
    const params = {
      page: page.value,
      page_size: pageSize,
    }
    if (searchQuery.value) params.search = searchQuery.value
    const data = await getPosts(params)
    posts.value = data.posts
    total.value = data.total
  } catch (err) {
    console.error('获取文章列表失败:', err)
  } finally {
    loading.value = false
  }
}

function search() {
  page.value = 1
  fetchPosts()
}

function clearSearch() {
  searchQuery.value = ''
  page.value = 1
  fetchPosts()
}

function goPage(p) {
  if (p < 1 || p > totalPages.value) return
  page.value = p
  fetchPosts()
}

function confirmDelete(post) {
  deleteTarget.value = post
  showDeleteModal.value = true
}

async function doDelete() {
  if (!deleteTarget.value) return
  try {
    await deletePost(deleteTarget.value.id)
    showDeleteModal.value = false
    deleteTarget.value = null
    fetchPosts()
  } catch (err) {
    console.error('删除失败:', err)
  }
}

onMounted(fetchPosts)
</script>

<style scoped>
.post-title-link {
  color: var(--primary);
  text-decoration: none;
  font-weight: 500;
}
.post-title-link:hover {
  text-decoration: underline;
}

.text-secondary {
  color: var(--text-secondary);
  font-size: 13px;
}

.actions {
  display: flex;
  gap: 6px;
  white-space: nowrap;
}
</style>
