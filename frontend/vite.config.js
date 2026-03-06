import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'

// https://vite.dev/config/
export default defineConfig({
  plugins: [
    react(),
    tailwindcss(),
  ],
  server: {
    host: '::',
    proxy: {
      '/auth': 'http://127.0.0.1:8000',
      '/api': 'http://127.0.0.1:8000',
      '/cases': 'http://127.0.0.1:8000',
      '/notifications': 'http://127.0.0.1:8000',
      '/search': 'http://127.0.0.1:8000',
      '/uploads': 'http://127.0.0.1:8000',
    }
  }
})
