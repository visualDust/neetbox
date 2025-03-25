import { defineConfig } from "@rsbuild/core";
import { pluginReact } from "@rsbuild/plugin-react";
import { SemiRspackPlugin } from "@douyinfe/semi-rspack-plugin";

const server = new URL("http://127.0.0.1:20202");

export default defineConfig({
  plugins: [pluginReact()],
  source: {
    alias: {
      "@": "./src",
    },
    entry: { index: "./src/main.tsx" },
  },
  tools: {
    rspack: (config) => {
      config.plugins!.push(
        new SemiRspackPlugin({
          theme: "@semi-bot/semi-theme-strapi",
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
      "/ws/project/": {
        target: `ws://${server.host}`,
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
