import { defineConfig } from "cypress";

const isCI = process.env.CI == "true";

export default defineConfig({
  viewportHeight: 1000,
  viewportWidth: 1600,
  scrollBehavior: "center",
  video: true,
  videoCompression: 28,
  e2e: {
    baseUrl: isCI ? "http://localhost:5000" : "http://localhost:5173",
    testIsolation: false,
  },
});
