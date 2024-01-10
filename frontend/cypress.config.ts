import { defineConfig } from "cypress";

const isCI = process.env.CI == "true";

export default defineConfig({
  viewportHeight: 1000,
  viewportWidth: 1600,
  scrollBehavior: "center",
  video: true,
  videoCompression: 28,
  e2e: {
    baseUrl: isCI ? "http://localhost:10101" : "http://localhost:5173",
    testIsolation: false,
  },
  setupNodeEvents(on, _config) {
    on("before:browser:launch", (browser, launchOptions) => {
      if (browser.name === "electron" && browser.isHeadless) {
        launchOptions.preferences.width = 1920;
        launchOptions.preferences.height = 1080;
      }

      return launchOptions;
    });
  },
});
