import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import SemiPlugin from "vite-plugin-semi-theme";

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react(), SemiPlugin({
    theme: "@semi-bot/semi-theme-nyx-c"
  }),],
  server: {
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:20202',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, ''),
      }
    }
  }
})
