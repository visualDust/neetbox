import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import SemiPlugin from "vite-plugin-semi-theme";

const server = new URL('http://127.0.0.1:5000');

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react(), SemiPlugin({
    theme: "@semi-bot/semi-theme-nyx-c"
  }),],
  server: {
    proxy: {
      '/web/': {
        target: server.href,
        changeOrigin: true,
        // rewrite: (path) => path.replace(/^\/api\//, ''),
      },
      '/ws/': {
        target: `ws://${server.host}:${(+server.port) + 1}`,
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/ws\//, ''),
        ws: true,
      }
    }
  },
  build: {
    outDir: "../frontend_dist"
  }
})
