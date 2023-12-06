// @ts-check
// Note: type annotations allow type checking and IDEs autocompletion

const lightCodeTheme = require('prism-react-renderer/themes/github');
const darkCodeTheme = require('prism-react-renderer/themes/dracula');

/** @type {import('@docusaurus/types').Config} */
const config = {
  title: 'NEETBOX',
  tagline: 'Logging/Debugging/Tracing/Managing/Facilitating long running python projects, especially a replacement of tensorboard for deep learning projects.',
  favicon: 'img/favicon.png',

  // Set the production url of your site here
  url: 'https://neetbox.550w.host',
  // Set the /<baseUrl>/ pathname under which your site is served
  // For GitHub pages deployment, it is often '/<projectName>/'
  baseUrl: '/',

  // GitHub pages deployment config.
  // If you aren't using GitHub pages, you don't need these.
  organizationName: 'NEET-CV', // Usually your GitHub org/user name.
  projectName: 'NEETBox', // Usually your repo name.

  onBrokenLinks: 'throw',
  onBrokenMarkdownLinks: 'warn',

  // Even if you don't use internalization, you can use this field to set useful
  // metadata like html lang. For example, if your site is Chinese, you may want
  // to replace "en" with "zh-Hans".
  i18n: {
    defaultLocale: 'en',
    locales: ['en'],
  },

  presets: [
    [
      'classic',
      /** @type {import('@docusaurus/preset-classic').Options} */
      ({
        docs: {
          sidebarPath: require.resolve('./sidebars.js'),
          // Please change this to your repo.
          // Remove this to remove the "edit this page" links.
          editUrl:
            'https://dev.github.com/visualdust/neetbox/',
        },
        theme: {
          customCss: require.resolve('./src/css/custom.css'),
        },
      }),
    ],
  ],

  themeConfig:
    /** @type {import('@docusaurus/preset-classic').ThemeConfig} */
    ({
      // Replace with your project's social card
      image: 'img/docusaurus-social-card.jpg',
      navbar: {
        title: 'NEETBOX',
        logo: {
          alt: 'DOC LOGO',
          src: 'img/logo.svg',
        },
        items: [
          {
            to: '/docs/howto',
            activeBasePath: '/docs/howto',
            label: 'How To',
            position: 'left'
          },
          {
            to: '/docs/guide',
            activeBasePath: '/docs/guide',
            label: 'Doc',
            position: 'left'
          },
          {
            to: 'https://github.com/visualDust/neetbox',
            label: 'Github',
            position: 'right'
          }
        ],
      },
      footer: {
        copyright: `Copyright © ${new Date().getFullYear()} NEETBox`,
      },
      prism: {
        theme: lightCodeTheme,
        darkTheme: darkCodeTheme,
      },
    }),
};

module.exports = config;
