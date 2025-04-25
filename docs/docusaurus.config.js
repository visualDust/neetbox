// @ts-check
// Note: type annotations allow type checking and IDEs autocompletion

const lightCodeTheme = require("prism-react-renderer").themes.github;
const darkCodeTheme = require("prism-react-renderer").themes.dracula;

/** @type {import('@docusaurus/types').Config} */
const config = {
  title: "NEETBOX",
  tagline:
    "Logging/Debugging/Tracing/Managing/Facilitating long running python projects, especially a replacement of tensorboard for deep learning projects.",
  favicon: "img/logo.svg",

  // Set the production url of your site here
  url: "https://neetbox.550w.host",
  // Set the /<baseUrl>/ pathname under which your site is served
  // For GitHub pages deployment, it is often '/<projectName>/'
  baseUrl: "/",

  // GitHub pages deployment config.
  // If you aren't using GitHub pages, you don't need these.
  organizationName: "NEET-CV", // Usually your GitHub org/user name.
  projectName: "NEETBOX", // Usually your repo name.

  onBrokenLinks: "throw",
  onBrokenMarkdownLinks: "warn",

  // Even if you don't use internalization, you can use this field to set useful
  // metadata like html lang. For example, if your site is Chinese, you may want
  // to replace "en" with "zh-Hans".
  i18n: {
    defaultLocale: "en",
    locales: ["en"],
  },

  presets: [
    [
      "classic",
      /** @type {import('@docusaurus/preset-classic').Options} */
      ({
        docs: {
          sidebarPath: require.resolve("./sidebars.js"),
          editUrl: "https://dev.github.com/visualdust/neetbox/",
          sidebarCollapsed: false,
        },
        theme: {
          customCss: require.resolve("./src/css/custom.css"),
        },
      }),
    ],
  ],

  themeConfig:
    /** @type {import('@docusaurus/preset-classic').ThemeConfig} */
    ({
      image: "img/docusaurus-social-card.png",
      navbar: {
        title: "NEETBOX",
        logo: {
          alt: "DOC LOGO",
          src: "img/logo.svg",
        },
        items: [
          {
            to: "/docs/howto/",
            activeBasePath: "/docs/howto/",
            label: "Docs",
            position: "left",
          },
          {
            to: "/docs/apidocs/",
            activeBasePath: "/docs/apidocs/",
            label: "API Docs",
            position: "left",
          },
          {
            to: "https://github.com/visualDust/neetbox",
            label: "Github",
            position: "right",
          },
          {
            to: "https://www.550w.host",
            label: "About",
            position: "right",
          }
        ],
      },
      footer: {
        copyright: `Open socurce license MIT, ${new Date().getFullYear()}, NEETBOX all right reserved`,
      },
      prism: {
        theme: lightCodeTheme,
        darkTheme: darkCodeTheme,
      },
    }),
};

module.exports = config;
