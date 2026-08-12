import { defineConfig, loadEnv } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), '')
  return {
    plugins: [react()],
    server: {
      port: 5173,
      host: true,
    },
    define: {
      // Hace que VITE_API_URL esté disponible en el código del navegador
      'import.meta.env.VITE_API_URL': JSON.stringify(
        env.VITE_API_URL || 'http://localhost:8000'
      )
    }
  }
})
