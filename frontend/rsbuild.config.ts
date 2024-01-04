import { defineConfig } from "@rsbuild/core";
import { pluginReact } from "@rsbuild/plugin-react";
import { SemiRspackPlugin } from "@douyinfe/semi-rspack-plugin";

const server = new URL("http://127.0.0.1:10101");

export default defineConfig({
  plugins: [pluginReact()],
  tools: {
    rspack: (config) => {
      config.plugins!.push(
        new SemiRspackPlugin({
          // theme: "@semi-bot/semi-theme-nyx-c",
        }),
      );
      // config.optimization = { ...config.optimization, minimize: false };
      config.module = {
        ...config.module,
        rules: [
          ...(config.module?.rules ?? []),
          {
            test: /echarts/,
            sideEffects: true,
          },
        ],
      };
    },
  },
  source: {
    entry: { index: "./src/main.tsx" },
  },
  html: {
    title: "Neetbox",
    favicon: "./public/logo.svg",
  },
  performance: {
    chunkSplit: { strategy: "all-in-one" },
  },
  server: {
    port: 5173,
    proxy: {
      "/api/": {
        target: server.href,
      },
      "/ws/": {
        target: `ws://${server.host}:${+server.port + 1}`,
        pathRewrite: { "/ws/": "" },
      },
    },
  },
  // dev: {
  //   writeToDisk: true,
  // },
  output: {
    assetPrefix: "/web/",
    distPath: {
      root: "../neetbox/frontend_dist",
    },
  },
});
