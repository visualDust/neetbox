import { defineConfig } from "cypress";

const isCI = process.env.CI == "true";

export default defineConfig({
  viewportHeight: 1000,
  viewportWidth: 1600,
  scrollBehavior: "center",
  e2e: {
    baseUrl: isCI ? "http://localhost:5000" : "http://localhost:5173",
    testIsolation: false,
    setupNodeEvents(on, config) {
      // implement node event listeners here
    },
  },
});
