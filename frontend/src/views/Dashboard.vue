<template>
  <div class="dashboard">
    <div class="page-header">
      <h1>📊 仪表盘</h1>
      <p>博客数据概览</p>
    </div>

    <!-- 统计卡片 -->
    <div class="stats-grid">
      <div class="stat-card">
        <div class="stat-icon">📄</div>
        <div class="stat-info">
          <span class="stat-value">{{ stats.total_posts }}</span>
          <span class="stat-label">文章总数</span>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon">📂</div>
        <div class="stat-info">
          <span class="stat-value">{{ stats.total_categories }}</span>
          <span class="stat-label">分类数</span>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon">🏷️</div>
        <div class="stat-info">
          <span class="stat-value">{{ stats.total_tags }}</span>
          <span class="stat-label">标签数</span>
        </div>
      </div>
    </div>

    <!-- 分类和标签 -->
    <div class="detail-grid">
      <div class="card">
        <div class="card-header">
          <h2>📂 分类列表</h2>
        </div>
        <div v-if="stats.categories?.length" class="tag-list">
          <span
            v-for="cat in stats.categories"
            :key="cat"
            class="tag tag-blue"
          >{{ cat }}</span>
        </div>
        <div v-else class="empty-state" style="padding: 30px">
          <p>暂无分类</p>
        </div>
      </div>

      <div class="card">
        <div class="card-header">
          <h2>🏷️ 标签列表</h2>
        </div>
        <div v-if="stats.tags?.length" class="tag-list">
          <span
            v-for="tag in stats.tags"
            :key="tag"
            class="tag tag-purple"
          >{{ tag }}</span>
        </div>
        <div v-else class="empty-state" style="padding: 30px">
          <p>暂无标签</p>
        </div>
      </div>
    </div>

    <!-- 一键部署 -->
    <div class="card">
      <div class="card-header">
        <h2>🚀 一键部署</h2>
      </div>
      <p style="margin-bottom: 12px; color: var(--text-secondary);">
        执行 <code>hexo generate --deploy</code>，将修改后的文章发布到网站。
      </p>
      <div style="display:flex; align-items:center; gap:12px;">
        <button class="btn btn-primary" @click="handleDeploy" :disabled="deploying">
          {{ deploying ? '⏳ 部署中...' : '🚀 部署到网站' }}
        </button>
        <span v-if="deployMsg" :style="{color: deployOk ? 'var(--success)' : 'var(--danger)', fontSize: '14px'}">
          {{ deployMsg }}
        </span>
      </div>
      <pre v-if="deployLog" class="deploy-log">{{ deployLog }}</pre>
    </div>

    <!-- 同步 -->
    <div class="card">
      <div class="card-header">
        <h2>🔄 文件同步</h2>
      </div>
      <p style="margin-bottom: 16px; color: var(--text-secondary);">
        将本地 Hexo 文章文件同步到数据库。新文件将被导入，已删除的文件将从数据库中移除。
      </p>
      <button class="btn btn-outline" @click="handleSync" :disabled="syncing">
        {{ syncing ? '同步中...' : '立即同步' }}
      </button>
      <span v-if="syncMsg" style="margin-left: 12px; color: var(--success); font-size: 14px;">
        {{ syncMsg }}
      </span>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { getStats, syncPosts, deployBlog } from '../api'

const stats = ref({
  total_posts: 0,
  total_categories: 0,
  total_tags: 0,
  categories: [],
  tags: [],
})

const syncing = ref(false)
const syncMsg = ref('')
const deploying = ref(false)
const deployMsg = ref('')
const deployOk = ref(false)
const deployLog = ref('')

const fetchStats = async () => {
  try {
    const data = await getStats()
    stats.value = data
  } catch (err) {
    console.error('获取统计信息失败:', err)
  }
}

const handleSync = async () => {
  syncing.value = true
  syncMsg.value = ''
  try {
    const result = await syncPosts()
    syncMsg.value = result.message
    await fetchStats()
  } catch (err) {
    syncMsg.value = '同步失败'
  } finally {
    syncing.value = false
  }
}

const handleDeploy = async () => {
  deploying.value = true
  deployMsg.value = ''
  deployLog.value = ''
  try {
    const result = await deployBlog()
    deployOk.value = result.success
    deployMsg.value = result.message
    deployLog.value = result.stdout || result.stderr || ''
  } catch (err) {
    deployOk.value = false
    deployMsg.value = err.response?.data?.detail || '部署请求失败'
  } finally {
    deploying.value = false
  }
}

onMounted(fetchStats)
</script>

<style scoped>
.stats-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 20px;
  margin-bottom: 24px;
}

.stat-card {
  background: var(--card-bg);
  border-radius: 12px;
  border: 1px solid var(--border);
  padding: 24px;
  display: flex;
  align-items: center;
  gap: 16px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
}

.stat-icon {
  font-size: 36px;
}

.stat-info {
  display: flex;
  flex-direction: column;
}

.stat-value {
  font-size: 32px;
  font-weight: 700;
  color: var(--text);
}

.stat-label {
  font-size: 14px;
  color: var(--text-secondary);
}

.deploy-log {
  background: #1e293b;
  color: #a8b2c1;
  padding: 16px;
  border-radius: 8px;
  font-size: 12px;
  line-height: 1.6;
  max-height: 300px;
  overflow-y: auto;
  margin-top: 16px;
  white-space: pre-wrap;
  word-break: break-all;
}

.detail-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
  margin-bottom: 24px;
}

.tag-list {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}
</style>
