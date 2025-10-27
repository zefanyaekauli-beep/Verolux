import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
        server: {
          port: 5173,
         proxy: {
           '/ws': { target: 'http://127.0.0.1:8002', changeOrigin: true, ws: true },
           '/health': { target: 'http://127.0.0.1:8002', changeOrigin: true },
           '/upload-video': { target: 'http://127.0.0.1:8002', changeOrigin: true },
           '/ingest-youtube': { target: 'http://127.0.0.1:8002', changeOrigin: true },
           '/stream': { target: 'http://127.0.0.1:8002', changeOrigin: true },
           '/config': { target: 'http://127.0.0.1:8002', changeOrigin: true },
           '/model-status': { target: 'http://127.0.0.1:8002', changeOrigin: true },
           '/gate-config': { target: 'http://127.0.0.1:8002', changeOrigin: true },
           '/session-data': { target: 'http://127.0.0.1:8002', changeOrigin: true },
           '/start-session': { target: 'http://127.0.0.1:8002', changeOrigin: true },
           '/generate-report': { target: 'http://127.0.0.1:8002', changeOrigin: true },
           '/video-files': { target: 'http://127.0.0.1:8002', changeOrigin: true },
           '/download-report': { target: 'http://127.0.0.1:8002', changeOrigin: true },
         },
        },
})