import { defineConfig } from "@rsbuild/core";
import { pluginReact } from "@rsbuild/plugin-react";
import { SemiRspackPlugin } from "@douyinfe/semi-rspack-plugin";

const server = new URL("http://127.0.0.1:5000");

export default defineConfig({
  plugins: [pluginReact()],
  // tools: {
  //   rspack: (config) => {
  //     config.plugins!.push(
  //       new SemiRspackPlugin({
  //         theme: "@semi-bot/semi-theme-nyx-c",
  //       }),
  //     );
  //   },
  // },
  source: {
    entry: { index: "./src/main.tsx" },
  },
  html: {
    template: "./index.html",
  },
  server: {
    port: 5173,
    proxy: {
      "/web/": {
        target: server.href,
      },
      "/ws/": {
        target: `ws://${server.host}:${+server.port + 1}`,
        pathRewrite: { "/ws/": "" },
      },
    },
  },
  output: {
    distPath: {
      root: "../neetbox/frontend_dist",
    },
  },
});
