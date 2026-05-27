import { defineConfig } from 'vite'
import path from 'node:path'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react(), tailwindcss()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
  server: {
    watch: {
      // json-server zapisuje POST-y do db.json (i czasem routes.json).
      // Bez tego Vite robi full reload przy każdym sendMessage.
      ignored: ['**/db.json', '**/routes.json'],
    },
  },
})
