import {themes as prismThemes} from 'prism-react-renderer';
import type {Config} from '@docusaurus/types';
import type * as Preset from '@docusaurus/preset-classic';

const config: Config = {
  title: 'Humanoid Robotics Textbook',
  tagline: 'AI-Native Learning Platform for Humanoid Robotics',
  favicon: 'img/favicon.svg',

  // Production URL - Vercel
  url: 'https://hackathon-one-humanoid-robotic-book.vercel.app',
  baseUrl: '/',

  // GitHub pages deployment config
  organizationName: 'Shaistatosif',
  projectName: 'Hackathon1-humanoid-robotic-book',
  trailingSlash: false,

  onBrokenLinks: 'warn',
  onBrokenMarkdownLinks: 'warn',

  // Internationalization - English and Urdu
  i18n: {
    defaultLocale: 'en',
    locales: ['en', 'ur'],
    localeConfigs: {
      en: {
        label: 'English',
        direction: 'ltr',
        htmlLang: 'en-US',
      },
      ur: {
        label: 'اردو',
        direction: 'rtl',
        htmlLang: 'ur-PK',
      },
    },
  },

  presets: [
    [
      'classic',
      {
        docs: {
          sidebarPath: './sidebars.ts',
          routeBasePath: '/', // Serve docs at root
          editUrl:
            'https://github.com/Shaistatosif/Hackathon1-humanoid-robotic-book/tree/001-book-generation/frontend/',
        },
        blog: false, // Disable blog
        theme: {
          customCss: './src/css/custom.css',
        },
      } satisfies Preset.Options,
    ],
  ],

  // Theme plugins
  themes: [
    // Local search can be added here when needed
    // '@docusaurus/theme-search-algolia' is available for production
  ],

  themeConfig: {
    // Social card image
    image: 'img/social-card.svg',

    // Search configuration (placeholder for Algolia)
    // To enable, add your Algolia credentials
    // algolia: {
    //   appId: 'YOUR_APP_ID',
    //   apiKey: 'YOUR_SEARCH_API_KEY',
    //   indexName: 'humanoid-robotics-textbook',
    // },

    navbar: {
      title: 'Humanoid Robotics',
      logo: {
        alt: 'Humanoid Robotics Textbook Logo',
        src: 'img/logo.svg',
      },
      items: [
        {
          type: 'docSidebar',
          sidebarId: 'textbookSidebar',
          position: 'left',
          label: 'Textbook',
        },
        {
          to: '/dashboard',
          label: 'Dashboard',
          position: 'left',
        },
        {
          to: '/login',
          label: 'Login',
          position: 'right',
        },
        {
          type: 'localeDropdown',
          position: 'right',
        },
        {
          href: 'https://github.com/Shaistatosif/Hackathon1-humanoid-robotic-book',
          label: 'GitHub',
          position: 'right',
        },
      ],
    },

    footer: {
      style: 'dark',
      links: [
        {
          title: 'Learn',
          items: [
            {
              label: 'Introduction',
              to: '/intro',
            },
            {
              label: 'Chapter 1',
              to: '/chapter-1',
            },
          ],
        },
        {
          title: 'Features',
          items: [
            {
              label: 'AI Chatbot',
              to: '/intro#chatbot',
            },
            {
              label: 'Quizzes',
              to: '/intro#quizzes',
            },
          ],
        },
        {
          title: 'More',
          items: [
            {
              label: 'GitHub',
              href: 'https://github.com/Shaistatosif/Hackathon1-humanoid-robotic-book',
            },
          ],
        },
      ],
      copyright: `Copyright © ${new Date().getFullYear()} Shaista Tosif. Built with Docusaurus.`,
    },

    prism: {
      theme: prismThemes.github,
      darkTheme: prismThemes.dracula,
      additionalLanguages: ['python', 'bash', 'json'],
    },

    // Color mode configuration
    colorMode: {
      defaultMode: 'light',
      disableSwitch: false,
      respectPrefersColorScheme: true,
    },

    // Announcement bar (optional)
    announcementBar: {
      id: 'hackathon_notice',
      content:
        '🤖 AI-Powered Humanoid Robotics Textbook - Built for the future of learning! <a target="_blank" rel="noopener noreferrer" href="https://github.com/Shaistatosif/Hackathon1-humanoid-robotic-book">View on GitHub</a>',
      backgroundColor: '#3b82f6',
      textColor: '#ffffff',
      isCloseable: true,
    },
  } satisfies Preset.ThemeConfig,
};

export default config;
