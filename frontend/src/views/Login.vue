<template>
  <div class="login-page">
    <div class="login-card">
      <div class="login-header">
        <div class="login-icon">🔐</div>
        <h1>Hexo Admin</h1>
        <p>请输入管理员密码</p>
      </div>
      <form @submit.prevent="handleLogin" class="login-form">
        <div class="form-group">
          <input
            v-model="password"
            type="password"
            placeholder="管理员密码"
            :disabled="loading"
            autofocus
          />
        </div>
        <p v-if="error" class="login-error">{{ error }}</p>
        <button type="submit" class="btn btn-primary btn-lg login-btn" :disabled="loading">
          {{ loading ? '登录中...' : '登 录' }}
        </button>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import api from '../api'

const router = useRouter()
const password = ref('')
const error = ref('')
const loading = ref(false)

async function handleLogin() {
  if (!password.value) {
    error.value = '请输入密码'
    return
  }
  loading.value = true
  error.value = ''
  try {
    const res = await api.post('/auth/login', { password: password.value })
    if (res.token) {
      localStorage.setItem('admin_token', res.token)
      router.push('/')
    } else {
      // 未设置密码，直接进入
      router.push('/')
    }
  } catch (err) {
    if (err.response?.status === 401) {
      error.value = '密码错误，请重试'
    } else {
      error.value = '登录失败，请检查网络连接'
    }
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-page {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: calc(100vh - 64px);
}

.login-card {
  background: var(--card-bg);
  border-radius: 16px;
  border: 1px solid var(--border);
  padding: 48px 40px;
  width: 100%;
  max-width: 400px;
  box-shadow: 0 4px 24px rgba(0, 0, 0, 0.08);
}

.login-header {
  text-align: center;
  margin-bottom: 32px;
}

.login-icon {
  font-size: 48px;
  margin-bottom: 12px;
}

.login-header h1 {
  font-size: 22px;
  font-weight: 700;
  margin-bottom: 6px;
}

.login-header p {
  color: var(--text-secondary);
  font-size: 14px;
}

.login-form .form-group {
  margin-bottom: 16px;
}

.login-form input {
  width: 100%;
  padding: 12px 16px;
  border: 1px solid var(--border);
  border-radius: 10px;
  font-size: 15px;
  text-align: center;
  letter-spacing: 4px;
  transition: border-color 0.2s;
}

.login-form input:focus {
  outline: none;
  border-color: var(--primary);
  box-shadow: 0 0 0 3px rgba(79, 70, 229, 0.1);
}

.login-error {
  color: var(--danger);
  font-size: 13px;
  text-align: center;
  margin-bottom: 12px;
}

.login-btn {
  width: 100%;
  padding: 12px;
  font-size: 16px;
}
</style>
