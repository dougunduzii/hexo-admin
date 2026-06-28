import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
})

// 请求拦截器 — 附加认证 token
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('admin_token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// 响应拦截器
api.interceptors.response.use(
  (response) => response.data,
  (error) => {
    const message = error.response?.data?.detail || error.message || '请求失败'
    console.error('API Error:', message)
    // 401 时清除过期 token
    if (error.response?.status === 401) {
      localStorage.removeItem('admin_token')
    }
    return Promise.reject(error)
  }
)

// ==================== 文章 API ====================

/** 获取文章列表 */
export function getPosts(params = {}) {
  return api.get('/posts', { params })
}

/** 获取单篇文章 */
export function getPost(id) {
  return api.get(`/posts/${id}`)
}

/** 创建文章 */
export function createPost(data) {
  return api.post('/posts', data)
}

/** 更新文章 */
export function updatePost(id, data) {
  return api.put(`/posts/${id}`, data)
}

/** 删除文章 */
export function deletePost(id) {
  return api.delete(`/posts/${id}`)
}

// ==================== 同步 API ====================

/** 从文件系统同步 */
export function syncPosts() {
  return api.post('/sync')
}

// ==================== 统计 API ====================

/** 获取统计信息 */
export function getStats() {
  return api.get('/stats')
}

// ==================== 健康检查 ====================

/** 健康检查 */
export function healthCheck() {
  return api.get('/health')
}

// ==================== 设置 API ====================

/** 获取 Butterfly 配置 */
export function getSettings() {
  return api.get('/settings')
}

/** 更新配置 */
export function updateSettings(data) {
  return api.put('/settings', data)
}

// ==================== 图片 API ====================

/** 获取图片列表 */
export function getImages(dir = '') {
  return api.get('/images', { params: { dir } })
}

/** 上传图片 */
export function uploadImage(file, dir = 'imgs') {
  const formData = new FormData()
  formData.append('file', file)
  return api.post(`/images/upload?dir=${dir}`, formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  })
}

/** 删除图片 */
export function deleteImage(path) {
  return api.delete('/images', { params: { path } })
}

/**
 * 获取图片的可用 URL。
 * 开发环境通过 API 代理（Vite 无法直接访问 blog-hexo/source/），
 * 生产环境 nginx 直接从博客根目录 serve。
 */
export function imageSrc(path) {
  if (!path) return ''
  // Vite 注入的全局变量，build 时会被替换为 true
  if (import.meta.env.PROD) return path
  return `/api/images/file?path=${encodeURIComponent(path)}`
}

// ==================== 部署 API ====================

/** 一键部署 hexo generate --deploy（超时 120 秒） */
export function deployBlog() {
  return api.post('/deploy', null, { timeout: 120000 })
}

// ==================== 认证 API ====================

/** 检查登录状态 */
export function checkAuth() {
  return api.get('/auth/check')
}

export default api
