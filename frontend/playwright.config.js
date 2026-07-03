const { defineConfig } = require('@playwright/test');

const baseURL = process.env.BASE_URL || 'http://control_frontend:5173';

module.exports = defineConfig({
  timeout: 30_000,
  use: {
    baseURL,
    headless: true,
    viewport: { width: 1280, height: 800 },
  },
  projects: [
    { name: 'chromium', use: { browserName: 'chromium' } }
  ],
});
