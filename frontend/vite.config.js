import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

// base 路径 — 部署到子路径时修改此处（如 '/admin/'），或通过 `vite build --base=/admin/` 指定
export default defineConfig(({ mode }) => ({
  plugins: [vue()],
  base: mode === 'production' ? '/admin/' : '/',
  server: {
    port: 5173,
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
      },
    },
  },
}))
