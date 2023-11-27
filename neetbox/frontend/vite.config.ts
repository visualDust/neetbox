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
      '/web/': {
        target: 'http://127.0.0.1:5000',
        changeOrigin: true,
        // rewrite: (path) => path.replace(/^\/api\//, ''),
      },
      '/ws/': {
        target: 'http://127.0.0.1:5001',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/ws\//, ''),
      }
    }
  },
  build: {
    outDir: "../frontend_dist"
  }
})
