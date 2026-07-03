import { defineConfig } from '@playwright/test';

// When running inside the test container via `docker-compose run control_frontend`,
// use the service DNS name; from host use http://localhost:5173
const baseURL = process.env.BASE_URL || 'http://control_frontend:5173';

export default defineConfig({
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
