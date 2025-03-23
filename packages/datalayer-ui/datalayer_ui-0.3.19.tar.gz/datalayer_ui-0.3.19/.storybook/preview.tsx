/*
 * Copyright (c) 2021-2024 Datalayer, Inc.
 *
 * Datalayer License
 */

import React from "react";
import { CodeOrSourceMdx } from "@storybook/addon-docs";
import { Mermaid } from "mdx-mermaid/lib/Mermaid"
import mermaid from 'mermaid';
import zenuml from '@mermaid-js/mermaid-zenuml';
import type { Preview } from '@storybook/react';
import { toolbarTypes, withDatalayer } from '../src/stories/_utils/story-helpers';

import '@jupyterlab/apputils/style/materialcolors.css';
import '@jupyterlab/application/style/buttons.css';
import '@jupyterlab/ui-components/style/base.css';
import '@jupyterlab/apputils/style/dialog.css';

import './custom.css';

export const globalTypes = toolbarTypes;
export const decorators = [withDatalayer];

const init = mermaid.registerExternalDiagrams([zenuml]);

const preview: Preview = {
  parameters: {
    docs: {
      components: {
        code: props => {
          return props.className?.includes("mermaid")
            ? 
              <Mermaid chart={props.children} />
            :
              <CodeOrSourceMdx {...props} />
        }
      },
    },
    actions: { argTypesRegex: '^on[A-Z].*' },
    html: {
      root: '#html-addon-root',
      removeEmptyComments: true,
    },
    controls: {
      expanded: true,
      hideNoControlsWarning: true,
      matchers: {
        color: /(background|color)$/i,
        date: /Date$/i,
      },
    },
    /*
    options: {
      storySort: (a, b) => {
        return (a.id === b.id ? 0 : a.id.localeCompare(b.id, undefined, { numeric: true }))
      }
    },
    */
    options: {
      storySort: {
          method: 'alphabetical',
          order: [
            'Welcome', 'Open Science Cases', 'Actors', 'Strategies', 'Quadrant',
              'Planning', 'Running on the Edge', 'Data Scientist Journey',
            'IAM', [
              'IAM', 'Personal Account', 'Sign Up', 'Sign In', 'Sign Out', 'Profile',
              'Organizations', 'Teams', 'Enterprises', 'Permissions', 'Roles', 'Vault', 'Tokens', 'MFA',
              'New Password', 'New Password Confirm', 'OIDC Provider', 'SAML Provider', 'SCIM',
            ],
            'Contents', [
              'Contents', 'Contents Browser', 'Local Files', 'S3 Buckets', 'Git Repositories', 'Data Sources',
            ],
            'Environments', [
              'Environments', 'Platform Environments', 'User Environments', 
              'Distributed Frameworks', 'Accelerated Computing (GPU)', 'Requests and Limits',
            ],
            'Kernels', [
              'Kernels', 'Protocol', 'State', 'Picker', 'Launcher', 'Server Kernels',
              'Browser Kernels', 'Remote Kernels', 'Terminal',
            ],
            'Notebooks', [
              'Notebooks', 'Base Editor', 'Lab Editor', 'Rich Editor', 'Cell', 'SQL Cell', 'Cells DAG', 'Console',
              'IPyWidgets', 'Input Forms', 'Mime Renderers', 'LSP Autocomplete', 'Dataframe Explorer',
              'Variables Explorer', 'Snippets', 'Table of Contents', 'Exports', 'Extensions',
            ],
            'Spaces', [
              'Spaces', 'Members', 'Contents', 'Notebooks', 'Environments', 'Kernels', 'Access Control', 'Settings',
            ],
            'Collaboration', [
              'Collaboration', 'Rooms', 'Collaborators', 'Room Access', 'Collaborative Notebook',
              'Collaborative Kernel', 'Versioning', 'Commenting', 'Suggestions',
            ],
            'Publications', [
              'Publications', 'Library', 'Search',
            ],
            'Deployments', [
              'Deployments', 'Viewer', 'Embedding', 'Functions', 'Applications', 'DAG', 'Access Control',
            ],
            'Automation', [
              'Automation', 'Scheduler',
            ],
            'Management', [
              'Management', 'Configuration', 'Services Monitoring', 'Usage Monitoring', 'Calendar', 'Logs Aggregation', 'SLA', 'Status', 'Alerting',
              'Availability', 'Benchmarks', 'Backup', 'Restore', 'Versions', 'Upgrades', 'License', 'Support', 'Auditing',
            ],
            'Usage', [
              'Usage', 'Tiers', 'Costs' , 'Activity' , 'Credits' , 'Redeem Credits',  'Billing', 'Refund', 'Ads',
            ],
            'AI', [
              'AI', 'AI Assistant', 'AI Completer',
            ],
            'Education', [
              'Education', 'Exercises', 'Lessons', 'Asisgnment', 'Grading',
            ],
            'Integrations', [
              'Integrations', 'JupyterHub',
            ],
            'About', [
              'About', 'Sponsor', 'Trust', 'Terms of Service', 'Comparison', 'Testimonials', 'Dataliens', 'FAQ',
            ],
          ],
          locales: 'en-US',
      }
    },
  },
};

export default preview;
