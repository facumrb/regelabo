import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    host: true,
    // El navegador habla solo con este origen; /api se reenvía al backend (igual que en producción)
    proxy: { '/api': 'http://localhost:8000' }
  }
})
