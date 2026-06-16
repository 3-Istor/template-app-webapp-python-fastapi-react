import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

const backendHost = process.env.BACKEND_HOST || 'http://localhost:8000';

export default defineConfig({
  plugins: [react()],
  server: {
    port: 3001,
    host: true, 
    watch: {
      usePolling: true,
    },
    proxy: {
      '/api': {
        target: backendHost,
        changeOrigin: true,
        rewrite: (path) => path
      }
    }
  }
})
