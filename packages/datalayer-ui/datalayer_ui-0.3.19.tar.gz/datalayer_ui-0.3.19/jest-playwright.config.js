/*
 * Copyright (c) 2021-2024 Datalayer, Inc.
 *
 * Datalayer License
 */

module.exports = {
  launchOptions: {
    headless: true
  },
  contextOptions: {
    ignoreHTTPSErrors: true,
    viewport: {
      width: 1920,
      height: 1080
    }
  },
  browsers: [
    "chromium",
//   "firefox",
//   "webkit"
  ],
  devices: []
}
