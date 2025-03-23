/*
 * Copyright (c) 2021-2024 Datalayer, Inc.
 *
 * Datalayer License
 */

const path = require("path");
const webpack = require("webpack");

const HtmlWebpackPlugin = require("html-webpack-plugin");
const BundleAnalyzerPlugin = require('webpack-bundle-analyzer').BundleAnalyzerPlugin;

const shimJS = path.resolve(__dirname, "src", "EmptyShim.js");
function shim(regExp) {
  return new webpack.NormalModuleReplacementPlugin(regExp, shimJS);
}

const INDEX_PAGE = process.env.INDEX_PAGE ?? 'index.ejs';
const IS_PRODUCTION = process.argv.indexOf('--mode=production') > -1;

const mode = IS_PRODUCTION ? "production" : "development";
// inline-source-map | eval-source-map | source-map | inline-cheap-source-map, see https://webpack.js.org/configuration/devtool
const devtool = IS_PRODUCTION ? false : "eval-source-map";
const minimize = IS_PRODUCTION ? true : false;

const entry = process.env.ENTRY ?? {
  io: './src/IOApp',
  cli: './src/CLIApp',
}

const publicPath = IS_PRODUCTION
  ? '/static/datalayer_ui/' // This has to remain /static/datalayer_ui/
  : 'http://localhost:3063/';

// Jupyter Server URL must end with '/' for JupyterLite compatibility
let jupyterServerURL = process.env.JUPYTER_SERVER_URL ?? 'http://localhost:8686/api/jupyter-server/';
if (!jupyterServerURL.endsWith('/')) {
  jupyterServerURL += '/';
}

module.exports = {
  entry,
  output: {
    publicPath,
//    filename: '[name].[contenthash].datalayer-ui.js',
    filename: '[name].datalayer-ui.js',
  },
  mode,
  devServer: {
    port: 3063,
    client: { overlay: false },
    historyApiFallback: true,
    hot: !IS_PRODUCTION,
//    static: path.join(__dirname, "dist"),
  },
  watchOptions: {
    aggregateTimeout: 300,
    poll: 2000, // Seems to stabilise HMR file change detection
    ignored: "/node_modules/"
  },
  devtool,
  optimization: {
    minimize,
//    usedExports: true,
  },
  resolve: {
    extensions: [".ts", ".tsx", ".js", ".jsx"],
    alias: {
      path: "path-browserify",
      stream: "stream-browserify",
    },
  },
  module: {
    rules: [
      {
        test: /\.tsx?$/,
        loader: "babel-loader",
        options: {
          plugins: [
            "@babel/plugin-proposal-class-properties",
          ],
          presets: [
            ["@babel/preset-react", {
                runtime: 'automatic',
                importSource: 'react'
              },
            ],
            "@babel/preset-typescript",
          ],
          cacheDirectory: true
        },
        exclude: /node_modules/,
      },
      {
        test: /\.m?js$/,
        resolve: {
          fullySpecified: false,
        },
      },
      {
        test: /\.jsx?$/,
        loader: "babel-loader",
        options: {
          presets: ["@babel/preset-react"],
          cacheDirectory: true
        }
      },
      {
        test: /\.js$/,
        enforce: "pre",
        use: ["source-map-loader"],
      },
      {
        test: /\.css?$/i,
        use: ['style-loader', 'css-loader'],
      },
      /*
      {
        // In .css files, svg is loaded as a data URI.
        test: /\.svg(\?v=\d+\.\d+\.\d+)?$/,
        issuer: /\.css$/,
        use: {
          loader: 'svg-url-loader',
          options: { encoding: 'none', limit: 10000 }
        }
      },
      */
      {
        test: /\.svg(\?v=\d+\.\d+\.\d+)?$/,
        issuer: /\.tsx$/,
//        type: "asset/resource",
        use: [
          '@svgr/webpack',
          /*
          'url-loader',
          {
            loader: 'svg-url-loader',
            options: { encoding: 'none', limit: 10000 }
          }
          */
        ],
      },
      {
        // In .ts and .tsx files (both of which compile to .js), svg files
        // must be loaded as a raw string instead of data URIs.
        test: /\.svg(\?v=\d+\.\d+\.\d+)?$/,
        issuer: /\.js$/,
        use: {
          loader: 'raw-loader'
        }
      },
      {
        test: /\.(png|jpg|jpeg|gif|ttf|woff|woff2|eot|mp4)(\?v=[0-9]\.[0-9]\.[0-9])?$/,
        use: [{ loader: 'url-loader', options: { limit: 10000 } }],
      },
      // Special webpack rule for the JupyterLab theme style sheets.
      {
        test: /style\/theme\.css$/i,
        loader: 'css-loader',
        options: { exportType: 'string' },
      },
      // Ship the JupyterLite service worker.
      {
        resourceQuery: /text/,
        type: 'asset/resource',
        generator: {
          filename: '[name][ext]',
        },
      },
      // Rule for pyodide kernel
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
     ]
  },
  plugins: [
    !IS_PRODUCTION ?
      new webpack.ProvidePlugin({
        process: 'process/browser'
      })
    :
      new webpack.ProvidePlugin({
        process: 'process/browser'
      }),
      new BundleAnalyzerPlugin({
          analyzerMode: IS_PRODUCTION ? "static" : "disabled", // 'server' | 'static' | 'json' | 'disabled'
          openAnalyzer: false,
          generateStatsFile: false,
          reportFilename: 'bundle-analysis-report.html',
        }),
    shim(/@fortawesome/),
    shim(/moment/),
    new HtmlWebpackPlugin({
      template: 'public/' + INDEX_PAGE,
      templateParameters: {
        runUrl: process.env.DATALAYER_RUN_URL ?? "https://prod1.datalayer.run",
        jupyterServerURL,
        appName: process.env.LAB ? 'JupyterLab' : 'Datalayer Ξ Accelerated and Trusted Jupyter',
      }
    }),
  ],
};
