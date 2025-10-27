import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      '/ws': { target: 'http://0.0.0.0:8000', changeOrigin: true, ws: true },
      '/health': { target: 'http://0.0.0.0:8000', changeOrigin: true },
      '/upload-video': { target: 'http://0.0.0.0:8000', changeOrigin: true },
      '/ingest-youtube': { target: 'http://0.0.0.0:8000', changeOrigin: true },
      '/stream': { target: 'http://0.0.0.0:8000', changeOrigin: true },
    },
  },
})
