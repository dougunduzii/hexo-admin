<template>
  <aside class="sidebar">
    <div class="sidebar-brand">
      <div class="brand-icon">📝</div>
      <div class="brand-text">
        <h1>Hexo Admin</h1>
        <span>博客管理后台</span>
      </div>
    </div>

    <nav class="sidebar-nav">
      <router-link to="/" class="nav-item" active-class="active">
        <span class="nav-icon">📊</span>
        <span>仪表盘</span>
      </router-link>
      <router-link to="/posts" class="nav-item" active-class="active">
        <span class="nav-icon">📄</span>
        <span>文章管理</span>
      </router-link>
      <router-link to="/posts/new" class="nav-item" active-class="active">
        <span class="nav-icon">✏️</span>
        <span>写文章</span>
      </router-link>
      <div class="nav-divider"></div>
      <router-link to="/settings" class="nav-item" active-class="active">
        <span class="nav-icon">⚙️</span>
        <span>网站设置</span>
      </router-link>
      <router-link to="/images" class="nav-item" active-class="active">
        <span class="nav-icon">🖼️</span>
        <span>图片管理</span>
      </router-link>
    </nav>

    <div class="sidebar-footer">
      <div class="status-indicator">
        <span class="dot" :class="connected ? 'online' : 'offline'"></span>
        <span>{{ connected ? 'API 已连接' : 'API 未连接' }}</span>
      </div>
      <button v-if="hasToken" class="logout-btn" @click="logout">退出登录</button>
    </div>
  </aside>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { healthCheck } from '../api'

const router = useRouter()
const connected = ref(false)
const hasToken = computed(() => !!localStorage.getItem('admin_token'))

function logout() {
  localStorage.removeItem('admin_token')
  router.push('/login')
}

onMounted(async () => {
  try {
    await healthCheck()
    connected.value = true
  } catch {
    connected.value = false
  }
})
</script>

<style scoped>
.sidebar {
  position: fixed;
  top: 0;
  left: 0;
  width: var(--sidebar-width);
  height: 100vh;
  background: var(--sidebar-bg);
  color: var(--sidebar-text);
  display: flex;
  flex-direction: column;
  z-index: 100;
}

.sidebar-brand {
  padding: 24px 20px;
  display: flex;
  align-items: center;
  gap: 12px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.08);
}

.brand-icon {
  font-size: 28px;
}

.brand-text h1 {
  font-size: 16px;
  font-weight: 700;
  color: white;
}

.brand-text span {
  font-size: 12px;
  color: var(--sidebar-text);
}

.sidebar-nav {
  flex: 1;
  padding: 16px 12px;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.nav-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 14px;
  border-radius: 8px;
  color: var(--sidebar-text);
  text-decoration: none;
  font-size: 14px;
  font-weight: 500;
  transition: all 0.15s;
}

.nav-item:hover {
  background: rgba(255, 255, 255, 0.08);
  color: white;
}

.nav-item.active {
  background: var(--sidebar-active);
  color: white;
}

.nav-icon {
  font-size: 18px;
}

.nav-divider {
  height: 1px;
  background: rgba(255, 255, 255, 0.08);
  margin: 4px 8px;
}

.sidebar-footer {
  padding: 16px 20px;
  border-top: 1px solid rgba(255, 255, 255, 0.08);
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.logout-btn {
  background: rgba(255, 255, 255, 0.08);
  color: var(--sidebar-text);
  border: 1px solid rgba(255, 255, 255, 0.12);
  padding: 6px 0;
  border-radius: 6px;
  cursor: pointer;
  font-size: 12px;
  transition: all 0.15s;
}

.logout-btn:hover {
  background: rgba(239, 68, 68, 0.3);
  color: #fca5a5;
  border-color: rgba(239, 68, 68, 0.4);
}

.status-indicator {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 12px;
}

.dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
}

.dot.online {
  background: var(--success);
  box-shadow: 0 0 6px var(--success);
}

.dot.offline {
  background: var(--danger);
}
</style>
