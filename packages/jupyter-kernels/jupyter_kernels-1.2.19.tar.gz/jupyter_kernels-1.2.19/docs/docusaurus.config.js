/*
 * Copyright (c) 2023-2024 Datalayer, Inc.
 *
 * Datalayer License
 */

/** @type {import('@docusaurus/types').DocusaurusConfig} */
module.exports = {
  title: '🪐 ⚪ Jupyter Kernels documentation',
  tagline: 'Jupyter Kernels documentation',
  url: 'https://datalayer.io',
  baseUrl: '/',
  onBrokenLinks: 'throw',
  onBrokenMarkdownLinks: 'warn',
  favicon: 'img/favicon.ico',
  organizationName: 'datalayer', // Usually your GitHub org/user name.
  projectName: 'datalayer', // Usually your repo name.
  markdown: {
    mermaid: true
  },
  themes: ['@docusaurus/theme-mermaid'],
  themeConfig: {
    colorMode: {
      defaultMode: 'light',
      disableSwitch: true
    },
    navbar: {
      title: 'Jupyter Kernels Docs',
      logo: {
        alt: 'Datalayer Logo',
        src: 'img/datalayer/logo.svg'
      },
      items: [
        {
          type: 'doc',
          docId: 'index',
          position: 'left',
          label: 'About'
        },
        /*
        {
          type: 'doc',
          docId: 'jupyterlab/index',
          position: 'left',
          label: 'JupyterLab'
        },
        {
          type: 'doc',
          docId: 'cli/index',
          position: 'left',
          label: 'CLI'
        },
        {
          type: 'doc',
          docId: 'contribute/index',
          position: 'left',
          label: 'Contribute'
        },
        */
        {
          href: 'https://www.linkedin.com/company/datalayer',
          position: 'right',
          className: 'header-linkedin-link',
          'aria-label': 'LinkedIn'
        },
        {
          href: 'https://bsky.app/profile/datalayer.io',
          position: 'right',
          className: 'header-bluesky-link',
          'aria-label': 'Bluesky'
        },
        {
          href: 'https://github.com/datalayer/jupyter-kernels',
          position: 'right',
          className: 'header-github-link',
          'aria-label': 'GitHub repository'
        },
        {
          href: 'https://datalayer.io',
          position: 'right',
          className: 'header-datalayer-io-link',
          'aria-label': 'Datalayer IO'
        }
      ]
    },
    footer: {
      style: 'dark',
      links: [
        {
          title: 'Docs',
          items: [
            {
              label: 'Jupyter Kernels',
              to: '/docs'
            }
          ]
        },
        {
          title: 'Community',
          items: [
            {
              label: 'GitHub',
              href: 'https://github.com/datalayer'
            },
            {
              label: 'Bluesky',
              href: 'https://assets.datalayer.tech/logos-social-grey/youtube.svg'
            },
            {
              label: 'LinkedIn',
              href: 'https://www.linkedin.com/company/datalayer'
            }
          ]
        },
        {
          title: 'More',
          items: [
            {
              label: 'Datalayer IO',
              href: 'https://datalayer.io'
            },
            {
              label: 'Datalayer Tech',
              href: 'https://datalayer.tech'
            },
            {
              label: 'Clouder',
              href: 'https://clouder.sh'
            },
            {
              label: 'Datalayer Blog',
              href: 'https://datalayer.blog'
            }
          ]
        }
      ],
      copyright: `Copyright © ${new Date().getFullYear()} Datalayer, Inc.`
    }
  },
  presets: [
    [
      '@docusaurus/preset-classic',
      {
        docs: {
          sidebarPath: require.resolve('./sidebars.js'),
          // Please change this to your repo.
          editUrl: 'https://github.com/datalayer/jupyter-kernels/edit/main/'
        },
        theme: {
          customCss: require.resolve('./src/css/custom.css')
        }
      }
    ]
  ]
};
