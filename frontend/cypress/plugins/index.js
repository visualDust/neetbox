// https://www.cypress.io/blog/2021/03/01/generate-high-resolution-videos-and-screenshots

// let's increase the browser window size when running headlessly
// this will produce higher resolution images and videos
// https://on.cypress.io/browser-launch-api
on("before:browser:launch", (browser = {}, launchOptions) => {
  console.log("launching browser %s is headless? %s", browser.name, browser.isHeadless);

  // the browser width and height we want to get
  // our screenshots and videos will be of that resolution
  const width = 1920;
  const height = 1080;

  console.log("setting the browser window size to %d x %d", width, height);

  if (browser.name === "electron" && browser.isHeadless) {
    // might not work on CI for some reason
    launchOptions.preferences.width = width;
    launchOptions.preferences.height = height;
  }

  // IMPORTANT: return the updated browser launch options
  return launchOptions;
});
