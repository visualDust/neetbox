import { defineConfig } from "cypress";

const isCI = process.env.CI == "true";

export default defineConfig({
  e2e: {
    baseUrl: isCI ? "http://localhost:5000" : "http://localhost:5173",
    testIsolation: false,
    setupNodeEvents(on, config) {
      // implement node event listeners here
    },
  },
});
