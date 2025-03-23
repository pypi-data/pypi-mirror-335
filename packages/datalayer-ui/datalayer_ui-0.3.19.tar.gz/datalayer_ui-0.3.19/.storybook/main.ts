/*
 * Copyright (c) 2021-2024 Datalayer, Inc.
 *
 * Datalayer License
 */

import type { StorybookConfig } from '@storybook/react-webpack5';
import { RuleSetRule } from 'webpack';
import { join, dirname } from 'path';

/**
 * This function is used to resolve the absolute path of a package.
 * It is needed in projects that use Yarn PnP or are set up within a monorepo.
 */
function getAbsolutePath(value: string): any {
  return dirname(require.resolve(join(value, 'package.json')));
}

const config: StorybookConfig = {
  stories: [
    '../src/stories/**/*.mdx',
    '../src/stories/**/*.stories.@(js|jsx|mjs|ts|tsx)',
  ],
  previewHead: (head) => `${head}
    <title>Datalayer Tech Storybook<title>
    <link
      href="https://use.fontawesome.com/releases/v5.0.10/css/all.css"
      rel="stylesheet"
    />
    <script id="datalayer-config-data" type="application/json">
      {
        "jupyterServerUrl": "https://prod1.datalayer.run/api/jupyter-server",
        "jupyterServerToken": "60c1661cc408f978c309d04157af55c9588ff9557c9380e4fb50785750703da6"
      }
    </script>
    <script id="jupyter-config-data" type="application/json">
      {
        "appName": "Datalayer",
        "baseUrl": "https://prod1.datalayer.run/api/jupyter-server",
        "wsUrl": "wss://prod1.datalayer.run/api/jupyter-server",
        "token": "60c1661cc408f978c309d04157af55c9588ff9557c9380e4fb50785750703da6",
        "appUrl": "/lab",
        "themesUrl": "/lab/api/themes",
        "disableRTC": false,
        "terminalsAvailable": "false",
        "mathjaxUrl": "https://cdnjs.cloudflare.com/ajax/libs/mathjax/2.7.5/MathJax.js",
        "mathjaxConfig": "TeX-AMS_CHTML-full,Safe"
      }
    </script>
    <script
      data-jupyter-widgets-cdn="https://cdn.jsdelivr.net/npm/"
      data-jupyter-widgets-cdn-only="true"
    >
    </script>
    <link rel="shortcut icon"
      href="data:image/x-icon;base64,iVBORw0KGgoAAAANSUhEUgAAACAAAAAgCAYAAABzenr0AAAABHNCSVQICAgIfAhkiAAAAAlwSFlzAAAN1wAADdcBQiibeAAAABl0RVh0U29mdHdhcmUAd3d3Lmlua3NjYXBlLm9yZ5vuPBoAAAC7SURBVFiF7ZU9CgIxEIXfTHbPopfYc+pJ9AALtmJnZSOIoJWFoCTzLHazxh/Ebpt5EPIxM8XXTCKTxYyMCYwJFhOYCo4JFiMuu317PZwaqEBUIar4YMmskL73DytGjgu4gAt4PDJdzkkzMBloBhqBgcu69XW+1I+rNSQESNDuaMEhdP/Fj/7oW+ACLuACHk/3F5BAfuMLBjm8/ZnxNvNtHmY4b7Ztut0bqStoVSHfWj9Z6mr8LXABF3CBB3nvkDfEVN6PAAAAAElFTkSuQmCC"
      type="image/x-icon" />
  `,
  addons: [
    getAbsolutePath('@storybook/addon-links'),
    {
      name: getAbsolutePath('@storybook/addon-essentials'),
      options: {
        backgrounds: false,
      },
    },
    getAbsolutePath('@storybook/addon-interactions'),
  ],
  framework: {
    name: getAbsolutePath('@storybook/react-webpack5'),
    options: {
      builder: {
//        useSWC: true,
      },
    },
  },
  webpackFinal: config => {
    /*
      config.module?.rules?.forEach((rule) => {
        if (
          rule &&
          typeof rule === "object" &&
          rule.test instanceof RegExp &&
          rule.test.test(".svg")
        ) {
          rule.exclude = /\.svg$/;
        }
      });
    */
    if (config.module?.rules) {
      const svgLoaderRule = config.module.rules.find(rule => (rule as RuleSetRule).test && ((rule as RuleSetRule).test as RegExp).test!('.svg'));
      if (svgLoaderRule) {
        (svgLoaderRule as RuleSetRule).exclude = /\.svg$/;
      }
    }
    config.module?.rules?.push(
      {
        test: /\.tsx?$/,
        loader: 'babel-loader',
        options: {
          plugins: [
            [
              '@babel/plugin-transform-typescript',
              {
                allowDeclareFields: true,
              },
            ],
            '@babel/plugin-proposal-class-properties',
          ],
          presets: [
            [
              '@babel/preset-react',
              {
                runtime: 'automatic',
                importSource: 'react',
              },
            ],
            '@babel/preset-typescript',
          ],
          cacheDirectory: true,
        },
        exclude: /node_modules/,
      },
      {
        test: /\.jsx?$/,
        loader: 'babel-loader',
        options: {
          presets: ['@babel/preset-react'],
          cacheDirectory: true
        }
      },
      /*
      {
        // In .css files, svg is loaded as a data URI.
        test: /\.svg(\?v=\d+\.\d+\.\d+)?$/,
        issuer: /\.css$/,
        use: {
          loader: 'svg-url-loader',
          options: { encoding: 'none', limit: 10000 },
        },
      },
      */
      {
        // In .ts and .tsx files (both of which compile to .js), svg files
        // must be loaded as a raw string instead of data URIs.
        test: /\.svg(\?v=\d+\.\d+\.\d+)?$/,
        issuer: /\.js$/,
        type: 'asset/source',
      },
      {
        test: /\.svg(\?v=\d+\.\d+\.\d+)?$/,
        issuer: /\.tsx$/,
        use: [
          '@svgr/webpack'
        ],
      },
      {
        test: /\.svg(\?v=\d+\.\d+\.\d+)?$/,
        issuer: /\.mdx$/,
        use: [
          '@svgr/webpack'
        ],
      },
      {
        test: /\.m?js/,
        resolve: {
          fullySpecified: false,
        },
      },
      {
        test: /\.c?js/,
        resolve: {
          fullySpecified: false,
        },
      },
      // Rule for jupyterlite service worker
      {
        resourceQuery: /text/,
        type: 'asset/resource',
        generator: {
          filename: '[name][ext]',
        },
      },
      // Rules for pyodide kernel assets
      {
        test: /pypi\/.*/,
        type: 'asset/resource',
        generator: {
          filename: 'pypi/[name][ext][query]',
        },
      },
      {
        test: /pyodide-kernel-extension\/schema\/.*/,
        type: 'asset/resource',
        generator: {
          filename: 'schema/[name][ext][query]',
        },
      }
    );
    return config;
  },
  docs: {
    autodocs: 'tag',
  },
};

export default config;
